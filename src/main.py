"""Точка входа: python -m src.main."""

import sys

from src.cargo_index import fetch_dependencies
from src.config import MODE_TEST, parse_config
from src.errors import AppError, ConfigError

EXIT_OK = 0
EXIT_ERROR = 2


def print_dependencies(package, dependencies):
    """Вывести список прямых зависимостей пакета."""
    print(f"Прямые зависимости пакета {package}:")
    for name in dependencies:
        print(f"  {name}")
    if not dependencies:
        print("  (нет)")


def run(config):
    """Выполнить работу по заданным параметрам."""
    if config.mode == MODE_TEST:
        raise ConfigError("режим test будет доступен на этапе 3")
    dependencies = fetch_dependencies(config.package, config.repo)
    print_dependencies(config.package, dependencies)


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