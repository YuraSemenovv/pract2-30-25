"""Загрузка и проверка конфигурационного файла JSON."""
import json
import os

REQUIRED_KEYS = ("package", "repository", "test_mode",
                 "ascii_tree", "max_depth")
URL_PREFIXES = ("http://", "https://", "file://")
MIN_DEPTH = 0
PARTS_COUNT = 3


class ConfigError(Exception):
    """Ошибка в конфигурационном файле."""


def read_json(path):
    """Читает JSON-файл и возвращает словарь."""
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except OSError as error:
        raise ConfigError(f"не удалось открыть файл {path}: {error}")
    except ValueError as error:
        raise ConfigError(f"в файле {path} неверный JSON: {error}")
    if not isinstance(data, dict):
        raise ConfigError("в корне JSON должен быть объект")
    return data


def check_keys(data):
    """Проверяет, что все параметры есть в конфиге."""
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ConfigError(f"не задан параметр '{key}'")


def check_string(data, key):
    """Проверяет, что параметр - непустая строка."""
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"параметр '{key}' должен быть непустой строкой")


def check_bool(data, key):
    """Проверяет, что параметр - true или false."""
    if not isinstance(data[key], bool):
        raise ConfigError(f"параметр '{key}' должен быть true или false")


def check_depth(data):
    """Проверяет, что глубина - целое число не меньше нуля."""
    depth = data["max_depth"]
    if not isinstance(depth, int) or isinstance(depth, bool):
        raise ConfigError("параметр 'max_depth' должен быть целым числом")
    if depth < MIN_DEPTH:
        raise ConfigError("параметр 'max_depth' не может быть отрицательным")


def check_package(data):
    """Для настоящего Maven пакет должен быть group:artifact:version."""
    if data["test_mode"]:
        return
    parts = data["package"].split(":")
    if len(parts) != PARTS_COUNT or not all(parts):
        raise ConfigError("package должен быть вида group:artifact:version")


def check_repository(data):
    """Проверяет URL репозитория или путь к тестовому файлу."""
    repository = data["repository"]
    if data["test_mode"]:
        if not os.path.isfile(repository):
            raise ConfigError(f"файл {repository} не найден")
    elif not repository.startswith(URL_PREFIXES):
        raise ConfigError("repository должен быть URL (http, https, file)")


def load_config(path):
    """Загружает конфиг и проверяет все параметры."""
    data = read_json(path)
    check_keys(data)
    check_string(data, "package")
    check_string(data, "repository")
    check_bool(data, "test_mode")
    check_bool(data, "ascii_tree")
    check_depth(data)
    check_package(data)
    check_repository(data)
    return data
