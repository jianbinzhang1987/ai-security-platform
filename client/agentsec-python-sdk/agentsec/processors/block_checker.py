from __future__ import annotations


class AgentSecBlockException(RuntimeError):
    """Raised when a blocked session attempts a guarded call."""


class BlockChecker:
    def __init__(self, blocked_session_ids: list[str] | None = None):
        self.blocked_session_ids = set(blocked_session_ids or [])

    def update(self, blocked_session_ids: list[str]) -> None:
        self.blocked_session_ids = set(blocked_session_ids)

    def check(self, session_id: str | None) -> None:
        if session_id and session_id in self.blocked_session_ids:
            raise AgentSecBlockException(f"session blocked: {session_id}")
