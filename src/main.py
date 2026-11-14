"""Точка входа: python -m src.main."""

import sys

from src.cargo_index import fetch_dependencies
from src.config import MODE_TEST, parse_config
from src.errors import AppError, RepositoryError
from src.graph import (
    build_graph,
    find_cycle_nodes,
    lookup_in,
    reverse_dependencies,
)
from src.graph_file import load_graph_file

EXIT_OK = 0
EXIT_ERROR = 2


def load_test_repository(config):
    """Загрузить тестовый репозиторий и проверить, что в нём есть пакет."""
    repository = load_graph_file(config.repo)
    if config.package not in repository:
        raise RepositoryError(
            f"пакет {config.package} не описан в файле {config.repo}"
        )
    return repository


def make_test_getter(config):
    """Создать функцию зависимостей по файлу тестового репозитория."""
    return lookup_in(load_test_repository(config))


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


def print_reverse(package, names):
    """Вывести пакеты, которые зависят от заданного."""
    print(f"Обратные зависимости пакета {package} (кто от него зависит):")
    for name in names:
        print(f"  {name}")
    if not names:
        print("  (нет)")


def run_reverse(config):
    """Найти и вывести обратные зависимости пакета."""
    repository = load_test_repository(config)
    print_reverse(config.package, reverse_dependencies(
        repository, config.package
    ))


def run(config):
    """Выполнить работу: обратные зависимости или граф зависимостей."""
    if config.reverse:
        run_reverse(config)
        return
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