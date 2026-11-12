"""Инструмент визуализации графа зависимостей Maven."""
import argparse
import json
import sys

from config import REQUIRED_KEYS, ConfigError, load_config


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Maven")
    parser.add_argument("config", help="путь к конфигу JSON")
    return parser.parse_args()


def print_params(config):
    """Печатает все параметры в формате ключ-значение."""
    for key in REQUIRED_KEYS:
        print(f"{key}: {json.dumps(config[key], ensure_ascii=False)}")


def main():
    """Точка входа в программу."""
    args = parse_args()
    try:
        config = load_config(args.config)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print_params(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
