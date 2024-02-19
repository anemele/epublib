import os.path as op
import tomllib
import uuid
from dataclasses import dataclass, field
from itertools import chain
from typing import Iterator, Optional, Self


@dataclass
class Chapter:
    title: str
    level: int
    _lines: list[str] = field(init=False)

    def __post_init__(self):
        self._lines = []

    def __lt__(self, other: Self):
        return self.level < other.level

    def append(self, line: str) -> Self:
        self._lines.append(line)
        return self

    def to_text(self):
        title = f'<h{self.level}>{self.title}</h{self.level}>'
        return title + ''.join(f'<p>{line}</p>' for line in self._lines)


@dataclass
class Manifest:
    id: str
    title: str
    language: str
    authors: list[str]

    cover: Optional[str]
    chapters: list[str]

    def __post_init__(self):
        if self.id == '':
            self.id = str(uuid.uuid4())


def _load_manifest(path: str) -> Manifest:
    with open(path, 'rb') as fp:
        sth = tomllib.load(fp)
    return Manifest(
        id=sth['id'],
        title=sth['title'],
        language=sth['language'],
        authors=sth['creators'],
        cover=sth.get('cover'),
        chapters=sth['chapters'],
    )


def parse(path: str) -> tuple[Manifest, list[Chapter]]:
    "input the manifest.toml file path"
    manifest = _load_manifest(path)
    pd = op.dirname(path)
    fps = (open(op.join(pd, chp), encoding='utf-8') for chp in manifest.chapters)
    lines = chain(*fps)
    return manifest, parse_text(lines)


def parse_text(lines: Iterator[str]) -> list[Chapter]:
    chapter_list = []

    # 设置一个初始值，避免 IDE 提示语法错误。
    # 实际情况应该是第一行就是 # 开头的标题。
    chp = Chapter('', 0)

    for line in lines:
        line = line.strip()

        if not line.startswith('#'):
            chp.append(line)
            continue

        # 此处要求标题格式一定符合 "# title"
        try:
            level, title = line.split(maxsplit=1)
        except ValueError:
            chp.append(line.lstrip('#'))
            continue

        level = len(level)
        # 最多只支持两级目录
        if level > 2:
            chp.append(line)
            continue

        chp = Chapter(title, level)
        chapter_list.append(chp)

    return chapter_list
