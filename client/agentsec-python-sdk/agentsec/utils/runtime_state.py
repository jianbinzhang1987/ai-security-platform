from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Optional


@dataclass
class RuntimeState:
    initialized: bool = False
    collector_connected: bool = False
    spans_sent_total: int = 0
    spans_dropped_total: int = 0
    spans_buffered: int = 0
    last_span_sent_at: Optional[datetime] = None
    last_config_fetch_at: Optional[datetime] = None
    next_config_fetch_at: Optional[datetime] = None
    last_config_fetch_ok: bool = False
    token_status: str = "missing"
    startup_time: float = field(default_factory=time.time)
    local_api_token: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    _lock: Lock = field(default_factory=Lock, repr=False)

    def mark_initialized(self) -> None:
        with self._lock:
            self.initialized = True

    def mark_span_export(self, count: int = 1) -> None:
        with self._lock:
            self.collector_connected = True
            self.spans_sent_total += count
            self.last_span_sent_at = datetime.now(timezone.utc)

    def set_collector_connected(self, connected: bool) -> None:
        with self._lock:
            self.collector_connected = connected

    def set_buffered(self, count: int) -> None:
        with self._lock:
            self.spans_buffered = count

    def mark_span_drop(self, count: int = 1) -> None:
        with self._lock:
            self.spans_dropped_total += count

    def record_config_fetch(self, interval_seconds: int, success: bool = True) -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            self.last_config_fetch_at = now
            self.last_config_fetch_ok = success
            self.next_config_fetch_at = now.fromtimestamp(now.timestamp() + interval_seconds, tz=timezone.utc)

    def set_token_status(self, status: str) -> None:
        with self._lock:
            self.token_status = status

    def spans_sent_recent(self, window_seconds: int = 60) -> int:
        with self._lock:
            if self.last_span_sent_at is None:
                return 0
            return self.spans_sent_total if (datetime.now(timezone.utc) - self.last_span_sent_at).total_seconds() <= window_seconds else 0

    def uptime_seconds(self) -> int:
        return max(int(time.time() - self.startup_time), 0)
