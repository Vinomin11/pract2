"""Построение диаграммы графа на языке PlantUML и её отображение."""

import os
import subprocess
import webbrowser
from pathlib import Path

from src.errors import RenderError

LAYOUT_LINE = "!pragma layout smetana"
ROOT_COLOR = "#LightGreen"


def to_plantuml(graph, root):
    """Преобразовать граф в текст диаграммы PlantUML.

    Каждый пакет — прямоугольник, каждая зависимость — стрелка от пакета
    к тому, от кого он зависит. Корневой пакет выделяется цветом.
    Строка LAYOUT_LINE включает встроенную раскладку Smetana, чтобы для
    отрисовки не требовался Graphviz.

    Args:
        graph: словарь {пакет: список зависимостей}.
        root: имя корневого пакета.

    Returns:
        Текст диаграммы.
    """
    aliases = {name: f"n{index}" for index, name in enumerate(graph)}
    lines = ["@startuml", LAYOUT_LINE]
    for name, alias in aliases.items():
        color = f" {ROOT_COLOR}" if name == root else ""
        lines.append(f'rectangle "{name}" as {alias}{color}')
    for name, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"{aliases[name]} --> {aliases[dependency]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def save_text(path, text):
    """Сохранить текст диаграммы в файл."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
    except OSError as error:
        raise RenderError(f"не удалось сохранить {path}: {error}") from error


def render_png(puml_path, jar_path):
    """Запустить PlantUML и получить PNG рядом с файлом диаграммы.

    Returns:
        Путь к созданному PNG-файлу.

    Raises:
        RenderError: если Java или PlantUML не удалось запустить
            либо PlantUML завершился с ошибкой.
    """
    command = ["java", "-jar", jar_path, "-tpng", puml_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except OSError as error:
        raise RenderError(f"не удалось запустить java: {error}") from error
    if result.returncode:
        raise RenderError(f"PlantUML завершился с ошибкой: {result.stderr}")
    return os.path.splitext(puml_path)[0] + ".png"


def show_image(png_path):
    """Открыть изображение в программе просмотра по умолчанию."""
    webbrowser.open(Path(png_path).resolve().as_uri())