"""Чтение тестового репозитория из текстового файла.

Формат файла: на каждой строке пакет, двоеточие и его зависимости
через пробел. Пример:
A: B C
B: C
C:
"""


def parse_line(line, repo):
    """Разбирает одну строку файла и добавляет её в словарь."""
    line = line.strip()
    if not line:
        return
    name, _, rest = line.partition(":")
    repo[name.strip()] = rest.split()


def read_test_repo(path):
    """Читает файл и возвращает словарь: пакет -> зависимости."""
    repo = {}
    with open(path, encoding="utf-8") as file:
        for line in file:
            parse_line(line, repo)
    return repo
