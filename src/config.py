"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from src.errors import ConfigError

MODE_REMOTE = "remote"
MODE_TEST = "test"
MODES = (MODE_REMOTE, MODE_TEST)

CRATE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
TEST_NAME_PATTERN = re.compile(r"^[A-Z]$")
URL_SCHEMES = ("http", "https")


@dataclass
class Config:
    """Параметры, настраиваемые пользователем."""

    package: str
    repo: str
    mode: str


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакета Cargo."
    )
    parser.add_argument(
        "--package", "-p", help="имя анализируемого пакета"
    )
    parser.add_argument(
        "--repo", "-r",
        help="URL репозитория (режим remote) "
             "или путь к файлу тестового репозитория (режим test)",
    )
    parser.add_argument(
        "--mode", "-m", default=MODE_REMOTE,
        help="режим работы: remote (по умолчанию) или test",
    )
    return parser


def check_mode(mode):
    """Проверить, что режим работы один из допустимых."""
    if mode not in MODES:
        allowed = ", ".join(MODES)
        raise ConfigError(
            f"неизвестный режим '{mode}', допустимо: {allowed}"
        )


def check_package(package, mode):
    """Проверить имя пакета с учётом режима работы."""
    if not package:
        raise ConfigError("не задано имя пакета (--package)")
    if mode == MODE_TEST:
        pattern = TEST_NAME_PATTERN
        hint = "одна большая латинская буква"
    else:
        pattern = CRATE_NAME_PATTERN
        hint = "буквы, цифры, '-' и '_', первой должна быть буква"
    if not pattern.match(package):
        raise ConfigError(
            f"некорректное имя пакета '{package}': ожидается {hint}"
        )


def check_repo(repo, mode):
    """Проверить URL репозитория или путь к файлу тестового репозитория."""
    if not repo:
        raise ConfigError("не задан репозиторий (--repo)")
    if mode == MODE_TEST:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: {repo}")
        return
    parsed = urlparse(repo)
    if parsed.scheme not in URL_SCHEMES or not parsed.netloc:
        raise ConfigError(
            f"некорректный URL '{repo}': ожидается http:// или https://"
        )


def parse_config(argv=None):
    """Разобрать параметры командной строки и проверить их.

    Args:
        argv: список аргументов; если None, берётся sys.argv[1:].

    Returns:
        Объект Config с проверенными параметрами.

    Raises:
        ConfigError: если какой-либо параметр задан неверно.
    """
    args = build_parser().parse_args(argv)
    config = Config(package=args.package, repo=args.repo, mode=args.mode)
    check_mode(config.mode)
    check_package(config.package, config.mode)
    check_repo(config.repo, config.mode)
    return config