import base64
import json
import time
import unittest

from agentsec.auth.token import TokenManager
from agentsec.config.models import AgentSecConfig, ToolWhitelistEntry
from agentsec.local_api.trace_store import LocalTraceStore
from agentsec.processors.tool_policy import ToolPolicyEnforcer


def build_token(payload: dict) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).rstrip(b"=").decode()
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"{header}.{body}.signature"


class TokenManagerTests(unittest.TestCase):
    def test_token_status_expired(self):
        token = build_token({"exp": time.time() - 60, "tenant_id": "t1", "app_id": "a1"})
        manager = TokenManager()
        self.assertEqual(manager.token_status(token), "expired")
        self.assertEqual(manager.parse_claims(token)["tenant_id"], "t1")


class ToolPolicyTests(unittest.TestCase):
    def test_tool_policy_blocks_unknown_tool(self):
        config = AgentSecConfig(
            tool_whitelist=[ToolWhitelistEntry(name_pattern="weather_*")],
            tool_unknown_action="block",
        )
        action, reason = ToolPolicyEnforcer().evaluate("shell_exec", {"cmd": "whoami"}, config)
        self.assertEqual(action, "block")
        self.assertEqual(reason, "tool_not_in_whitelist")

    def test_tool_policy_enforces_param_constraints(self):
        config = AgentSecConfig(
            tool_whitelist=[
                ToolWhitelistEntry(
                    name_pattern="weather_*",
                    param_constraints={"required_keys": ["city"], "allowed_keys": ["city"], "max_string_length": 10},
                )
            ],
            tool_unknown_action="alert",
        )
        action, reason = ToolPolicyEnforcer().evaluate("weather_query", {"city": "hangzhou"}, config)
        self.assertEqual((action, reason), ("allow", "tool_whitelist_match"))
        action, reason = ToolPolicyEnforcer().evaluate("weather_query", {"city": "hangzhou-west-lake"}, config)
        self.assertEqual((action, reason), ("alert", "tool_param_constraint_failed"))


class TraceStoreTests(unittest.TestCase):
    def test_trace_store_paginates_and_aggregates(self):
        store = LocalTraceStore(max_size=5)
        store.add_span("trace-1", {"type": "llm_call", "security.risk.level": "medium", "start_time": 1, "end_time": 2})
        store.add_span("trace-1", {"type": "tool_call", "security.risk.level": "none", "start_time": 3, "end_time": 4})
        payload = store.list_traces(limit=10, offset=0, has_security_event=True)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["items"][0]["span_count"], 2)
        self.assertEqual(payload["items"][0]["risk_level"], "medium")


if __name__ == "__main__":
    unittest.main()
