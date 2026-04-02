# AI Agent 安全监控平台 — 客户端技术概要设计文档
<!-- test sync -->

**文档编号**：AGENTSEC-TECH-CLIENT-OVR-v1.1
**版本**：v1.1
**日期**：2026-03
**状态**：评审中
**关联文档**：架构设计文档 v1.0 / 客户端 PRD v1.0

**变更记录**：
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03 | 初稿 |
| v1.1 | 2026-03 | 注册激活流程改为机器指纹自动注册，移除 enroll-key 依赖（适配纯内网部署场景） |

---

## 1. 文档目的与范围

本文档描述 AI Agent 安全监控平台**客户端侧**（Client Side）的技术概要设计，涵盖：

- 技术语言与运行时选型
- 核心组件与技术栈选型
- 整体模块结构与代码组织规划
- 关键技术决策与稳定性保障策略

客户端的核心定位是：**低侵入、零修改、高可靠地将客户 AI Agent 纳入安全监控体系**，任何 SDK 内部错误均不得影响 Agent 业务进程（Fail-Open 原则）。

---

## 2. 业务流程与核心功能

### 2.1 核心业务场景

客户端覆盖以下三类核心业务场景：

| # | 场景 | 典型触发 | 客户端行为 |
|---|------|----------|------------|
| 1 | **LLM 调用监控** | Agent 调用 OpenAI / Anthropic / 本地模型 | 自动捕获 prompt / response / token 用量，进行端侧脱敏、密钥扫描与注入拦截 |
| 2 | **工具调用监控** | Agent 调用 MCP 工具 / 外部 HTTP API / DB | 捕获工具名、入参、出参，检查白名单与危险参数 |
| 3 | **算力配额管控** | Token 消耗接近或达到预算上限 | 实时熔断非预期的高额调用 |
| 4 | **实时阻断响应** | 管理端下发阻断指令 | BlockCheckProcessor 拦截下一次 LLM 调用，返回安全回复 |

### 2.2 全业务生命周期流程图

本节描述从 SDK 安装到安全检测上报的**完整生命周期**，分为五个阶段。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  阶段一：安装（Install）                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Python:  pip install agentsec-sdk                                          │
│  Java:    下载 agentsec-javaagent.jar，配置 JVM 启动参数                     │
│  CLI:     curl 下载 agentsec-cli 二进制 / brew / apt 安装                   │
│                                                                             │
│  安装完成 ──► 进入阶段二                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  阶段二：注册 & 激活（Register & Activate）                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  【内网零配置自动注册模式】                                                  │
│                                                                             │
│  1. SDK / CLI 启动时自动采集机器指纹                                        │
│       fingerprint = { hostname, machine_id, os, arch, ip, sdk_version }     │
│       │                                                                     │
│       ▼                                                                     │
│  2. POST /api/v1/agents/auto-register  （无需 enroll-key）                   │
│       Body: { fingerprint }                                                 │
│       │                                                                     │
│       ▼                                                                     │
│  3. 管理端自动审批 → 返回 agent_token                                       │
│       │                                                                     │
│       ├──► token 写入本地缓存 ~/.agentsec/agent.token                       │
│       │                                                                     │
│       ▼                                                                     │
│  4. 后续启动直接读取缓存 token，跳过注册步骤                                │
│                                                                             │
│  注：若设置了 AGENTSEC_TOKEN 环境变量，直接使用，跳过自动注册               │
│                                                                             │
│  注册完成 ──► 进入阶段三                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  阶段三：部署 & 初始化（Deploy & Init）                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Agent 进程启动                                                              │
│       │                                                                     │
│       ├──► [Init-1] 插桩注册                                                 │
│       │       instrument_openai() / instrument_anthropic() / instrument_mcp()│
│       │       openllmetry TracerProvider 注入全局                            │
│       │                                                                     │
│       ├──► [Init-2] Processor Pipeline 挂载                                 │
│       │       PIIRedactor → SecurityTagger → BlockChecker → SamplingProcessor│
│       │                                                                     │
│       ├──► [Init-3] Exporter 初始化                                          │
│       │       OTLPExporter(collector_url) → RetryExporter → LocalBuffer     │
│       │       建立 OTLP gRPC 连接（TLS），握手成功则 ready                   │
│       │                                                                     │
│       ├──► [Init-4] 后台服务启动（daemon 线程）                              │
│       │       ConfigManager.start()   — 拉取初始配置                        │
│       │       HeartbeatService.start() — 30s 心跳                           │
│       │       LocalApiServer.start()  — :13133 健康端点                     │
│       │                                                                     │
│       └──► [Init-5] SDK 自注册上报                                           │
│               POST /v1/agents/register                                      │
│               Body: { tenant_id, app_id, agent_token, sdk_version, pid }    │
│               管理端标记该 Agent 实例为「在线」                               │
│                                                                             │
│  初始化完成 ──► 进入阶段四                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  阶段四：运行时检测（Runtime Detection）                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户输入 ──► Agent 主循环                                                   │
│                    │                                                        │
│       ┌────────────▼────────────┐                                           │
│       │  LLM / 工具调用触发      │                                           │
│       │  自动插桩开启 Span        │                                           │
│       └────────────┬────────────┘                                           │
│                    │                                                        │
│       ┌────────────▼────────────┐   命中阻断/配额？                          │
│       │  SecurityGateProcessor  │──── 是 ──► 抛 AgentSecBlockException      │
│       │  [Block + RateLimit]    │           业务层返回安全回复/429           │
│       └────────────┬────────────┘                                           │
│                    │ 未命中，放行                                             │
│       ┌────────────▼────────────┐                                           │
│       │  LocalSecurityScanner   │  1. LLM Guard (注入检测)                  │
│       │  [Injection + Secret]   │  2. detect-secrets (凭证扫描)             │
│       └────────────┬────────────┘                                           │
│                    │                                                        │
│       ┌────────────▼────────────┐                                           │
│       │  PIIRedactor            │  调用 Microsoft Presidio 本地清洗隐私数据  │
│       │  (本地脱敏引擎)         │  手机号/身份证/APIKey/银行卡/Email          │
│       └────────────┬────────────┘                                           │
│                    │                                                        │
│       ┌────────────▼────────────┐                                           │
│       │  Enricher & Tagger      │  注入 security.risk.level / tag           │
│       │  注入多租户标识          │  注入 tenant_id / app_id / session_id     │
│       └────────────┬────────────┘                                           │
│                    │                                                        │
│       ┌────────────▼────────────┐   被采样丢弃？                             │
│       │  SamplingProcessor      │──── 是 ──► span 丢弃，不上报              │
│       │  按配置采样率决策        │                                           │
│       └────────────┬────────────┘                                           │
│                    │ 保留上报                                                │
│       ┌────────────▼────────────┐                                           │
│       │  LLM 调用实际执行        │  SDK 等待 LLM 响应（业务主路径）           │
│       │  response 写回 Span      │  response/completion 同步写入 span        │
│       └────────────┬────────────┘                                           │
│                    │                                                        │
│                    ▼  span.end()                                             │
│             进入阶段五：上报                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  阶段五：上报 & 反馈闭环（Export & Feedback Loop）                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  span.end() 触发                                                            │
│       │                                                                     │
│       ▼                                                                     │
│  BatchSpanExporter 缓冲区（批量聚合，默认 512 span 或 5s 到期）               │
│       │                                                                     │
│       ├──► 网络正常 ──► OTLP gRPC (TLS) ──► OTel Collector (:4317)
│       │                   重试策略：失败最多 5 次，指数退避 1→16s
│       │
│       │       ├──► 本地审计溯源 ──► File Exporter ──► /var/log/agentsec/compliance.log
│       │
│       │                                    ▼
│       │                              Kafka Topic                            │
│       │                                    │                                │
│       │                    ┌───────────────┼───────────────┐                │
│       │                    ▼               ▼               ▼                │
│       │             安全检测引擎      行为分析引擎      PII 二次审计           │
│       │          (Prompt Injection)  (异常调用链)    (服务端脱敏复核)         │
│       │                    │               │               │                │
│       │                    └───────────────┼───────────────┘                │
│       │                                    ▼                                │
│       │                         ClickHouse / PostgreSQL                     │
│       │                                    │                                │
│       │                          风险等级 ≥ high？                           │
│       │                          是 ──► 告警引擎                             │
│       │                                    │                                │
│       │                    ┌───────────────┼──────────────────┐             │
│       │                    ▼               ▼                  ▼             │
│       │             邮件/钉钉告警    Dashboard 标注         阻断指令生成      │
│       │                                                        │             │
│       │                                    WebSocket 推送      │             │
│       │                                    ◄───────────────────┘             │
│       │                                    │                                │
│       │                              SDK BlockCheckProcessor                │
│       │                              更新本地阻断列表（TTL 1h）              │
│       │                              下次 LLM 调用前命中 → 阻断              │
│       │                                                                     │
│       └──► 网络中断 ──► LocalSpanBuffer（环形队列，上限 10,000 span）        │
│                          网络恢复后自动重传                                   │
│                                                                             │
│  ◄─────────────────── 持续运行，回到阶段四 ────────────────────────────────  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 阶段状态转换一览

| 阶段 | 前置条件 | 完成标志 | 异常处理 |
|------|----------|----------|----------|
| 安装 | 网络可达 PyPI / CDN | 依赖安装无报错 | 私有源镜像兜底 |
| 注册 | 管理端服务可达（内网） | 收到 agent_token 并写入本地缓存 | 注册失败 → Fail-Open，SDK 降级为旁路模式；token 缓存命中则跳过注册 |
| 激活 | config.yaml 存在且 token 有效 | bootstrap.init() 无异常 | Fail-Open，SDK 降级为旁路模式 |
| 部署初始化 | Collector 网络可达 | gRPC 握手成功 + 自注册响应 200 | Collector 不可达 → LocalBuffer 兜底，异步重连 |
| 运行时检测 | SDK 已激活 | 持续拦截 LLM/工具调用 | 插桩异常隔离，不影响业务调用 |
| 上报反馈 | Span 数据完整 | Collector 返回 200 | 重试 5 次后仍失败 → 写入 LocalBuffer |

### 2.4 主要功能清单

#### F1 — LLM 调用自动插桩
- 零代码修改接入：通过 openllmetry 自动插桩 OpenAI SDK / Anthropic SDK / LangChain / LlamaIndex / CrewAI
- Java 端通过 JavaAgent 字节码织入，覆盖 HTTP 客户端 + 自定义 LLM 调用框架
- 捕获字段：`gen_ai.prompt`、`gen_ai.completion`、`gen_ai.model`、`gen_ai.usage.prompt_tokens`、`gen_ai.usage.completion_tokens`

#### F2 — 本地 PII 与密钥脱敏 (DLP)
- 在 span 离开进程前执行，数据**不出境**即完成脱敏与扫描
- 核心引擎：Microsoft Presidio (PII) + detect-secrets (Secrets)
- 支持 hash 模式（SHA256）和掩码模式（`***`），可按字段配置
- 提供审计模式：发现敏感信息但不脱敏，仅在 span 中打标，用于内部合规审计

#### F11 — 算力配额与速率熔断
- 实时统计端侧 Token 消耗，支持配置日/时配额
- 超限即阻断，防止 Agent 故障演变为高额账单风险

#### F12 — 本地合规审计日志
- 根据合规需求，将所有「拦截动作」与「脱敏操作」本地落盘留档
- JSON 滚动日志，支持加密存储与外部日志采集器（Fluentd/Filebeat）挂载

#### F3 — 安全标签注入
- 为每个 LLM / 工具调用 span 注入 `security.risk.level`（none / low / medium / high / critical）
- 客户端仅做初步标注（基于简单规则），深度检测由服务端安全引擎完成
- 注入 `agentsec.tenant_id`、`agentsec.app_id`、`agentsec.session_id` 多租户隔离标识

#### F4 — 动态采样控制
- 默认采样率 100%，支持管理端下发采样率配置
- 采样率变更通过 WebSocket 推送，**5 秒内生效**（无需重启 Agent）
- 支持按 `security.risk.level` 差异化采样（高风险全量采集，低风险按比例采集）

#### F5 — 异步批量导出 & 本地缓冲
- `BatchSpanExporter` 异步批量发送，额外延迟 < 5ms (P99)，不阻塞 LLM 调用
- 网络中断时切换至 `LocalSpanBuffer`（内存环形队列，上限 10,000 span）
- `RetryExporter` 最多重试 5 次（指数退避：1s / 2s / 4s / 8s / 16s），恢复后自动重传缓冲 span

#### F6 — 配置热更新
- `ConfigManager` 每 30 秒轮询管理端配置 API（`ETag` / `304 Not Modified` 优化）
- 原子替换内存配置对象（`threading.Lock`），变更实时通知各 Processor
- 管理的配置项：采样率、PII 脱敏开关、阻断模式、span 内容截断长度

#### F7 — 心跳与连通性检测
- `HeartbeatSvc` 每 30 秒向管理端上报 SDK 存活状态
- 上报内容：SDK 版本、运行时语言/版本、Collector 连通性、缓冲队列水位
- 管理端据此判断 Agent 是否离线并触发断连告警

#### F8 — 本地健康 API
- 内嵌轻量 HTTP 服务监听 `localhost:13133`
- `/agentsec/health` — K8s 存活/就绪探针可直接对接
- `/agentsec/metrics` — Prometheus 格式指标（span 上报量、导出延迟 P99、缓冲队列水位、错误率）
- `/agentsec/traces` — 查询本地缓冲中最近 N 条 span（调试用）

#### F9 — 实时阻断响应
- 管理端检测到高风险事件后，通过 WebSocket 长连接向 SDK 推送 `BlockCommand`
- `BlockCheckProcessor` 在**每次 LLM 调用前**检查阻断列表（Redis key: `block:{session_id}`）
- 命中阻断 → 抛出 `AgentSecBlockException` → 业务层捕获 → 返回配置的安全回复文案
- 阻断指令带 TTL（默认 1 小时），自动过期

#### F10 — CLI 诊断工具
- `agentsec register` — 手动触发机器指纹采集与自动注册（首次部署或 token 失效时使用）
- `agentsec verify` — 发送测试 span，端到端验证 SDK → Collector → 管理端链路
- `agentsec diagnose` — 本地环境诊断（网络连通性、Token 有效性、配置合法性）
- `agentsec status` — 查看当前 SDK 运行状态（调用本地 Health API）
- `agentsec traces` — 查看最近上报的 span 列表

---

## 3. 技术语言选型

### 2.1 选型原则

| 原则 | 说明 |
|------|------|
| 生态优先 | 优先选择 OpenTelemetry 官方生态一致的语言，降低维护成本 |
| 低侵入 | Python 的自动插桩、Java 字节码插桩均要求零代码修改 |
| 隔离安全 | SDK 内部异常不得传播至业务进程，需语言级异常隔离 |
| 多语言覆盖 | 主流 AI Agent 以 Python/Java 为主，CLI 工具用 Go 保证跨平台分发 |

### 2.2 各组件语言分配

| 组件 | 语言 | 版本要求 | 选型理由 |
|------|------|----------|----------|
| Python SDK（agentsec-sdk） | Python | >= 3.9 | 覆盖 90%+ AI Agent 生态（LangChain/OpenAI SDK/LlamaIndex），OTel Python 生态成熟 |
| Java SDK（agentsec-javaagent.jar） | Java | JDK >= 11 | JVM 字节码插桩（java.lang.instrument），零代码修改；OTel JavaAgent 官方生态 |
| CLI 工具（agentsec-cli） | Go | >= 1.21 | 静态编译单二进制，无运行时依赖，跨平台（Linux/macOS/Windows）分发简单 |
| 本地 HTTP 服务（健康检查 / Trace API） | Python / Go | 同 SDK 宿主语言 | 内嵌在 SDK 进程中，复用宿主语言；健康 API 用 Go 内嵌更轻量 |
| Node.js SDK（v2，规划中） | TypeScript | >= 18 | 覆盖 Node.js Agent 生态，openllmetry 已有 JS 实现 |

---

## 3. 核心技术组件选型

### 3.1 采集插桩层

| 组件 | 版本 | 用途 | 引入方式 |
|------|------|------|----------|
| openllmetry（traceloop-sdk） | >= 0.22 | Python SDK 核心：自动插桩 openai/anthropic/LangChain/LlamaIndex/CrewAI，捕获 prompt/response/token | pip install traceloop-sdk |
| opentelemetry-instrumentation-openai-v2 | >= 0.22 | 捕获 OpenAI SDK 完整 messages/model/temperature 写入 span attributes | pip install |
| opentelemetry-python-contrib | >= 0.44 | requests/httpx/aiohttp/Flask/FastAPI HTTP 自动插桩 | pip install |
| opentelemetry-javaagent.jar（定制版） | >= 2.0 | Java 字节码插桩，覆盖 OkHttp/Apache HttpClient/Feign/JDBC/Kafka/gRPC/Spring Web 等 100+ 框架 | javaagent 启动参数 |
| opentelemetry-sdk-go | >= 1.20 | CLI 工具内部 trace 上报（verify 命令发送测试 span） | go mod |

### 3.2 数据传输层

| 组件 | 版本 | 用途 |
|------|------|------|
| opentelemetry-exporter-otlp-grpc | >= 0.44 | OTLP/gRPC 协议导出，TLS 加密，批量发送 |
| opentelemetry-exporter-otlp-http | >= 0.44 | OTLP/HTTP 备用协议（兼容部分网络环境） |
| grpcio / grpc-go | Python >= 1.59 / Go >= 1.20 | gRPC 传输底层 |

### 3.3 本地服务层（SDK 内嵌）

| 组件 | 版本 | 用途 |
|------|------|------|
| aiohttp（Python） / net/http（Go） | Python >= 3.9 / 标准库 | 内嵌轻量 HTTP 服务器，暴露 /agentsec/health 和 /agentsec/metrics |
| prometheus-client（Python）/ prometheus/client_golang | >= 0.18 | 暴露 Prometheus 格式 metrics（span 上报量、延迟分位数、错误数） |
| threading / asyncio（Python） | 标准库 | SDK 健康服务与主进程并发隔离，不阻塞业务线程 |

### 3.4 配置管理层

| 组件 | 版本 | 用途 |
|------|------|------|
| httpx（Python）/ net/http（Go） | >= 0.25 | 轮询管理端配置 API（30s 间隔），支持 HTTP 代理 |
| pydantic（Python） | >= 2.0 | 配置模型定义与验证，类型安全保障 |
| watchdog / polling | - | 本地 .env 文件变更监听（可选） |

### 3.5 本地 PII 脱敏

| 组件 | 版本 | 用途 |
|------|------|------|
| re（标准库） | - | 内置正则规则（手机号/身份证/银行卡/API Key）本地脱敏 |
| hashlib（标准库） | - | hash 脱敏模式（SHA256） |
| 自研 SensitiveFieldProcessor | - | OTel SpanProcessor 扩展，在 span 导出前执行脱敏 |

---

## 4. 整体架构设计

### 4.1 客户端架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent 业务进程                      │
│   (Python / Java / Node.js)                             │
├─────────────────────────────────────────────────────────┤
│  L1: 插桩采集层（零侵入）                                │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Python SDK       │  │ Java JavaAgent               │ │
│  │ openllmetry      │  │ OTel JavaAgent +             │ │
│  │ OTel Contrib     │  │ 自定义 LLM Instrumentation   │ │
│  └────────┬─────────┘  └──────────────┬───────────────┘ │
├───────────│──────────────────────────│─────────────────┤
│  L2: SDK 核心层                        │                 │
│  ┌────────▼──────────────────────────▼─────────────┐   │
│  │  SpanProcessor 链                                │   │
│  │  ① SensitiveFieldProcessor（PII 脱敏）           │   │
│  │  ② SecurityTagProcessor（安全标签注入）          │   │
│  │  ③ SamplingProcessor（采样决策）                 │   │
│  │  ④ BatchSpanExporter → OTLP gRPC（TLS）         │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  L3: SDK 基础服务层                                      │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ ConfigManager    │  │ HeartbeatSvc │  │ LocalAPI  │  │
│  │ 配置拉取 / 热更新 │  │ 心跳上报     │  │ 健康检查  │  │
│  │ 版本管理         │  │ 断连告警     │  │ Trace 查询│  │
│  └──────────────────┘  └──────────────┘  └───────────┘  │
├─────────────────────────────────────────────────────────┤
│  L4: 本地缓冲与重传层                                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │ LocalSpanBuffer（内存环形队列，最多 10000 span）  │   │
│  │ RetryExporter（断线重连，指数退避）              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │ OTLP gRPC / TLS
         ▼
   管理端 OTel Collector
```

### 4.2 进程隔离设计（稳定性核心）

SDK 所有内部服务均与 Agent 业务线程**完全隔离**：

- **Python**：使用独立 daemon 线程运行 ConfigManager、HeartbeatSvc、LocalAPI；BatchExporter 使用独立线程池
- **Java**：使用 OTel JavaAgent 内置线程池；自定义 Instrumentation 通过字节码织入，不阻塞业务方法
- **异常隔离**：所有 SDK 内部线程的 uncaught exception 只记录日志，绝不向上传播至业务进程

---

## 5. 代码结构规划

### 5.1 Python SDK 代码结构

```
agentsec-python-sdk/
├── agentsec/
│   ├── __init__.py               # 公开 API: init(), shutdown()
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py             # Pydantic 配置模型（AgentSecConfig）
│   │   ├── manager.py            # ConfigManager: 拉取/热更新/版本管理
│   │   └── defaults.py           # 默认配置值
│   ├── instrumentation/
│   │   ├── __init__.py
│   │   ├── bootstrap.py          # 自动插桩入口（opentelemetry-instrument 集成）
│   │   ├── openai_v2.py          # OpenAI SDK 插桩（基于 opentelemetry-instrumentation-openai-v2）
│   │   ├── anthropic.py          # Anthropic SDK 插桩
│   │   └── mcp_client.py         # MCP 工具调用插桩（自研）
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── injection_guard.py    # Prompt 注入拦截 SpanProcessor
│   │   ├── pii_redactor.py       # 基于 Presidio 的 PII 脱敏 SpanProcessor
│   │   ├── secret_scanner.py     # 基于 detect-secrets 的凭证扫描 SpanProcessor
│   │   ├── rate_limiter.py       # Token 配额与速率限制 SpanProcessor
│   │   └── security_tagger.py    # 安全标签注入 SpanProcessor
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── otlp_exporter.py      # OTLP gRPC/HTTP 导出器封装
│   │   ├── local_file_exporter.py # 合规审计日志落盘导出器
│   │   ├── local_buffer.py       # 内存环形队列（10000 span）
│   │   └── retry_exporter.py     # 断线重连 + 指数退避
│   ├── heartbeat/
│   │   ├── __init__.py
│   │   └── service.py            # 心跳上报（30s 间隔，daemon 线程）
│   ├── local_api/
│   │   ├── __init__.py
│   │   ├── server.py             # aiohttp 内嵌 HTTP 服务（端口 13133）
│   │   ├── health.py             # GET /agentsec/health
│   │   ├── metrics.py            # GET /agentsec/metrics（Prometheus 格式）
│   │   ├── traces.py             # GET /agentsec/traces
│   │   └── config_status.py      # GET /agentsec/config/status
│   ├── auth/
│   │   ├── __init__.py
│   │   └── token.py              # Token 管理（JWT 解析、过期检测、自动轮转）
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # 结构化日志（SDK 内部使用，不污染业务日志）
│       └── env.py                # 环境变量读取与验证
├── tests/
│   ├── unit/                     # 单元测试（pytest）
│   ├── integration/              # 集成测试（需要 Collector）
│   └── fixtures/                 # 测试数据和 mock
├── pyproject.toml                # 依赖声明（支持 pip install agentsec-sdk）
└── README.md
```

### 5.2 Java SDK 代码结构

```
agentsec-java-agent/
├── buildSrc/                     # Gradle 构建工具
├── agent-bootstrap/              # JavaAgent 引导模块
│   └── src/main/java/com/agentsec/agent/
│       ├── AgentSecBootstrap.java         # premain() 入口
│       ├── AgentClassloaderHack.java      # classloader 隔离
│       └── ExtensionLoader.java           # 加载自定义 Instrumentation
├── instrumentation/
│   ├── openai-java/              # OpenAI Java SDK 插桩
│   │   └── src/main/java/com/agentsec/instrumentation/openai/
│   │       ├── OpenAIInstrumentation.java
│   │       └── ChatCompletionAdvice.java  # ByteBuddy @Advice 织入
│   └── anthropic-java/           # Anthropic Java SDK 插桩（规划）
├── sdk-core/                     # SDK 核心服务（不依赖字节码库）
│   └── src/main/java/com/agentsec/core/
│       ├── config/
│       │   ├── AgentSecConfig.java
│       │   └── ConfigManager.java
│       ├── processor/
│       │   ├── PiiRedactProcessor.java
│       │   ├── SecurityTagProcessor.java
│       │   └── BlockCheckProcessor.java
│       ├── exporter/
│       │   ├── AgentSecOtlpExporter.java
│       │   └── LocalSpanBuffer.java
│       ├── heartbeat/
│       │   └── HeartbeatService.java
│       └── localapi/
│           ├── LocalHttpServer.java       # 内嵌 HTTP 服务
│           ├── HealthHandler.java
│           └── MetricsHandler.java
├── agent-tooling/                # 构建 fat jar 的工具模块
├── tests/
│   ├── smoke-tests/              # 冒烟测试
│   └── integration-tests/        # 集成测试
└── build.gradle
```

### 5.3 CLI 工具代码结构（Go）

```
agentsec-cli/
├── cmd/
│   ├── root.go                   # 根命令（cobra）
│   ├── register.go               # agentsec-cli register（机器指纹采集 & 自动注册）
│   ├── verify.go                 # agentsec-cli verify
│   ├── diagnose.go               # agentsec-cli diagnose
│   ├── status.go                 # agentsec-cli status
│   ├── config.go                 # agentsec-cli config show|diff
│   └── traces.go                 # agentsec-cli traces list|get
├── internal/
│   ├── auth/
│   │   └── token.go              # Token 读取、缓存（~/.agentsec/agent.token）与验证
│   ├── registration/
│   │   └── fingerprint.go        # 机器指纹采集（hostname/machine-id/OS/arch/IP）
│   ├── collector/
│   │   └── client.go             # OTLP gRPC 客户端（发送测试 span）
│   ├── api/
│   │   └── platform_client.go    # 平台 REST API 客户端（register / verify 回调）
│   ├── diagnose/
│   │   └── checker.go            # 诊断检查（环境变量/网络/TLS/Token）
│   └── output/
│       └── formatter.go          # 彩色终端输出（ANSI 颜色）
├── main.go
├── go.mod
└── Makefile                      # 交叉编译：linux/amd64, darwin/arm64, windows/amd64
```

---

## 6. 关键技术决策

### 6.1 Fail-Open 机制

客户端的最高优先原则是：**SDK 任何故障不影响 Agent 业务**。

| 故障场景 | SDK 行为 | 业务影响 |
|----------|----------|----------|
| Collector 网络不可达 | 本地缓冲 span（最多 10000 条），静默重连 | 无影响 |
| Token 过期/无效 | 记录本地日志，停止上报，继续运行 | 无影响 |
| 配置拉取失败 | 使用上次成功的配置快照继续运行 | 无影响 |
| PII 脱敏异常 | 捕获异常，跳过该 span 脱敏，记录错误日志 | 无影响 |
| SDK 内部线程崩溃 | daemon 线程自动重启（最多 3 次），3 次后静默停止 | 无影响 |
| JavaAgent 加载失败 | JVM 正常启动（-javaagent 不影响 JVM 生命周期） | 无影响 |

### 6.2 热更新设计

配置热更新是客户端稳定性的核心要求（30s 内生效，无需重启 Agent）：

```
ConfigManager 轮询线程（30s 间隔）
  │
  ├─ 向平台配置 API 发送 GET /config?version={current_version}
  │
  ├─ 返回 304 Not Modified → 无变化，continue
  │
  └─ 返回新配置 JSON
       │
       ├─ pydantic 校验配置格式
       ├─ 原子性替换内存中的 config 对象（threading.Lock）
       ├─ 通知各 Processor 重新加载配置
       └─ 更新 config_version，写入健康检查端点状态
```

**采样率紧急下发**：采样率变更通过独立的高优先级 WebSocket 推送通道下发，5s 内生效（不等 30s 轮询）。

### 6.3 阻断指令接收

管理端检测到高风险事件后，通过以下路径向 SDK 下发阻断指令：

```
管理端 → Redis（写入 block:{session_id}，TTL=1h）
       → WebSocket 长连接（实时推送 BlockCommand）
SDK    → BlockCheckProcessor（在每次 LLM 调用前检查）
       → 命中阻断 → 抛出 AgentSecBlockException
       → 业务层捕获，返回配置的安全回复文案
```

### 6.4 多语言 span 属性统一规范

所有语言 SDK 输出的 span 必须遵循统一属性规范，确保管理端存储和检测的一致性：

| Attribute | 类型 | 说明 |
|-----------|------|------|
| agentsec.tenant_id | string | 租户 ID（从 Token 解析） |
| agentsec.app_id | string | Agent 应用 ID |
| agentsec.session_id | string | 会话 ID（自动生成或业务传入） |
| gen_ai.prompt | string | LLM prompt 内容（脱敏后，截断至配置长度） |
| gen_ai.completion | string | LLM response 内容（脱敏后） |
| gen_ai.model | string | 使用的模型名称 |
| gen_ai.usage.prompt_tokens | int | Prompt token 数 |
| gen_ai.usage.completion_tokens | int | Completion token 数 |
| mcp.tool_name | string | MCP 工具名称 |
| mcp.input_params | string | 工具输入参数（JSON，脱敏后） |
| security.risk.level | string | 安全风险等级（none/low/medium/high/critical） |

---

## 7. 稳定性保障策略

### 7.1 性能开销控制

| 指标 | 目标 | 保障手段 |
|------|------|----------|
| LLM 调用额外延迟 | < 5ms (P99) | 异步 BatchExporter，不阻塞业务调用路径 |
| SDK 内存占用 (Python) | < 64MB | 环形队列大小上限 10000 span；span 内容截断 |
| SDK 内存占用 (Java) | < 128MB | OTel JavaAgent 内置内存管理 |
| CPU 占用 | < 1% | 所有后台任务限频（心跳 30s/配置轮询 30s） |

### 7.2 数据可靠性保障

- **至少一次投递**：BatchExporter 带重试（最多 5 次，指数退避），确保 span 不丢失
- **本地缓冲**：环形队列兜底，Collector 不可达时最多缓冲 10000 span
- **幂等写入**：每个 span 有全局唯一 span_id，Collector 侧去重，避免重复记录

### 7.3 版本兼容性管理

- SDK 遵循语义化版本（SemVer），只要主版本号不变，向后兼容
- Python SDK 支持 Python 3.9+，Java SDK 支持 JDK 11+
- 新功能通过 feature flag 控制，默认关闭，灰度启用

### 7.4 可观测性

SDK 自身提供三层可观测性：

1. **本地日志**：结构化 JSON 日志（与业务日志隔离，通过独立 logger 输出）
2. **健康端点**：/agentsec/health（K8s 探针可用）
3. **Prometheus 指标**：/agentsec/metrics（运维监控可集成）

---

## 8. 部署与分发

| 组件 | 分发方式 | 说明 |
|------|----------|------|
| Python SDK | PyPI 公开源 / 私有 PyPI 源 | pip install agentsec-sdk |
| Java JavaAgent | Maven 中央仓库 / 私有 Nexus / CDN 直链 | 单 fat JAR，35MB |
| CLI 工具 | GitHub Releases / CDN | 静态二进制，支持 homebrew/apt/curl 安装 |
| Docker 镜像 | Docker Hub / 私有镜像仓库 | 预装 SDK 的 Agent 基础镜像（可选） |

---

## 9. 技术风险与缓解措施

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| openllmetry 版本升级不兼容 | 中 | 锁定依赖版本，定期评估升级；自研 fallback 插桩 |
| PII 脱敏正则误杀正常数据 | 中 | 脱敏规则在沙箱测试；提供 dry-run 模式预览脱敏效果 |
| WebSocket 长连接不稳定 | 中 | 断线自动重连；备用轮询模式（降级到 30s 配置拉取） |
| Java 字节码插桩与某些框架冲突 | 高 | 参照 OTel JavaAgent 兼容性矩阵；提供冲突工具列表；支持按 class 禁用插桩 |
| 客户网络无法访问 Collector | 中 | 支持 HTTP 代理；提供私有化部署的内网 Collector |

---

*文档结束*
