from __future__ import annotations

import threading
import json

import httpx

from agentsec.utils.logger import get_logger

logger = get_logger("heartbeat")


class HeartbeatService:
    def __init__(self, config_manager, runtime_state, block_watcher=None, interval: int = 30):
        self.config_manager = config_manager
        self.runtime_state = runtime_state
        self.block_watcher = block_watcher
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="agentsec-heartbeat")

    def start(self) -> None:
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self.thread.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._send_heartbeat()
            self._stop_event.wait(self.interval)

    def _send_heartbeat(self) -> None:
        token = self.config_manager.token
        config = self.config_manager.config
        if not token or not config.heartbeat_url:
            return
        try:
            response = httpx.post(
                config.heartbeat_url,
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "instance_id": getattr(self.runtime_state, "instance_id", None),
                    "sdk_version": config.sdk_version,
                    "spans_sent_1m": self.runtime_state.spans_sent_recent(config.spans_per_minute_window),
                    "spans_buffered": self.runtime_state.spans_buffered,
                    "collector_connected": self.runtime_state.collector_connected,
                    "config_version": config.version,
                    "uptime_seconds": self.runtime_state.uptime_seconds(),
                },
                timeout=5.0,
            )
            if response.status_code == 401:
                self.config_manager.invalidate_token("token_invalid")
                return
            response.raise_for_status()
            self.runtime_state.set_collector_connected(True)
            payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            for command in payload.get("block_commands", []):
                if self.block_watcher is not None:
                    self.block_watcher._handle_message(json.dumps(command))
        except Exception as exc:
            self.runtime_state.set_collector_connected(False)
            logger.debug("Heartbeat failed: %s", exc)
