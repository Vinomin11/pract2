"""Построение графа зависимостей и операции над ним."""

from collections import deque


def lookup_in(graph):
    """Вернуть функцию, которая ищет зависимости пакета в готовом графе."""
    def get_dependencies(name):
        """Вернуть список зависимостей пакета (пустой, если пакета нет)."""
        return graph.get(name, [])
    return get_dependencies


def build_graph(start, get_dependencies):
    """Построить граф зависимостей обходом в ширину (BFS) без рекурсии.

    Каждый пакет обрабатывается один раз, поэтому циклические
    зависимости не приводят к бесконечному обходу.

    Args:
        start: имя пакета, с которого начинается обход.
        get_dependencies: функция, принимающая имя пакета и возвращающая
            список его прямых зависимостей.

    Returns:
        Словарь {пакет: список зависимостей}; пакеты идут в порядке обхода.
    """
    graph = {}
    seen = {start}
    queue = deque([start])
    while queue:
        name = queue.popleft()
        dependencies = get_dependencies(name)
        graph[name] = dependencies
        for dependency in dependencies:
            if dependency not in seen:
                seen.add(dependency)
                queue.append(dependency)
    return graph


def depends_on_itself(graph, name):
    """Проверить, зависит ли пакет сам от себя (прямо или через другие)."""
    get_dependencies = lookup_in(graph)
    for dependency in graph[name]:
        if name in build_graph(dependency, get_dependencies):
            return True
    return False


def find_cycle_nodes(graph):
    """Вернуть пакеты, участвующие в циклических зависимостях."""
    return [name for name in graph if depends_on_itself(graph, name)]


def reverse_graph(graph):
    """Перевернуть граф: для каждого пакета список тех, кто от него зависит."""
    reverse = {}
    for name, dependencies in graph.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, []).append(name)
    return reverse


def reverse_dependencies(graph, package):
    """Найти пакеты, которые зависят от package прямо или через другие.

    Используется тот же обход в ширину, что и для прямых зависимостей,
    но по перевёрнутому графу. Ближайшие пакеты идут первыми.

    Args:
        graph: полный граф репозитория {пакет: список зависимостей}.
        package: пакет, для которого ищутся обратные зависимости.

    Returns:
        Список имён пакетов. Сам пакет входит в него, только если он
        зависит от себя (участвует в цикле).
    """
    found = build_graph(package, lookup_in(reverse_graph(graph)))
    result = [name for name in found if name != package]
    if depends_on_itself(graph, package):
        result.append(package)
    return result