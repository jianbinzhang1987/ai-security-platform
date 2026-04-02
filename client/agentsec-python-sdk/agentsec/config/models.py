from __future__ import annotations

import re
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentsec.config.defaults import (
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_COLLECTOR_URL,
    DEFAULT_CONFIG_POLL_INTERVAL,
    DEFAULT_HEARTBEAT_INTERVAL,
    DEFAULT_LOCAL_API_HOST,
    DEFAULT_LOCAL_API_PORT,
    DEFAULT_PLATFORM_URL,
    DEFAULT_SAMPLING_RATE,
)


class LocalApiConfig(BaseModel):
    enabled: bool = True
    host: str = DEFAULT_LOCAL_API_HOST
    port: int = DEFAULT_LOCAL_API_PORT


class PIIRule(BaseModel):
    name: str
    pattern: str
    action: Literal["mask", "hash", "remove"] = "mask"
    scope: List[str] = Field(default_factory=lambda: ["*"])
    enabled: bool = True

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, value: str) -> str:
        re.compile(value)
        return value


class ToolWhitelistEntry(BaseModel):
    name_pattern: str
    max_calls_per_minute: Optional[int] = None
    param_constraints: Optional[dict[str, Any]] = None


def _default_pii_rules() -> list[PIIRule]:
    return [
        PIIRule(name="email", pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", action="mask"),
        PIIRule(name="chinese_mobile", pattern=r"1[3-9]\d{9}", action="mask"),
        PIIRule(name="openai_api_key", pattern=r"sk-[A-Za-z0-9]{16,}", action="remove"),
        PIIRule(name="anthropic_api_key", pattern=r"sk-ant-[A-Za-z0-9\-]{16,}", action="remove"),
        PIIRule(name="aws_access_key", pattern=r"AKIA[0-9A-Z]{16}", action="hash"),
    ]


class AgentSecConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    version: int = 0
    tenant_id: str = "unknown"
    app_id: str = "unknown"
    sdk_version: str = "0.1.0"
    collector_url: str = DEFAULT_COLLECTOR_URL
    platform_url: str = DEFAULT_PLATFORM_URL
    config_url: Optional[str] = None
    heartbeat_url: Optional[str] = None
    local_api: LocalApiConfig = Field(default_factory=LocalApiConfig)
    sampling_rate: float = Field(default=DEFAULT_SAMPLING_RATE, ge=0.0, le=1.0, alias="sample_rate")
    pii_redaction_enabled: bool = True
    secret_scan_enabled: bool = True
    injection_guard_enabled: bool = True
    collect_llm_calls: bool = True
    collect_tool_calls: bool = True
    collect_http_calls: bool = False
    collect_db_queries: bool = False
    prompt_max_length: int = 4096
    response_max_length: int = 2048
    force_sample_token_threshold: int = 4000
    config_poll_interval: int = Field(default=DEFAULT_CONFIG_POLL_INTERVAL, ge=5)
    heartbeat_interval: int = Field(default=DEFAULT_HEARTBEAT_INTERVAL, ge=5)
    buffer_capacity: int = Field(default=DEFAULT_BUFFER_CAPACITY, ge=100)
    blocked_session_ids: List[str] = Field(default_factory=list)
    blocked_keywords: List[str] = Field(default_factory=list)
    pii_rules: List[PIIRule] = Field(default_factory=_default_pii_rules)
    tool_whitelist: List[ToolWhitelistEntry] = Field(default_factory=list)
    tool_unknown_action: Literal["alert", "block", "shadow"] = "alert"
    block_action_high: Literal["block", "alert", "shadow"] = "alert"
    block_action_critical: Literal["block", "alert", "shadow"] = "block"
    block_reply_template: str = "由于检测到异常行为，此请求已被安全系统拦截"
    token_budget_limit: Optional[int] = Field(default=None, ge=1)
    audit_log_path: Optional[str] = None
    risk_level: str = "none"
    config_version: str = "bootstrap"
    config_schema_version: str = "v1"
    otlp_protocol: Literal["grpc", "http/protobuf"] = "grpc"
    local_trace_max_size: int = Field(default=1000, ge=10, le=100000)
    spans_per_minute_window: int = Field(default=60, ge=10, le=3600)
