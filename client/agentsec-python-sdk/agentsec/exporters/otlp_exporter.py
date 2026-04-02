from __future__ import annotations

from collections.abc import Sequence

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from agentsec.exporters.local_buffer import LocalBuffer
from agentsec.utils.logger import get_logger

logger = get_logger("exporters.otlp")


class AgentSecOTLPExporter(SpanExporter):
    def __init__(
        self,
        endpoint: str,
        token: str | None,
        runtime_state,
        buffer_capacity: int = 10000,
        protocol: str = "grpc",
    ):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._runtime_state = runtime_state
        self._buffer = LocalBuffer(capacity=buffer_capacity)
        self._protocol = protocol
        if protocol == "http/protobuf":
            self._inner = HTTPExporter(endpoint=self._normalize_http_endpoint(endpoint), headers=headers or None)
        else:
            self._inner = GRPCExporter(endpoint=self._normalize_grpc_endpoint(endpoint), headers=headers or None, insecure=endpoint.startswith("http://"))

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        sampled_spans = [span for span in spans if span.attributes.get("agentsec.sampled", True)]
        dropped = len(spans) - len(sampled_spans)
        if dropped:
            self._runtime_state.mark_span_drop(dropped)
        if not sampled_spans:
            return SpanExportResult.SUCCESS
        try:
            result = self._inner.export(sampled_spans)
            if result == SpanExportResult.SUCCESS:
                self._runtime_state.mark_span_export(len(sampled_spans))
                self._runtime_state.set_buffered(len(self._buffer.snapshot()))
                return result
        except Exception as exc:
            logger.warning("Span export failed, buffering locally: %s", exc)
        self._runtime_state.set_collector_connected(False)
        self._buffer.extend(sampled_spans)
        self._runtime_state.set_buffered(len(self._buffer.snapshot()))
        return SpanExportResult.SUCCESS

    def flush_buffer(self) -> SpanExportResult:
        pending = self._buffer.drain()
        if not pending:
            return SpanExportResult.SUCCESS
        try:
            result = self._inner.export(pending)
        except Exception as exc:
            logger.debug("Buffered span flush failed: %s", exc)
            result = SpanExportResult.FAILURE
        if result == SpanExportResult.SUCCESS:
            self._runtime_state.mark_span_export(len(pending))
            self._runtime_state.set_buffered(0)
        else:
            self._buffer.extend(pending)
            self._runtime_state.set_buffered(len(self._buffer.snapshot()))
        return result

    def shutdown(self) -> None:
        self._inner.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self._inner.force_flush(timeout_millis)

    @staticmethod
    def _normalize_http_endpoint(endpoint: str) -> str:
        normalized = endpoint.rstrip("/")
        if normalized.endswith("/v1/traces"):
            return normalized
        return normalized + "/v1/traces"

    @staticmethod
    def _normalize_grpc_endpoint(endpoint: str) -> str:
        return endpoint.replace("http://", "").replace("https://", "")
