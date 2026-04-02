# 客户端 (端侧) 安全与合规功能支撑清单

在构建大模型安全监测平台时，**客户端（端侧，即 Agent 运行环境）** 是防线的第一关。为了最大限度降低对业务的影响，并保障数据不出办公内网，端侧的安全与合规实现应聚焦于**无感采集、本地脱敏、行为拦截与基础审计**。

以下是针对端侧（Client-Side）的安全和合规实现功能清单，以及可直接支撑或集成的开源方案选型：

---

## 一、 数据采集与可观测性 (Data Collection & Observability)

**合规诉求**：全面、准确地记录 AI Agent 的所有行为轨迹，满足审计溯源的要求（即“谁在什么时间、用什么提示词、调用了什么工具、得到了什么结果”），但不干预正常业务逻辑。

| 功能模块 | 详细说明 | 推荐开源实现支撑 |
| --- | --- | --- |
| **无感插桩采集 (Auto-Instrumentation)** | 自动拦截并采集 OpenAI、LangChain、LlamaIndex 等主流框架的底层调用，无需业务代码大量修改，捕获完整的 Prompt、Response 和 Token 消耗。 | **`OpenLLMetry (traceloop-sdk)`** (首选，专为 LLM 优化) <br> **`opentelemetry-javaagent`** (Java 端，通过字节码增强实现) |
| **基础网络与系统监控** | 监控 Agent 的基础网络请求（HTTP）和数据库查询，防范 Agent 发起的非预期外网连接或异常的数据库探测。 | **`opentelemetry-python-contrib`** (监控 requests, httpx, sqlalchemy 等底层库) |
| **调用链追踪 (Trace Context)** | 为单次 Agent 会话生成全局唯一的 Session ID 和 Trace ID，将分散的 LLM 思考过程和工具调用串联成完整的调用链，用于事后审计分析。 | **OpenTelemetry SDK** (原生能力，通过 W3C Trace Context 规范传递上下文) |

---

## 二、 数据防泄漏与隐私保护 (DLP & Privacy)

**合规诉求**：遵守《个人信息保护法》及企业内网数据安全规定，确保敏感数据（PII、公司代码、API 密钥等）在上传至监控管理端或外部大模型服务商之前，已在**本地**完成拦截或脱敏。

| 功能模块 | 详细说明 | 推荐开源实现支撑 |
| --- | --- | --- |
| **实时 PII 识别与脱敏** | 在端侧的 OTel Span Processor 阶段，拦截包含手机号、身份证、邮箱等 PII 信息的 Prompt 或 Response，将其替换为 `[PHONE_NUMBER]` 或哈希值。 | **`Microsoft Presidio`** (业界标杆，支持本地化部署，支持多语言和自定义 PII 实体扩展) |
| **凭证与密钥扫描** | 对应用内产生的文本扫描，识别是否包含了硬编码的 API Key、RSA 私钥或内部数据库凭证。 | **`Deepfence SecretScanner`** (轻量级扫描器，可集成于数据流转前) <br> **`Yelp/detect-secrets`** (适用于代码级扫描，也可用于文本流匹配) |
| **局部数据脱敏策略设置** | 提供配置热更新能力，允许不同部门的 Agent 实例加载不同的脱敏级别（如：研发部严格脱敏代码，HR 部严格脱敏 PII）。 | 结合 **`pydantic-settings`** 及平台的配置下发通道，控制 Presidio 的 Analyzer 启停。 |

---

## 三、 会话控制与合规审计 (Interaction Control & Auditing)

**合规诉求**：规范 Agent 的对话边界，防止其被引导输出有害内容（越狱），或执行超出预期的工具调用（权限越界）。

| 功能模块 | 详细说明 | 推荐开源实现支撑 |
| --- | --- | --- |
| **Prompt 注入与越狱拦截** | 在 Agent 请求真正发出前，通过本地的轻量级检查器（或外接专属安全网关）评估 Prompt 是否包含注入攻击、诱导生成政治敏感/违法内容。 | **`NVIDIA NeMo Guardrails`** (可集成于对话流前端，使用可编程的 Rail 拦截不良意图) <br> **`LLM Guard (Laiyer AI)`** (提供针对 Injection、Toxicity 的轻量级扫描探针) |
| **MCP 工具调用安全审计** | 监控通过 MCP (Model Context Protocol) 调用的工具参数，检查是否存在命令注入、路径穿越或敏感内部 API 调用。 | 结合 **`MCP SDK`** 和自定义的正则表达式/白名单机制，或集成轻量级 WAF 规则库。 |
| **合规日志留存与防篡改** | 将端侧产生的关键安全事件（如拦截动作、脱敏记录）本地化落盘或以可靠的方式向远端推送，确保证据的不可篡改和可追溯性。 | **`File Exporter` (OpenTelemetry)** (以 JSON 格式本地滚动存储日志) <br> **`Fluentd/Filebeat`** (收集本地文件日志并加密向中央存储库转发) |

---

## 四、 资源管控与异常防范 (Resource Quota & Anomaly Prevention)

**合规诉求**：防止 Agent 被投毒导致无限循环，或被恶意利用导致企业算力/API 成本激增。

| 功能模块 | 详细说明 | 推荐开源实现支撑 |
| --- | --- | --- |
| **流量与 Token 配额熔断** | 根据部门或 Agent ID 限制单位时间内的请求频率（Rate Limit）或 Token 花费（Budget Limit）。当超出配额时，端侧予以阻断。 | 可基于开源 API 网关如 **`LiteLLM Proxy`** (内置 Budget & Spend Tracking)，或者在端侧自研基于 Redis 的分布式令牌桶限流组件。 |
| **响应体积与耗时异常检测** | 监控单次请求的响应延迟（如果是同步请求）和回复的体积。防范比如要求模型吐出大量训练资料的“提取攻击（Extraction Attack）”。 | 利用 **OpenTelemetry Metrics** 记录 `http.server.duration` 和响应包大小，结合平台侧告警策略实现阻断。 |

---

## 总结：端侧实现架构参考

一个典型的端侧安全架构数据流建议如下设计：

1. **业务层**：正常的 Agent 代码（LangChain/OpenAI）。
2. **拦截层 (Instrumentors)**：由 `OpenLLMetry` 自动拦截调用，生成原始上下文（Trace & Span）。
3. **安全处理管线 (Processors - 本地执行)**:
   - **检查站 1 (注入防护)**：[可选] 调用 `LLM Guard` 或轻量模型对 Prompt 进行快速评分，高危则直接截断。
   - **检查站 2 (DLP 脱敏)**：调用 `Presidio` 清洗 Prompt/Response 中的隐私数据和 Secret。
   - **检查站 3 (元数据增强)**：添加当前的部门标识、Agent 版本等合规关联信息。
4. **输出层 (Exporters)**：安全合规的加密数据通过 OTLP 协议发往管理端（Collector）。

这份清单为您梳理了客户端安全能力的重点，并且保证了关键组件都有成熟的开源实现可立即引入验证。您看这份清单是否涵盖了您对于“端侧”及“内网环境”的预期？
