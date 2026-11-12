"""Построение графа зависимостей."""
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
