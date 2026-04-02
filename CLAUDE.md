# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Agent Runtime Security Monitoring Platform** — a 6-layer system that instruments AI agent applications (LLM calls, tool calls) via OpenTelemetry, streams telemetry through a data pipeline, and performs real-time security detection (prompt injection, behavior analysis, PII redaction). Only the client-side components are currently implemented in this repo; the server-side is designed but not yet built here.

## Repository Structure

```
client/
  agentsec-cli/          # Go CLI tool (cobra)
  agentsec-python-sdk/   # Python instrumentation SDK
third_party/             # Git submodules — do NOT edit directly
  openllmetry
  opentelemetry-collector-contrib
  opentelemetry-go
  opentelemetry-java-instrumentation
  opentelemetry-python-contrib
设计文档/                 # Architecture and design documents (Chinese)
```

## Commands

### Python SDK (`client/agentsec-python-sdk`)

```bash
# Install in editable mode
pip install -e .

# Run tests
pytest

# Run a single test file
pytest tests/test_config.py
```

### Go CLI (`client/agentsec-cli`)

```bash
# Build
make build
# or
go build -o agentsec-cli main.go

# Test
make test
# or
go test ./...

# Run a single test package
go test ./cmd/...
```

## Architecture

Data flow: **Agent → SDK instrumentation → OTel Collector (OTLP gRPC/HTTP 4317/4318) → Kafka → Security Detection Engine → ClickHouse/PostgreSQL → Alert Engine → Block/Notify/Dashboard**

### Python SDK internals (`agentsec/`)

- `config/` — Pydantic `AgentSecConfig` model (tenant_id, app_id, collector_url, sampling_rate, pii_redaction_enabled); `manager.py` polls config every 30s
- `exporters/` — `OTLPExporter` wraps `RetryExporter` (5x exponential backoff); `LocalBuffer` ring queue (10,000 spans) buffers when Collector is unreachable
- `heartbeat/` — `HeartbeatService` daemon thread fires every 30s
- `instrumentation/` — Stubs for `instrument_openai()`, `instrument_anthropic()`, `instrument_mcp()`; `bootstrap.py` wires everything together
- `local_api/` — Embedded aiohttp server on `localhost:13133` exposing `/agentsec/health`, `/agentsec/metrics`, `/agentsec/traces`
- `processors/` — `PIIRedactor` (regex, enabled by default), `BlockChecker`, `SecurityTagger`, `SamplingProcessor` run in span processor pipeline
- `utils/registration.py` — SDK self-registration with the management API on startup

### Go CLI commands

`config`, `diagnose`, `status`, `traces`, `verify` (flags: `--token`, `--enroll-key`, `--collector`, default `https://api.agentsec.io`)

## Key Conventions

- **Fail-open**: All SDK internals must be exception-isolated — SDK errors must never affect the agent's business logic.
- **Non-blocking export**: The export path adds < 5ms P99 latency. Never make synchronous blocking calls on the instrumentation hot path.
- **OTel semantic conventions**: Span attributes follow OTel conventions extended with `security.*` attributes (`security.risk.level`: none/low/medium/high/critical) and `gen_ai.*` attributes.
- **Default Collector URL**: `http://localhost:4317` (gRPC) locally; `https://api.agentsec.io` in production.
- **Multi-tenancy**: Every API call is scoped by `tenant_id`; enforced at gateway + DB row-level security.
- **Third-party submodules**: All repos under `third_party/` are git submodules. Read them for reference; never commit changes inside them.
