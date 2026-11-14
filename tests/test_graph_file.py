"""Тесты чтения файла тестового репозитория."""

import os
import tempfile
import unittest

from src.errors import RepositoryError
from src.graph_file import load_graph_file, parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки разбора одной строки."""

    def test_valid_line(self):
        """Строка с зависимостями разбирается, повторы убираются."""
        self.assertEqual(parse_line("A: B C B", 1), ("A", ["B", "C"]))

    def test_no_dependencies(self):
        """Пакет без зависимостей записывается как 'D:'."""
        self.assertEqual(parse_line("D:", 1), ("D", []))

    def test_no_colon(self):
        """Строка без двоеточия отклоняется."""
        with self.assertRaises(RepositoryError):
            parse_line("A B", 1)

    def test_bad_name(self):
        """Имя не из одной большой буквы отклоняется."""
        with self.assertRaises(RepositoryError):
            parse_line("A: b", 1)


class LoadGraphFileTest(unittest.TestCase):
    """Проверки загрузки файла целиком."""

    def write_file(self, text):
        """Записать текст во временный файл и вернуть путь к нему."""
        handle, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_comments_and_empty_lines(self):
        """Комментарии и пустые строки пропускаются."""
        path = self.write_file("# заметка\n\nA: B\nB:\n")
        self.assertEqual(load_graph_file(path), {"A": ["B"], "B": []})

    def test_mentioned_package_is_added(self):
        """Пакет, упомянутый только как зависимость, попадает в граф."""
        path = self.write_file("A: B\n")
        self.assertEqual(load_graph_file(path), {"A": ["B"], "B": []})

    def test_duplicate_package(self):
        """Повторное описание пакета отклоняется."""
        path = self.write_file("A: B\nA: C\n")
        with self.assertRaises(RepositoryError):
            load_graph_file(path)

    def test_missing_file(self):
        """Несуществующий файл вызывает RepositoryError."""
        with self.assertRaises(RepositoryError):
            load_graph_file("no_such_file.txt")


if __name__ == "__main__":
    unittest.main()