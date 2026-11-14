"""Точка входа: python -m src.main."""

import sys
from dataclasses import asdict

from src.config import parse_config
from src.errors import AppError

EXIT_OK = 0
EXIT_ERROR = 2


def print_config(config):
    """Вывести параметры в формате ключ-значение."""
    for key, value in asdict(config).items():
        print(f"{key}: {value}")


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    try:
        config = parse_config(argv)
    except AppError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print_config(config)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())