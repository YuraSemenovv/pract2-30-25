"""Инструмент визуализации графа зависимостей Maven."""
import argparse
import sys

from config import ConfigError, load_config
from graph import build_graph
from maven import MavenError, get_dependencies
from repo_file import read_test_repo


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Maven")
    parser.add_argument("config", help="путь к конфигу JSON")
    return parser.parse_args()


def make_maven_getter(base, root):
    """Возвращает функцию, которая скачивает зависимости пакета."""
    cache = {}

    def getter(node):
        if node not in cache:
            try:
                cache[node] = get_dependencies(base, node)
            except MavenError as error:
                if node == root:
                    raise
                print(f"Предупреждение: {error}", file=sys.stderr)
                cache[node] = []
        return cache[node]

    return getter


def make_getter(config):
    """Выбирает источник зависимостей: тестовый файл или Maven."""
    if not config["test_mode"]:
        return make_maven_getter(config["repository"], config["package"])
    repo = read_test_repo(config["repository"])
    if config["package"] not in repo:
        raise ConfigError("пакета нет в тестовом репозитории")

    def getter(node):
        return repo.get(node, [])

    return getter


def print_graph(graph):
    """Печатает граф: пакет и список его зависимостей."""
    for node, deps in graph.items():
        print(f"{node}: {' '.join(deps)}".rstrip())


def main():
    """Точка входа в программу."""
    args = parse_args()
    try:
        config = load_config(args.config)
        getter = make_getter(config)
        graph = build_graph(config["package"], getter, config["max_depth"])
    except (ConfigError, MavenError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print_graph(graph)
    return 0


if __name__ == "__main__":
    sys.exit(main())
