from __future__ import annotations

import functools
from typing import Any

from opentelemetry import trace

from agentsec.utils.logger import get_logger

logger = get_logger("instrumentation.anthropic")

_patched = False


def instrument_anthropic() -> None:
    global _patched
    if _patched:
        return
    try:
        from anthropic.resources.messages import AsyncMessages, Messages
    except Exception as exc:
        logger.info("Anthropic instrumentation skipped: %s", exc)
        return

    if hasattr(Messages, "create"):
        Messages.create = _wrap_sync(Messages.create)  # type: ignore[method-assign]
    if hasattr(AsyncMessages, "create"):
        AsyncMessages.create = _wrap_async(AsyncMessages.create)  # type: ignore[method-assign]
    _patched = True


def _extract_prompt(kwargs: dict[str, Any]) -> str:
    messages = kwargs.get("messages") or []
    parts = []
    for message in messages:
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
    return "\n".join(parts)[:4096]


def _extract_completion(result: Any) -> str:
    content = getattr(result, "content", None)
    if isinstance(content, list):
        values = []
        for item in content:
            text = getattr(item, "text", None)
            if isinstance(text, str):
                values.append(text)
        return "\n".join(values)[:2048]
    return str(result)[:2048]


def _wrap_sync(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        tracer = trace.get_tracer("agentsec.anthropic")
        with tracer.start_as_current_span("llm.anthropic.messages.create") as span:
            span.set_attribute("agentsec.span_type", "llm_call")
            span.set_attribute("gen_ai.vendor", "anthropic")
            span.set_attribute("gen_ai.model", kwargs.get("model", "unknown"))
            span.set_attribute("gen_ai.prompt", _extract_prompt(kwargs))
            result = func(self, *args, **kwargs)
            span.set_attribute("gen_ai.completion", _extract_completion(result))
            usage = getattr(result, "usage", None)
            if usage is not None:
                input_tokens = getattr(usage, "input_tokens", None)
                output_tokens = getattr(usage, "output_tokens", None)
                if input_tokens is not None:
                    span.set_attribute("gen_ai.usage.prompt_tokens", int(input_tokens))
                if output_tokens is not None:
                    span.set_attribute("gen_ai.usage.completion_tokens", int(output_tokens))
                    if input_tokens is not None:
                        span.set_attribute("gen_ai.usage.total_tokens", int(input_tokens) + int(output_tokens))
            return result

    return wrapper


def _wrap_async(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        tracer = trace.get_tracer("agentsec.anthropic")
        with tracer.start_as_current_span("llm.anthropic.messages.create") as span:
            span.set_attribute("agentsec.span_type", "llm_call")
            span.set_attribute("gen_ai.vendor", "anthropic")
            span.set_attribute("gen_ai.model", kwargs.get("model", "unknown"))
            span.set_attribute("gen_ai.prompt", _extract_prompt(kwargs))
            result = await func(self, *args, **kwargs)
            span.set_attribute("gen_ai.completion", _extract_completion(result))
            usage = getattr(result, "usage", None)
            if usage is not None:
                input_tokens = getattr(usage, "input_tokens", None)
                output_tokens = getattr(usage, "output_tokens", None)
                if input_tokens is not None:
                    span.set_attribute("gen_ai.usage.prompt_tokens", int(input_tokens))
                if output_tokens is not None:
                    span.set_attribute("gen_ai.usage.completion_tokens", int(output_tokens))
                    if input_tokens is not None:
                        span.set_attribute("gen_ai.usage.total_tokens", int(input_tokens) + int(output_tokens))
            return result

    return wrapper
