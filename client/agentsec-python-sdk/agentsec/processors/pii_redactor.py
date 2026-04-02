from __future__ import annotations

import hashlib
import re
from typing import Iterable

from agentsec.config.models import PIIRule


class PIIRedactor:
    def redact_text(self, value: str, rules: Iterable[PIIRule] | None = None) -> str:
        if not value:
            return value
        applied_rules = list(rules or [])
        if not applied_rules:
            applied_rules = [
                PIIRule(name="email", pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", action="mask"),
                PIIRule(name="phone", pattern=r"1[3-9]\d{9}", action="mask"),
                PIIRule(name="api_key", pattern=r"sk-[A-Za-z0-9]{16,}", action="remove"),
            ]
        redacted = value
        for rule in applied_rules:
            if not rule.enabled:
                continue
            if rule.action == "mask":
                redacted = re.sub(rule.pattern, self._mask_match, redacted)
            elif rule.action == "hash":
                redacted = re.sub(rule.pattern, self._hash_match, redacted)
            elif rule.action == "remove":
                redacted = re.sub(rule.pattern, "[REDACTED]", redacted)
        return redacted

    def redact(self, span: dict, rules: Iterable[PIIRule] | None = None) -> dict:
        redacted = dict(span)
        for key in ("gen_ai.prompt", "gen_ai.completion", "mcp.input_params", "mcp.output"):
            if isinstance(redacted.get(key), str):
                redacted[key] = self.redact_text(redacted[key], rules=rules)
        return redacted

    @staticmethod
    def _mask_match(match: re.Match[str]) -> str:
        value = match.group(0)
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    @staticmethod
    def _hash_match(match: re.Match[str]) -> str:
        digest = hashlib.sha256(match.group(0).encode("utf-8")).hexdigest()[:8]
        return f"[HASH:{digest}]"
