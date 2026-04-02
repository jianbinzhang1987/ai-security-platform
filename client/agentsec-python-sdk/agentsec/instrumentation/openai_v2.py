from __future__ import annotations

import functools
from typing import Any

from opentelemetry import trace

from agentsec.utils.logger import get_logger

logger = get_logger("instrumentation.openai")
_patched = False


def instrument_openai() -> None:
    global _patched
    if _patched:
        return
    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

        OpenAIInstrumentor().instrument()
        _patched = True
        return
    except Exception as exc:
        logger.info("OpenAI OTel instrumentor unavailable, falling back to local patch: %s", exc)

    try:
        import openai
    except Exception as exc:
        logger.info("OpenAI instrumentation skipped: %s", exc)
        return

    patched_any = False
    candidates = []
    chat_completions = getattr(getattr(openai, "resources", None), "chat", None)
    if chat_completions is not None:
        completions = getattr(chat_completions, "completions", None)
        if completions is not None:
            candidates.append((getattr(completions, "Completions", None), "create"))
            candidates.append((getattr(completions, "AsyncCompletions", None), "create"))
    legacy_chat = getattr(openai, "ChatCompletion", None)
    if legacy_chat is not None:
        candidates.append((legacy_chat, "create"))

    for cls, method_name in candidates:
        if cls is None or not hasattr(cls, method_name):
            continue
        setattr(cls, method_name, _wrap_call(getattr(cls, method_name)))  # type: ignore[arg-type]
        patched_any = True
    _patched = patched_any
    if patched_any:
        logger.info("OpenAI instrumentation enabled via fallback wrappers")


def _wrap_call(func):
    if getattr(func, "__agentsec_wrapped__", False):
        return func

    if _is_async(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _run_in_span_async(func, args, kwargs)

        async_wrapper.__agentsec_wrapped__ = True  # type: ignore[attr-defined]
        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        return _run_in_span_sync(func, args, kwargs)

    sync_wrapper.__agentsec_wrapped__ = True  # type: ignore[attr-defined]
    return sync_wrapper


def _run_in_span_sync(func, args, kwargs):
    tracer = trace.get_tracer("agentsec.openai")
    with tracer.start_as_current_span("llm.openai.chat.completions.create") as span:
        span.set_attribute("agentsec.span_type", "llm_call")
        span.set_attribute("gen_ai.vendor", "openai")
        span.set_attribute("gen_ai.model", _extract_model(kwargs))
        span.set_attribute("gen_ai.prompt", _extract_prompt(kwargs))
        try:
            result = func(*args, **kwargs)
            _annotate_result(span, result)
            return result
        except Exception as exc:
            span.record_exception(exc)
            span.set_attribute("error.type", type(exc).__name__)
            raise


async def _run_in_span_async(func, args, kwargs):
    tracer = trace.get_tracer("agentsec.openai")
    with tracer.start_as_current_span("llm.openai.chat.completions.create") as span:
        span.set_attribute("agentsec.span_type", "llm_call")
        span.set_attribute("gen_ai.vendor", "openai")
        span.set_attribute("gen_ai.model", _extract_model(kwargs))
        span.set_attribute("gen_ai.prompt", _extract_prompt(kwargs))
        try:
            result = await func(*args, **kwargs)
            _annotate_result(span, result)
            return result
        except Exception as exc:
            span.record_exception(exc)
            span.set_attribute("error.type", type(exc).__name__)
            raise


def _extract_model(kwargs: dict[str, Any]) -> str:
    return str(kwargs.get("model", "unknown"))


def _extract_prompt(kwargs: dict[str, Any]) -> str:
    messages = kwargs.get("messages") or []
    parts: list[str] = []
    for message in messages:
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts.append(item["text"])
    return "\n".join(parts)[:4096]


def _annotate_result(span, result: Any) -> None:
    choices = getattr(result, "choices", None)
    if choices:
        contents = []
        for choice in choices:
            message = getattr(choice, "message", None)
            content = getattr(message, "content", None) if message is not None else None
            if isinstance(content, str):
                contents.append(content)
        if contents:
            span.set_attribute("gen_ai.completion", "\n".join(contents)[:2048])
    usage = getattr(result, "usage", None)
    if usage is not None:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        if prompt_tokens is not None:
            span.set_attribute("gen_ai.usage.prompt_tokens", int(prompt_tokens))
        if completion_tokens is not None:
            span.set_attribute("gen_ai.usage.completion_tokens", int(completion_tokens))
        if total_tokens is not None:
            span.set_attribute("gen_ai.usage.total_tokens", int(total_tokens))


def _is_async(func) -> bool:
    return getattr(func, "__code__", None) is not None and bool(func.__code__.co_flags & 0x80)
