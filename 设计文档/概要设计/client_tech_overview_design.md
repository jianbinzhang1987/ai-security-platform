# AI Agent 安全监控平台 — 客户端技术概要设计文档

**文档编号**：AGENTSEC-TECH-CLIENT-OVR-v1.0  
**版本**：v1.0  
**日期**：2026-03  
**状态**：评审中  
**关联文档**：架构设计文档 v1.0 / 客户端 PRD v1.0

---

## 1. 文档目的与范围

本文档描述 AI Agent 安全监控平台**客户端侧**（Client Side）的技术概要设计，涵盖：

- 技术语言与运行时选型
- 核心组件与技术栈选型
- 整体模块结构与代码组织规划
- 关键技术决策与稳定性保障策略

客户端的核心定位是：**低侵入、零修改、高可靠地将客户 AI Agent 纳入安全监控体系**，任何 SDK 内部错误均不得影响 Agent 业务进程（Fail-Open 原则）。

---

## 2. 技术语言选型

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
│   │   ├── pii_redactor.py       # PII 脱敏 SpanProcessor
│   │   ├── security_tagger.py    # 安全标签注入 SpanProcessor
│   │   ├── sampling_processor.py # 采样决策 SpanProcessor
│   │   └── block_checker.py      # 阻断指令检查（WebSocket 接收阻断信号）
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── otlp_exporter.py      # OTLP gRPC/HTTP 导出器封装
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
│   ├── verify.go                 # agentsec-cli verify
│   ├── diagnose.go               # agentsec-cli diagnose
│   ├── status.go                 # agentsec-cli status
│   ├── config.go                 # agentsec-cli config show|diff
│   └── traces.go                 # agentsec-cli traces list|get
├── internal/
│   ├── auth/
│   │   └── token.go              # Token 读取与验证
│   ├── collector/
│   │   └── client.go             # OTLP gRPC 客户端（发送测试 span）
│   ├── api/
│   │   └── platform_client.go    # 平台 REST API 客户端（verify 回调）
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
