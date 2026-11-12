"""Тесты чтения и проверки конфигурационного файла."""
import json
import os
import sys
import tempfile
import unittest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)

from config import ConfigError, load_config

GOOD = {
    "package": "junit:junit:4.13.2",
    "repository": "https://repo1.maven.org/maven2",
    "test_mode": False,
    "ascii_tree": True,
    "max_depth": 2,
}


def make_folder(test):
    """Создаёт временную папку, которая удалится после теста."""
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return folder.name


def change(**values):
    """Возвращает правильный конфиг с изменёнными параметрами."""
    data = dict(GOOD)
    data.update(values)
    return data


class ConfigTest(unittest.TestCase):
    """Проверки загрузки конфига."""

    def write(self, data):
        """Записывает данные в файл (словарь или текст), даёт путь."""
        path = os.path.join(make_folder(self), "config.json")
        with open(path, "w", encoding="utf-8") as file:
            if isinstance(data, str):
                file.write(data)
            else:
                json.dump(data, file)
        return path

    def assert_error(self, data, text):
        """Проверяет, что загрузка даёт ошибку с нужным текстом."""
        path = self.write(data)
        with self.assertRaises(ConfigError) as context:
            load_config(path)
        self.assertIn(text, str(context.exception))

    def test_good_config(self):
        path = self.write(GOOD)
        self.assertEqual(load_config(path), GOOD)

    def test_test_mode_config(self):
        repo = self.write("A: B\n")
        data = change(package="A", repository=repo, test_mode=True)
        self.assertEqual(load_config(self.write(data))["package"], "A")

    def test_no_file(self):
        path = os.path.join(make_folder(self), "none.json")
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_bad_json(self):
        self.assert_error("{ это не json", "неверный JSON")

    def test_root_not_object(self):
        self.assert_error([1, 2], "объект")

    def test_missing_key(self):
        data = change()
        del data["max_depth"]
        self.assert_error(data, "max_depth")

    def test_empty_package(self):
        self.assert_error(change(package="  "), "package")

    def test_bad_package_format(self):
        self.assert_error(change(package="junit"), "group:artifact")

    def test_bad_repository(self):
        self.assert_error(change(repository="abc"), "URL")

    def test_test_repo_not_found(self):
        data = change(package="A", repository="no/such.txt",
                      test_mode=True)
        self.assert_error(data, "не найден")

    def test_bad_bool(self):
        self.assert_error(change(test_mode="yes"), "test_mode")
        self.assert_error(change(ascii_tree=1), "ascii_tree")

    def test_bad_depth(self):
        self.assert_error(change(max_depth="3"), "целым")
        self.assert_error(change(max_depth=True), "целым")
        self.assert_error(change(max_depth=-1), "отрицательным")


if __name__ == "__main__":
    unittest.main()
