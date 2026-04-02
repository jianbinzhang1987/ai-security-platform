from __future__ import annotations

import random
from typing import Optional

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanProcessor

from agentsec.processors.injection_guard import InjectionGuard
from agentsec.processors.pii_redactor import PIIRedactor
from agentsec.processors.rate_limiter import RateLimiter
from agentsec.processors.secret_scanner import SecretScanner
from agentsec.processors.security_tagger import SecurityTagger
from agentsec.utils.logger import get_logger

logger = get_logger("processors.otel")


class SensitiveFieldSpanProcessor(SpanProcessor):
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.redactor = PIIRedactor()

    def on_start(self, span, parent_context=None) -> None:
        return None

    def on_end(self, span: ReadableSpan) -> None:
        config = self.config_manager.config
        if not config.pii_redaction_enabled:
            return
        for key, value in list(span.attributes.items()):
            if isinstance(value, str):
                span._attributes[key] = self.redactor.redact_text(value, rules=config.pii_rules)

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class SecurityTagSpanProcessor(SpanProcessor):
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.secret_scanner = SecretScanner()
        self.injection_guard = InjectionGuard()

    def on_start(self, span, parent_context=None) -> None:
        config = self.config_manager.config
        tagger = SecurityTagger(config.tenant_id, config.app_id, config.risk_level)
        tagged = tagger.tag(dict(span.attributes))
        for key, value in tagged.items():
            span.set_attribute(key, value)

    def on_end(self, span: ReadableSpan) -> None:
        config = self.config_manager.config
        level = span.attributes.get("security.risk.level", "none")
        prompt = str(span.attributes.get("gen_ai.prompt", ""))
        completion = str(span.attributes.get("gen_ai.completion", ""))
        tool_input = str(span.attributes.get("mcp.input_params", ""))
        joined_text = "\n".join([prompt, completion])

        if config.secret_scan_enabled and self.secret_scanner.find_matches("\n".join([joined_text, tool_input])):
            span._attributes["security.risk.level"] = "high"
            span._attributes["security.secret_detected"] = True
            level = "high"

        if config.injection_guard_enabled and self.injection_guard.detect(prompt):
            span._attributes["security.risk.level"] = "high"
            span._attributes["security.injection_detected"] = True
            level = "high"

        if level == "none" and span.attributes.get("error.type"):
            span._attributes["security.risk.level"] = "low"

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class SamplingDecisionSpanProcessor(SpanProcessor):
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_start(self, span, parent_context=None) -> None:
        return None

    def on_end(self, span: ReadableSpan) -> None:
        config = self.config_manager.config
        level = span.attributes.get("security.risk.level", "none")
        token_count = int(span.attributes.get("gen_ai.usage.prompt_tokens", 0) or 0)
        if level in ("high", "critical"):
            span._attributes["agentsec.sampled"] = True
            return
        if token_count > config.force_sample_token_threshold:
            span._attributes["agentsec.sampled"] = True
            return
        sampled = random.random() <= config.sampling_rate
        span._attributes["agentsec.sampled"] = sampled

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class LocalTraceRecordingSpanProcessor(SpanProcessor):
    def __init__(self, trace_store):
        self.trace_store = trace_store

    def on_start(self, span, parent_context=None) -> None:
        return None

    def on_end(self, span: ReadableSpan) -> None:
        context = span.get_span_context()
        trace_id = f"{context.trace_id:032x}"
        span_data = {
            "span_id": f"{context.span_id:016x}",
            "name": span.name,
            "type": span.attributes.get("agentsec.span_type", "unknown"),
            "attributes": dict(span.attributes),
            "security.risk.level": span.attributes.get("security.risk.level", "none"),
            "vendor": span.attributes.get("gen_ai.vendor"),
            "model": span.attributes.get("gen_ai.model"),
            "tool_name": span.attributes.get("mcp.tool_name"),
            "start_time": span.start_time,
            "end_time": span.end_time,
        }
        self.trace_store.add_span(trace_id, span_data)

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class RateLimitSpanProcessor(SpanProcessor):
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.rate_limiter = RateLimiter()

    def on_start(self, span, parent_context=None) -> None:
        config = self.config_manager.config
        self.rate_limiter.token_budget_limit = config.token_budget_limit

    def on_end(self, span: ReadableSpan) -> None:
        token_cost = int(span.attributes.get("gen_ai.usage.total_tokens", 0) or 0)
        if token_cost and not self.rate_limiter.allow(token_cost):
            span._attributes["security.risk.level"] = "high"
            span._attributes["security.rate_limited"] = True

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
