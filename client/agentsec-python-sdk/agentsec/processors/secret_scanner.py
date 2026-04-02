from __future__ import annotations

import re


class SecretScanner:
    SECRET_PATTERNS = [
        re.compile(r"sk-[A-Za-z0-9]{16,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ]

    def find_matches(self, text: str) -> list[str]:
        matches = []
        for pattern in self.SECRET_PATTERNS:
            matches.extend(pattern.findall(text or ""))
        return matches
