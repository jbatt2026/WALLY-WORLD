"""File-backed memory store: one Markdown file per memory, keyword-ranked search."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_WORD = re.compile(r"[a-z0-9']+")


@dataclass(frozen=True)
class Memory:
    slug: str
    title: str
    tags: tuple[str, ...]
    body: str


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2}


def _slugify(title: str) -> str:
    slug = "-".join(_WORD.findall(title.lower()))[:60].strip("-")
    return slug or "untitled"


class MemoryStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, title: str, body: str, tags: list[str] | None = None) -> Memory:
        tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        slug = _slugify(title)
        path = self.root / f"{slug}.md"
        n = 2
        while path.exists():
            path = self.root / f"{slug}-{n}.md"
            n += 1
        path.write_text(
            f"---\ntitle: {title}\ntags: {', '.join(tags)}\nsaved: {date.today().isoformat()}\n---\n{body.strip()}\n",
            encoding="utf-8",
        )
        return Memory(path.stem, title, tuple(tags), body.strip())

    def _load(self, path: Path) -> Memory:
        text = path.read_text(encoding="utf-8")
        title, tags, body = path.stem, (), text
        if text.startswith("---\n"):
            head, _, body = text[4:].partition("\n---\n")
            for line in head.splitlines():
                key, _, val = line.partition(":")
                if key == "title":
                    title = val.strip()
                elif key == "tags":
                    tags = tuple(t.strip() for t in val.split(",") if t.strip())
        return Memory(path.stem, title, tags, body.strip())

    def all(self) -> list[Memory]:
        return [self._load(p) for p in sorted(self.root.glob("*.md"))]

    def search(self, query: str, limit: int = 5) -> list[Memory]:
        q = _tokens(query)
        scored = []
        for m in self.all():
            score = 3 * len(q & _tokens(" ".join(m.tags))) + 2 * len(q & _tokens(m.title)) + len(q & _tokens(m.body))
            if score:
                scored.append((score, m))
        scored.sort(key=lambda s: -s[0])
        return [m for _, m in scored[:limit]]
