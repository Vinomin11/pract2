"""Чтение файла тестового репозитория.

Формат файла: одна строка на пакет, имя пакета и через двоеточие его
зависимости. Имена пакетов — большие латинские буквы. Пустые строки
и строки, начинающиеся с '#', игнорируются. Пример:

    A: B C
    B: C
    C:
"""

import re

from src.errors import RepositoryError

NAME_PATTERN = re.compile(r"^[A-Z]$")
COMMENT_MARK = "#"


def parse_line(line, number):
    """Разобрать строку вида 'A: B C'.

    Returns:
        Пара (имя пакета, список его зависимостей без повторов).

    Raises:
        RepositoryError: если строка записана неверно.
    """
    name, separator, rest = line.partition(":")
    if not separator:
        raise RepositoryError(f"строка {number}: ожидается формат 'A: B C'")
    name = name.strip()
    dependencies = list(dict.fromkeys(rest.split()))
    for item in [name] + dependencies:
        if not NAME_PATTERN.match(item):
            raise RepositoryError(
                f"строка {number}: имя '{item}' должно быть "
                "одной большой латинской буквой"
            )
    return name, dependencies


def read_lines(path):
    """Прочитать файл и вернуть пары (номер строки, текст) без пустых."""
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise RepositoryError(f"не удалось прочитать {path}: {error}")
    numbered = [(number, line.strip()) for number, line in enumerate(lines, 1)]
    return [
        (number, line) for number, line in numbered
        if line and not line.startswith(COMMENT_MARK)
    ]


def load_graph_file(path):
    """Загрузить граф репозитория из файла.

    Returns:
        Словарь {пакет: список зависимостей}. Пакеты, которые только
        упомянуты как зависимости, добавляются с пустым списком.
    """
    graph = {}
    for number, line in read_lines(path):
        name, dependencies = parse_line(line, number)
        if name in graph:
            raise RepositoryError(f"строка {number}: пакет {name} уже описан")
        graph[name] = dependencies
    for dependencies in list(graph.values()):
        for name in dependencies:
            graph.setdefault(name, [])
    return graph