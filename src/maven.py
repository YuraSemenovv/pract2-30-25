"""Получение зависимостей из pom-файлов репозитория Maven."""
import urllib.request
import xml.etree.ElementTree as ET

TIMEOUT = 10
PARTS_COUNT = 3
MAX_PARENTS = 10
SKIP_SCOPES = ("test", "provided", "system")


class MavenError(Exception):
    """Ошибка при работе с репозиторием Maven."""


def split_package(name):
    """Делит строку group:artifact:version на три части."""
    parts = name.split(":")
    if len(parts) != PARTS_COUNT:
        raise MavenError("пакет должен быть вида group:artifact:version")
    return parts


def make_url(base, name):
    """Собирает ссылку на pom-файл пакета."""
    group, artifact, version = split_package(name)
    path = group.replace(".", "/")
    file_name = f"{artifact}-{version}.pom"
    return "/".join([base.rstrip("/"), path, artifact, version, file_name])


def download(url):
    """Скачивает текст по ссылке."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
            return response.read().decode("utf-8")
    except (OSError, ValueError) as error:
        raise MavenError(f"не удалось скачать {url}: {error}")


def parse_xml(text):
    """Разбирает pom и убирает пространство имён из названий тегов."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise MavenError(f"неверный pom-файл: {error}")
    for element in root.iter():
        element.tag = element.tag.split("}")[-1]
    return root


def own_or_parent(root, tag):
    """Берёт значение тега у пакета или у его parent."""
    value = root.findtext(tag) or root.findtext("parent/" + tag)
    return (value or "").strip()


def get_properties(root):
    """Собирает свойства pom-файла для подстановки ${...}."""
    props = {}
    for key in ("version", "groupId"):
        value = own_or_parent(root, key)
        if value:
            props["project." + key] = value
    node = root.find("properties")
    if node is not None:
        for child in node:
            props[child.tag] = (child.text or "").strip()
    return props


def parent_name(root):
    """Возвращает group:artifact:version родителя или None."""
    node = root.find("parent")
    if node is None:
        return None
    keys = ("groupId", "artifactId", "version")
    parts = [(node.findtext(key) or "").strip() for key in keys]
    if not all(parts):
        return None
    return ":".join(parts)


def collect_properties(base, root):
    """Собирает свойства самого pom и всех его родителей."""
    props = get_properties(root)
    parent = parent_name(root)
    count = 0
    while parent and count < MAX_PARENTS:
        try:
            parent_root = parse_xml(download(make_url(base, parent)))
        except MavenError:
            break
        for key, value in get_properties(parent_root).items():
            props.setdefault(key, value)
        parent = parent_name(parent_root)
        count += 1
    return props


def resolve(value, props):
    """Подставляет значение свойства, если оно записано как ${name}."""
    value = (value or "").strip()
    if value.startswith("${") and value.endswith("}"):
        return props.get(value[2:-1], "")
    return value


def read_dependency(dep, props):
    """Превращает тег dependency в строку group:artifact:version."""
    scope = (dep.findtext("scope") or "compile").strip()
    optional = (dep.findtext("optional") or "").strip()
    if scope in SKIP_SCOPES or optional == "true":
        return None
    group = resolve(dep.findtext("groupId"), props)
    artifact = resolve(dep.findtext("artifactId"), props)
    version = resolve(dep.findtext("version"), props)
    if not (group and artifact and version):
        return None
    return f"{group}:{artifact}:{version}"


def dependencies_of(root, props):
    """Возвращает список прямых зависимостей из разобранного pom."""
    result = []
    for dep in root.findall("dependencies/dependency"):
        item = read_dependency(dep, props)
        if item:
            result.append(item)
    return result


def parse_pom(text):
    """Возвращает прямые зависимости из текста pom (без родителей)."""
    root = parse_xml(text)
    return dependencies_of(root, get_properties(root))


def get_dependencies(base, name):
    """Скачивает pom пакета и возвращает его прямые зависимости."""
    root = parse_xml(download(make_url(base, name)))
    props = collect_properties(base, root)
    return dependencies_of(root, props)
