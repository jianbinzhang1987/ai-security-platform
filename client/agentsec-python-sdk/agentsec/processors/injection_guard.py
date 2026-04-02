from __future__ import annotations

import re


class InjectionGuard:
    DEFAULT_PATTERNS = [
        re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt", re.IGNORECASE),
        re.compile(r"reveal\s+hidden\s+instructions", re.IGNORECASE),
    ]

    def __init__(self, patterns=None):
        self.patterns = patterns or self.DEFAULT_PATTERNS

    def detect(self, text: str) -> bool:
        return any(pattern.search(text or "") for pattern in self.patterns)
