from __future__ import annotations

import fnmatch
import time
from collections import deque
from threading import Lock
from typing import Any

from agentsec.config.models import AgentSecConfig, ToolWhitelistEntry


class MCPToolBlockedException(RuntimeError):
    """Raised when a tool call is blocked by local policy."""


class ToolPolicyEnforcer:
    def __init__(self) -> None:
        self._calls: dict[str, deque[float]] = {}
        self._lock = Lock()

    def evaluate(self, tool_name: str, params: dict[str, Any] | None, config: AgentSecConfig) -> tuple[str, str]:
        if not config.tool_whitelist:
            return "allow", "tool_whitelist_disabled"

        params = params or {}
        for entry in config.tool_whitelist:
            if not fnmatch.fnmatch(tool_name, entry.name_pattern):
                continue
            if self._is_rate_limited(tool_name, entry):
                return config.tool_unknown_action, "tool_rate_limited"
            if not self._validate_constraints(params, entry):
                return config.tool_unknown_action, "tool_param_constraint_failed"
            return "allow", "tool_whitelist_match"
        return config.tool_unknown_action, "tool_not_in_whitelist"

    def _is_rate_limited(self, tool_name: str, entry: ToolWhitelistEntry) -> bool:
        if not entry.max_calls_per_minute:
            return False
        now = time.time()
        with self._lock:
            history = self._calls.setdefault(tool_name, deque())
            while history and now - history[0] > 60:
                history.popleft()
            if len(history) >= entry.max_calls_per_minute:
                return True
            history.append(now)
            return False

    @staticmethod
    def _validate_constraints(params: dict[str, Any], entry: ToolWhitelistEntry) -> bool:
        constraints = entry.param_constraints or {}
        allowed_keys = constraints.get("allowed_keys")
        required_keys = constraints.get("required_keys")
        max_string_length = constraints.get("max_string_length")
        if allowed_keys is not None and any(key not in set(allowed_keys) for key in params):
            return False
        if required_keys is not None and any(key not in params for key in required_keys):
            return False
        if max_string_length is not None:
            for value in params.values():
                if isinstance(value, str) and len(value) > int(max_string_length):
                    return False
        return True
