"""Тесты построения графа и поиска циклов."""

import unittest

from src.graph import (
    build_graph,
    find_cycle_nodes,
    lookup_in,
    reverse_dependencies,
    reverse_graph,
)


class BuildGraphTest(unittest.TestCase):
    """Проверки обхода в ширину."""

    def test_diamond(self):
        """Общая зависимость D попадает в граф один раз."""
        repository = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = build_graph("A", lookup_in(repository))
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["B"], ["D"])

    def test_bfs_order(self):
        """Пакеты идут по уровням: сначала все прямые зависимости."""
        repository = {"A": ["B", "C"], "B": ["D"], "C": ["E"]}
        graph = build_graph("A", lookup_in(repository))
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E"])

    def test_cycle_does_not_hang(self):
        """Цикл A -> B -> A не приводит к бесконечному обходу."""
        repository = {"A": ["B"], "B": ["A"]}
        graph = build_graph("A", lookup_in(repository))
        self.assertEqual(list(graph), ["A", "B"])

    def test_self_dependency(self):
        """Пакет, зависящий от себя, обрабатывается один раз."""
        graph = build_graph("A", lookup_in({"A": ["A"]}))
        self.assertEqual(graph, {"A": ["A"]})

    def test_unknown_package_has_no_dependencies(self):
        """Пакет, которого нет в репозитории, считается без зависимостей."""
        graph = build_graph("Z", lookup_in({}))
        self.assertEqual(graph, {"Z": []})

    def test_deep_chain_without_recursion(self):
        """Длинная цепочка пакетов не вызывает переполнение стека."""
        size = 5000
        repository = {str(i): [str(i + 1)] for i in range(size)}
        graph = build_graph("0", lookup_in(repository))
        self.assertEqual(len(graph), size + 1)


class CycleNodesTest(unittest.TestCase):
    """Проверки поиска пакетов в циклах."""

    def test_no_cycles(self):
        """В графе без циклов таких пакетов нет."""
        graph = {"A": ["B"], "B": []}
        self.assertEqual(find_cycle_nodes(graph), [])

    def test_cycle_members_only(self):
        """В результат попадают только пакеты цикла, а не зависящие от него."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
        self.assertEqual(find_cycle_nodes(graph), ["A", "B", "C"])

    def test_self_dependency_is_cycle(self):
        """Зависимость пакета от самого себя считается циклом."""
        self.assertEqual(find_cycle_nodes({"A": ["A"]}), ["A"])


class ReverseTest(unittest.TestCase):
    """Проверки обратных зависимостей."""

    def setUp(self):
        """Подготовить граф-ромб."""
        self.graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}

    def test_reverse_graph(self):
        """Граф переворачивается: у D появляются B и C."""
        self.assertEqual(reverse_graph(self.graph)["D"], ["B", "C"])

    def test_transitive(self):
        """От D зависят B и C напрямую и A через них."""
        result = reverse_dependencies(self.graph, "D")
        self.assertEqual(result, ["B", "C", "A"])

    def test_nobody_depends(self):
        """От корневого пакета никто не зависит."""
        self.assertEqual(reverse_dependencies(self.graph, "A"), [])

    def test_cycle(self):
        """Пакет в цикле зависит сам от себя и попадает в свой список."""
        graph = {"A": ["B"], "B": ["A"]}
        self.assertEqual(reverse_dependencies(graph, "A"), ["B", "A"])


if __name__ == "__main__":
    unittest.main()