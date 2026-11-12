"""Построение графа зависимостей и обратные зависимости."""
from collections import deque


def build_graph(start, get_deps, max_depth):
    """Строит граф обходом в ширину (BFS) без рекурсии.

    Возвращает словарь: пакет -> список его зависимостей.
    Пакеты на глубине max_depth не раскрываются.
    Уже посещённые пакеты не обходятся второй раз, поэтому
    циклические зависимости не вызывают зацикливания.
    """
    graph = {}
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            graph[node] = []
            continue
        deps = get_deps(node)
        graph[node] = deps
        for dep in deps:
            if dep not in visited:
                visited.add(dep)
                queue.append((dep, depth + 1))
    return graph


def reverse_graph(graph):
    """Переворачивает граф: пакет -> те, кто от него зависит."""
    result = {}
    for node, deps in graph.items():
        for dep in deps:
            result.setdefault(dep, []).append(node)
    return result


def find_reverse_deps(graph, target, max_depth):
    """Находит все пакеты, которые зависят от target.

    Для обхода используется тот же алгоритм BFS.
    """
    reversed_graph = reverse_graph(graph)

    def get_parents(node):
        return reversed_graph.get(node, [])

    found = build_graph(target, get_parents, max_depth)
    return [node for node in found if node != target]
