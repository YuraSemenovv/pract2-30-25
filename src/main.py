"""Инструмент визуализации графа зависимостей Maven."""
import argparse
import sys

from config import ConfigError, load_config
from graph import build_graph, find_reverse_deps
from maven import MavenError, get_dependencies
from output import ascii_tree, to_d2
from repo_file import read_test_repo


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Maven")
    parser.add_argument("config", help="путь к конфигу JSON")
    parser.add_argument("--reverse", action="store_true",
                        help="показать обратные зависимости пакета")
    parser.add_argument("--target",
                        help="для какого пакета искать обратные "
                             "зависимости (по умолчанию - package)")
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


def load_graph(config, reverse):
    """Строит граф зависимостей.

    Для обратных зависимостей в тестовом режиме берётся весь
    тестовый репозиторий, чтобы были видны все пакеты.
    """
    if reverse and config["test_mode"]:
        return read_test_repo(config["repository"])
    getter = make_getter(config)
    return build_graph(config["package"], getter, config["max_depth"])


def show_graph(config, graph):
    d2_text = to_d2(graph)

    print("=== D2 ===")
    print(d2_text)

    with open("graph.d2", "w", encoding="utf-8") as file:
        file.write(d2_text)

    if config["ascii_tree"]:
        tree = ascii_tree(graph, config["package"])
        print()
        print("=== ASCII TREE ===")
        print(tree)


def show_reverse(config, graph, target):
    """Печатает пакеты, которые зависят от target."""
    print(f"Обратные зависимости пакета {target}:")
    names = find_reverse_deps(graph, target, config["max_depth"])
    for name in names:
        print(name)
    if not names:
        print("(нет)")


def main():
    """Точка входа в программу."""
    args = parse_args()
    try:
        config = load_config(args.config)
        graph = load_graph(config, args.reverse)
    except (ConfigError, MavenError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    if args.reverse:
        show_reverse(config, graph, args.target or config["package"])
    else:
        show_graph(config, graph)
    return 0


if __name__ == "__main__":
    sys.exit(main())
