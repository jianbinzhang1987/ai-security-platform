from __future__ import annotations

from collections import OrderedDict
from threading import Lock
from typing import Optional


class LocalTraceStore:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._traces: OrderedDict[str, dict] = OrderedDict()
        self._lock = Lock()

    def add_span(self, trace_id: str, span: dict) -> None:
        with self._lock:
            if trace_id not in self._traces and len(self._traces) >= self.max_size:
                self._traces.popitem(last=False)
            trace = self._traces.setdefault(
                trace_id,
                {
                    "trace_id": trace_id,
                    "span_count": 0,
                    "span_types": [],
                    "risk_level": "none",
                    "security_events": 0,
                    "start_time": span.get("start_time"),
                    "end_time": span.get("end_time"),
                    "spans": [],
                },
            )
            trace["spans"].append(span)
            trace["span_count"] = len(trace["spans"])
            trace["span_types"] = sorted({item.get("type", "unknown") for item in trace["spans"]})
            trace["risk_level"] = self._max_risk([item.get("security.risk.level", "none") for item in trace["spans"]])
            trace["security_events"] = sum(
                1 for item in trace["spans"] if item.get("security.risk.level", "none") not in (None, "", "none")
            )
            trace["start_time"] = min(value for value in [trace.get("start_time"), span.get("start_time")] if value is not None)
            trace["end_time"] = max(value for value in [trace.get("end_time"), span.get("end_time")] if value is not None)
            self._traces.move_to_end(trace_id)

    def list_traces(
        self,
        limit: int = 10,
        offset: int = 0,
        span_type: Optional[str] = None,
        has_security_event: bool = False,
        risk_level: Optional[str] = None,
    ) -> dict:
        with self._lock:
            traces = [self._copy_trace(trace) for trace in reversed(list(self._traces.values()))]
        if span_type:
            traces = [trace for trace in traces if span_type in trace["span_types"]]
        if has_security_event:
            traces = [trace for trace in traces if trace["security_events"] > 0]
        if risk_level:
            traces = [trace for trace in traces if trace["risk_level"] == risk_level]
        total = len(traces)
        page = traces[offset : offset + limit]
        return {"items": page, "total": total, "limit": limit, "offset": offset, "has_more": offset + limit < total}

    def get_trace(self, trace_id: str) -> Optional[dict]:
        with self._lock:
            trace = self._traces.get(trace_id)
            return None if trace is None else self._copy_trace(trace)

    @staticmethod
    def _max_risk(levels: list[str]) -> str:
        order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        return max(levels, key=lambda item: order.get(item or "none", 0), default="none")

    @staticmethod
    def _copy_trace(trace: dict) -> dict:
        copied = dict(trace)
        copied["spans"] = [dict(span) for span in trace["spans"]]
        return copied
