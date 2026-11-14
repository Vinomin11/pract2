"""Тесты разбора и проверки параметров командной строки."""

import os
import tempfile
import unittest

from src.config import parse_config
from src.errors import ConfigError

CRATES_URL = "https://index.crates.io"


class RemoteModeTest(unittest.TestCase):
    """Проверки режима remote."""

    def test_valid_parameters(self):
        """Корректные параметры разбираются без ошибок."""
        config = parse_config(["-p", "serde", "-r", CRATES_URL])
        self.assertEqual(config.package, "serde")
        self.assertEqual(config.repo, CRATES_URL)
        self.assertEqual(config.mode, "remote")

    def test_missing_package(self):
        """Без имени пакета возникает ошибка."""
        with self.assertRaises(ConfigError):
            parse_config(["-r", CRATES_URL])

    def test_bad_package_name(self):
        """Имя пакета с недопустимыми символами отклоняется."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "bad name!", "-r", CRATES_URL])

    def test_missing_repo(self):
        """Без URL репозитория возникает ошибка."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "serde"])

    def test_bad_url(self):
        """URL без http/https отклоняется."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "serde", "-r", "ftp://example.com"])

    def test_reverse_needs_test_mode(self):
        """Опция --reverse в режиме remote отклоняется."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "serde", "-r", CRATES_URL, "--reverse"])

    def test_unknown_mode(self):
        """Неизвестный режим работы отклоняется."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "serde", "-r", CRATES_URL, "-m", "fast"])


class TestModeTest(unittest.TestCase):
    """Проверки режима test."""

    def setUp(self):
        """Создать временный файл тестового репозитория."""
        handle, self.path = tempfile.mkstemp(suffix=".txt")
        os.close(handle)

    def tearDown(self):
        """Удалить временный файл."""
        os.remove(self.path)

    def test_valid_parameters(self):
        """Имя из одной большой буквы и существующий файл допустимы."""
        config = parse_config(["-p", "A", "-r", self.path, "-m", "test"])
        self.assertEqual(config.mode, "test")

    def test_reverse_in_test_mode(self):
        """В режиме test опция --reverse допустима."""
        args = ["-p", "A", "-r", self.path, "-m", "test", "--reverse"]
        self.assertTrue(parse_config(args).reverse)

    def test_jar_requires_output(self):
        """Для --plantuml-jar нужно указать --output."""
        args = ["-p", "A", "-r", self.path, "-m", "test",
                "--plantuml-jar", self.path]
        with self.assertRaises(ConfigError):
            parse_config(args)

    def test_missing_jar(self):
        """Несуществующий jar-файл отклоняется."""
        args = ["-p", "A", "-r", self.path, "-m", "test",
                "-o", "g.puml", "--plantuml-jar", "no_such.jar"]
        with self.assertRaises(ConfigError):
            parse_config(args)

    def test_lowercase_name(self):
        """Маленькая буква в режиме test недопустима."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "a", "-r", self.path, "-m", "test"])

    def test_missing_file(self):
        """Несуществующий файл репозитория отклоняется."""
        with self.assertRaises(ConfigError):
            parse_config(["-p", "A", "-r", "no_such.txt", "-m", "test"])


if __name__ == "__main__":
    unittest.main()