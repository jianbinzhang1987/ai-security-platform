from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Optional

import websockets

from agentsec.utils.logger import get_logger

logger = get_logger("block_watcher")


class BlockWatcher:
    RECONNECT_DELAY = 5

    def __init__(self, platform_base_url: str, token: Optional[str]):
        self._token = token
        self._ws_url = platform_base_url.rstrip("/").replace("https://", "wss://").replace("http://", "ws://") + "/ws/block"
        self._blocked_sessions: dict[str, dict] = {}
        self._lock = threading.RLock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._connected = False
        self._last_message_at: Optional[float] = None

    def start(self) -> None:
        if not self._token:
            return
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True, name="agentsec-block-watcher")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=1.0)

    def is_blocked(self, session_id: str) -> Optional[str]:
        with self._lock:
            entry = self._blocked_sessions.get(session_id)
            if not entry:
                return None
            if entry["expires_at"] < time.time():
                self._blocked_sessions.pop(session_id, None)
                return None
            return entry["reason"]

    def snapshot(self) -> dict:
        now = time.time()
        with self._lock:
            active_blocks = [
                {
                    "session_id": session_id,
                    "reason": entry["reason"],
                    "action": entry["action"],
                    "issued_at": entry["issued_at"],
                    "expires_at": entry["expires_at"],
                    "source": entry["source"],
                }
                for session_id, entry in self._blocked_sessions.items()
                if entry["expires_at"] >= now
            ]
            return {
                "active_blocks": active_blocks,
                "block_count": len(active_blocks),
                "ws_connected": self._connected,
                "last_ws_message_at": self._last_message_at,
            }

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._listen_loop())

    async def _listen_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(
                    self._ws_url,
                    additional_headers={"Authorization": f"Bearer {self._token}"},
                ) as ws:
                    self._connected = True
                    async for message in ws:
                        self._handle_message(message)
            except Exception as exc:
                self._connected = False
                logger.debug("Block watcher reconnecting: %s", exc)
                await asyncio.sleep(self.RECONNECT_DELAY)

    def _handle_message(self, message: str) -> None:
        payload = json.loads(message)
        ttl_seconds = int(payload.get("ttl_seconds", 3600))
        with self._lock:
            self._blocked_sessions[payload["session_id"]] = {
                "reason": payload.get("reason", "blocked"),
                "action": payload.get("action", "block"),
                "issued_at": payload.get("issued_at", time.time()),
                "expires_at": time.time() + ttl_seconds,
                "source": payload.get("source", "websocket"),
            }
            self._last_message_at = time.time()
