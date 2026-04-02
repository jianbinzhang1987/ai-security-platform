from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


class LocalFileExporter:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def export(self, spans: Iterable[object]) -> bool:
        with self.path.open("a", encoding="utf-8") as handle:
            for span in spans:
                handle.write(json.dumps(span, ensure_ascii=False) + "\n")
        return True
