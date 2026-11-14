"""Тесты получения зависимостей из индекса реестра."""

import json
import unittest
from unittest import mock

from src import cargo_index
from src.errors import RepositoryError


def make_line(version, deps, yanked=False):
    """Собрать строку индекса для одной версии."""
    return json.dumps({"vers": version, "deps": deps, "yanked": yanked})


def dep(name, kind="normal", optional=False, package=None):
    """Собрать описание зависимости в формате индекса."""
    return {"name": name, "kind": kind, "optional": optional,
            "package": package}


class IndexPathTest(unittest.TestCase):
    """Проверки пути файла пакета в индексе."""

    def test_short_names(self):
        """Короткие имена лежат в отдельных папках."""
        self.assertEqual(cargo_index.index_path("a"), "1/a")
        self.assertEqual(cargo_index.index_path("ab"), "2/ab")
        self.assertEqual(cargo_index.index_path("abc"), "3/a/abc")

    def test_long_names(self):
        """Длинные имена раскладываются по двум папкам, регистр понижается."""
        self.assertEqual(cargo_index.index_path("Serde"), "se/rd/serde")


class DirectDependenciesTest(unittest.TestCase):
    """Проверки выбора прямых зависимостей."""

    def test_only_normal_required(self):
        """dev, build и optional зависимости пропускаются."""
        version = {"deps": [
            dep("b"), dep("a"), dep("t", kind="dev"),
            dep("c", kind="build"), dep("o", optional=True),
        ]}
        self.assertEqual(cargo_index.direct_dependencies(version), ["a", "b"])

    def test_renamed_dependency(self):
        """Для переименованной зависимости берётся настоящее имя."""
        version = {"deps": [dep("alias", package="real-name")]}
        self.assertEqual(
            cargo_index.direct_dependencies(version), ["real-name"]
        )

    def test_duplicates_removed(self):
        """Одна и та же зависимость не повторяется."""
        version = {"deps": [dep("a"), dep("a")]}
        self.assertEqual(cargo_index.direct_dependencies(version), ["a"])


class FetchDependenciesTest(unittest.TestCase):
    """Проверки полного получения зависимостей (сеть подменена)."""

    def test_latest_not_yanked_version(self):
        """Берётся последняя версия, которая не отозвана."""
        text = "\n".join([
            make_line("1.0.0", [dep("old")]),
            make_line("1.1.0", [dep("new")]),
            make_line("1.2.0", [dep("yanked")], yanked=True),
        ])
        with mock.patch.object(cargo_index, "fetch_text", return_value=text):
            result = cargo_index.fetch_dependencies("pkg", "http://x/")
        self.assertEqual(result, ["new"])

    def test_url_is_built_from_repo_and_name(self):
        """Адрес файла состоит из URL репозитория и пути пакета."""
        text = make_line("1.0.0", [])
        with mock.patch.object(
            cargo_index, "fetch_text", return_value=text
        ) as fake:
            cargo_index.fetch_dependencies("serde", "http://x/")
        fake.assert_called_once_with("http://x/se/rd/serde")

    def test_bad_index_file(self):
        """Некорректный JSON приводит к RepositoryError."""
        with self.assertRaises(RepositoryError):
            cargo_index.parse_versions("not json")

    def test_all_versions_yanked(self):
        """Если все версии отозваны, возникает ошибка."""
        with self.assertRaises(RepositoryError):
            cargo_index.pick_latest([{"yanked": True}])


if __name__ == "__main__":
    unittest.main()