from __future__ import annotations

from typing import Any, Optional

_runtime: Optional[Any] = None


def init():
    """Initialize the AgentSec runtime once and return the singleton."""
    global _runtime
    if _runtime is None:
        from agentsec.instrumentation.bootstrap import bootstrap

        _runtime = bootstrap()
    return _runtime


def shutdown() -> None:
    """Shutdown background services started by the runtime."""
    global _runtime
    if _runtime is not None:
        _runtime.shutdown()
        _runtime = None
