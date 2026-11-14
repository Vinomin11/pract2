"""Точка входа: python -m src.main."""

import sys

from src.cargo_index import fetch_dependencies
from src.config import MODE_TEST, parse_config
from src.errors import AppError, RepositoryError
from src.graph import build_graph, find_cycle_nodes, lookup_in
from src.graph_file import load_graph_file

EXIT_OK = 0
EXIT_ERROR = 2


def make_test_getter(config):
    """Создать функцию зависимостей по файлу тестового репозитория."""
    repository = load_graph_file(config.repo)
    if config.package not in repository:
        raise RepositoryError(
            f"пакет {config.package} не описан в файле {config.repo}"
        )
    return lookup_in(repository)


def make_remote_getter(config):
    """Создать функцию зависимостей, которая обращается к реестру."""
    def get_dependencies(name):
        """Получить прямые зависимости пакета из индекса реестра."""
        return fetch_dependencies(name, config.repo)
    return get_dependencies


def make_getter(config):
    """Выбрать источник зависимостей в зависимости от режима работы."""
    if config.mode == MODE_TEST:
        return make_test_getter(config)
    return make_remote_getter(config)


def print_graph(package, graph):
    """Вывести граф зависимостей: по строке на пакет."""
    print(f"Граф зависимостей пакета {package}:")
    for name, dependencies in graph.items():
        text = ", ".join(dependencies) if dependencies else "(нет)"
        print(f"  {name} -> {text}")


def print_cycles(graph):
    """Вывести пакеты, входящие в циклы, или сообщить, что циклов нет."""
    members = find_cycle_nodes(graph)
    if members:
        print("Циклические зависимости: " + ", ".join(members))
    else:
        print("Циклических зависимостей нет")


def run(config):
    """Построить граф зависимостей пакета и вывести его."""
    graph = build_graph(config.package, make_getter(config))
    print_graph(config.package, graph)
    print_cycles(graph)


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    try:
        run(parse_config(argv))
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())