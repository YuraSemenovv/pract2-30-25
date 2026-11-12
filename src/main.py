"""Инструмент визуализации графа зависимостей Maven."""
import argparse
import sys

from config import ConfigError, load_config
from maven import MavenError, get_dependencies


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Maven")
    parser.add_argument("config", help="путь к конфигу JSON")
    return parser.parse_args()


def print_dependencies(package, dependencies):
    """Печатает прямые зависимости пакета."""
    print(f"Прямые зависимости пакета {package}:")
    if not dependencies:
        print("(нет)")
    for dep in dependencies:
        print(dep)


def main():
    """Точка входа в программу."""
    args = parse_args()
    try:
        config = load_config(args.config)
        package = config["package"]
        dependencies = get_dependencies(config["repository"], package)
    except (ConfigError, MavenError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print_dependencies(package, dependencies)
    return 0


if __name__ == "__main__":
    sys.exit(main())
