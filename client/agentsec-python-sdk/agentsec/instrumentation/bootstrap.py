from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from agentsec.blocking.watcher import BlockWatcher
from agentsec.config.manager import ConfigManager
from agentsec.exporters.otlp_exporter import AgentSecOTLPExporter
from agentsec.exporters.retry_exporter import RetryExporter
from agentsec.heartbeat.service import HeartbeatService
from agentsec.instrumentation.anthropic import instrument_anthropic
from agentsec.instrumentation.mcp_client import instrument_mcp
from agentsec.instrumentation.openai_v2 import instrument_openai
from agentsec.local_api.server import LocalApiServer
from agentsec.local_api.trace_store import LocalTraceStore
from agentsec.processors.otel_processors import (
    LocalTraceRecordingSpanProcessor,
    RateLimitSpanProcessor,
    SamplingDecisionSpanProcessor,
    SecurityTagSpanProcessor,
    SensitiveFieldSpanProcessor,
)
from agentsec.utils.logger import get_logger
from agentsec.utils.platform_events import PlatformEventClient
from agentsec.utils.runtime_state import RuntimeState

logger = get_logger("bootstrap")

_current_runtime: Optional["AgentSecRuntime"] = None


def get_runtime() -> Optional["AgentSecRuntime"]:
    return _current_runtime


@dataclass
class AgentSecRuntime:
    config_manager: ConfigManager
    runtime_state: RuntimeState
    trace_store: LocalTraceStore
    block_watcher: BlockWatcher | None = None
    tracer_provider: TracerProvider | None = None
    exporter: RetryExporter | None = None
    event_client: PlatformEventClient | None = None
    services: List[object] = field(default_factory=list)
    fail_open: bool = True

    def shutdown(self) -> None:
        if self.event_client is not None:
            self.event_client.update_token(self.config_manager.token)
            self.event_client.send_disconnected()
        for service in reversed(self.services):
            stop = getattr(service, "stop", None)
            if callable(stop):
                stop()
            else:
                shutdown = getattr(service, "shutdown", None)
                if callable(shutdown):
                    shutdown()


def bootstrap() -> AgentSecRuntime:
    """Automatic instrumentation entry point."""
    global _current_runtime

    config_manager = ConfigManager()
    runtime_state = RuntimeState()
    trace_store = LocalTraceStore(max_size=config_manager.config.local_trace_max_size)
    block_watcher = BlockWatcher(config_manager.config.platform_url, config_manager.token)
    event_client = PlatformEventClient(config_manager.config.platform_url, config_manager.token, runtime_state)
    runtime_state.instance_id = event_client.instance_id  # type: ignore[attr-defined]
    runtime = AgentSecRuntime(
        config_manager=config_manager,
        runtime_state=runtime_state,
        trace_store=trace_store,
        block_watcher=block_watcher,
        event_client=event_client,
        fail_open=config_manager.token is None,
    )
    _current_runtime = runtime
    config_manager.attach_runtime_state(runtime_state)

    instrument_openai()
    instrument_anthropic()
    instrument_mcp()

    resource = Resource.create(
        {
            "service.name": "agentsec-sdk",
            "agentsec.tenant_id": config_manager.config.tenant_id,
            "agentsec.app_id": config_manager.config.app_id,
            "agentsec.instance_id": event_client.instance_id,
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(SensitiveFieldSpanProcessor(config_manager))
    tracer_provider.add_span_processor(SecurityTagSpanProcessor(config_manager))
    tracer_provider.add_span_processor(RateLimitSpanProcessor(config_manager))
    tracer_provider.add_span_processor(SamplingDecisionSpanProcessor(config_manager))
    tracer_provider.add_span_processor(LocalTraceRecordingSpanProcessor(trace_store))

    otlp_exporter = AgentSecOTLPExporter(
        endpoint=config_manager.config.collector_url,
        token=config_manager.token,
        runtime_state=runtime_state,
        buffer_capacity=config_manager.config.buffer_capacity,
        protocol=config_manager.config.otlp_protocol,
    )
    retry_exporter = RetryExporter(otlp_exporter)
    retry_exporter.start()
    tracer_provider.add_span_processor(BatchSpanProcessor(retry_exporter))
    trace.set_tracer_provider(tracer_provider)
    runtime.tracer_provider = tracer_provider
    runtime.exporter = retry_exporter
    runtime.services.append(retry_exporter)

    config_manager.start()
    runtime.services.append(config_manager)

    config = config_manager.config
    heartbeat = HeartbeatService(
        config_manager,
        runtime_state,
        block_watcher=block_watcher,
        interval=config.heartbeat_interval,
    )
    heartbeat.start()
    runtime.services.append(heartbeat)

    block_watcher.start()
    runtime.services.append(block_watcher)

    if config.local_api.enabled:
        local_api = LocalApiServer(config_manager, runtime_state, trace_store, block_watcher)
        local_api.start()
        runtime.services.append(local_api)

    runtime_state.mark_initialized()
    event_client.send_connected(config_manager.config)
    logger.info(
        "AgentSec bootstrap completed: fail_open=%s collector=%s protocol=%s",
        runtime.fail_open,
        config.collector_url,
        config.otlp_protocol,
    )
    return runtime
