"""Тесты вывода в D2 и ASCII-дерева."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from output import ascii_tree, to_d2

SIMPLE = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}


class D2Test(unittest.TestCase):
    """Проверки вывода на языке D2."""

    def test_d2(self):
        text = to_d2({"A": ["B"], "B": []})
        self.assertEqual(text, '"A" -> "B"\n"B"')

    def test_d2_maven_names(self):
        text = to_d2({"org.a:a:1.0": ["org.b:b:2.0"], "org.b:b:2.0": []})
        self.assertIn('"org.a:a:1.0" -> "org.b:b:2.0"', text)

    def test_d2_cycle(self):
        text = to_d2(CYCLE)
        self.assertIn('"C" -> "A"', text)


class TreeTest(unittest.TestCase):
    """Проверки ASCII-дерева."""

    def test_tree(self):
        text = ascii_tree(SIMPLE, "A")
        expected = "A\n├── B\n│   └── D\n└── C\n    └── D"
        self.assertEqual(text, expected)

    def test_tree_only_root(self):
        self.assertEqual(ascii_tree({"A": []}, "A"), "A")

    def test_tree_cycle(self):
        text = ascii_tree(CYCLE, "A")
        self.assertTrue(text.endswith("A (цикл)"))


if __name__ == "__main__":
    unittest.main()
