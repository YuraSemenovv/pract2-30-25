"""Тесты построения графа и чтения тестового репозитория."""
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from graph import build_graph
from repo_file import read_test_repo

SIMPLE = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}
SELF_LOOP = {"A": ["A", "B"], "B": []}


def make_getter(repo):
    """Делает функцию получения зависимостей из словаря."""
    return lambda node: repo.get(node, [])


class GraphTest(unittest.TestCase):
    """Проверки построения графа."""

    def test_bfs_order(self):
        graph = build_graph("A", make_getter(SIMPLE), 10)
        self.assertEqual(list(graph), ["A", "B", "C", "D"])

    def test_shared_dependency_once(self):
        graph = build_graph("A", make_getter(SIMPLE), 10)
        self.assertEqual(graph, SIMPLE)

    def test_cycle(self):
        graph = build_graph("A", make_getter(CYCLE), 10)
        self.assertEqual(graph, CYCLE)

    def test_self_loop(self):
        graph = build_graph("A", make_getter(SELF_LOOP), 10)
        self.assertEqual(graph, SELF_LOOP)

    def test_max_depth(self):
        graph = build_graph("A", make_getter(SIMPLE), 1)
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_zero_depth(self):
        graph = build_graph("A", make_getter(SIMPLE), 0)
        self.assertEqual(graph, {"A": []})

    def test_unknown_package_has_no_deps(self):
        graph = build_graph("Z", make_getter(SIMPLE), 5)
        self.assertEqual(graph, {"Z": []})


class RepoFileTest(unittest.TestCase):
    """Проверки чтения файлов тестового репозитория."""

    def test_cycle_file(self):
        repo = read_test_repo(os.path.join(HERE, "repo_cycle.txt"))
        self.assertEqual(repo, CYCLE)

    def test_big_file(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        self.assertEqual(repo["E"], ["G", "A"])
        self.assertEqual(repo["G"], [])

    def test_big_file_graph(self):
        repo = read_test_repo(os.path.join(HERE, "repo_big.txt"))
        graph = build_graph("A", make_getter(repo), 10)
        self.assertEqual(sorted(graph), list("ABCDEFG"))


if __name__ == "__main__":
    unittest.main()
