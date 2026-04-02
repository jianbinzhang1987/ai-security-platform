from __future__ import annotations

import platform
import socket
import uuid
from typing import Optional

import httpx

from agentsec.auth.token import TokenManager
from agentsec.utils.logger import get_logger

logger = get_logger("registration")


class RegistrationManager:
    """Handles auto-registration using a stable host fingerprint."""

    def __init__(self, platform_url: str, token_manager: Optional[TokenManager] = None) -> None:
        self.platform_url = platform_url.rstrip("/")
        self.token_manager = token_manager or TokenManager()

    def get_device_fingerprint(self, sdk_version: str) -> dict:
        ip = self._get_primary_ip()
        return {
            "hostname": socket.gethostname(),
            "machine_id": self._get_unique_id(),
            "os": platform.system(),
            "os_release": platform.release(),
            "arch": platform.machine(),
            "ip": ip,
            "ips": [ip],
            "sdk_version": sdk_version,
            "agent_version": sdk_version,
        }

    def _get_unique_id(self) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))

    def _get_primary_ip(self) -> str:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"

    def register_if_needed(self, sdk_version: str) -> Optional[str]:
        cached_token = self.token_manager.read_cached_token()
        if cached_token:
            return cached_token

        url = f"{self.platform_url}/api/v1/agents/auto-register"
        try:
            response = httpx.post(
                url,
                json=self.get_device_fingerprint(sdk_version),
                timeout=10.0,
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("agent_token") or payload.get("token")
            if token:
                self.token_manager.cache_token(token)
                return token
            logger.warning("Registration succeeded without agent token in response")
        except Exception as exc:
            logger.warning("Automatic registration failed: %s", exc)
        return None
