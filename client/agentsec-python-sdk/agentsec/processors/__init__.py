__all__ = [
    "AgentSecBlockException",
    "BlockChecker",
    "InjectionGuard",
    "LocalTraceRecordingSpanProcessor",
    "PIIRedactor",
    "RateLimiter",
    "RateLimitSpanProcessor",
    "SamplingProcessor",
    "SamplingDecisionSpanProcessor",
    "SecretScanner",
    "SecurityTagger",
    "SecurityTagSpanProcessor",
    "SensitiveFieldSpanProcessor",
    "MCPToolBlockedException",
    "ToolPolicyEnforcer",
]


def __getattr__(name):
    if name in {"AgentSecBlockException", "BlockChecker"}:
        from agentsec.processors.block_checker import AgentSecBlockException, BlockChecker

        return {"AgentSecBlockException": AgentSecBlockException, "BlockChecker": BlockChecker}[name]
    if name == "InjectionGuard":
        from agentsec.processors.injection_guard import InjectionGuard

        return InjectionGuard
    if name in {"LocalTraceRecordingSpanProcessor", "RateLimitSpanProcessor", "SamplingDecisionSpanProcessor", "SecurityTagSpanProcessor", "SensitiveFieldSpanProcessor"}:
        from agentsec.processors.otel_processors import (
            LocalTraceRecordingSpanProcessor,
            RateLimitSpanProcessor,
            SamplingDecisionSpanProcessor,
            SecurityTagSpanProcessor,
            SensitiveFieldSpanProcessor,
        )

        return {
            "LocalTraceRecordingSpanProcessor": LocalTraceRecordingSpanProcessor,
            "RateLimitSpanProcessor": RateLimitSpanProcessor,
            "SamplingDecisionSpanProcessor": SamplingDecisionSpanProcessor,
            "SecurityTagSpanProcessor": SecurityTagSpanProcessor,
            "SensitiveFieldSpanProcessor": SensitiveFieldSpanProcessor,
        }[name]
    if name == "PIIRedactor":
        from agentsec.processors.pii_redactor import PIIRedactor

        return PIIRedactor
    if name == "RateLimiter":
        from agentsec.processors.rate_limiter import RateLimiter

        return RateLimiter
    if name == "SamplingProcessor":
        from agentsec.processors.sampling_processor import SamplingProcessor

        return SamplingProcessor
    if name == "SecretScanner":
        from agentsec.processors.secret_scanner import SecretScanner

        return SecretScanner
    if name == "SecurityTagger":
        from agentsec.processors.security_tagger import SecurityTagger

        return SecurityTagger
    if name in {"MCPToolBlockedException", "ToolPolicyEnforcer"}:
        from agentsec.processors.tool_policy import MCPToolBlockedException, ToolPolicyEnforcer

        return {"MCPToolBlockedException": MCPToolBlockedException, "ToolPolicyEnforcer": ToolPolicyEnforcer}[name]
    raise AttributeError(name)
