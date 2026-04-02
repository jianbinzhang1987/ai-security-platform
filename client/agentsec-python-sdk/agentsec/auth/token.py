from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any, Optional


class TokenManager:
    CACHE_PATH = Path.home() / ".agentsec" / "agent.token"

    def load_token(self) -> Optional[str]:
        token = os.getenv("AGENTSEC_TOKEN")
        if token:
            return token.strip()
        return self.read_cached_token()

    def read_cached_token(self) -> Optional[str]:
        try:
            if self.CACHE_PATH.exists():
                token = self.CACHE_PATH.read_text(encoding="utf-8").strip()
                return token or None
        except OSError:
            return None
        return None

    def cache_token(self, token: str) -> None:
        self.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CACHE_PATH.write_text(token.strip(), encoding="utf-8")

    def clear_cached_token(self) -> None:
        try:
            self.CACHE_PATH.unlink(missing_ok=True)
        except OSError:
            return

    def parse_claims(self, token: str) -> dict[str, Any]:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        try:
            decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
            return json.loads(decoded.decode("utf-8"))
        except Exception:
            return {}

    def token_status(self, token: Optional[str]) -> str:
        if not token:
            return "missing"
        claims = self.parse_claims(token)
        if not claims:
            return "invalid"
        exp = claims.get("exp")
        if exp is None:
            return "valid"
        try:
            if float(exp) <= time.time():
                return "expired"
        except (TypeError, ValueError):
            return "invalid"
        return "valid"
