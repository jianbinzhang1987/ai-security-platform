# AI Agent 安全监控平台 — 管理端技术概要设计文档

**文档编号**：AGENTSEC-TECH-ADMIN-OVR-v1.0  
**版本**：v1.0  
**日期**：2026-03  
**状态**：评审中  
**关联文档**：架构设计文档 v1.0 / 管理端 PRD v1.0

---

## 1. 文档目的与范围

本文档描述 AI Agent 安全监控平台**管理端侧**（Admin Side）的技术概要设计，涵盖：

- 技术语言与运行时选型
- 核心开源组件与技术栈选型
- 整体服务架构与代码结构规划
- 关键技术决策与稳定性保障策略

管理端是平台的服务核心，运行在平台自身的基础设施上，负责接收海量 span 事件、执行安全检测、存储分析数据、触发响应动作，并提供安全运营控制台。

---

## 2. 技术语言选型

### 2.1 选型原则

| 原则 | 说明 |
|------|------|
| 性能优先 | 高并发数据管道、检测引擎需要高性能语言 |
| 生态匹配 | 安全检测组件（NeMo/LlamaFirewall/LLM Guard）以 Python 为主，需 Python 服务承载 |
| 可观测性 | 所有服务原生支持 Prometheus metrics 暴露 |
| 运维友好 | Go 编译为静态二进制，容器化部署体积小；Java 可选用于特定场景 |

### 2.2 各服务语言分配

| 服务 | 语言 | 版本要求 | 选型理由 |
|------|------|----------|----------|
| API 网关服务 | Go | >= 1.21 | 高并发 HTTP 处理，低延迟，静态编译部署简单 |
| 配置服务 | Go | >= 1.21 | 轻量，配置下发低延迟 |
| Agent 注册服务 | Go | >= 1.21 | 高并发注册场景 |
| 心跳服务 | Go | >= 1.21 | 高频心跳处理（万级 Agent） |
| 阻断指令服务 | Go | >= 1.21 | WebSocket 长连接管理，低延迟指令下发 |
| 安全检测引擎（Prompt 检测） | Python | >= 3.10 | NeMo Guardrails / LlamaFirewall / LLM Guard 均为 Python 库 |
| 安全检测引擎（行为序列分析） | Python | >= 3.10 | 图计算、序列建模，numpy/networkx 生态成熟 |
| 告警规则引擎 | Go | >= 1.21 | 高频规则匹配，低延迟告警触发 |
| 查询 API 服务 | Go | >= 1.21 | ClickHouse/OpenSearch 查询，高并发接口 |
| 报告生成服务 | Python | >= 3.10 | PDF 生成（WeasyPrint），数据聚合（pandas） |
| 任务调度服务 | Go | >= 1.21 | 定时任务（周报/月报/TTL 清理） |
| 控制台前端 | React + TypeScript | React >= 18 | 现代化安全运营控制台，TypeScript 类型安全 |

---

## 3. 核心技术组件选型

### 3.1 数据管道层

| 组件 | 版本 | 用途 | 部署方式 |
|------|------|------|----------|
| OpenTelemetry Collector Contrib | >= 0.90 | 统一数据接收（OTLP gRPC/HTTP），Processor 处理链，多路由 Exporter | K8s StatefulSet，多副本 |
| Apache Kafka | >= 3.5 | 异步事件流总线，解耦 Collector 与检测引擎，支持高吞吐 span 缓冲与重放 | K8s StatefulSet，3 Broker |
| LiteLLM Proxy | >= 1.40 | LLM API 透明代理（层2），拦截 LLM 调用，内置 logging/guardrails | K8s Deployment |

### 3.2 安全检测层

| 组件 | 版本 | 用途 | 部署方式 |
|------|------|------|----------|
| NeMo Guardrails | >= 0.9 | Prompt 注入检测（直接注入）；可编程 input/dialog/output rails | Python 检测服务 |
| LlamaFirewall (Meta) | >= 0.1 | 间接 Prompt 注入（PromptGuard 模型）；意图对齐审计（AlignmentCheck，少样本 CoT） | Python 检测服务 |
| LLM Guard | >= 0.3 | Response PII 扫描；毒性内容检测；相关性检测 | Python 检测服务 |
| Guardrails AI | >= 0.5 | 输出结构验证；RAIL 规范；Guardrails Hub 预构建验证器 | Python 检测服务 |
| Falco | >= 0.36 | 容器/进程/文件系统异常检测（行为基线补充） | DaemonSet |

### 3.3 存储层

| 组件 | 版本 | 用途 | 部署方式 |
|------|------|------|----------|
| ClickHouse | >= 23.x | 时序事件主存储（agent_spans 表），列式存储，时序聚合查询极快 | K8s StatefulSet，2 副本 |
| OpenSearch | >= 2.x | Prompt 内容全文检索；告警 Dashboard；告警规则引擎 | K8s StatefulSet，3 节点 |
| PostgreSQL | >= 15.x | 业务元数据（租户/Agent/规则/配置/告警）结构化存储 | K8s StatefulSet，主从复制 |
| Redis | >= 7.x | 阻断指令存储（TTL）；实时限流计数器；配置版本缓存；会话状态 | K8s StatefulSet，Sentinel 模式 |
| MinIO | >= RELEASE.2024 | 冷数据对象存储（> 30 天 span 数据）；报告 PDF 存储 | K8s 或独立部署 |

### 3.4 可观测性层

| 组件 | 版本 | 用途 |
|------|------|------|
| Langfuse | >= 2.x | LLM Agent 调用链 Trace 可视化，原生 OTel 支持，开源可自部署 |
| Grafana | >= 10.x | 平台自监控看板（Collector QPS、Kafka Lag、ClickHouse 写入速度） |
| Prometheus | >= 2.x | 指标采集（所有服务暴露 /metrics） |

### 3.5 认证与授权层

| 组件 | 版本 | 用途 |
|------|------|------|
| Keycloak | >= 22.x | OAuth2 / OIDC / MFA / LDAP / SSO 完整支持，RBAC 集成 |
| JWKS / JWT | - | 服务间认证（Go 标准库 + github.com/golang-jwt/jwt） |

### 3.6 部署与基础设施

| 组件 | 版本 | 用途 |
|------|------|------|
| Kubernetes | >= 1.27 | 容器编排，所有服务统一部署 |
| Helm | >= 3.12 | 平台一键部署，values.yaml 统一配置 |
| Flyway | >= 9.x | PostgreSQL schema 版本管理，Helm upgrade 时自动 migration |
| Nginx Ingress | >= 1.9 | 统一入口，TLS 终止，请求路由 |

---

## 4. 整体架构设计

### 4.1 管理端服务总体架构

```
                        ┌──────────────────────────────────────────┐
  客户端 SDK            │           Nginx Ingress（TLS 终止）       │
  ─────────────────────►│  /otlp/...  /api/v1/...  /console/...    │
                        └──────┬─────────────────────┬─────────────┘
                               │                     │
              ┌────────────────▼──────┐   ┌──────────▼──────────────┐
              │  OTel Collector 集群   │   │   API 网关服务（Go）      │
              │  (StatefulSet, 3副本)  │   │   认证/限流/路由/审计日志 │
              │  OTLP gRPC:4317       │   └──────────┬──────────────┘
              │  OTLP HTTP:4318       │              │
              └────────┬──────────────┘              │
                       │ Processor 链                 │ REST API
                       │ (PII脱敏/安全标签/采样)      │
                       ▼                             │
              ┌────────────────────┐                 │
              │    Kafka 集群       │                 │
              │  (3 Broker)         │                 │
              │  Topic: agentsec-  │                 │
              │  spans             │                 │
              └─────┬──────────────┘                 │
                    │                                │
       ┌────────────┼──────────────┐                 │
       │            │              │                 │
       ▼            ▼              ▼                 │
  ┌─────────┐ ┌──────────┐ ┌──────────────┐         │
  │ClickHouse│ │OpenSearch│ │ 安全检测引擎  │         │
  │ 写入服务 │ │ 写入服务  │ │  (Python)    │         │
  │ (Go)    │ │  (Go)    │ │  Prompt检测  │         │
  └─────────┘ └──────────┘ │  MCP审计     │         │
       │            │       │  行为序列    │         │
       │            │       │  意图对齐    │         │
       │            │       └──────┬───────┘         │
       │            │              │ 风险事件          │
       │            │              ▼                  │
       │            │       ┌─────────────┐           │
       │            │       │ 告警规则引擎  │           │
       │            │       │   (Go)       │           │
       │            │       └──────┬───────┘           │
       │            │              │                   │
       │            │              ▼                   │
       │            │       ┌─────────────┐            │
       │            │       │ 通知/阻断服务 │            │
       │            │       │   (Go)       │            │
       │            │       └─────────────┘            │
       │            │                                  │
       └────────────┼─────────────────────────────────►│
                    │                          查询 API 服务(Go)
                    │                              │
                    │                              ▼
                    │                       ┌─────────────┐
                    └──────────────────────►│  控制台前端   │
                                           │React+TypeScript│
                                           └─────────────┘

   PostgreSQL（元数据）   Redis（缓存/阻断）  Keycloak（认证）
```

### 4.2 检测引擎架构

检测引擎分为四个子引擎，各自作为独立 Python 服务从 Kafka 消费数据：

```
Kafka: agentsec-spans
       │
       ├─► [Prompt 检测消费者] ────► NeMo Guardrails（注入检测）
       │                       ────► LlamaFirewall PromptGuard（间接注入）
       │                       ────► LLM Guard（PII/毒性扫描）
       │                       ────► 越狱模式库匹配
       │                       └──► risk_events 写入 PostgreSQL
       │
       ├─► [MCP 审计消费者] ─────► 白名单/黑名单校验
       │                     ────► 参数危险模式扫描（SQL注入/路径穿越/SSRF）
       │                     ────► 调用频率异常检测
       │                     └──► risk_events 写入 PostgreSQL
       │
       ├─► [行为序列消费者] ─────► Trace / Session 调用链重建
       │   （session 级触发）  ────► 威胁模式库匹配（已知攻击链）
       │                     ────► 统计异常检测（P99 阈值）
       │                     ────► 综合异常分计算（0-100）
       │                     └──► risk_events 写入 PostgreSQL
       │
       └─► [意图对齐消费者] ─────► 意图提取（LLM 调用）
           （高价值任务触发）  ────► AlignmentCheck（LlamaFirewall）
                             ────► 意图相关性评分（0-1）
                             ────► 任务劫持检测（< 0.2 相关性）
                             └──► risk_events + 可解释性文本
```

---

## 5. 代码结构规划

### 5.1 管理端 Monorepo 整体结构

```
agentsec-platform/
├── services/                     # 后端微服务（Go + Python）
│   ├── api-gateway/              # API 网关服务（Go）
│   ├── agent-registry/           # Agent 注册服务（Go）
│   ├── config-service/           # 配置管理服务（Go）
│   ├── heartbeat-service/        # 心跳处理服务（Go）
│   ├── block-service/            # 阻断指令服务（Go）
│   ├── query-service/            # 统一查询 API 服务（Go）
│   ├── alert-engine/             # 告警规则引擎（Go）
│   ├── notification-service/     # 多渠道通知服务（Go）
│   ├── report-service/           # 报告生成服务（Python）
│   ├── scheduler/                # 任务调度服务（Go）
│   └── detection/                # 安全检测引擎（Python）
│       ├── prompt-detector/      # Prompt 安全检测子引擎
│       ├── mcp-auditor/          # MCP 工具调用审计子引擎
│       ├── behavior-analyzer/    # 行为序列分析子引擎
│       └── intent-auditor/       # 意图对齐审计子引擎
├── collector/                    # OTel Collector 配置
│   ├── config/
│   │   ├── base-config.yaml      # 基础 Collector 配置
│   │   ├── processors/           # 自定义 Processor 配置模板
│   │   └── exporters/            # Exporter 配置模板
│   └── extensions/               # 自定义 Collector 扩展（Go）
│       ├── auth-extension/       # Token 认证扩展
│       └── pii-processor/        # PII 脱敏自定义 Processor
├── frontend/                     # 安全运营控制台（React + TypeScript）
│   ├── src/
│   └── ...
├── infra/                        # 基础设施即代码
│   ├── helm/                     # Helm Chart（平台一键部署）
│   │   └── agentsec/
│   ├── k8s/                      # K8s 资源清单（Helm 渲染来源）
│   └── terraform/                # 云资源配置（可选）
├── migrations/                   # Flyway SQL 迁移脚本
│   ├── V1__init_schema.sql
│   └── V2__add_risk_events.sql
├── proto/                        # Protobuf 协议定义（服务间 gRPC）
│   └── agentsec/v1/
├── shared/                       # 共享库
│   ├── go/                       # Go 共享库（认证/日志/metrics）
│   └── python/                   # Python 共享库（Kafka consumer base）
└── docs/                         # 技术文档
```

### 5.2 Go 服务通用代码结构（以 query-service 为例）

```
services/query-service/
├── cmd/
│   └── server/
│       └── main.go               # 启动入口
├── internal/
│   ├── handler/                  # HTTP Handler（gin/echo）
│   │   ├── session.go            # GET /api/v1/sessions
│   │   ├── metrics.go            # GET /api/v1/metrics/timeseries
│   │   ├── risk_events.go        # GET /api/v1/risk-events
│   │   └── search.go             # POST /api/v1/search/prompts
│   ├── service/                  # 业务逻辑层
│   │   ├── session_service.go
│   │   ├── metrics_service.go
│   │   └── search_service.go
│   ├── repository/               # 数据访问层
│   │   ├── clickhouse_repo.go    # ClickHouse 查询
│   │   └── opensearch_repo.go    # OpenSearch 查询
│   ├── middleware/               # 中间件
│   │   ├── auth.go               # JWT 验证 + RBAC
│   │   ├── tenant.go             # 租户 ID 注入与隔离
│   │   └── rate_limit.go         # 限流（Redis）
│   └── config/
│       └── config.go             # 服务配置（viper）
├── pkg/                          # 可复用的工具包
├── Dockerfile
└── go.mod
```

### 5.3 Python 检测引擎代码结构（以 prompt-detector 为例）

```
services/detection/prompt-detector/
├── app/
│   ├── __init__.py
│   ├── consumer.py               # Kafka Consumer 主循环
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── nemo_detector.py      # NeMo Guardrails 直接注入检测
│   │   ├── llamafirewall_detector.py  # 间接注入检测（PromptGuard）
│   │   ├── llm_guard_detector.py      # PII/毒性扫描
│   │   └── jailbreak_detector.py     # 越狱模式库匹配
│   ├── pipeline.py               # 检测管道（串行/并行执行多个检测器）
│   ├── models.py                 # 数据模型（Span、RiskEvent）
│   ├── repository.py             # PostgreSQL 写入（risk_events）
│   └── metrics.py                # Prometheus 指标（检测延迟/误报率）
├── config/
│   ├── settings.py               # 配置（pydantic-settings）
│   └── nemo_config/              # NeMo Guardrails 配置文件
│       └── config.yml
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
└── requirements.txt
```

### 5.4 前端代码结构（React + TypeScript）

```
frontend/
├── src/
│   ├── pages/
│   │   ├── dashboard/            # 实时监控大盘
│   │   ├── agents/               # Agent 应用管理
│   │   ├── security-events/      # 安全事件列表 + 详情
│   │   ├── trace-viewer/         # 调用链 Trace 可视化
│   │   ├── rules/                # 告警规则管理
│   │   ├── reports/              # 安全报告
│   │   ├── settings/             # 系统配置（租户/用户/通知）
│   │   └── onboarding/           # 接入向导
│   ├── components/
│   │   ├── TraceWaterfall/       # Trace 瀑布图组件（基于 Langfuse 扩展）
│   │   ├── SecurityEventCard/    # 安全事件卡片
│   │   ├── RiskHeatmap/          # 风险热力图
│   │   ├── AlertBadge/           # 告警标记组件
│   │   └── RuleEditor/           # 规则编辑器（可视化 AND/OR/NOT）
│   ├── hooks/                    # React 自定义 Hooks
│   ├── stores/                   # Zustand 状态管理
│   ├── api/                      # API 客户端（axios + react-query）
│   ├── utils/
│   └── types/                    # TypeScript 类型定义
├── vite.config.ts                # Vite 构建配置
├── tailwind.config.ts            # Tailwind CSS 配置
└── package.json
```

---

## 6. 关键技术决策

### 6.1 微服务拆分策略

管理端采用**按业务能力拆分**的微服务架构，而非按技术层拆分：

| 拆分原则 | 说明 |
|----------|------|
| 高频服务独立 | 心跳服务、配置服务（高频访问）独立部署，不与业务逻辑混用 |
| 检测引擎隔离 | Python 检测引擎（依赖重型 ML 库）与 Go 服务完全隔离，避免资源竞争 |
| 数据写入与查询分离 | 写入服务（高吞吐）与查询服务（低延迟）独立部署，分别优化 |
| 告警与通知分离 | 规则引擎与通知服务解耦，通知失败不影响规则匹配 |

### 6.2 多租户数据隔离

```
PostgreSQL 层：
  - 所有业务表含 tenant_id 字段
  - API 层中间件强制注入 tenant_id 到所有查询
  - Row Level Security（RLS）作为兜底防御

ClickHouse 层：
  - 分区键：(tenant_id, toYYYYMM(timestamp))
  - 查询 API 强制携带 tenant_id WHERE 条件

OpenSearch 层：
  - 索引名包含 tenant_id：agentsec-{tenant_id}-prompts
  - 查询强制添加 tenant_id filter

Redis 层：
  - Key 命名规范：{tenant_id}:{key_type}:{id}
  - 阻断 Key：block:{tenant_id}:{session_id}
```

### 6.3 OTel Collector Processor 热更新机制

```
管理端配置变更（安全管理员在控制台修改规则）
  │
  ├─► PostgreSQL 更新 processor_rules 表（版本号 +1）
  ├─► Redis 通知 Collector（pub/sub: config:updated）
  │
Collector 扩展（每 30s 轮询 or 收到 Redis 通知）
  ├─► 向配置服务 GET /internal/collector-config?version={current}
  ├─► 返回新配置 → 原子性重载 Processor 链
  └─► 无需重启 Collector 进程
```

### 6.4 检测引擎并发控制

```
Kafka Consumer Group 设计：
  - prompt-detector：消费者组 agentsec-prompt-detector
  - mcp-auditor：消费者组 agentsec-mcp-auditor
  - behavior-analyzer：消费者组 agentsec-behavior-analyzer
  - intent-auditor：消费者组 agentsec-intent-auditor

各消费者组独立消费 agentsec-spans Topic
每个消费者组配置不同的并发度：
  - Prompt 检测：高并发（每 span 独立检测），partition 数 = 24
  - 行为序列分析：session 级聚合，按 session_id hash 路由到固定 partition
  - 意图对齐审计：LLM 调用成本高，限制并发度（max 8 并发）
```

---

## 7. 稳定性保障策略

### 7.1 高可用设计

| 组件 | 副本策略 | 故障恢复 |
|------|----------|----------|
| OTel Collector | 3 副本，HPA 自动扩缩容 | LoadBalancer 30s 内切换，Kafka 缓冲兜底 |
| Kafka | 3 Broker，RF=3 | 任意 1 Broker 宕机不影响读写 |
| ClickHouse | 2 副本 + ZooKeeper | 主从自动切换 |
| PostgreSQL | 主从复制 + Patroni | 自动故障切换（< 30s） |
| Redis | Sentinel 模式（3 节点） | 自动主从切换 |
| 检测引擎 | 每个子引擎 2+ 副本 | Pod 重启自动恢复，Kafka offset 保留 |
| API 网关 | 3 副本 | 无状态，任意副本可服务 |

### 7.2 背压与限流

```
数据管道背压控制：
  Collector 本地队列（10000 span）→ Kafka → 检测引擎消费
  
  队列水位控制：
  - 队列达 80%：通知上游 SDK 降速（OTLP 返回 RESOURCE_EXHAUSTED）
  - 队列达 95%：返回 429，SDK 本地缓冲
  - Kafka Consumer Lag > 10000：告警运维团队

API 层限流：
  - 默认 1000 req/min/API Key（Redis 计数器，滑动窗口）
  - 超限返回 429 + Retry-After 头
  - 关键 API（数据查询）独立限流配额
```

### 7.3 数据可靠性

```
写入可靠性保障链：
  OTel Collector
    → Kafka（持久化，RF=3）
    → ClickHouse 写入服务（批量写入，失败重试 + 死信队列）
    → ClickHouse（ReplacingMergeTree，span_id 去重；同时保留 trace_id / parent_span_id 用于还原 Trace）

风险事件可靠性：
  检测引擎 → PostgreSQL（事务写入，risk_events 以 span_id 为最小证据锚点，并冗余 trace_id / span_kind / block_action / block_reason）
  PostgreSQL → 告警引擎（polling 或 CDC）
  告警引擎 → Redis/WebSocket（阻断）+ 通知服务

通知可靠性：
  告警通知失败 → 自动重试 3 次（指数退避）
  最终失败 → 记录 notification_failures 表 + 控制台告警图标
```

### 7.4 平台自监控

所有服务的关键指标通过 Prometheus 采集，Grafana 展示：

| 指标 | 来源 | 告警阈值 |
|------|------|----------|
| Collector 接收 QPS | OTel Collector /metrics | < 预期 50% 触发告警 |
| Kafka Consumer Lag | Kafka Exporter | > 10000 条告警 |
| ClickHouse 写入延迟 | ClickHouse Exporter | > 5s (P99) 告警 |
| 检测引擎处理延迟 | Python 服务 /metrics | > 3s (P99) 告警 |
| PostgreSQL 主从延迟 | pg_replication_slots | > 10s 告警 |
| 服务错误率 | 各服务 /metrics | > 1% 告警 |

---

## 8. 技术风险与缓解措施

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| NeMo Guardrails 检测延迟高（LLM 调用） | 高 | 异步检测（不阻塞 span 写入）；轻量规则快速路径；结果缓存（相同 prompt hash） |
| Kafka 消费 Lag 积压 | 高 | 水平扩展消费者；检测引擎降级（跳过意图对齐等重量级检测） |
| ClickHouse 写入热点 | 中 | 按 tenant_id 分片；批量写入聚合；SSD 热数据层 |
| LlamaFirewall/AlignmentCheck 成本高 | 高 | 仅对高价值任务触发；限制并发度（max 8）；成本监控告警 |
| 多租户数据泄露 | 极高 | API 层强制过滤；数据库 RLS；定期安全审计；租户隔离测试 |
| Keycloak 单点故障 | 中 | K8s 多副本；会话缓存到 Redis；API Key 模式作为降级手段 |

---

## 9. 部署规模参考

### 9.1 MVP 阶段（Phase 1）最小部署

| 组件 | 副本数 | 规格 |
|------|--------|------|
| OTel Collector | 2 | 2C 4G |
| Kafka | 3 Broker | 4C 8G，100G SSD |
| ClickHouse | 1 | 8C 32G，500G SSD |
| PostgreSQL | 1 主 + 1 从 | 4C 8G |
| Redis | 3 Sentinel | 2C 4G |
| Prompt 检测引擎 | 2 | 4C 8G（含 NeMo 模型） |
| API 网关 | 2 | 1C 2G |
| 控制台前端 | 2 | 1C 1G |

### 9.2 生产阶段扩展基准

- Collector：每 10000 span/s 增加 1 副本（2C 4G）
- 检测引擎：每新增 1 个高价值 Agent 应用增加 1 个意图审计并发
- ClickHouse：超过 1TB 数据时考虑分片（Shard）扩展

---

*文档结束*

