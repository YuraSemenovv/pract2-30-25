"""Тесты разбора pom-файлов и получения зависимостей."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)

from maven import MavenError, get_dependencies, make_url, parse_pom
from maven import split_package

POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <groupId>org.test</groupId>
  <version>1.0</version>
  <properties><lib.version>2.5</lib.version></properties>
  <dependencies>
    <dependency>
      <groupId>org.a</groupId><artifactId>a</artifactId>
      <version>1.1</version>
    </dependency>
    <dependency>
      <groupId>org.b</groupId><artifactId>b</artifactId>
      <version>${lib.version}</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId><artifactId>junit</artifactId>
      <version>4.0</version><scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.c</groupId><artifactId>c</artifactId>
      <version>3.0</version><optional>true</optional>
    </dependency>
  </dependencies>
</project>"""

CHILD = """<project>
  <parent>
    <groupId>org.test</groupId><artifactId>parent</artifactId>
    <version>1</version>
  </parent>
  <artifactId>child</artifactId>
  <dependencies>
    <dependency>
      <groupId>org.x</groupId><artifactId>x</artifactId>
      <version>${x.version}</version>
    </dependency>
    <dependency>
      <groupId>org.test</groupId><artifactId>self</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</project>"""

PARENT = """<project>
  <groupId>org.test</groupId><artifactId>parent</artifactId>
  <version>1</version>
  <properties><x.version>7.0</x.version></properties>
</project>"""


def write_pom(base, name, text):
    """Кладёт pom в папку так, как лежит в репозитории Maven."""
    group, artifact, version = name.split(":")
    folder = Path(base, *group.split("."), artifact, version)
    folder.mkdir(parents=True)
    file = folder / f"{artifact}-{version}.pom"
    file.write_text(text, encoding="utf-8")


class PomTest(unittest.TestCase):
    """Проверки разбора pom."""

    def test_parse_pom(self):
        deps = parse_pom(POM)
        self.assertEqual(deps, ["org.a:a:1.1", "org.b:b:2.5"])

    def test_bad_xml(self):
        with self.assertRaises(MavenError):
            parse_pom("<project>")

    def test_make_url(self):
        url = make_url("https://repo.test/maven2/", "org.a:b:1.0")
        expected = "https://repo.test/maven2/org/a/b/1.0/b-1.0.pom"
        self.assertEqual(url, expected)

    def test_bad_package(self):
        with self.assertRaises(MavenError):
            split_package("a:b")


class RepositoryTest(unittest.TestCase):
    """Проверки получения зависимостей из папки-репозитория."""

    def make_repo(self):
        """Создаёт папку-репозиторий с pom и возвращает её адрес."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        write_pom(folder.name, "org.test:child:2.0", CHILD)
        write_pom(folder.name, "org.test:parent:1", PARENT)
        return Path(folder.name).as_uri()

    def test_parent_properties(self):
        deps = get_dependencies(self.make_repo(), "org.test:child:2.0")
        self.assertEqual(deps, ["org.x:x:7.0", "org.test:self:1"])

    def test_missing_package(self):
        with self.assertRaises(MavenError):
            get_dependencies(self.make_repo(), "org.no:such:1.0")


if __name__ == "__main__":
    unittest.main()
