from __future__ import annotations

import threading
import time

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from agentsec.utils.logger import get_logger

logger = get_logger("exporters.retry")


class RetryExporter(SpanExporter):
    def __init__(self, exporter, attempts: int = 5, initial_backoff: int = 1):
        self.exporter = exporter
        self.attempts = attempts
        self.initial_backoff = initial_backoff
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._retry_loop, daemon=True, name="agentsec-export-retry")

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def export(self, spans):
        return self.exporter.export(spans)

    def _retry_loop(self) -> None:
        backoff = self.initial_backoff
        while not self._stop_event.is_set():
            try:
                result = self.exporter.flush_buffer()
                if result == SpanExportResult.SUCCESS:
                    backoff = self.initial_backoff
                else:
                    backoff = min(backoff * 2, 16)
            except Exception as exc:
                logger.debug("Retry loop flush failed: %s", exc)
                backoff = min(backoff * 2, 16)
            self._stop_event.wait(backoff)

    def shutdown(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        try:
            return self.exporter.flush_buffer() == SpanExportResult.SUCCESS
        except Exception:
            return False
