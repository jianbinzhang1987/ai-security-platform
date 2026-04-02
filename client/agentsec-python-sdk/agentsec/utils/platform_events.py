from __future__ import annotations

import platform
import socket
import uuid
from datetime import datetime, timezone

import httpx

from agentsec.utils.logger import get_logger

logger = get_logger("events")


class PlatformEventClient:
    def __init__(self, platform_url: str, token: str | None, runtime_state) -> None:
        self._platform_url = platform_url.rstrip("/")
        self._token = token
        self._runtime_state = runtime_state
        self._instance_id = f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"

    @property
    def instance_id(self) -> str:
        return self._instance_id

    def update_token(self, token: str | None) -> None:
        self._token = token

    def send_connected(self, config) -> None:
        if not self._token:
            return
        payload = {
            "instance_id": self._instance_id,
            "sdk_version": config.sdk_version,
            "sdk_language": "python",
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "arch": platform.machine(),
            "config_version": config.version,
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._post("/internal/events/agent-connected", payload)

    def send_disconnected(self, reason: str = "graceful_shutdown") -> None:
        if not self._token:
            return
        payload = {
            "instance_id": self._instance_id,
            "reason": reason,
            "uptime_seconds": self._runtime_state.uptime_seconds(),
            "disconnected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._post("/internal/events/agent-disconnected", payload)

    def _post(self, path: str, payload: dict) -> None:
        try:
            response = httpx.post(
                self._platform_url + path,
                headers={"Authorization": f"Bearer {self._token}"},
                json=payload,
                timeout=5.0,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.debug("Platform event %s failed: %s", path, exc)
