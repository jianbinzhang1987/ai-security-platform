# 客户端与管理端技术选型与代码架构设计
# AI Agent 安全监控平台 — 管理端架构设计文档

**文档编号**：AGENTSEC-ARCH-ADMIN-v1.0
**版本**：v1.0
**日期**：2026-03
**状态**：评审中
**关联文档**：管理端概要设计 v1.0 / 管理端详细设计 v1.0 / 管理端 PRD v1.0

---

## 1. 总体定位梳理

本项目产品分为客户端和管理端两个完全不同的系统：
本项目产品分为**客户端（Client SDK）**和**管理端（Admin Console）**两个完全独立的系统：

| 端 | 对应模块 | 使用者 | 核心目标 |
| :--- | :--- | :--- | :--- |
| **管理端 (Admin Console)** | M6 安全运营控制台 + M4 消息审计 + M5 告警响应 + M7 平台基础设施 | 平台安全运营团队 / 管理员 | 监控告警、规则管理、调用观测分析、安全运营 |

### 1.1 管理端职责边界

管理端（Admin Side）是平台运营方部署和维护的服务集群，客户不直接接触管理端基础设施，只通过 SDK 上报数据并通过控制台 Web 界面进行配置管理。管理端的完整职责包括：

- 接收、处理和存储来自所有客户端 SDK 的 span 事件数据
- 执行多层次安全检测（Prompt 注入、工具调用审计、行为序列分析、意图对齐）
- 管理客户的 Agent 应用、监控配置、告警规则
- 提供安全运营控制台（实时监控大盘、调用观测工作台、事件处置、报告生成）
- 提供多租户隔离、RBAC 权限管理、API 网关等平台基础能力

### 1.2 目标用户

| 用户角色 | 描述 | 主要使用功能 |
| :--- | :--- | :--- |
| 平台管理员（SA） | 负责平台运营和租户管理的人员 | 租户管理、用户权限、系统配置 |
| 安全管理员（SecAdmin） | 客户方的安全负责人，制定安全策略 | 规则配置、告警设置、Agent 配置管理、安全报告 |
| 安全运营工程师（SOC） | 日常处理安全告警和事件的工程师 | 实时监控、告警处置、事件调查、调用观测分析 |
| 只读查看员（RO） | 需要查看监控状态但无操作权限的人员 | 监控看板、报告查看 |

### 1.3 功能模块总览

| 模块编号 | 模块名称 | 核心职责 | 优先级 |
| :--- | :--- | :--- | :--- |
| A-M1 | Agent 接入与租户管理 | Agent 应用注册、配置管理、多租户隔离 | P0 |
| A-M2 | 数据接收与管道处理 | OTel Collector 集群、PII脱敏、路由分发 | P0 |
| A-M3 | 安全检测引擎 | Prompt检测、MCP审计、行为序列、意图对齐 | P0/P1 |
| A-M4 | 存储与查询服务 | ClickHouse事件库、查询API、数据生命周期 | P0 |
| A-M5 | 告警与响应系统 | 规则引擎、实时告警、阻断指令、通知渠道 | P1 |
| A-M6 | 安全运营控制台 | 监控大盘、调用链可视化、事件管理、报告 | P1 |
| A-M7 | 平台基础设施 | RBAC、API网关、审计日志、部署管理 | P0/P1 |

---

## 2. 技术选型

### 2.1 选型原则

| 原则 | 说明 |
| :--- | :--- |
| 性能优先 | 高并发数据管道、检测引擎需要高性能语言 |
| 生态匹配 | 安全检测组件（NeMo/LlamaFirewall/LLM Guard）以 Python 为主 |
| 可观测性 | 所有服务原生支持 Prometheus metrics 暴露 |
| 运维友好 | Go 编译为静态二进制，部署体积小，启动快 |
| 失败隔离 | 各层独立，单个组件故障不蔓延至整体 |

### 2.2 各服务语言分配

| 服务 | 语言 | 版本要求 | 选型理由 |
| :--- | :--- | :--- | :--- |
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
| 控制台前端 | Vue 3 + JavaScript | Vue 3 / Element Plus / Vite | 与当前 `server/RuoYi-Vue3` 工程保持一致，便于复用若依前端脚手架 |

### 2.3 核心技术组件选型

#### 2.3.1 数据管道层

| 组件 | 版本 | 用途 | 部署方式 |
| :--- | :--- | :--- | :--- |
| OpenTelemetry Collector Contrib | >= 0.90 | 统一数据接收（OTLP gRPC/HTTP），Processor 处理链，多路由 Exporter | 多副本集群部署 |
| Apache Kafka | >= 3.5 | 异步事件流总线，解耦 Collector 与检测引擎，支持高吞吐 span 缓冲与重放 | 3 Broker 集群 |
| LiteLLM Proxy | >= 1.40 | LLM API 透明代理（层2），拦截 LLM 调用，内置 logging/guardrails | 独立服务部署 |

#### 2.3.2 安全检测层

| 组件 | 版本 | 用途 | 部署方式 |
| :--- | :--- | :--- | :--- |
| NeMo Guardrails | >= 0.9 | Prompt 注入检测（直接注入）；可编程 input/dialog/output rails | Python 检测服务 |
| LlamaFirewall (Meta) | >= 0.1 | 间接 Prompt 注入（PromptGuard 模型）；意图对齐审计（AlignmentCheck） | Python 检测服务 |
| LLM Guard | >= 0.3 | Response PII 扫描；毒性内容检测；相关性检测 | Python 检测服务 |
| Guardrails AI | >= 0.5 | 输出结构验证；RAIL 规范；Guardrails Hub 预构建验证器 | Python 检测服务 |
| Falco | >= 0.36 | 进程/文件系统异常检测（行为基线补充） | 独立部署 |

#### 2.3.3 存储层

| 组件 | 版本 | 用途 | 部署方式 |
| :--- | :--- | :--- | :--- |
| ClickHouse | >= 23.x | 时序事件主存储（agent_spans 表），列式存储，时序聚合查询极快 | 2 副本集群 |
| OpenSearch | >= 2.x | Prompt 内容全文检索；告警 Dashboard | 3 节点集群 |
| PostgreSQL | >= 15.x | 业务元数据（租户/Agent/规则/配置/告警）结构化存储 | 主从复制 |
| Redis | >= 7.x | 阻断指令存储（TTL）；实时限流计数器；配置版本缓存；会话状态 | Sentinel 模式（3 节点） |
| MinIO | >= RELEASE.2024 | 冷数据对象存储（> 30 天 span 数据）；报告 PDF 存储 | 独立部署 |

#### 2.3.4 可观测性层

| 组件 | 版本 | 用途 |
| :--- | :--- | :--- |
| Langfuse | >= 2.x | LLM Agent 调用链 Trace 可视化，原生 OTel 支持，开源可自部署 |
| Grafana | >= 10.x | 平台自监控看板（Collector QPS、Kafka Lag、ClickHouse 写入速度） |
| Prometheus | >= 2.x | 指标采集（所有服务暴露 /metrics） |

#### 2.3.5 认证与授权层

| 组件 | 版本 | 用途 |
| :--- | :--- | :--- |
| Keycloak | >= 22.x | OAuth2 / OIDC / MFA / LDAP / SSO 完整支持，RBAC 集成 |
| JWKS / JWT | - | 服务间认证（Go 标准库 + github.com/golang-jwt/jwt） |

## 4. 管理端 (Admin Console) 技术选型
#### 2.3.6 部署与基础设施

### 4.1 核心设计原则
管理端作为 **安全运营工作台**，需具备：
- **实时性**：安全事件秒级推送。
- **数据密度**：大量监控数据的可视化呈现。
- **复杂交互**：调用观测工作台、规则编辑器。
| 组件 | 版本 | 用途 |
| :--- | :--- | :--- |
| Flyway | >= 9.x | PostgreSQL schema 版本管理，服务启动时自动 migration |
| Nginx | >= 1.24 | 统一入口，TLS 终止，请求路由 |

### 4.2 技术栈详细说明
#### 2.3.7 管理端前端技术栈

| 技术领域 | 选型 | 版本 | 选型理由 |
| :--- | :--- | :--- | :--- |
| **UI 框架** | `Vue 3` | 当前工程版本 | 与 `RuoYi-Vue3` 保持一致，复用现有布局、路由、权限体系 |
| **开发语言** | `JavaScript` | ES2020+ | 与当前仓库实现一致，降低迁移成本 |
| **构建工具** | `Vite` | >= 5.x | 开发体验极佳，HMR 极速 |
| **UI 组件库** | `Element Plus` | 当前工程版本 | 与若依 Vue3 默认组件体系一致 |
| **图表库** | `Apache ECharts` | >= 5.x | 处理大数据集性能优秀，热力图支持好 |
| **状态管理** | `Pinia` | 当前工程版本 | 与 `RuoYi-Vue3/src/store` 演进方向保持一致 |
| **异步请求** | `Axios` | 当前工程版本 | 复用 `src/utils/request.js` 与既有 API 分层方式 |
| **实时通信** | `WebSocket` | - | 关键告警实时推送 |
| **认证集成** | 若依登录态 + Token | 当前工程实现 | 复用若依权限模型，再按需扩展 SSO |
| **规则编辑** | `Monaco Editor` | latest | 支持 Sigma 规则语法高亮与提示 |

---

## 5. 管理端代码架构设计

### 5.1 项目结构
```text
server/
├── RuoYi/                                   # 若依后端聚合工程
│   ├── ruoyi-admin/                         # Web 入口、Controller、启动类
│   ├── ruoyi-framework/                     # 安全、AOP、配置、拦截器
│   ├── ruoyi-system/                        # 领域模型、Mapper、Service
│   ├── ruoyi-common/                        # 公共常量、基础对象、工具类
│   ├── ruoyi-quartz/                        # 定时任务模块
│   ├── ruoyi-generator/                     # 代码生成模块
│   ├── sql/                                 # 若依基础脚本及平台扩展脚本
│   │   └── agentsec-platform/               # 管理端业务初始化/迁移 SQL
│   └── pom.xml                              # Maven 聚合 POM
└── RuoYi-Vue3/                              # 若依 Vue3 管理端
    ├── src/router/                          # 路由管理
    ├── src/layout/                          # 主布局
    ├── src/views/                           # 页面视图
    ├── src/api/                             # 前端 API 封装
    ├── src/components/                      # 公共组件
    ├── src/store/                           # 状态管理
    └── vite.config.js                       # 构建配置
```

### 5.2 核心组件设计：Trace 瀑布图
管理端最复杂的交互部分，用于可视化单次 Agent 运行行为。
- **数据结构**：基于 `parentSpanId` 重建树形结构。
- **渲染策略**：使用 ECharts 自定义系列或纯 CSS 渲染时间轴，关键风险节点红色高亮。
- **交互**：点击节点展示右侧侧边栏，包含完整的 Prompt/Response（脱敏后）及工具调用参数。

---

## 6. 接口契约设计 (API Contract)

| API 端点 | 功能描述 | 对应模块 |
| UI 框架 | `Vue 3` | 当前工程版本 | 与现有若依前端保持一致 |
| 开发语言 | `JavaScript` | ES2020+ | 与现有仓库实现一致 |
| 构建工具 | `Vite` | >= 5.x | 开发体验极佳，HMR 极速 |
| UI 组件库 | `Element Plus` | 当前工程版本 | 复用若依现有 UI 体系 |
| 图表库 | `Apache ECharts` | >= 5.x | 处理大数据集性能优秀，热力图支持好 |
| 状态管理 | `Pinia` | 当前工程版本 | 与若依 Vue3 状态管理体系一致 |
| 异步请求 | `Axios` | 当前工程版本 | 通过 `src/utils/request.js` 统一封装 |
| 实时通信 | `WebSocket` | - | 关键告警实时推送 |
| 认证集成 | 若依登录态 + Token | 当前工程实现 | 先复用若依鉴权，再按需扩展 OIDC |
| 规则编辑 | `Monaco Editor` | latest | 支持 Sigma 规则语法高亮与提示 |

---

## 3. 整体架构设计

### 3.1 管理端服务总体架构

```
                        ┌──────────────────────────────────────────┐
  客户端 SDK            │           Nginx（TLS 终止）               │
  ─────────────────────►│ /otlp/... /agentsec/... /ruoyi/...       │
                        └──────┬──────────────────────┬────────────┘
                               │                      │
              ┌────────────────▼───────┐  ┌───────────▼─────────────┐
              │   OTel Collector 集群   │  │   API 网关服务（Go）      │
              │  (3副本)               │  │   认证/限流/路由/审计日志 │
              │  OTLP gRPC :4317       │  └───────────┬─────────────┘
              │  OTLP HTTP :4318       │              │
              └─────────┬──────────────┘              │
                        │ Processor 处理链              │ REST / WS API
                        │  PII脱敏 → 安全标签           │
                        │  → 尾部采样 → 批量            │
                        ▼                              │
              ┌──────────────────────┐                 │
              │      Kafka 集群       │                 │
              │  (3 Broker, RF=3)    │                 │
              │  Topic:              │                 │
              │    agentsec-spans    │                 │
              └──────┬───────────────┘                 │
                     │                                 │
       ┌─────────────┼──────────────────┐              │
       │             │                  │              │
       ▼             ▼                  ▼              │
  ┌──────────┐  ┌──────────┐  ┌────────────────┐      │
  │ClickHouse│  │OpenSearch│  │  安全检测引擎    │      │
  │ 写入服务  │  │ 写入服务  │  │   (Python)     │      │
  │  (Go)   │  │  (Go)    │  │  ① Prompt检测  │      │
  └──────────┘  └──────────┘  │  ② MCP审计     │      │
       │             │         │  ③ 行为序列    │      │
       │             │         │  ④ 意图对齐    │      │
       │             │         └──────┬─────────┘      │
       │             │                │ 风险事件         │
       │             │                ▼                 │
       │             │         ┌────────────────┐       │
       │             │         │  告警规则引擎    │       │
       │             │         │    (Go)         │       │
       │             │         └──────┬──────────┘       │
       │             │                │                  │
       │             │         ┌──────▼──────────┐       │
       │             │         │  通知 / 阻断服务  │       │
       │             │         │     (Go)         │       │
       │             │         └─────────────────┘       │
       │             │                                   │
       └─────────────┼──────────────────────────────────►│
                     │                           查询 API 服务 (Go)
                     │                                   │
                     │                                   ▼
                     │                          ┌────────────────┐
                     └─────────────────────────►│   控制台前端    │
                                               │   Vue3 + Vite   │
                                               └────────────────┘

      ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐
      │   PostgreSQL     │  │  Redis (Sentinel) │  │   Keycloak     │
      │  （元数据/规则）  │  │  （缓存/阻断指令） │  │  （OIDC/RBAC） │
      └─────────────────┘  └──────────────────┘  └────────────────┘
```

### 3.2 数据流全链路

```
Agent 运行时
    │
    │ OTLP gRPC/HTTP
    ▼
Nginx (TLS 终止)
    │
    ▼
OTel Collector (Processor 链)
    │ ① filter    → 过滤健康检查等噪音 span
    │ ② attributes → 注入 platform/tenant_id/app_id
    │ ③ redact    → PII 二次脱敏保障
    │ ④ transform  → OTTL 条件表达式安全标签
    │ ⑤ tail_sampling → 正常流量按比例采样，安全 span 100% 保留
    │ ⑥ batch     → 批量 5s/1000条
    ▼
Kafka Topic: agentsec-spans
    │
    ├──► ClickHouse 写入服务 → agent_spans 表（时序主存储）
    ├──► OpenSearch 写入服务 → prompt 全文索引
    └──► 安全检测引擎（4个独立消费者组）
              │
              └── 风险事件 → PostgreSQL: risk_events 表
                                │
                                ▼
                        告警规则引擎（Go）
                                │
                    ┌───────────┼────────────┐
                    ▼           ▼            ▼
               通知服务     阻断服务      工单创建
             （飞书/邮件）  （Redis+WS）  （PostgreSQL）
                                │
                                ▼
                         SDK 实时阻断
```

---

## 4. 数据管道层架构（A-M2）

### 4.1 OTel Collector Processor 处理链

Collector 以集群方式部署，前置 LoadBalancer（gRPC + HTTP 双协议），支持水平扩展（目标 CPU 利用率 70% 时触发扩容）。

```
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  # 1. 自定义 Token 认证（Go 扩展）→ 401 拒绝无效 Token
  auth/token_validator: ...

  # 2. 过滤健康检查、内部探针等噪音 Span
  filter/exclude_health_check:
    traces:
      span:
        - 'attributes["http.route"] == "/healthz"'

  # 3. 统一注入平台标签
  attributes/inject_platform:
    actions:
      - { key: platform, value: agentsec, action: insert }
      - { key: tenant_id, from_attribute: token.tenant_id, action: insert }
      - { key: app_id,    from_attribute: token.app_id,    action: insert }

  # 4. PII 二次脱敏（兜底保障）
  redaction/pii_secondary:
    allow_all_keys: true
    blocked_values:
      - '\b1[3-9]\d{9}\b'           # 手机号
      - '\b\d{15}|\d{18}\b'         # 身份证
      - '\b4[0-9]{12}(?:[0-9]{3})?\b' # 银行卡

  # 5. OTTL 安全标签注入
  transform/security_tags:
    trace_statements:
      - context: span
        statements:
          - 'set(attributes["security.risk.hint"], "prompt_too_long") where
             len(attributes["gen_ai.prompt"]) > 8000'

  # 6. 尾部采样：安全 Span 100% 保留，普通 Span 按比例采样
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      - { name: security-always, type: string_attribute,
          string_attribute: { key: security.risk.level,
          values: [low, medium, high, critical] } }
      - { name: normal-sample, type: probabilistic,
          probabilistic: { sampling_percentage: 10 } }

  # 7. 批量聚合
  batch:
    timeout: 5s
    send_batch_size: 1000
    send_batch_max_size: 2000

exporters:
  kafka:       # → agentsec-spans Topic（检测引擎 + 存储）
  otlp/langfuse:  # → Langfuse（调用链可视化）
  # SIEM Exporter：高危 Span 以 CEF 格式推送外部 SIEM

service:
  pipelines:
    traces:
      receivers:  [otlp]
      processors: [auth/token_validator, filter/exclude_health_check,
                   attributes/inject_platform, redaction/pii_secondary,
                   transform/security_tags, tail_sampling, batch]
      exporters:  [kafka, otlp/langfuse]
```

### 4.2 Collector 配置热更新机制

Processor 规则（PII 正则、采样率等）无需重启 Collector 即可更新：

```
管理员在控制台修改 Processor 规则
    │
    ├─► PostgreSQL 更新 processor_rules 表（version +1）
    └─► Redis Pub/Sub 发布通知（channel: config:updated）

Collector 扩展（每 30s 轮询 OR 收到 Redis 通知）
    ├─► 向配置服务 GET /internal/collector-config?version={current}
    ├─► 版本一致 → 跳过（304 Not Modified）
    └─► 版本更新 → 原子性重载 Processor 链（不重启进程）
```

### 4.3 Kafka Topic 设计

| Topic | 分区数 | 副本数 | 消费者组 | 说明 |
| :--- | :---: | :---: | :--- | :--- |
| `agentsec-spans` | 24 | 3 | 各引擎独立消费者组 | 主 span 事件流 |
| `agentsec-risk-events` | 12 | 3 | `alert-engine` | 检测引擎输出风险事件 |
| `agentsec-dlq` | 6 | 3 | 运维人工处理 | 死信队列（处理失败超重试限制） |

**分区路由策略**：
- 普通 span → Round-Robin 分区（最大化并行度）
- 行为序列分析 span → 按 `session_id` Hash 路由到固定分区（保障 session 内顺序消费）

### 4.4 多路由 Exporter 分发规则

```
所有 span                    → ClickHouse（主存储）+ Kafka（检测引擎）
含 prompt/response 的 span   → 额外写入 OpenSearch（全文检索）
LLM 调用 + 工具调用 span     → 额外上报 Langfuse（Trace 可视化）
risk_level = high/critical   → 额外推送 SIEM（CEF 格式）
```

---

## 5. 安全检测引擎架构（A-M3）

### 5.1 检测引擎整体设计

检测引擎分为四个独立 Python 服务，各自作为独立 Kafka 消费者组消费 `agentsec-spans` Topic：

```
Kafka: agentsec-spans
       │
       ├─► [① Prompt 检测消费者组: agentsec-prompt-detector]
       │       → NeMo Guardrails       直接注入检测（user 消息）
       │       → LlamaFirewall PromptGuard  间接注入（system/tool 消息）
       │       → LLM Guard             Response PII 扫描 + 毒性检测
       │       → Guardrails AI         结构验证 + 关系性检测
       │       → 越狱模式库（500+模式） 命中 → jailbreak_attempt
       │       └── 输出 → risk_events 写入 PostgreSQL
       │
       ├─► [② MCP 审计消费者组: agentsec-mcp-auditor]
       │       → 白名单/黑名单校验（工具名精确/通配符匹配）
       │       → 参数危险模式扫描（SQL注入/路径穿越/SSRF/命令注入）
       │       → 调用频率异常检测（超过基线均值 3 倍标准差）
       │       → Markov 链工具调用序列建模（转移概率 < 0.01 告警）
       │       → 权限越界追踪（多 Agent 协作场景）
       │       └── 输出 → risk_events + 阻断指令（黑名单命中时）
       │
       ├─► [③ 行为序列消费者组: agentsec-behavior-analyzer]
       │   （session 级触发：超时 5min 或 span 数 > 50）
       │       → Session 调用链重建（按 session_id 聚合，时间排序）
       │       → 威胁模式库匹配（已知攻击链：inject→read_file→exfil）
       │       → 统计异常检测（P99 阈值：Token消耗/工具调用次数/外部请求数）
       │       → 综合异常分计算（0-100，多维加权）
       │       └── 输出 → risk_events（异常分 > 70 时）+ 攻击时间线结构体
       │
       └─► [④ 意图对齐消费者组: agentsec-intent-auditor]
           （仅对高价值任务触发：财务/文件系统/网络访问）
               → 意图提取（LLM 调用，输出结构化意图 JSON）
               → AlignmentCheck（Meta LlamaFirewall，评估每个工具调用）
               → 意图相关性评分（0-1，持续下降触发告警）
               → 任务劫持检测（相关性 < 0.2 → 潜在任务劫持）
               → 可解释性文本生成（自然语言解释，供 SOC 审阅）
               └── 输出 → risk_events + 意图对齐报告
```

### 5.2 检测管道并发设计

| 子引擎 | 消费者组 | 并发度 | 特殊策略 |
| :--- | :--- | :---: | :--- |
| Prompt 检测 | `agentsec-prompt-detector` | 24（等于分区数） | 高并发，每 span 独立检测 |
| MCP 审计 | `agentsec-mcp-auditor` | 24 | 高并发，参数扫描轻量 |
| 行为序列分析 | `agentsec-behavior-analyzer` | 12 | session_id Hash 分区，保序消费 |
| 意图对齐审计 | `agentsec-intent-auditor` | 8 | LLM 调用成本高，严格限制并发 |

### 5.3 检测结果数据模型（风险事件）

```
RiskEvent {
    id              UUID        风险事件唯一标识
    tenant_id       UUID        租户隔离
    app_id          UUID        所属接入应用
    session_id      String      关联 Session（可空，跨轮聚合时使用）
    trace_id        String      所在 Trace，默认调查入口
    span_id         String      触发风险的具体 Span，最小证据锚点
    span_kind       Enum        llm / tool / retriever / network / db / guardrail / internal
    block_action    String      阻断 / 降级 / 告警放行等动作
    block_reason    String      阻断或响应原因
    risk_type       Enum        prompt_injection / indirect_injection /
                                jailbreak / pii_leak / toxicity /
                                mcp_blacklist / mcp_param_injection /
                                tool_freq_anomaly / behavior_anomaly /
                                intent_misalignment
    risk_level      Enum        none / low / medium / high / critical
    confidence      Float[0,1]  检测置信度
    evidence        JSONB       原始匹配证据（命中规则/匹配片段）
    explanation     Text        可解释性自然语言说明（意图对齐引擎输出）
    anomaly_score   Int[0,100]  综合异常分（行为序列引擎输出）
    status          Enum        new / in_progress / confirmed /
                                false_positive / closed
    detected_at     Timestamp   检测时间
}
```

### 5.4 检测性能设计

- **轻量快速路径**：越狱模式库（正则匹配）→ 白名单/黑名单校验（哈希查找）先行，命中则跳过重量级检测
- **检测结果缓存**：相同 `prompt_hash` 的 span 命中缓存（Redis，TTL 5min），避免重复调用 LLM
- **降级策略**：Kafka Consumer Lag > 10000 时，意图对齐等重量级检测自动降级，仅保留轻量规则检测

---

## 6. 存储层架构（A-M4）

### 6.1 ClickHouse 时序主存储

```sql
-- 主表：Agent Span 事件（时序存储）
CREATE TABLE agent_spans (
    span_id           String,
    trace_id          String,
    parent_span_id    String,
    session_id        String,
    tenant_id         String,           -- 分区键之一
    app_id            String,
    instance_id       String,
    span_name         String,
    span_kind         Enum8('llm'=1, 'tool'=2, 'network'=3, 'db'=4, 'internal'=5, 'retriever'=6, 'guardrail'=7),
    agentsec_span_type String,     -- SDK 原始字段，如 llm_call/tool_call
    framework         String,      -- gen_ai.framework，如 langchain
    node_display_name String,
    node_class_name   String,
    node_method_name  String,
    timestamp         DateTime64(3),    -- 分区键之一
    duration_ms       Float64,
    model             String,
    prompt_hash       String,           -- Hash 而非明文（安全+去重）
    prompt_truncated  String,           -- 前 500 字（可配置）
    response_truncated String,
    token_prompt      UInt32,
    token_completion  UInt32,
    token_total       UInt32,
    tool_name         String,
    tool_input_params String,
    tool_output       String,
    risk_level        Enum8('none'=0, 'low'=1, 'medium'=2, 'high'=3, 'critical'=4),
    status            Enum8('ok'=1, 'blocked'=2, 'error'=3),
    block_action      String,
    block_reason      String,
    error_type        String,
    risk_type         String,
    security_tags     Array(String),
    anomaly_score     UInt8,
    sdk_version       String
)
ENGINE = ReplacingMergeTree(timestamp)
PARTITION BY (tenant_id, toYYYYMM(timestamp))   -- 多租户 + 时间分区
ORDER BY (tenant_id, app_id, session_id, timestamp)
TTL timestamp + INTERVAL 90 DAY;                 -- 按租户配置可调整

-- 物化视图：LLM 调用量时序聚合（1 分钟粒度，查询加速）
CREATE MATERIALIZED VIEW agent_spans_1m_agg
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(window_start)
ORDER BY (tenant_id, app_id, window_start) AS
SELECT
    tenant_id, app_id,
    toStartOfMinute(timestamp) AS window_start,
    countIf(span_kind = 1)  AS llm_calls,
    sum(token_total)         AS total_tokens,
    avg(duration_ms)         AS avg_latency_ms,
    countIf(risk_level >= 2) AS security_events
FROM agent_spans
GROUP BY tenant_id, app_id, window_start;
```

**写入策略**：批量写入（每批 1000 条 / 5s），`ReplacingMergeTree` 基于 `span_id` 保证幂等去重。
**冷热分层**：30 天内数据在 SSD 节点，超过 30 天自动迁移至 HDD 或 MinIO（对象存储）。

### 6.2 PostgreSQL 业务元数据库

核心表清单（详见详细设计文档第 2 节）：

| 表名 | 用途 | 关键字段 |
| :--- | :--- | :--- |
| `GET /agentsec/assets/app/list` | 接入应用列表（状态/心跳/SDK版本） | M1-02 |
| `POST /agentsec/assets/app/autoRegister` | 接入应用自动注册（机器指纹） | M1-02 |
| `GET /agentsec/session/{sessionId}` | 完整 Session 调用链重建 | M4-02 |
| `GET /agentsec/event/list` | 安全事件列表（分页/过滤） | M6-03 |
| `POST /agentsec/rule/test/{id}` | 规则沙箱回放测试 | M5-02 |
| `WS /ws/agentsec/alerts` | 实时告警推送 (WebSocket) | M5-03 |
| `tenants` | 租户信息与资源配额 | id, status, plan, max_agents, data_retention_days |
| `agent_apps` | Agent 应用注册信息 | id, tenant_id, name, status |
| `app_tokens` | App Token 管理 | id, app_id, token_hash, status, expires_at |
| `agent_instances` | Agent 实例心跳状态 | id, app_id, instance_id, hostname, last_heartbeat |
| `risk_events` | 检测引擎输出（风险事件） | id, app_id, trace_id, session_id, span_id, span_kind, risk_type, risk_level, confidence, status, block_action, block_reason, evidence |
| `alert_rules` | 告警规则定义 | id, conditions(JSONB), actions(JSONB), scope_app_ids |
| `notification_channels` | 通知渠道配置 | id, type, config(JSONB) |
| `block_logs` | 阻断日志（Append-Only） | id, session_id, reason, blocked_at |
| `audit_logs` | 操作审计日志（不可删除） | id, actor_id, action, resource_type, request_ip |

### 6.3 OpenSearch 全文检索

- **索引命名规范**：`agentsec-{tenant_id}-prompts`（租户物理隔离）
- **写入内容**：仅含 prompt/response 内容的 span，脱敏后写入
- **查询能力**：关键词精确搜索、近似语义搜索（KNN 向量）、正则表达式搜索
- **保留策略**：ILM（Index Lifecycle Management）自动 Rollover + 按 TTL 删除

### 6.4 Redis 缓存与阻断

```
Key 命名规范（租户隔离）：
  阻断指令：  block:{tenant_id}:{session_id}         TTL: 1h
  配置版本：  config:{tenant_id}:{app_id}:version   TTL: 5min
  限流计数：  ratelimit:{tenant_id}:{api_key}:{min} TTL: 2min
  Token 校验缓存：token:{token_hash}                TTL: 30s

Redis Sentinel 配置（3 节点）：
  - 主节点写入（阻断指令）
  - 从节点读取（SDK 轮询检查）
  - Sentinel 自动故障切换 < 30s
```

### 6.5 数据生命周期管理

```
数据保留策略（按租户配置）：
  ClickHouse: TTL timestamp + INTERVAL {retention_days} DAY
              冷热分层：30天 SSD → MinIO
  PostgreSQL: risk_events 按 detected_at 分区，TTL 定期清理
  OpenSearch: ILM Policy，按天 Rollover，超期自动删除
  
  最短保留：30 天
  最长保留：365 天（企业版）
  默认保留：90 天
```

---

## 7. 关键设计决策总结
## 7. 告警与响应系统架构（A-M5）

### 7.1 告警规则引擎

规则引擎以 Go 实现，从 PostgreSQL 加载规则，以滑动窗口计数（Redis）匹配复合条件：

```
AlertRule 数据结构：
  conditions: AND/OR/NOT 条件树（JSON 表达式）
    - 叶子节点：{ op: "gte", field: "confidence", value: 0.8 }
    - 支持字段：risk_level / risk_type / confidence /
                app_id / tool_name / anomaly_score 等
  window: 滑动窗口（如 count > 3 in 5min）
  actions: 响应动作列表（notify / block / ticket）
  scope: 生效 Agent 应用范围

规则匹配流程：
  消费 agentsec-risk-events Topic
    → 检查规则作用范围（app_id 过滤）
    → 评估条件树（递归 eval）
    → 滑动窗口计数校验（Redis INCRBY + EXPIRE）
    → 条件全部满足 → 并发执行响应动作
```

**内置规则库**：预置 20+ 条规则，覆盖常见威胁（Prompt 注入置信度 > 0.8、黑名单工具调用、高异常分 session 等）。
**Sigma 规则兼容**：支持导入 YAML 格式 Sigma 规则，从安全社区直接导入。
**规则测试沙箱**：上线前可选择历史时间段（最近 7 天）回跑，查看 TP/FP 数量，防误配置。

### 7.2 阻断指令下发架构

```
高风险事件检测（如黑名单工具调用）
    │
    ▼
BlockService.Block(session_id, reason)
    │
    ├─► ① 写入 Redis                    主要路径
    │       Key:   block:{tenant_id}:{session_id}
    │       Value: {reason, rule_id, blocked_at}
    │       TTL:   1h
    │
    └─► ② WebSocket 实时推送             辅助路径（降低延迟）
            Hub.BroadcastToApp(app_id)
            向该 app 下所有在线 SDK 实例广播阻断指令

SDK 侧（每次 LLM 调用前）：
    ├─► 轮询检查 Redis（最大延迟 = 心跳间隔 ≤ 30s）
    └─► 接收 WebSocket 推送（实时，延迟 < 1s）
    → 发现阻断指令 → 不发起 LLM 调用，直接返回安全拒绝文本

端到端阻断延迟目标：< 5s（从风险事件产生到 SDK 执行拦截）

阻断粒度：
  Session 级  block:{tenant_id}:{session_id}
  实例级      block:{tenant_id}:{instance_id}
  应用级      block:{tenant_id}:{app_id}:*
```

### 7.3 多渠道告警通知

| 通知渠道 | 触发等级 | 配置方式 |
| :--- | :--- | :--- |
| 飞书 Webhook | critical / high | Bot Webhook URL |
| 钉钉 Webhook | critical / high | Bot Webhook URL |
| 企业微信 Webhook | critical / high | Bot Webhook URL |
| Slack Webhook | 可配 | Bot Webhook URL |
| 邮件（SMTP） | medium + | SMTP 配置 |
| 短信（云短信） | critical | 云服务 API Key |
| PagerDuty | critical | Integration Key |
| SIEM（CEF 格式） | high + | Syslog / HTTP 推送 |

**告警聚合**：5 分钟窗口内相同 `rule_id + app_id` 的告警合并为一条，附带"本批次 N 条"计数，防止告警风暴。
**通知可靠性**：失败自动重试 3 次（指数退避），最终失败记录 `notification_failures` 表并在控制台告警图标提示。

---

## 8. 安全运营控制台架构（A-M6）

### 8.1 控制台功能结构

```
管理端控制台（RuoYi-Vue3 SPA）
├── 安全大盘 /agentsec/dashboard
│     顶部指标卡（30s 刷新）+ 安全事件趋势图 + 风险分布饼图 + 告警列表
│
├── 资产管理 /agentsec/assets/apps
│     接入应用列表 → 应用详情（概览/运行实例/接入凭证/监控配置/工具资源/逻辑智能体/策略覆盖）+ 接入审批 + 基础资产拓扑
│
├── 安全监控 /agentsec/observe /agentsec/search
│     调用观测工作台（Trace 默认视图 + Span 证据列表 + Session 可选聚合）+ 内容检索（Prompt/Response/Tool 输入输出）
│
├── 安全事件 /agentsec/events /agentsec/alerts
│     事件处置中心 + 告警与响应记录（通知/阻断/降级/放行）
│
├── 安全策略 /agentsec/policies/*
│     告警规则（测试沙箱）+ 检测引擎配置 + Guardrail 规则 + 通知渠道
│
├── 报告中心 /agentsec/reports
│     报告列表 + 自定义生成 + 邮件订阅
│
└── 系统管理 /system/* + /agentsec/admin/*
      用户权限复用若依系统管理；租户、API Key、平台审计等新增到 agentsec 业务菜单
```

### 8.1.1 若依菜单与权限落位约定

- 一级目录建议新增为“AgentSec 安全监测”，前端目录对应 `src/views/agentsec/`
- 页面路由、菜单、按钮权限统一沿用若依约定，通过菜单表维护，不在前端硬编码完整权限树
- 后端控制器建议统一使用 `@RequestMapping("/agentsec/...")`
- 按钮权限标识建议采用 `agentsec:app:list`、`agentsec:event:handle`、`agentsec:rule:add` 这类若依风格命名
- 前端 API 建议放入 `src/api/agentsec/`，与控制器模块一一对应

### 8.2 调用观测工作台组件架构

调用观测工作台是控制台最复杂的交互组件。MVP 默认围绕 Trace 视图和 Span 详情建设，Session 仅在存在稳定 session_id 时作为聚合视图启用：

```
数据流：
  SOC 工程师点击"查看证据"
    │
    ├─► GET /agentsec/trace/{trace_id}/spans        → Trace 内 spans 列表
    ├─► GET /agentsec/event/list?spanId=...         → 关联风险事件
    └─► GET /agentsec/session/{session_id}          → 可选 Session 聚合上下文

渲染策略：
  1. buildSpanTree(spans) → 基于 parentSpanId 重建树状结构
  2. 时间轴比例换算：(offset / sessionDuration) × 100%
  3. 每条 Span 渲染为一行（层级缩进 = depth × 16px）
  4. Span 颜色编码：LLM=蓝 / Tool=绿 / Retriever=青 / Network=橙 / DB=紫 / Guardrail=红
  5. 风险标注层叠加（红/橙/黄告警图标）
  6. 点击 Span → 右侧展开 SpanDetailPanel
       LLM Span: prompt messages + response（PII 已脱敏）
       Tool Span: tool_name + input_params + output
       有风险事件: 原始证据 + 置信度 + 可解释性说明

性能优化：
  - SWR stale-while-revalidate（展示旧数据同时后台拉新）
  - span 数 < 200 时虚拟化关闭，直接全量渲染
  - span 数 ≥ 200 时使用 react-virtualized 虚拟列表
```

### 8.3 实时大盘数据刷新策略

```typescript
// 各模块刷新周期设计

// 指标卡（活跃Agent数 / LLM调用量 / 安全事件数）：30s 刷新
request({ url: '/agentsec/dashboard/summary', method: 'get' })

// 安全事件趋势图（5min 粒度）：60s 刷新
request({ url: '/agentsec/dashboard/timeseries', method: 'get', params: { granularity: '5m' } })

// 最近告警列表：30s 刷新
request({ url: '/agentsec/event/list', method: 'get', params: { status: 'new', pageSize: 20 } })

// WebSocket 实时推送：critical 级别告警立即推送，浏览器弹出通知
ws.on('alert', (msg) => {
  if (msg.risk_level === 'critical') {
    showNotification(msg)      // 浏览器 Notification API
    // 收到实时事件后刷新告警列表与看板数据
  }
})
```

### 8.4 RBAC 权限矩阵

| 功能模块 | SA | TA | SecAdmin | SOC | RO |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 安全大盘（查看） | ✓ | ✓ | ✓ | ✓ | ✓ |
| Agent 应用（增删改） | ✓ | ✓ | ✓ | - | - |
| Agent 应用（只读） | ✓ | ✓ | ✓ | ✓ | ✓ |
| 监控配置（改） | ✓ | ✓ | ✓ | - | - |
| 调用观测工作台（查看） | ✓ | ✓ | ✓ | ✓ | ✓ |
| 安全事件（处置） | ✓ | ✓ | ✓ | ✓ | - |
| 告警规则（增删改） | ✓ | ✓ | ✓ | - | - |
| 手动阻断（执行） | ✓ | ✓ | ✓ | - | - |
| 安全报告（查看） | ✓ | ✓ | ✓ | ✓ | ✓ |
| 用户管理（改） | ✓ | ✓ | - | - | - |
| 租户管理 | ✓ | - | - | - | - |
| 平台运维状态 | ✓ | - | - | - | - |

**认证实现**：Keycloak OAuth2/OIDC，支持企业 LDAP/AD 同步、Google/GitHub SSO、MFA 二次认证（关键操作强制）。
**权限生效时机**：角色变更后按若依权限体系重新加载菜单与按钮权限，必要时通过重新登录或刷新权限缓存生效。
**实现基线**：优先复用若依现有用户、角色、菜单、部门、数据权限模型，在此基础上扩展 AgentSec 业务菜单和按钮权限，不另建一套平行 RBAC 系统。

---

## 9. 多租户隔离架构

### 9.1 数据隔离设计

```
隔离层次（纵深防御）：

① API 层（第一道防线）：
   API 网关中间件从 JWT Claims 提取 tenant_id
   所有查询接口强制注入 tenant_id WHERE 条件
   代码层面：context 传递 tenantID，Repository 层强制使用

② 数据库层（第二道防线）：
   PostgreSQL：所有业务表含 tenant_id 字段 + Row Level Security（RLS）
   ClickHouse：分区键包含 tenant_id，查询 API 强制 tenant_id 过滤
   OpenSearch：索引名包含 tenant_id（agentsec-{tenant_id}-prompts）
   Redis：Key 命名规范 {tenant_id}:{key_type}:{id}

③ 应用层（第三道防线）：
   Collector 扩展：Token 认证时绑定 tenant_id，Processor 自动注入
   检测引擎：Consumer Group 按 tenant_id 隔离处理队列

多租户安全验收：
   - 自动化测试：租户 A 用户使用所有 API 无法读取租户 B 任何数据
   - 定期渗透测试：越权访问测试、IDOR（不安全直接对象引用）测试
```

### 9.2 资源配额管理

| 配额项 | 基础版 | 专业版 | 企业版 |
| :--- | :---: | :---: | :---: |
| 最大 Agent 数量 | 10 | 50 | 无限 |
| 最大 span 接收量/天 | 100 万 | 1000 万 | 自定义 |
| 数据保留天数 | 30 天 | 90 天 | 最长 365 天 |
| 存储容量上限 | 50 GB | 500 GB | 自定义 |
| 检测引擎并发 | 标准 | 高 | 独享 |

超出配额时，Collector 返回 429 RESOURCE_EXHAUSTED，SDK 本地缓冲并重试。

---

## 10. 管理端代码架构设计

管理端后端基于**若依（RuoYi）框架**进行二次开发，采用 Spring Boot + MyBatis + Shiro 的单体分模块架构；安全检测引擎作为独立 Python 服务通过 HTTP/gRPC 接口与主服务交互。

### 10.1 整体项目结构

```
server/
├── RuoYi/
│   ├── ruoyi-admin/               # Web 入口模块（Controller 层 + 启动类）
│   ├── ruoyi-system/              # 核心业务模块（domain/mapper/service）
│   ├── ruoyi-framework/           # 框架配置模块（认证/权限/AOP/拦截器）
│   ├── ruoyi-common/              # 公共基础模块（工具类/常量/异常/注解）
│   ├── ruoyi-quartz/              # 定时任务模块（周报/月报/TTL清理）
│   ├── ruoyi-generator/           # 代码生成模块
│   ├── sql/
│   │   ├── ry_20260319.sql        # 若依基础表结构
│   │   ├── quartz.sql             # 若依定时任务表
│   │   └── agentsec-platform/     # 管理端业务初始化与增量脚本
│   │       ├── agentsec_init.sql
│   │       └── migrations/
│   └── pom.xml                    # 父 POM，统一依赖版本管理
└── RuoYi-Vue3/
    └── src/
        ├── views/                 # 页面视图目录
        │   ├── monitor/           # 可承载监控相关页面
        │   ├── system/            # 系统管理页面
        │   └── agentsec/          # 建议新增的业务页面目录
        ├── api/                   # 前端 API 封装
        │   ├── monitor/
        │   ├── system/
        │   └── agentsec/          # 建议新增的业务接口目录
        ├── components/            # 共享组件
        ├── router/                # 路由配置
        ├── store/                 # 状态管理
        ├── layout/                # 布局骨架
        └── utils/                 # 请求与工具方法
```

### 10.2 Java 后端模块详细结构

#### 10.2.1 ruoyi-admin（Web 入口模块）

```
ruoyi-admin/
├── src/main/java/com/ruoyi/
│   ├── RuoYiApplication.java              # Spring Boot 启动类
│   └── web/
│       └── controller/
│           ├── monitor/                   # 若依现有监控控制器目录
│           ├── system/                    # 若依现有系统控制器目录
│           └── agentsec/                  # 建议新增的管理端业务控制器目录
│               ├── AgentAppController.java
│               ├── AgentInstanceController.java
│               ├── SessionController.java
│               ├── RiskEventController.java
│               ├── AlertRuleController.java
│               ├── BlockController.java
│               └── SecurityReportController.java
└── src/main/resources/
    ├── application.yml                    # 主配置
    ├── application-druid.yml              # 数据源配置
    ├── logback.xml                        # 日志配置
    └── banner.txt                         # 启动 Banner
```

#### 10.2.2 ruoyi-system（核心业务模块）

```
ruoyi-system/
├── src/main/java/com/ruoyi/system/
│   ├── domain/
│   │   └── agentsec/                      # 建议新增业务实体目录
│   │       ├── AgentApp.java
│   │       ├── AgentInstance.java
│   │       ├── AppToken.java
│   │       ├── RiskEvent.java
│   │       ├── AlertRule.java
│   │       ├── BlockLog.java
│   │       ├── NotificationChannel.java
│   │       └── SecurityReport.java
│   ├── mapper/
│   │   └── agentsec/                      # 建议新增业务 Mapper 目录
│   │       ├── AgentAppMapper.java
│   │       ├── RiskEventMapper.java
│   │       └── AlertRuleMapper.java
│   └── service/
│       ├── agentsec/                      # 建议新增业务 Service 接口目录
│       │   ├── IAgentAppService.java
│       │   ├── ISessionQueryService.java
│       │   ├── IRiskEventService.java
│       │   ├── IAlertRuleService.java
│       │   ├── IBlockService.java
│       │   ├── INotificationService.java
│       │   └── ISecurityReportService.java
│       └── impl/agentsec/                 # 业务 Service 实现目录
│           ├── AgentAppServiceImpl.java
│           ├── SessionQueryServiceImpl.java
│           ├── RiskEventServiceImpl.java
│           ├── AlertRuleServiceImpl.java
│           ├── BlockServiceImpl.java
│           ├── NotificationServiceImpl.java
│           └── SecurityReportServiceImpl.java
└── src/main/resources/mapper/
    └── agentsec/                          # MyBatis XML 映射文件
        ├── AgentAppMapper.xml
        ├── RiskEventMapper.xml
        └── AlertRuleMapper.xml
```

#### 10.2.3 ruoyi-framework（框架配置模块）

```
ruoyi-framework/
└── src/main/java/com/ruoyi/framework/
    ├── config/                            # 框架配置
    │   ├── ShiroConfig.java
    │   ├── ThreadPoolConfig.java
    │   └── agentsec/                      # 建议新增业务扩展配置
    │       ├── KafkaConfig.java
    │       ├── RedisConfig.java
    │       ├── ClickHouseConfig.java
    │       ├── OpenSearchConfig.java
    │       └── WebSocketConfig.java
    ├── aspectj/                           # AOP 扩展
    ├── manager/                           # 异步任务管理
    ├── security/                          # 安全能力
    └── websocket/                         # WebSocket 扩展
```

#### 10.2.4

---

## 11. 接口契约设计

### 11.1 REST API 规范总览

所有 API 遵循统一规范：
- **认证**：优先复用若依登录态与 Token 鉴权，SDK/外部接入再扩展 `X-API-Key`
- **租户隔离**：租户上下文由服务端鉴权和数据权限统一注入，前端不直接传递 `tenant_id`
- **路径风格**：沿用若依控制器风格，以模块前缀组织，例如 `/agentsec/app/*`、`/agentsec/event/*`
- **分页**：沿用若依分页参数与返回结构，接口通过 `pageNum`、`pageSize` 接收分页参数
- **错误格式**：优先复用若依统一响应对象 `AjaxResult` 与表格分页对象 `TableDataInfo`

### 11.2 核心 API 端点

| API 端点 | 方法 | 功能描述 | 对应模块 |
| :--- | :---: | :--- | :--- |
| `/agentsec/assets/app/list` | GET | 接入应用列表（状态/心跳/SDK版本） | A-M1-02 |
| `/agentsec/app` | POST | 创建 Agent 应用，返回 App Token | A-M1-02 |
| `/agentsec/app/config/{id}` | GET/PUT | 获取/更新 Agent 监控配置 | A-M1-03 |
| `/agentsec/app/autoRegister` | POST | Agent 自动注册（设备指纹） | A-M1-04 |
| `/agentsec/observe/traces` | GET | Trace 视图列表（分页/过滤/风险排序） | A-M4-02 |
| `/agentsec/observe/spans` | GET | Span 证据列表（按 span_kind/status/risk 过滤） | A-M4-02 |
| `/agentsec/session/list` | GET | Session 聚合列表（仅多轮/长任务） | A-M4-02 |
| `/agentsec/trace/{id}/spans` | GET | 完整 Trace 调用链重建 | A-M4-02 |
| `/agentsec/session/{id}` | GET | 完整 Session 聚合上下文 | A-M4-02 |
| `/agentsec/dashboard/timeseries` | GET | 时序聚合查询（LLM调用量/Token/延迟） | A-M4-02 |
| `/agentsec/dashboard/summary` | GET | 近24h/7d/30d 关键安全指标汇总 | A-M4-02 |
| `/agentsec/event/list` | GET | 安全事件列表（分页/多维过滤） | A-M6-03 |
| `/agentsec/event/{id}` | PUT | 更新事件状态（认领/确认/误报/关闭） | A-M6-03 |
| `/agentsec/search/content` | POST | 内容检索：Prompt/Response/Tool 输入输出（OpenSearch） | A-M4-02 |
| `/agentsec/rule/list` | GET | 告警规则列表 | A-M5-01 |
| `/agentsec/rule` | POST | 创建告警规则 | A-M5-01 |
| `/agentsec/rule/test/{id}` | POST | 规则沙箱回放测试（历史数据） | A-M5-01 |
| `/agentsec/block` | POST | 手动触发阻断（Session/实例/应用级） | A-M5-02 |
| `/agentsec/blockLog/list` | GET | 阻断日志列表 | A-M5-02 |
| `/agentsec/report/list` | GET | 安全报告列表 | A-M6-04 |
| `/agentsec/report` | POST | 触发报告生成 | A-M6-04 |
| `/agentsec/tenant/list` | GET | 租户管理（仅 SA） | A-M7-01 |
| `/agentsec/user/list` | GET | 用户与权限管理 | A-M7-01 |
| `/agentsec/apiKey/list` | GET | API Key 管理 | A-M7-02 |
| `/agentsec/audit/list` | GET | 操作审计日志查询（只读） | A-M7-02 |
| `WS /ws/agentsec/alerts` | WebSocket | 实时告警推送（critical 级别） | A-M5-03 |
| `WS /ws/agentsec/commands` | WebSocket | 阻断指令实时下发（SDK 接入） | A-M5-02 |

### 11.3 Session 调用链查询响应示例

```json
GET /agentsec/session/{session_id}

Response 200:
{
  "session_id": "sess-abc123",
  "app_id": "uuid-...",
  "total_spans": 15,
  "duration_ms": 3421,
  "anomaly_score": 72,
  "risk_events": [
    {
      "id": "uuid",
      "span_id": "span-001",
      "risk_type": "prompt_injection",
      "risk_level": "high",
      "confidence": 0.92,
      "evidence": { "matched_pattern": "忽略之前的指令" }
    }
  ],
  "spans": [
    {
      "span_id": "span-001",
      "parent_span_id": null,
      "span_name": "llm.chat_completion",
      "span_kind": "llm",
      "timestamp": "2026-03-01T12:00:00Z",
      "duration_ms": 1200,
      "model": "gpt-4o",
      "token_prompt": 512,
      "token_completion": 256,
      "risk_level": "high",
      "risk_type": "prompt_injection",
      "security_tags": ["prompt_injection"]
    }
  ]
}
```

---

## 12. 关键技术决策

### 12.1 微服务拆分策略

管理端采用**按业务能力拆分**的微服务架构：

| 拆分原则 | 说明 |
| :--- | :--- |
| 高频服务独立 | 心跳服务、配置服务（万级 Agent 高频访问）独立部署，不与业务逻辑混用 |
| 检测引擎隔离 | Python 检测引擎（依赖重型 ML 库，内存占用大）与 Go 服务完全隔离 |
| 数据写入与查询分离 | ClickHouse 写入服务（高吞吐 Kafka 消费）与查询服务（低延迟 REST API）独立优化 |
| 告警与通知分离 | 规则引擎与通知服务解耦，通知失败不影响规则匹配和阻断指令执行 |

### 12.2 失败隔离（Fail-Open 原则）

- **检测引擎降级**：任意子引擎不可用，其他子引擎正常工作，span 仍正常写入存储（不丢数据）
- **通知失败兜底**：通知渠道不可达，风险事件仍写入数据库，控制台可查看
- **Collector 故障兜底**：SDK 本地环形缓冲（10,000 span），Kafka 持久化（RF=3），双重兜底
- **检测结果缓存**：相同 `prompt_hash` 命中 Redis 缓存，避免单点 ML 服务故障影响全量 span

### 12.3 前端状态管理策略

- **服务端状态**：基于 `Axios` 请求封装与页面级数据加载组织查询逻辑，必要时再增量引入缓存层
- **客户端状态**：基于 `Pinia` / 若依现有 `store` 体系管理 UI 状态与业务状态
- **实时状态**：WebSocket 消息触发页面刷新或局部数据重载，保证数据一致性

### 12.4 安全审计日志不可篡改设计

```sql
-- 审计日志表：Append-Only，不授予 DELETE / UPDATE 权限
-- 数据库层：REVOKE DELETE ON audit_logs FROM admin_role;

CREATE TABLE audit_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id      UUID,
    actor_type    VARCHAR(20),    -- user / api_key / system
    action        VARCHAR(100),   -- list_risk_events / create_rule / block_session
    resource_type VARCHAR(50),
    resource_id   VARCHAR(100),
    request_ip    INET,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- 注意：无 updated_at，无 deleted_at，设计为不可修改
);
```

---

## 13. 稳定性保障策略

### 13.1 高可用设计

| 组件 | 副本策略 | 故障恢复机制 |
| :--- | :--- | :--- |
| OTel Collector | 3 副本 | LoadBalancer 30s 内切换，Kafka 缓冲兜底 |
| Kafka | 3 Broker，RF=3 | 任意 1 Broker 宕机不影响读写 |
| ClickHouse | 2 副本 + ZooKeeper | 主从自动切换 |
| PostgreSQL | 主从复制 + Patroni | 自动故障切换（< 30s） |
| Redis | Sentinel 模式（3 节点） | 自动主从切换，SDK 本地轮询兜底 |
| 检测引擎 | 每个子引擎 2+ 副本 | 进程重启自动恢复，Kafka offset 持久化 |
| API 网关 | 3 副本 | 无状态，任意副本可服务 |
| Keycloak | 2 副本 + Redis 会话缓存 | 会话持久化到 Redis，实例重启不影响登录态 |

**平台整体可用性目标**：99.9%（年允许停机 < 8.7h）
**数据丢失目标**：RPO = 0（Kafka 持久化 + SDK 本地缓冲双重保障）

### 13.2 背压与限流

```
数据管道背压控制：
  Collector 本地队列（10,000 span）
    → 水位达 80%：通知上游 SDK 降速（OTLP 返回 RESOURCE_EXHAUSTED）
    → 水位达 95%：返回 429，SDK 切换本地缓冲
    → Kafka Consumer Lag > 10,000：运维告警

API 层限流（Redis 滑动窗口）：
  默认：1,000 req/min/API Key
  超限：返回 429 + Retry-After 头
  关键 API（查询/导出）独立限流配额
  控制台用户：基于 JWT 的用户级限流
```

### 13.3 数据可靠性保障链

```
写入可靠性：
  SDK 本地缓冲
    → OTel Collector（本地队列 10,000）
    → Kafka（RF=3，持久化）
    → ClickHouse 写入服务（批量 + 失败重试 + 死信队列）
    → ClickHouse（ReplacingMergeTree，span_id 去重）

风险事件可靠性：
  检测引擎
    → PostgreSQL（事务写入）
    → 告警引擎（Kafka agentsec-risk-events）
    → Redis + WebSocket（阻断，双通道）

通知可靠性：
  告警通知失败 → 自动重试 3 次（指数退避：1s/5s/30s）
  最终失败 → notification_failures 表 + 控制台告警图标
```

### 13.4 平台自监控

| 指标 | 来源 | 告警阈值 |
| :--- | :--- | :--- |
| Collector 接收 QPS | OTel Collector /metrics | < 预期 50% 持续 5min 告警 |
| Kafka Consumer Lag | Kafka Exporter | > 10,000 条告警 |
| ClickHouse 写入延迟 | ClickHouse Exporter | > 5s（P99）告警 |
| ClickHouse 写入失败率 | 自定义 metrics | > 1% 持续 2min 告警 |
| 检测引擎处理延迟 | Python 服务 /metrics | > 3s（P99）告警 |
| PostgreSQL 主从延迟 | pg_replication_slots | > 10s 告警 |
| API 服务错误率 | 各服务 /metrics | > 1% 持续 2min 告警 |
| Collector 进程存活 | 健康检查接口 /healthz | 存活探针失败立即告警 |

---

## 14. 性能基准

### 14.1 关键性能指标

| 指标 | 目标 | 测试方法 |
| :--- | :--- | :--- |
| Collector 接收 QPS | > 50,000 span/s（集群） | k6 gRPC 压测，线性增加并发 |
| ClickHouse 写入延迟 | < 5s P99（端到端） | Span 时间戳 vs 写入时间戳 |
| Prompt 检测延迟 | < 3s P99（入 Kafka 到风险事件入库） | Kafka 消费延迟监控 |
| MCP 阻断延迟 | < 5s（端到端，事件→SDK 执行） | 端到端链路打点 |
| Session 查询响应 | < 500ms P99（span 数 < 200） | wrk 并发 HTTP 压测 |
| 时序聚合查询 | < 2s（7天，5min粒度） | 数据库查询计划分析 |
| Prompt 全文检索 | < 1s（OpenSearch） | ab 压测 |
| 控制台首屏加载 | < 2s | Lighthouse CI 集成 |
| 告警端到端延迟 | < 10s（事件→飞书通知收到） | 端到端链路打点 |

### 14.2 测试策略

| 测试类型 | 工具 | 目的 |
| :--- | :--- | :--- |
| 压力测试 | k6 / wrk / ab | 验证各接口在目标 QPS 下的响应时间 |
| 大数据量测试 | 自研脚本 | 单租户 1 亿 span，验证 ClickHouse 查询不退化 |
| 多租户隔离测试 | 自动化测试套件 | 任何 API 请求无法跨租户读取数据 |
| 安全渗透测试 | 手工 + OWASP ZAP | SQL 注入 / 越权访问 / IDOR / XSS |

---

## 16. 技术风险与缓解措施

| 风险 | 等级 | 缓解措施 |
| :--- | :---: | :--- |
| NeMo Guardrails 检测延迟高（LLM 调用） | 高 | 异步检测（不阻塞 span 写入）；轻量规则快速路径；相同 prompt_hash 结果缓存 |
| Kafka Consumer Lag 积压 | 高 | 水平扩展消费者；检测引擎降级（跳过意图对齐等重量级检测） |
| ClickHouse 写入热点 | 中 | 按 tenant_id 分片；批量写入聚合（1000条/5s）；SSD 热数据层 |
| LlamaFirewall AlignmentCheck 成本高 | 高 | 仅对高价值任务触发；严格限制并发（max 8）；LLM 调用成本监控告警 |
| 多租户数据泄露 | 极高 | API 层强制过滤 + 数据库 RLS 双重防御；定期安全审计；自动化隔离测试 |
| Keycloak 单点故障 | 中 | 多副本部署；会话缓存到 Redis；API Key 模式作为降级手段 |
| 越狱模式库覆盖率不足 | 中 | 定期从安全社区（GitHub）同步更新模式库；误报反馈机制自动优化 |
| 规则引擎误配置导致大量误报 | 中 | 规则测试沙箱（上线前历史回跑）；规则版本管理（一键回滚）；FP 率监控告警 |

---

- **前端状态管理**：基于若依 Vue3 现有 `store` 体系演进，避免脱离当前代码结构另起一套前端框架。
- **规则引擎兼容性**：全面支持 `Sigma` 规则格式，降低安全团队迁移和编写规则的成本。
*文档结束*




