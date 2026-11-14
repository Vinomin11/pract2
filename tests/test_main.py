"""Сквозные тесты: запуск приложения на файлах из папки examples."""

import contextlib
import io
import os
import unittest

from src.main import EXIT_ERROR, EXIT_OK, main

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def run_app(package, example, *extra):
    """Запустить приложение в режиме test и вернуть (код, stdout, stderr)."""
    path = os.path.join(EXAMPLES, example)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(["-p", package, "-r", path, "-m", "test", *extra])
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Проверки работы приложения в режиме test."""

    def test_simple_graph(self):
        """Граф без циклов выводится полностью."""
        code, out, _ = run_app("A", "simple.txt")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("A -> B, C", out)
        self.assertIn("Циклических зависимостей нет", out)

    def test_cycle_is_reported(self):
        """Цикл находится и выводится."""
        code, out, _ = run_app("A", "cycle.txt")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("Циклические зависимости: A, B, C", out)

    def test_other_start_package(self):
        """Можно начинать обход не с A: тогда в граф входит только его часть."""
        _, out, _ = run_app("G", "big.txt")
        self.assertIn("G -> (нет)", out)
        self.assertNotIn("A ->", out)

    def test_unknown_package(self):
        """Пакет, которого нет в файле, даёт ошибку."""
        code, _, err = run_app("Q", "simple.txt")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не описан", err)


class ReverseModeTest(unittest.TestCase):
    """Проверки режима --reverse."""

    def test_reverse_simple(self):
        """Обратные зависимости D в ромбе: B, C и A."""
        code, out, _ = run_app("D", "simple.txt", "--reverse")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("  B\n  C\n  A\n", out)

    def test_reverse_nobody(self):
        """Если от пакета никто не зависит, выводится '(нет)'."""
        _, out, _ = run_app("A", "simple.txt", "--reverse")
        self.assertIn("(нет)", out)

    def test_reverse_includes_packages_outside_graph(self):
        """Учитываются все пакеты файла, в том числе не достижимые из A."""
        _, out, _ = run_app("G", "big.txt", "--reverse")
        self.assertIn("  X\n", out)

    def test_reverse_unknown_package(self):
        """Пакет, которого нет в файле, даёт ошибку."""
        code, _, err = run_app("Q", "simple.txt", "--reverse")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не описан", err)


if __name__ == "__main__":
    unittest.main()