"""Получение зависимостей пакетов Cargo из индекса реестра.

Индекс реестра (например, https://index.crates.io) хранит для каждого
пакета текстовый файл: одна строка JSON на каждую опубликованную версию.
В строке есть список зависимостей "deps".
"""

import json
import urllib.error
import urllib.request
from http import HTTPStatus

from src.errors import RepositoryError

REQUEST_TIMEOUT = 15
USER_AGENT = "dependency-graph-study/1.0"
KIND_NORMAL = "normal"
SHORT_NAME_ONE = 1
SHORT_NAME_TWO = 2
SHORT_NAME_THREE = 3


def index_path(name):
    """Вернуть путь файла пакета внутри индекса.

    Правила индекса: имя в нижнем регистре; для имён длиной 1, 2 и 3
    символа отдельные папки, для остальных две папки по 2 символа.
    """
    name = name.lower()
    if len(name) == SHORT_NAME_ONE:
        return f"1/{name}"
    if len(name) == SHORT_NAME_TWO:
        return f"2/{name}"
    if len(name) == SHORT_NAME_THREE:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


def fetch_text(url):
    """Скачать текст по URL.

    Raises:
        RepositoryError: если пакет не найден или сайт недоступен.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as page:
            return page.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == HTTPStatus.NOT_FOUND:
            raise RepositoryError(f"пакет не найден: {url}") from error
        raise RepositoryError(f"ошибка HTTP {error.code}: {url}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise RepositoryError(f"не удалось загрузить {url}: {error}") from error


def parse_versions(text):
    """Разобрать файл индекса в список версий (словарей)."""
    versions = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            versions.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise RepositoryError(f"некорректный файл индекса: {error}")
    return versions


def pick_latest(versions):
    """Выбрать последнюю опубликованную версию, не отозванную (yanked)."""
    for version in reversed(versions):
        if not version.get("yanked"):
            return version
    raise RepositoryError("у пакета нет доступных версий")


def direct_dependencies(version):
    """Вернуть отсортированные имена прямых зависимостей версии.

    Учитываются только обычные (normal) зависимости без пометки optional:
    dev- и build-зависимости, а также необязательные пропускаются.
    Если зависимость переименована, берётся настоящее имя пакета.
    """
    names = set()
    for dep in version.get("deps", []):
        kind = dep.get("kind") or KIND_NORMAL
        if kind != KIND_NORMAL or dep.get("optional"):
            continue
        names.add(dep.get("package") or dep["name"])
    return sorted(names)


def fetch_dependencies(package, repo_url):
    """Получить прямые зависимости пакета из индекса реестра.

    Args:
        package: имя пакета, например "serde".
        repo_url: адрес индекса, например "https://index.crates.io".

    Returns:
        Отсортированный список имён пакетов.
    """
    url = repo_url.rstrip("/") + "/" + index_path(package)
    versions = parse_versions(fetch_text(url))
    return direct_dependencies(pick_latest(versions))