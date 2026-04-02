from __future__ import annotations


class SecurityTagger:
    def __init__(self, tenant_id: str, app_id: str, risk_level: str = "none"):
        self.tenant_id = tenant_id
        self.app_id = app_id
        self.risk_level = risk_level

    def tag(self, span: dict, session_id: str | None = None) -> dict:
        tagged = dict(span)
        tagged["agentsec.tenant_id"] = self.tenant_id
        tagged["agentsec.app_id"] = self.app_id
        tagged["security.risk.level"] = self.risk_level
        if session_id:
            tagged["agentsec.session_id"] = session_id
        return tagged
