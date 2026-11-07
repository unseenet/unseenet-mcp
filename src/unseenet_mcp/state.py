"""What the MCP server remembers between runs: how far "what's new" has read.

Kept by article number per group, not by date: Message dates are rounded
(coarse), article numbers are not. Also the author keys seen so far, so a key
that posts for the first time can be told apart. Nothing secret is kept here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

VERSION = 1


class State:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.seen: dict[str, int] = {}        # group -> highest article number reported
        self.authors: set[str] = set()        # author keys seen in any watched group
        if self.path.exists():
            data = json.loads(self.path.read_text())
            if data.get("v") == VERSION:
                self.seen = {g: int(n) for g, n in data.get("seen", {}).items()}
                self.authors = set(data.get("authors", []))

    @property
    def first_run(self) -> bool:
        return not self.seen

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump({"v": VERSION, "seen": self.seen, "authors": sorted(self.authors)}, f)
        os.replace(tmp, self.path)
