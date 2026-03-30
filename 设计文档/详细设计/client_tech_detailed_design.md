# AI Agent 安全监控平台 — 客户端详细设计文档

**文档编号**：AGENTSEC-TECH-CLIENT-DET-v1.0  
**版本**：v1.0  
**日期**：2026-03  
**状态**：评审中  
**关联文档**：客户端概要设计 v1.0 / 客户端 PRD v1.0 / 架构设计文档 v1.0

---

## 1. 总体说明

本文档是客户端技术概要设计的细化，对每个核心模块提供：接口定义、数据流、关键算法、错误处理、测试策略等详细设计内容，供开发工程师直接参考实现。

---

## 2. C-M1：SDK 接入与初始化详细设计

### 2.1 Python SDK 初始化流程

#### 2.1.1 启动序列（Fail-Open 保障）

```
AgentSecSDK.init() 调用栈：

1. _load_config_from_env()
   - 读取 AGENTSEC_TOKEN、AGENTSEC_COLLECTOR
   - 缺失必填项 → 打印警告日志，返回 NoopSDK（空操作 SDK）
   - 不抛出异常，不影响业务启动

2. _validate_token()
   - JWT 解码（不验证签名，仅读取 payload）
   - 提取 tenant_id、app_id
   - Token 格式非法 → 记录错误，返回 NoopSDK

3. _build_tracer_provider()
   - 构建 OTel TracerProvider
   - 添加 SpanProcessor 链：
     ① SensitiveFieldProcessor（PII 脱敏）
     ② SecurityTagProcessor（安全标签注入）
     ③ SamplingProcessor（采样决策）
     ④ BatchSpanExporter → RetryOTLPExporter
   - 注册为全局 TracerProvider

4. _start_background_services()（daemon 线程，try-except 兜底）
   - ConfigManager.start()：启动配置拉取线程
   - HeartbeatService.start()：启动心跳线程
   - LocalAPIServer.start()：启动健康检查 HTTP 服务
   - BlockWatcher.start()：启动 WebSocket 阻断指令监听

5. _register_with_platform()（异步，不阻塞）
   - 向管理端发送 agent.connected 事件
   - 失败不影响 SDK 启动
```

#### 2.1.2 SpanProcessor 链实现

```python
class SensitiveFieldProcessor(SpanProcessor):
    """PII 脱敏 Processor，在 span 导出前执行"""
    
    def on_end(self, span: ReadableSpan) -> None:
        """在 span 结束时执行脱敏（异步，不阻塞 span 创建）"""
        try:
            config = self._config_manager.get_current()
            for attr_key, attr_value in span.attributes.items():
                if isinstance(attr_value, str):
                    redacted = self._apply_rules(attr_value, config.pii_rules)
                    if redacted != attr_value:
                        # OTel span attributes 不可变，通过包装处理
                        span._attributes[attr_key] = redacted
                        self._log_redaction(attr_key, rule_name)
        except Exception as e:
            # 脱敏失败不阻塞 span 导出
            logger.error(f"PII redaction failed: {e}", exc_info=False)

class SamplingProcessor(SpanProcessor):
    """采样决策 Processor"""
    
    def on_start(self, span: Span, parent_context: Optional[Context]) -> None:
        config = self._config_manager.get_current()
        
        # 安全标签 span 强制采集（100%）
        if span.attributes.get("security.risk.level") in ("high", "critical"):
            return
        
        # Token 数超阈值强制采集
        token_count = span.attributes.get("gen_ai.usage.prompt_tokens", 0)
        if token_count > config.force_sample_token_threshold:
            return
        
        # 基础采样率决策
        if random.random() > config.sample_rate:
            span._set_sampling_result(Decision.DROP)
```

#### 2.1.3 RetryOTLPExporter 设计

```python
class RetryOTLPExporter(SpanExporter):
    """带本地缓冲和重试的 OTLP 导出器"""
    
    MAX_BUFFER_SIZE = 10000  # 环形队列上限
    MAX_RETRY = 5
    BACKOFF_BASE = 1.0       # 指数退避基数（秒）
    
    def __init__(self, endpoint: str, token: str):
        self._inner = OTLPSpanExporter(
            endpoint=endpoint,
            headers={"Authorization": f"Bearer {token}"},
            insecure=False
        )
        self._buffer = collections.deque(maxlen=self.MAX_BUFFER_SIZE)
        self._connected = True
        self._retry_thread = threading.Thread(
            target=self._retry_loop, daemon=True
        )
        self._retry_thread.start()
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            result = self._inner.export(spans)
            if result == SpanExportResult.SUCCESS:
                self._connected = True
                return result
        except Exception:
            pass
        
        # 导出失败，放入本地缓冲
        self._connected = False
        self._buffer.extend(spans)  # deque 自动滚动覆盖旧数据
        return SpanExportResult.SUCCESS  # 对上层返回成功，不阻塞业务
    
    def _retry_loop(self):
        """断线重连重传循环（daemon 线程）"""
        retry_count = 0
        while True:
            time.sleep(self.BACKOFF_BASE * (2 ** min(retry_count, 6)))
            if self._buffer and self._connected:
                batch = list(self._buffer)[:512]
                try:
                    self._inner.export(batch)
                    for _ in batch:
                        self._buffer.popleft()
                    retry_count = 0
                except Exception:
                    retry_count += 1
```

### 2.2 Java JavaAgent 详细设计

#### 2.2.1 premain 引导流程

```java
public class AgentSecBootstrap {
    public static void premain(String agentArgs, Instrumentation inst) {
        try {
            // 1. 隔离 classloader，避免与业务类冲突
            ClassLoader agentClassLoader = new AgentClassLoader(
                AgentSecBootstrap.class.getProtectionDomain().getCodeSource().getLocation()
            );
            
            // 2. 反射加载 SDK 核心（在 agent classloader 中）
            Class<?> sdkClass = agentClassLoader.loadClass(
                "com.agentsec.core.AgentSecCore"
            );
            
            // 3. 初始化 SDK（fail-open：异常不影响 JVM 启动）
            sdkClass.getMethod("init", Instrumentation.class)
                    .invoke(null, inst);
                    
        } catch (Throwable t) {
            // 任何异常都静默处理，JVM 正常启动
            System.err.println("[AgentSec] Agent initialization failed (fail-open): " + t.getMessage());
        }
    }
}
```

#### 2.2.2 OpenAI Java SDK 字节码插桩

```java
@AutoService(InstrumentationModule.class)
public class OpenAIInstrumentationModule extends InstrumentationModule {
    
    @Override
    public List<TypeInstrumentation> typeInstrumentations() {
        return Collections.singletonList(new ChatCompletionTypeInstrumentation());
    }
}

public class ChatCompletionAdvice {
    
    @Advice.OnMethodEnter(suppress = Throwable.class)
    public static void onEnter(
        @Advice.Argument(0) ChatCompletionRequest request,
        @Advice.Local("otelSpan") Span span
    ) {
        // 在 LLM 调用前创建 span，提取 prompt 信息
        Tracer tracer = GlobalOpenTelemetry.getTracer("agentsec.openai");
        span = tracer.spanBuilder("llm.chat_completion")
            .setSpanKind(SpanKind.CLIENT)
            .startSpan();
        
        // 提取并写入 prompt 属性（截断至配置长度）
        String prompt = extractPrompt(request.messages());
        span.setAttribute("gen_ai.prompt", truncate(prompt, getConfig().promptMaxLength));
        span.setAttribute("gen_ai.model", request.model());
    }
    
    @Advice.OnMethodExit(suppress = Throwable.class, onThrowable = Throwable.class)
    public static void onExit(
        @Advice.Return ChatCompletion response,
        @Advice.Local("otelSpan") Span span
    ) {
        if (response != null) {
            span.setAttribute("gen_ai.completion", 
                truncate(extractCompletion(response), getConfig().responseMaxLength));
            span.setAttribute("gen_ai.usage.prompt_tokens", 
                response.usage().promptTokens());
            span.setAttribute("gen_ai.usage.completion_tokens", 
                response.usage().completionTokens());
        }
        span.end();
    }
}
```

### 2.3 CLI 工具详细设计

#### 2.3.1 verify 命令实现

```go
// cmd/verify.go
func runVerify(cmd *cobra.Command, args []string) error {
    token, _ := cmd.Flags().GetString("token")
    collector, _ := cmd.Flags().GetString("collector")
    
    // 1. 创建测试 span
    testSpanID := uuid.New().String()
    span := buildTestSpan(testSpanID, token)
    
    // 2. 发送到 Collector
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    
    if err := sendOTLPSpan(ctx, collector, token, span); err != nil {
        return fmt.Errorf("failed to send test span: %w", err)
    }
    
    // 3. 轮询平台 API 确认收到（最多等待 10s）
    platformClient := api.NewPlatformClient(getPlatformBaseURL(token), token)
    
    for i := 0; i < 10; i++ {
        time.Sleep(time.Second)
        received, err := platformClient.CheckSpanReceived(ctx, testSpanID)
        if err == nil && received {
            fmt.Printf(greenText("✓ 接入验证通过\n"))
            fmt.Printf("  span_id: %s\n  接收时间: %s\n", testSpanID, time.Now().Format(time.RFC3339))
            return nil
        }
    }
    
    // 4. 超时则运行 diagnose
    fmt.Printf(redText("✗ 接入验证失败，运行诊断...\n"))
    return runDiagnose(cmd, args)
}
```

#### 2.3.2 diagnose 命令实现

```go
type DiagnosticResult struct {
    Name    string
    Status  string  // ok / warn / error
    Message string
    Fix     string
}

func runDiagnose(cmd *cobra.Command, args []string) error {
    checks := []func() DiagnosticResult{
        checkEnvVars,           // 环境变量完整性
        checkTokenValidity,     // Token 有效性（JWT 解码）
        checkTokenExpiry,       // Token 过期检查
        checkCollectorReachable, // Collector 网络连通（TCP Dial）
        checkTLSHandshake,      // TLS 握手（证书有效性）
        checkCollectorAuth,     // Collector 认证（发送无效 Token 确认返回 401）
    }
    
    allOk := true
    for _, check := range checks {
        result := check()
        printDiagnosticResult(result)
        if result.Status == "error" {
            allOk = false
        }
    }
    
    if !allOk {
        return fmt.Errorf("diagnostics found issues, exit code 1")
    }
    return nil
}
```

---

## 3. C-M2：数据采集与上报控制详细设计

### 3.1 ConfigManager 详细设计

#### 3.1.1 配置数据模型

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal

class PIIRule(BaseModel):
    name: str
    pattern: str                    # 正则表达式
    action: Literal["mask", "hash", "remove"]
    scope: List[str] = ["*"]       # 作用的 span attribute keys
    enabled: bool = True
    
    @validator("pattern")
    def validate_regex(cls, v):
        import re
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}")
        return v

class ToolWhitelistEntry(BaseModel):
    name_pattern: str               # 精确匹配或通配符（weather_*）
    max_calls_per_minute: Optional[int] = None
    param_constraints: Optional[dict] = None  # JSON Schema 约束
    
class AgentSecConfig(BaseModel):
    version: int = 0
    sample_rate: float = Field(default=1.0, ge=0.01, le=1.0)
    force_sample_token_threshold: int = 4000
    
    # 采集范围
    collect_llm_calls: bool = True
    collect_tool_calls: bool = True
    collect_http_calls: bool = False
    collect_db_queries: bool = False
    
    # 内容截断
    prompt_max_length: int = 4096
    response_max_length: int = 2048
    
    # PII 脱敏规则
    pii_rules: List[PIIRule] = Field(default_factory=_default_pii_rules)
    
    # 工具白名单
    tool_whitelist: List[ToolWhitelistEntry] = []
    tool_unknown_action: Literal["alert", "block", "shadow"] = "alert"
    
    # 阻断配置
    block_action_high: Literal["block", "alert", "shadow"] = "alert"
    block_action_critical: Literal["block", "alert", "shadow"] = "block"
    block_reply_template: str = "由于检测到异常行为，此请求已被安全系统拦截"
```

#### 3.1.2 ConfigManager 热更新实现

```python
class ConfigManager:
    POLL_INTERVAL = 30  # 秒
    
    def __init__(self, token: str, platform_base_url: str):
        self._token = token
        self._base_url = platform_base_url
        self._config: AgentSecConfig = AgentSecConfig()  # 默认配置
        self._lock = threading.RLock()
        self._subscribers: List[Callable] = []
        self._poll_thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="agentsec-config"
        )
    
    def get_current(self) -> AgentSecConfig:
        with self._lock:
            return self._config
    
    def subscribe(self, callback: Callable[[AgentSecConfig], None]) -> None:
        """注册配置变更回调（Processor 等组件通过此接口感知变更）"""
        self._subscribers.append(callback)
    
    def _poll_loop(self):
        while True:
            try:
                self._fetch_and_update()
            except Exception as e:
                logger.debug(f"Config poll failed: {e}")  # 不告警，静默继续
            time.sleep(self.POLL_INTERVAL)
    
    def _fetch_and_update(self):
        current_version = self._config.version
        response = httpx.get(
            f"{self._base_url}/internal/sdk-config",
            headers={"Authorization": f"Bearer {self._token}"},
            params={"version": current_version},
            timeout=5.0
        )
        
        if response.status_code == 304:
            return  # 无变化
        
        if response.status_code != 200:
            return  # 网络错误，继续使用旧配置
        
        new_config = AgentSecConfig.model_validate(response.json())
        
        with self._lock:
            self._config = new_config
        
        # 通知所有订阅者
        for callback in self._subscribers:
            try:
                callback(new_config)
            except Exception:
                pass  # 回调异常不影响配置更新
```

### 3.2 PII 脱敏详细设计

#### 3.2.1 内置规则集

```python
def _default_pii_rules() -> List[PIIRule]:
    return [
        PIIRule(
            name="chinese_mobile",
            pattern=r"1[3-9]\d{9}",
            action="mask",
            # 138****8888 格式
        ),
        PIIRule(
            name="chinese_id_card",
            pattern=r"\d{17}[\dXx]",
            action="mask",
            # 1101**********1234 格式
        ),
        PIIRule(
            name="credit_card",
            pattern=r"\b(?:\d[ -]?){13,16}\b",
            action="mask",
        ),
        PIIRule(
            name="openai_api_key",
            pattern=r"sk-[A-Za-z0-9]{32,}",
            action="remove",
        ),
        PIIRule(
            name="anthropic_api_key",
            pattern=r"sk-ant-[A-Za-z0-9\-]{32,}",
            action="remove",
        ),
        PIIRule(
            name="aws_access_key",
            pattern=r"AKIA[0-9A-Z]{16}",
            action="hash",
        ),
    ]

class PIIRedactor:
    def redact(self, text: str, rules: List[PIIRule]) -> str:
        for rule in rules:
            if not rule.enabled:
                continue
            if rule.action == "mask":
                text = self._mask(text, rule.pattern)
            elif rule.action == "hash":
                text = self._hash_replace(text, rule.pattern)
            elif rule.action == "remove":
                text = re.sub(rule.pattern, "[REDACTED]", text)
        return text
    
    def _mask(self, text: str, pattern: str) -> str:
        def mask_match(m):
            s = m.group(0)
            if len(s) <= 4:
                return "*" * len(s)
            return s[:2] + "*" * (len(s) - 4) + s[-2:]
        return re.sub(pattern, mask_match, text)
    
    def _hash_replace(self, text: str, pattern: str) -> str:
        def hash_match(m):
            return "[HASH:" + hashlib.sha256(m.group(0).encode()).hexdigest()[:8] + "]"
        return re.sub(pattern, hash_match, text)
```

### 3.3 阻断指令接收详细设计

```python
class BlockWatcher:
    """WebSocket 长连接，实时接收阻断指令"""
    
    RECONNECT_DELAY = 5  # 秒
    
    def __init__(self, platform_base_url: str, token: str):
        self._ws_url = platform_base_url.replace("https://", "wss://") + "/ws/block"
        self._token = token
        self._blocked_sessions: Dict[str, BlockEntry] = {}
        self._lock = threading.RLock()
    
    def is_blocked(self, session_id: str) -> Optional[str]:
        """在 LLM 调用前检查是否被阻断，返回阻断原因或 None"""
        with self._lock:
            entry = self._blocked_sessions.get(session_id)
            if entry and not entry.is_expired():
                return entry.reason
        return None
    
    async def _listen_loop(self):
        while True:
            try:
                async with websockets.connect(
                    self._ws_url,
                    additional_headers={"Authorization": f"Bearer {self._token}"}
                ) as ws:
                    async for message in ws:
                        cmd = BlockCommand.model_validate_json(message)
                        with self._lock:
                            self._blocked_sessions[cmd.session_id] = BlockEntry(
                                reason=cmd.reason,
                                expires_at=time.time() + cmd.ttl_seconds
                            )
            except Exception as e:
                logger.debug(f"BlockWatcher reconnecting: {e}")
                await asyncio.sleep(self.RECONNECT_DELAY)
```

---

## 4. C-M3：本地安全策略配置详细设计

### 4.1 MCP 工具调用插桩实现

#### 4.1.1 MCP Client 插桩（Python）

```python
class MCPClientInstrumentation:
    """自动插桩 MCP 客户端的 call_tool 方法"""
    
    def _instrument_mcp_client(self, mcp_client):
        original_call = mcp_client.call_tool
        
        async def instrumented_call(tool_name: str, params: dict, **kwargs):
            # 创建工具调用 span
            tracer = get_tracer("agentsec.mcp")
            with tracer.start_as_current_span(f"mcp.tool.{tool_name}") as span:
                span.set_attribute("mcp.tool_name", tool_name)
                span.set_attribute("mcp.input_params", json.dumps(params)[:2048])
                
                # 白名单检查
                config = get_config_manager().get_current()
                action = self._check_whitelist(tool_name, params, config)
                
                if action == "block":
                    span.set_attribute("security.risk.level", "high")
                    span.set_attribute("security.block_reason", "tool_not_in_whitelist")
                    raise MCPToolBlockedException(
                        f"工具 {tool_name} 未在白名单中，调用已被阻断"
                    )
                
                if action == "alert":
                    span.set_attribute("security.risk.level", "medium")
                    span.set_attribute("security.alert_reason", "tool_not_in_whitelist")
                
                # 执行实际调用
                try:
                    result = await original_call(tool_name, params, **kwargs)
                    span.set_attribute("mcp.output", str(result)[:2048])
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise
        
        mcp_client.call_tool = instrumented_call
    
    def _check_whitelist(self, tool_name: str, params: dict, config: AgentSecConfig) -> str:
        """返回 'allow'、'alert' 或 'block'"""
        if not config.tool_whitelist:
            return "allow"  # 未配置白名单，全部放行
        
        for entry in config.tool_whitelist:
            if fnmatch.fnmatch(tool_name, entry.name_pattern):
                # 检查频率限制
                if entry.max_calls_per_minute:
                    if self._rate_limiter.is_exceeded(tool_name, entry.max_calls_per_minute):
                        return config.tool_unknown_action  # 降级为未知工具处理
                return "allow"
        
        return config.tool_unknown_action  # 未匹配到白名单
```

---

## 5. C-M4：接入状态与本地查询详细设计

### 5.1 健康检查端点实现

#### 5.1.1 健康端点 HTTP 服务

```python
class LocalAPIServer:
    """内嵌轻量 HTTP 服务，端口 13133（标准 OTel Health Check 端口）"""
    
    def __init__(self, port: int = 13133):
        self._port = port
        self._app = aiohttp.web.Application()
        self._app.router.add_get("/agentsec/health", self._health_handler)
        self._app.router.add_get("/agentsec/metrics", self._metrics_handler)
        self._app.router.add_get("/agentsec/traces", self._traces_handler)
        self._app.router.add_get("/agentsec/traces/{trace_id}", self._trace_detail_handler)
        self._app.router.add_get("/agentsec/config/status", self._config_status_handler)
    
    async def _health_handler(self, request):
        """
        响应示例：
        {
            "status": "ok",
            "collector_connected": true,
            "last_span_sent_at": "2026-03-01T12:00:00Z",
            "spans_sent_1m": 42,
            "config_version": 7
        }
        """
        exporter_state = get_exporter().get_state()
        config_version = get_config_manager().get_current().version
        
        status = "ok"
        if not exporter_state.connected:
            status = "degraded"  # 断线但业务不受影响
        if not get_sdk().initialized:
            status = "error"
        
        http_status = 200 if status in ("ok", "degraded") else 503
        
        return aiohttp.web.json_response({
            "status": status,
            "collector_connected": exporter_state.connected,
            "last_span_sent_at": exporter_state.last_sent_at.isoformat() if exporter_state.last_sent_at else None,
            "spans_sent_1m": exporter_state.spans_sent_1m,
            "config_version": config_version,
        }, status=http_status)
    
    async def _metrics_handler(self, request):
        """返回 Prometheus 格式 metrics"""
        registry = CollectorRegistry()
        # ... prometheus_client metrics 注册
        output = generate_latest(registry)
        return aiohttp.web.Response(body=output, content_type="text/plain")
```

### 5.2 本地 Trace 存储设计

#### 5.2.1 内存环形队列

```python
class LocalTraceStore:
    """SDK 内存中保留最近 1000 条 Trace，滚动覆盖"""
    
    MAX_SIZE = 1000
    
    def __init__(self):
        self._traces: collections.OrderedDict[str, LocalTrace] = collections.OrderedDict()
        self._lock = threading.Lock()
    
    def add_span(self, span: ReadableSpan):
        """每个 span 结束时调用，归并到对应 trace"""
        trace_id = format_trace_id(span.context.trace_id)
        
        with self._lock:
            if trace_id not in self._traces:
                # 超出上限，删除最旧的 trace
                if len(self._traces) >= self.MAX_SIZE:
                    oldest_key = next(iter(self._traces))
                    del self._traces[oldest_key]
                self._traces[trace_id] = LocalTrace(trace_id=trace_id)
            
            self._traces[trace_id].add_span(span)
            # 移到末尾（LRU 语义，最新访问的保留最久）
            self._traces.move_to_end(trace_id)
    
    def list_traces(
        self,
        limit: int = 10,
        span_type: Optional[str] = None,
        has_security_event: bool = False
    ) -> List[LocalTrace]:
        with self._lock:
            traces = list(reversed(list(self._traces.values())))
        
        if span_type:
            traces = [t for t in traces if t.has_span_type(span_type)]
        if has_security_event:
            traces = [t for t in traces if t.has_security_event()]
        
        return traces[:limit]
```

#### 5.2.2 Trace 查询 API 认证

```python
async def _authenticate_local_api(self, request) -> bool:
    """
    本地 API 使用轻量认证（防止同机其他进程随意访问）：
    - 认证 Token 在 SDK 启动时自动生成，存入 /tmp/agentsec-{pid}.token
    - 或通过 AGENTSEC_LOCAL_TOKEN 环境变量指定
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    
    provided_token = auth_header[7:]
    expected_token = self._local_token
    
    # 使用 secrets.compare_digest 防止时序攻击
    return secrets.compare_digest(provided_token, expected_token)
```

---

## 6. 非功能性详细设计

### 6.1 性能测试基准

| 测试场景 | 目标指标 | 测试方法 |
|----------|----------|----------|
| SDK 对 LLM 调用额外延迟 | < 5ms P99 | 对比有/无 SDK 的 LLM 调用延迟分布（py-spy 火焰图） |
| SDK 内存基线 | Python < 64MB | memory_profiler 稳定状态内存快照 |
| PII 脱敏 CPU 开销 | < 1ms/span | cProfile 采集脱敏 Processor 执行时间 |
| 本地 Trace 查询响应 | < 100ms | 内存 1000 条 Trace 下的查询 P99 |
| 健康检查端点响应 | < 10ms | 本地 HTTP 请求往返延迟 |

### 6.2 兼容性矩阵

| SDK | 兼容范围 |
|-----|----------|
| Python SDK | Python 3.9 / 3.10 / 3.11 / 3.12；openai >= 0.27；anthropic >= 0.8；LangChain >= 0.1 |
| Java JavaAgent | JDK 11 / 17 / 21；Spring Boot 2.x / 3.x；OkHttp 3.x / 4.x；Quarkus 3.x |
| CLI 工具 | Linux amd64/arm64；macOS amd64/arm64；Windows amd64 |

### 6.3 版本升级策略

```
SDK 版本号：{major}.{minor}.{patch}

major 版本升级：
  - 破坏性变更（如环境变量重命名、SpanAttribute 规范变更）
  - 提前 4 周通知，发布迁移指南
  
minor 版本升级：
  - 新增功能，向后兼容
  - 管理端控制台显示"推荐升级"提示
  
patch 版本升级：
  - Bug 修复，安全补丁
  - 强烈建议立即升级

配置文件格式版本：独立版本号，通过 config_schema_version 字段标识
```

### 6.4 日志设计

SDK 内部日志与业务日志完全隔离：

```python
# SDK 使用独立命名空间的 logger
SDK_LOGGER_NAME = "agentsec.sdk"
sdk_logger = logging.getLogger(SDK_LOGGER_NAME)

# 默认只输出 WARNING 及以上（不污染业务日志）
# 用户可通过 AGENTSEC_LOG_LEVEL=DEBUG 开启详细日志

# 日志格式（JSON 结构化）
{
    "time": "2026-03-01T12:00:00Z",
    "level": "warning",
    "logger": "agentsec.sdk.exporter",
    "msg": "span export failed, buffering locally",
    "error": "connection refused",
    "buffer_size": 42,
    "span_id": "abc123"
}
```

---

## 7. 接口规范

### 7.1 SDK 与管理端接口

#### 7.1.1 配置拉取接口

```
GET /internal/sdk-config
Authorization: Bearer {agent_token}
Query: version={current_config_version}

Response 200（有新配置）：
{
    "version": 8,
    "sample_rate": 0.5,
    "pii_rules": [...],
    "tool_whitelist": [...],
    ...
}

Response 304（无变化）：无 Body

Response 401：Token 无效或过期
Response 429：请求过于频繁
```

#### 7.1.2 心跳上报接口

```
POST /internal/heartbeat
Authorization: Bearer {agent_token}
Content-Type: application/json

Body：
{
    "instance_id": "hostname-pid-uuid",
    "sdk_version": "1.2.3",
    "spans_sent_1m": 42,
    "spans_buffered": 0,
    "collector_connected": true,
    "config_version": 8,
    "uptime_seconds": 3600
}

Response 200：
{
    "status": "ok",
    "block_commands": [...]  // 积压的阻断指令（WebSocket 降级兜底）
}
```

#### 7.1.3 接入验证接口（CLI verify 使用）

```
GET /internal/verify-span?span_id={test_span_id}
Authorization: Bearer {agent_token}

Response 200（已收到）：
{
    "received": true,
    "received_at": "2026-03-01T12:00:05Z"
}

Response 200（未收到）：
{
    "received": false
}
```

### 7.2 本地 API 规范

```
健康检查：
GET http://localhost:13133/agentsec/health
（无需认证）

Prometheus 指标：
GET http://localhost:13133/agentsec/metrics
（无需认证）

Trace 列表：
GET http://localhost:13133/agentsec/traces
Authorization: Bearer {local_token}
Query: limit=10&type=llm_call&has_security_event=false

Trace 详情：
GET http://localhost:13133/agentsec/traces/{trace_id}
Authorization: Bearer {local_token}

配置状态：
GET http://localhost:13133/agentsec/config/status
Authorization: Bearer {local_token}

Response：
{
    "config_version": 8,
    "last_fetched_at": "2026-03-01T12:00:00Z",
    "next_fetch_at": "2026-03-01T12:00:30Z",
    "in_sync": true
}
```

---

## 8. 测试策略

### 8.1 单元测试

| 模块 | 测试重点 | 框架 |
|------|----------|------|
| SensitiveFieldProcessor | 各类 PII 正则命中 / 误杀 / 嵌套文本 | pytest + hypothesis（属性测试） |
| SamplingProcessor | 采样率边界 / 安全事件强制采集 / Token 阈值 | pytest |
| ConfigManager | 热更新原子性 / 网络超时 / 配置格式错误 | pytest + respx（mock HTTP） |
| RetryOTLPExporter | 断线缓冲 / 重连重传 / 队列溢出 | pytest + asyncmock |
| BlockWatcher | WebSocket 断线重连 / 阻断指令解析 / TTL 过期 | pytest + websockets mock |
| LocalTraceStore | 环形队列溢出 / 并发写入安全 | pytest + threading |

### 8.2 集成测试

- 启动真实 OTel Collector（Docker）
- SDK 发送测试 span，断言 Collector 接收到正确 span
- 验证 PII 脱敏效果（Collector 侧检查 span attributes）
- 验证采样率（统计实际上报比例）
- 验证断线缓冲与重传（模拟 Collector 临时下线）

### 8.3 性能测试

- py-spy 采集 SDK 在高频 LLM 调用（1000 QPS）下的 CPU 火焰图
- memory_profiler 测量稳定状态内存基线
- locust 模拟高并发下的健康检查端点性能

---

*文档结束*
