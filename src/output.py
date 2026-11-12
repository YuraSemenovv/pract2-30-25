"""Вывод графа: текст на языке D2 и ASCII-дерево."""

MIDDLE = "├── "
LAST = "└── "
VLINE = "│   "
SPACE = "    "


def quote(name):
    """Берёт имя пакета в кавычки для D2."""
    return '"' + name + '"'


def to_d2(graph):
    """Возвращает описание графа на языке диаграмм D2."""
    lines = []
    for node, deps in graph.items():
        if not deps:
            lines.append(quote(node))
        for dep in deps:
            lines.append(f"{quote(node)} -> {quote(dep)}")
    return "\n".join(lines)


def children_items(graph, node, prefix, path):
    """Готовит детей узла для стека (в обратном порядке)."""
    children = graph.get(node, [])
    last_index = len(children) - 1
    items = []
    for index, child in enumerate(children):
        items.append((child, prefix, index == last_index, path))
    items.reverse()
    return items


def ascii_tree(graph, root):
    """Возвращает зависимости в виде ASCII-дерева (без рекурсии)."""
    lines = [root]
    stack = children_items(graph, root, "", (root,))
    while stack:
        node, prefix, last, path = stack.pop()
        connector = LAST if last else MIDDLE
        if node in path:
            lines.append(prefix + connector + node + " (цикл)")
            continue
        lines.append(prefix + connector + node)
        new_prefix = prefix + (SPACE if last else VLINE)
        new_path = path + (node,)
        stack.extend(children_items(graph, node, new_prefix, new_path))
    return "\n".join(lines)
