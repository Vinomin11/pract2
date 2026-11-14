"""Тесты построения диаграммы PlantUML и её отрисовки."""

import subprocess
import unittest
from unittest import mock

from src import plantuml
from src.errors import RenderError


class ToPlantumlTest(unittest.TestCase):
    """Проверки текста диаграммы."""

    def test_text(self):
        """Диаграмма содержит пакеты, стрелки и выделенный корень."""
        graph = {"A": ["B"], "B": []}
        expected = (
            "@startuml\n"
            "!pragma layout smetana\n"
            'rectangle "A" as n0 #LightGreen\n'
            'rectangle "B" as n1\n'
            "n0 --> n1\n"
            "@enduml\n"
        )
        self.assertEqual(plantuml.to_plantuml(graph, "A"), expected)

    def test_names_with_dash(self):
        """Имена с дефисом безопасны: в стрелках используются псевдонимы."""
        text = plantuml.to_plantuml({"a-b": ["c_d"], "c_d": []}, "a-b")
        self.assertIn('rectangle "a-b" as n0', text)
        self.assertIn("n0 --> n1", text)

    def test_cycle_edges(self):
        """Циклические зависимости превращаются в обычные стрелки."""
        text = plantuml.to_plantuml({"A": ["B"], "B": ["A"]}, "A")
        self.assertIn("n0 --> n1", text)
        self.assertIn("n1 --> n0", text)


class RenderPngTest(unittest.TestCase):
    """Проверки запуска PlantUML (процесс подменён)."""

    def test_success(self):
        """При успехе возвращается путь к PNG рядом с .puml."""
        done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with mock.patch.object(subprocess, "run", return_value=done) as run:
            path = plantuml.render_png("out/graph.puml", "plantuml.jar")
        self.assertEqual(path, "out/graph.png")
        command = run.call_args[0][0]
        self.assertEqual(command[:3], ["java", "-jar", "plantuml.jar"])

    def test_plantuml_failure(self):
        """Ненулевой код возврата PlantUML превращается в RenderError."""
        done = subprocess.CompletedProcess([], 1, stdout="", stderr="oops")
        with mock.patch.object(subprocess, "run", return_value=done):
            with self.assertRaises(RenderError):
                plantuml.render_png("graph.puml", "plantuml.jar")

    def test_java_missing(self):
        """Если java не установлена, возникает RenderError."""
        with mock.patch.object(subprocess, "run", side_effect=OSError("no")):
            with self.assertRaises(RenderError):
                plantuml.render_png("graph.puml", "plantuml.jar")


if __name__ == "__main__":
    unittest.main()