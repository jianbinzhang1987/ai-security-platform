from __future__ import annotations


class RateLimiter:
    def __init__(self, token_budget_limit: int | None = None):
        self.token_budget_limit = token_budget_limit
        self.current_tokens = 0

    def allow(self, token_cost: int) -> bool:
        if self.token_budget_limit is None:
            return True
        if self.current_tokens + token_cost > self.token_budget_limit:
            return False
        self.current_tokens += token_cost
        return True
