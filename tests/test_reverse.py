"""Тесты обратных зависимостей."""
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from graph import build_graph, find_reverse_deps, reverse_graph
from repo_file import read_test_repo

SIMPLE = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}


def make_getter(repo):
    """Делает функцию получения зависимостей из словаря."""
    return lambda node: repo.get(node, [])


class ReverseTest(unittest.TestCase):
    """Проверки обратных зависимостей."""

    def test_reverse_graph(self):
        result = reverse_graph(SIMPLE)
        self.assertEqual(result, {"B": ["A"], "C": ["A"], "D": ["B", "C"]})

    def test_reverse(self):
        graph = build_graph("A", make_getter(SIMPLE), 10)
        self.assertEqual(find_reverse_deps(graph, "D", 10), ["B", "C", "A"])

    def test_nobody_depends_on_root(self):
        graph = build_graph("A", make_getter(SIMPLE), 10)
        self.assertEqual(find_reverse_deps(graph, "A", 10), [])

    def test_reverse_depth(self):
        graph = build_graph("A", make_getter(SIMPLE), 10)
        self.assertEqual(find_reverse_deps(graph, "D", 1), ["B", "C"])

    def test_reverse_cycle(self):
        graph = build_graph("A", make_getter(CYCLE), 10)
        self.assertEqual(find_reverse_deps(graph, "A", 10), ["C", "B"])

    def test_reverse_big_repo(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        self.assertEqual(find_reverse_deps(repo, "G", 10),
                         ["D", "E", "B", "A"])

    def test_reverse_big_repo_leaf(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        self.assertEqual(find_reverse_deps(repo, "F", 10),
                         ["C", "A", "E", "B"])

    def test_reverse_big_repo_depth(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        self.assertEqual(find_reverse_deps(repo, "G", 1), ["D", "E"])

    def test_reverse_unknown_package(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        self.assertEqual(find_reverse_deps(repo, "Z", 10), [])


if __name__ == "__main__":
    unittest.main()
