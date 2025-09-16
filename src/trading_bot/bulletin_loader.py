"""Utilities for loading text bulletins that will drive trading decisions."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Bulletin:
    """A structured representation of a market bulletin."""

    title: str
    content: str
    source: str
    path: Optional[pathlib.Path]

    def __post_init__(self) -> None:
        self.content = self.content.strip()


def load_bulletins(path: str | pathlib.Path) -> List[Bulletin]:
    """Load every bulletin contained in ``path``."""

    directory = pathlib.Path(path)
    if not directory.exists():
        raise FileNotFoundError(f"Bulletin directory {directory} does not exist")

    bulletins: List[Bulletin] = []
    for file_path in sorted(directory.glob("*.txt")):
        title = file_path.stem.replace("_", " ")
        content = file_path.read_text(encoding="utf-8")
        source = file_path.parent.name
        bulletins.append(Bulletin(title=title, content=content, source=source, path=file_path))

    return bulletins


def iter_bulletin_files(paths: Iterable[str | pathlib.Path]) -> List[Bulletin]:
    """Convenience helper to load bulletins from multiple directories."""

    bulletins: List[Bulletin] = []
    for path in paths:
        bulletins.extend(load_bulletins(path))
    return bulletins
