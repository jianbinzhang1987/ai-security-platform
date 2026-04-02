from __future__ import annotations

import functools
import json

from opentelemetry import trace

from agentsec.processors.tool_policy import MCPToolBlockedException, ToolPolicyEnforcer
from agentsec.utils.logger import get_logger

logger = get_logger("instrumentation.mcp")

_patched = False
_enforcer = ToolPolicyEnforcer()


def instrument_mcp() -> None:
    global _patched
    if _patched:
        return
    candidates = [
        ("mcp", "ClientSession"),
        ("mcp.client.session", "ClientSession"),
    ]
    for module_name, class_name in candidates:
        try:
            module = __import__(module_name, fromlist=[class_name])
            client_cls = getattr(module, class_name, None)
            if client_cls is None or not hasattr(client_cls, "call_tool"):
                continue
            client_cls.call_tool = _wrap_call_tool(client_cls.call_tool)  # type: ignore[method-assign]
            _patched = True
            logger.info("MCP instrumentation enabled for %s.%s", module_name, class_name)
            return
        except Exception:
            continue
    logger.info("MCP instrumentation skipped: no supported client class found")


def _get_runtime():
    try:
        from agentsec.instrumentation.bootstrap import get_runtime

        return get_runtime()
    except Exception:
        return None


def _wrap_call_tool(func):
    @functools.wraps(func)
    async def wrapper(self, tool_name, params=None, *args, **kwargs):
        tracer = trace.get_tracer("agentsec.mcp")
        config = None
        runtime = _get_runtime()
        if runtime is not None:
            config = runtime.config_manager.config
        with tracer.start_as_current_span(f"mcp.tool.{tool_name}") as span:
            span.set_attribute("agentsec.span_type", "tool_call")
            span.set_attribute("mcp.tool_name", str(tool_name))
            span.set_attribute("mcp.input_params", json.dumps(params or {}, ensure_ascii=False)[:2048])
            if config is not None:
                action, reason = _enforcer.evaluate(str(tool_name), params or {}, config)
                span.set_attribute("agentsec.tool.policy.action", action)
                span.set_attribute("agentsec.tool.policy.reason", reason)
                if action == "alert":
                    span.set_attribute("security.risk.level", "medium")
                elif action in {"block", "shadow"}:
                    span.set_attribute("security.risk.level", "high")
                    span.set_attribute("security.block_reason", reason)
                    if action == "block":
                        raise MCPToolBlockedException(f"tool blocked: {tool_name} ({reason})")
            try:
                result = await func(self, tool_name, params, *args, **kwargs)
                span.set_attribute("mcp.output", str(result)[:2048])
                return result
            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute("error.type", type(exc).__name__)
                raise

    return wrapper
