# AI Agent 安全监控平台 — 管理端详细设计文档

**文档编号**：AGENTSEC-TECH-ADMIN-DET-v1.0
**版本**：v1.0
**日期**：2026-03
**状态**：评审中
**关联文档**：管理端概要设计 v1.0 / 管理端 PRD v1.0 / 架构设计文档 v1.0

---

## 1. 总体说明

本文档是管理端技术概要设计的细化，对每个核心服务/模块提供：数据模型、接口定义、关键算法、部署配置、错误处理等详细设计内容，供开发工程师直接参考实现。

---

## 2. 数据库详细设计

### 2.1 PostgreSQL 表结构（元数据库）

#### 2.1.1 多租户核心表

```sql
-- 租户表
CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    company     VARCHAR(200),
    email       VARCHAR(200) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'trial', 'frozen', 'deleted')),
    plan        VARCHAR(20) NOT NULL DEFAULT 'basic',
    max_agents          INTEGER NOT NULL DEFAULT 10,
    max_spans_per_day   BIGINT NOT NULL DEFAULT 1000000,
    max_storage_gb      INTEGER NOT NULL DEFAULT 50,
    data_retention_days INTEGER NOT NULL DEFAULT 90,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent 应用表
CREATE TABLE agent_apps (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    team        VARCHAR(100),
    language    VARCHAR(20),
    status      VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- App Token 表
CREATE TABLE app_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    app_id      UUID NOT NULL REFERENCES agent_apps(id),
    name        VARCHAR(100) NOT NULL,
    token_hash  VARCHAR(64) NOT NULL UNIQUE,
    status      VARCHAR(20) NOT NULL DEFAULT 'active',
    expires_at  TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent 实例表
CREATE TABLE agent_instances (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    app_id          UUID NOT NULL REFERENCES agent_apps(id),
    token_id        UUID NOT NULL REFERENCES app_tokens(id),
    instance_id     VARCHAR(200) NOT NULL UNIQUE,
    hostname        VARCHAR(200),
    ip_address      INET,
    sdk_version     VARCHAR(50),
    sdk_language    VARCHAR(20),
    last_heartbeat  TIMESTAMPTZ,
    config_version  INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'online',
    registered_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 风险事件表（检测引擎输出）
CREATE TABLE risk_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    app_id          UUID NOT NULL REFERENCES agent_apps(id),
    session_id      VARCHAR(200),
    trace_id        VARCHAR(32) NOT NULL,
    span_id         VARCHAR(32) NOT NULL,
    span_kind       VARCHAR(30) NOT NULL,
    risk_type       VARCHAR(50) NOT NULL,
    risk_level      VARCHAR(20) NOT NULL,
    confidence      FLOAT NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    block_action    VARCHAR(50),
    block_reason    TEXT,
    evidence        JSONB,
    explanation     TEXT,
    anomaly_score   INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'new',
    assigned_to     UUID,
    resolution      TEXT,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    closed_at       TIMESTAMPTZ
);

CREATE INDEX idx_risk_events_tenant_time ON risk_events(tenant_id, detected_at DESC);
CREATE INDEX idx_risk_events_app_status ON risk_events(app_id, status);
CREATE INDEX idx_risk_events_session ON risk_events(session_id);
CREATE INDEX idx_risk_events_trace ON risk_events(trace_id);
CREATE INDEX idx_risk_events_span ON risk_events(span_id);
CREATE INDEX idx_risk_events_span_kind ON risk_events(span_kind);

-- 告警规则表
CREATE TABLE alert_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    conditions      JSONB NOT NULL,
    actions         JSONB NOT NULL,
    scope_app_ids   UUID[],
    window_seconds  INTEGER,
    window_count_threshold INTEGER,
    enabled         BOOLEAN NOT NULL DEFAULT true,
    version         INTEGER NOT NULL DEFAULT 1,
    sigma_rule_id   VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 审计日志表（Append-Only，不可修改）
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID,
    actor_id    UUID,
    actor_type  VARCHAR(20) NOT NULL,  -- user / api_key / system
    actor_name  VARCHAR(200),
    action      VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    request_ip  INET,
    request_params JSONB,
    response_code SMALLINT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- 注意：审计日志表不授予 DELETE 权限
```

### 2.2 ClickHouse 表设计（事件存储）

```sql
CREATE TABLE agent_spans (
    span_id         String,
    trace_id        String,
    parent_span_id  String,
    session_id      String,
    tenant_id       String,
    app_id          String,
    instance_id     String,
    span_name       String,
    span_kind       Enum8('llm'=1, 'tool'=2, 'network'=3, 'db'=4, 'internal'=5, 'retriever'=6, 'guardrail'=7),
    agentsec_span_type String,
    framework       String,
    node_display_name String,
    node_class_name String,
    node_method_name String,
    timestamp       DateTime64(3),
    duration_ms     Float64,
    model           String,
    prompt_hash     String,
    prompt_truncated String,
    response_truncated String,
    token_prompt    UInt32,
    token_completion UInt32,
    token_total     UInt32,
    tool_name       String,
    tool_input_params String,
    tool_output     String,
    risk_level      Enum8('none'=0, 'low'=1, 'medium'=2, 'high'=3, 'critical'=4),
    status          Enum8('ok'=1, 'blocked'=2, 'error'=3),
    block_action    String,
    block_reason    String,
    error_type      String,
    risk_type       String,
    security_tags   Array(String),
    anomaly_score   UInt8,
    source_ip       String,
    sdk_version     String
)
ENGINE = ReplacingMergeTree(timestamp)
PARTITION BY (tenant_id, toYYYYMM(timestamp))
ORDER BY (tenant_id, app_id, session_id, timestamp)
TTL timestamp + INTERVAL 90 DAY;

-- 物化视图：LLM 调用量时序聚合（1 分钟粒度）
CREATE MATERIALIZED VIEW agent_spans_1m_agg
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(window_start)
ORDER BY (tenant_id, app_id, window_start)
AS SELECT
    tenant_id,
    app_id,
    toStartOfMinute(timestamp) AS window_start,
    countIf(span_kind = 1) AS llm_calls,
    sum(token_total) AS total_tokens,
    avg(duration_ms) AS avg_latency_ms,
    countIf(risk_level >= 2) AS security_events
FROM agent_spans
GROUP BY tenant_id, app_id, window_start;
```

---

## 3. OTel Collector 详细配置设计

### 3.1 Processor 处理链配置

```yaml
processors:
  # 1. 属性注入（平台来源标签）
  attributes/inject_platform:
    actions:
      - key: platform
        value: agentsec
        action: insert

  # 2. 过滤噪音 span（健康检查/内部探针）
  filter/exclude_health_check:
    traces:
      span:
        - 'attributes["http.route"] == "/health"'
        - 'attributes["http.route"] == "/readyz"'

  # 3. PII 二次脱敏（Collector 层兜底，防 SDK 侧漏网）
  redaction/pii_secondary:
    allow_all_keys: true
    blocked_values:
      - "1[3-9]\\d{9}"           # 手机号
      - "sk-[A-Za-z0-9]{32,}"    # OpenAI Key

  # 4. 动态安全标签（OTTL 条件表达式）
  transform/security_tags:
    trace_statements:
      - context: span
        statements:
          - set(attributes["security.risk.hint"], "prompt_too_long") where IsString(attributes["gen_ai.prompt"]) and Len(attributes["gen_ai.prompt"]) > 8000
          - set(attributes["security.risk.hint"], "api_key_detected") where IsMatch(attributes["gen_ai.prompt"], "sk-[A-Za-z0-9]{32,}")

  # 5. 尾部采样（安全事件 100% 保留，普通 span 10% 采样）
  tail_sampling:
    decision_wait: 10s
    num_traces: 50000
    policies:
      - name: security-events-always-sample
        type: string_attribute
        string_attribute:
          key: security.risk.level
          values: ["high", "critical"]
      - name: normal-percentage
        type: probabilistic
        probabilistic:
          sampling_percentage: 10

  # 6. 批量聚合
  batch:
    timeout: 5s
    send_batch_size: 1000
    send_batch_max_size: 2000
```

### 3.2 自定义 Token 认证扩展设计（Go）

认证扩展在 Collector Receiver 层拦截请求，验证客户端 SDK 携带的 Session Token：

```
请求进入 Receiver
  │
  ├─ 提取 Authorization: Bearer {token}
  ├─ SHA256(token) 在本地缓存查找（TTL=60s）
  │     命中 → 取 AuthInfo（tenant_id, app_id），注入请求 context
  │     未命中 → 向管理端 /internal/validate-token 发 HTTP 请求
  │               成功 → 写缓存，注入 context
  │               失败 → 返回 OTLP Status UNAUTHENTICATED(16)
  │
  └─ 请求通过，进入 Processor 链
```

缓存设计：
- 使用 sync.Map 存储 token_hash -> AuthInfo（含过期时间）
- Token 吊销时，管理端通过 Redis Pub/Sub 广播失效事件，Collector 接收后从缓存删除
- 缓存 TTL=60s，即 Token 吊销后最多 60s 内 Collector 仍接受旧 Token（可接受）

---

## 4. 安全检测引擎详细设计

### 4.1 Prompt 安全检测子引擎

#### 4.1.1 检测管道设计

```
Kafka Consumer: agentsec-prompt-detector
  │
  ├─ 并行执行（asyncio.gather）：
  │   ├─ [轻量] JailbreakPatternDetector：正则匹配越狱模式库（500+ 模式）
  │   ├─ [轻量] PIILeakDetector（LLM Guard）：扫描 response 中 PII
  │   ├─ [中量] NeMoDetector：直接 Prompt 注入检测
  │   └─ [重量] LlamaFirewallDetector：间接注入（PromptGuard 模型推理）
  │
  └─ 汇总结果 → 选取最高置信度风险 → 写入 risk_events
```

```python
class PromptDetectionPipeline:
    async def detect(self, span: SpanData) -> Optional[RiskEvent]:
        """并行执行所有检测器，返回最高风险结果"""
        tasks = []
        
        # 根据 span 类型决定执行哪些检测器
        if span.has_prompt:
            tasks.extend([
                self._jailbreak_detector.detect(span),
                self._nemo_detector.detect(span),
                self._llamafirewall_detector.detect(span),
            ])
        
        if span.has_response:
            tasks.append(self._pii_leak_detector.detect(span))
        
        # 设置超时（单个检测器超时不影响其他）
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if isinstance(r, DetectionResult) and r.risk_level > 0]
        
        if not valid_results:
            return None
        
        # 取置信度最高的结果
        best = max(valid_results, key=lambda r: r.confidence)
        
        return RiskEvent(
            session_id=span.session_id,
            trace_id=span.trace_id,
            span_id=span.span_id,
            span_kind=span.span_kind,
            risk_type=best.risk_type,
            risk_level=best.risk_level_name,
            confidence=best.confidence,
            block_action=span.block_action,
            block_reason=span.block_reason,
            evidence=best.evidence
        )
```

#### 4.1.2 NeMo Guardrails 集成

```python
class NeMoDetector:
    def __init__(self, config_dir: str):
        from nemoguardrails import RailsConfig, LLMRails
        config = RailsConfig.from_path(config_dir)
        self._rails = LLMRails(config)
    
    async def detect(self, span: SpanData) -> DetectionResult:
        try:
            # 仅对 user 角色消息执行注入检测
            user_messages = [m for m in span.messages if m["role"] == "user"]
            if not user_messages:
                return DetectionResult(risk_level=0)
            
            # NeMo Guardrails 检测
            result = await self._rails.generate_async(
                messages=[{"role": "user", "content": user_messages[-1]["content"]}]
            )
            
            # 解析 guardrails 检测结果
            if result.get("security", {}).get("injection_detected"):
                confidence = result["security"]["confidence"]
                return DetectionResult(
                    risk_type="prompt_injection_direct",
                    risk_level=RiskLevel.HIGH if confidence > 0.8 else RiskLevel.MEDIUM,
                    confidence=confidence,
                    evidence={"matched_pattern": result["security"].get("pattern")}
                )
        except Exception as e:
            logger.error(f"NeMo detection failed: {e}")
        
        return DetectionResult(risk_level=0)
```

#### 4.1.3 LlamaFirewall（间接注入 + 意图对齐）集成

```python
class LlamaFirewallDetector:
    """
    使用 Meta LlamaFirewall 进行：
    1. 间接 Prompt 注入检测（PromptGuard 模型）
    2. 意图对齐审计（AlignmentCheck 少样本 CoT 推理）
    """
    
    async def detect_indirect_injection(self, span: SpanData) -> DetectionResult:
        from llamafirewall import PromptGuard
        
        # 检测 tool/system 消息中的隐藏注入指令
        tool_messages = [m for m in span.messages if m["role"] in ("tool", "system")]
        
        for msg in tool_messages:
            score = await PromptGuard.scan(msg["content"])
            if score > 0.7:
                return DetectionResult(
                    risk_type="prompt_injection_indirect",
                    risk_level=RiskLevel.HIGH,
                    confidence=score,
                    evidence={"source_role": msg["role"], "score": score}
                )
        
        return DetectionResult(risk_level=0)
    
    async def check_intent_alignment(
        self,
        initial_prompt: str,
        tool_call: ToolCallData
    ) -> AlignmentResult:
        from llamafirewall import AlignmentCheck
        
        result = await AlignmentCheck.evaluate(
            user_intent=initial_prompt,
            action_description=f"调用工具 {tool_call.tool_name}，参数：{tool_call.params}",
        )
        
        return AlignmentResult(
            alignment_score=result.score,
            explanation=result.explanation,
            is_misaligned=result.score < 0.3
        )
```

### 4.2 MCP 工具调用审计子引擎

#### 4.2.1 白名单校验与参数扫描

```python
class MCPAuditor:
    
    # 危险参数模式（参数注入检测）
    DANGEROUS_PATTERNS = [
        (r"(?i)(union\s+select|or\s+1=1|drop\s+table)", "sql_injection"),
        (r"\.\./|\.\.\\", "path_traversal"),
        (r"file://|gopher://", "ssrf"),
        (r";\s*(rm|chmod|curl|wget|bash|sh|python)\s", "shell_injection"),
    ]
    
    async def audit(self, span: SpanData, app_config: AgentConfig) -> Optional[RiskEvent]:
        tool_name = span.tool_name
        params = span.tool_input_params
        
        # 1. 黑名单检查（最高优先级）
        if tool_name in app_config.tool_blacklist:
            return RiskEvent(
                risk_type="mcp_blacklist_tool",
                risk_level="critical",
                confidence=1.0,
                evidence={"tool_name": tool_name, "reason": "tool_in_blacklist"}
            )
        
        # 2. 白名单检查
        if app_config.tool_whitelist and not self._in_whitelist(tool_name, app_config.tool_whitelist):
            action = app_config.tool_unknown_action  # alert/block/shadow
            if action in ("alert", "shadow"):
                return RiskEvent(
                    risk_type="mcp_unlisted_tool",
                    risk_level="medium",
                    confidence=0.9,
                    evidence={"tool_name": tool_name}
                )
        
        # 3. 参数危险模式扫描
        for pattern, attack_type in self.DANGEROUS_PATTERNS:
            if re.search(pattern, str(params)):
                return RiskEvent(
                    risk_type=f"mcp_param_{attack_type}",
                    risk_level="high",
                    confidence=0.95,
                    evidence={"tool_name": tool_name, "attack_type": attack_type}
                )
        
        # 4. 调用频率异常检测
        freq_result = await self._check_frequency(span.session_id, tool_name)
        if freq_result.is_anomalous:
            return RiskEvent(
                risk_type="mcp_frequency_anomaly",
                risk_level="medium",
                confidence=freq_result.confidence,
                evidence={"current_rate": freq_result.current_rate, "baseline": freq_result.baseline}
            )
        
        return None
```

#### 4.2.2 调用频率异常检测（Markov 链）

```python
class ToolCallFrequencyMonitor:
    """
    使用滑动窗口统计工具调用频率，
    与历史基线对比，超过 3 个标准差时告警
    """
    
    def __init__(self, redis_client: Redis):
        self._redis = redis_client
    
    async def check_frequency(
        self,
        session_id: str,
        tool_name: str,
        app_id: str
    ) -> FrequencyResult:
        window = 60  # 1 分钟滑动窗口
        now = time.time()
        
        # 记录当前调用（Redis ZADD）
        key = f"tool_freq:{session_id}:{tool_name}"
        await self._redis.zadd(key, {str(now): now})
        await self._redis.zremrangebyscore(key, 0, now - window)
        await self._redis.expire(key, 300)
        
        # 当前频率
        current_count = await self._redis.zcard(key)
        current_rate = current_count / window  # 次/秒
        
        # 获取历史基线（来自 app 级统计）
        baseline_key = f"tool_baseline:{app_id}:{tool_name}"
        baseline_data = await self._redis.hgetall(baseline_key)
        
        if not baseline_data:
            return FrequencyResult(is_anomalous=False)
        
        mean = float(baseline_data.get("mean", 0))
        std = float(baseline_data.get("std", 0))
        
        # 超过 3 个标准差视为异常
        if std > 0 and current_rate > mean + 3 * std:
            return FrequencyResult(
                is_anomalous=True,
                confidence=min(0.99, (current_rate - mean) / (3 * std + 1e-10) * 0.3),
                current_rate=current_rate,
                baseline={"mean": mean, "std": std}
            )
        
        return FrequencyResult(is_anomalous=False)
```

### 4.3 行为序列分析子引擎

#### 4.3.1 Trace / Session 调用链重建

```python
class BehaviorSequenceAnalyzer:
    
    async def analyze_session(self, session_id: str, tenant_id: str) -> SessionAnalysisResult:
        """session 结束（5 分钟无新 span）或 span 数 > 50 时触发"""
        
        # 从 ClickHouse 读取该 session 所有 span
        spans = await self._clickhouse.query(
            "SELECT * FROM agent_spans WHERE session_id = {session_id} AND tenant_id = {tenant_id} ORDER BY timestamp",
            {"session_id": session_id, "tenant_id": tenant_id}
        )
        
        if not spans:
            return SessionAnalysisResult(anomaly_score=0)
        
        # 重建调用序列
        sequence = [span.span_kind for span in spans]  # ['llm', 'tool', 'llm', 'tool', ...]
        
        # 1. 威胁模式库匹配
        threat_match = self._match_threat_patterns(sequence, spans)
        
        # 2. 统计异常检测（对比历史 P99）
        stats_anomaly = await self._detect_statistical_anomaly(spans, tenant_id)
        
        # 3. 综合异常分计算（加权）
        score = self._calculate_anomaly_score(threat_match, stats_anomaly)
        
        return SessionAnalysisResult(
            anomaly_score=score,
            threat_patterns=threat_match.patterns if threat_match else [],
            anomaly_reasons=stats_anomaly.reasons
        )
    
    # 已知威胁模式库
    THREAT_PATTERNS = [
        {
            "name": "injection_to_exfil",
            "description": "Prompt 注入后立即发起外部请求",
            "pattern": lambda spans: (
                any(s.risk_type == "prompt_injection" for s in spans) and
                any(s.span_kind == "network" for s in spans if s.timestamp > injection_time(spans))
            )
        },
        {
            "name": "mass_file_read",
            "description": "短时间内大量文件读取操作",
            "pattern": lambda spans: len([s for s in spans if "read_file" in s.tool_name]) > 20
        },
        {
            "name": "privilege_escalation_chain",
            "description": "工具调用序列呈现权限提升特征",
            "pattern": lambda spans: detect_privilege_chain(spans)
        }
    ]
    
    def _calculate_anomaly_score(self, threat_match, stats_anomaly) -> int:
        """加权计算综合异常分（0-100）"""
        score = 0
        
        # 威胁模式命中（权重 50）
        if threat_match and threat_match.matched:
            score += 50 * threat_match.confidence
        
        # 统计异常（权重 30）
        score += 30 * stats_anomaly.normalized_score
        
        # Prompt 注入信号（权重 20）
        injection_spans = [s for s in threat_match.spans if s.risk_type == "prompt_injection"]
        if injection_spans:
            score += 20 * max(s.confidence for s in injection_spans)
        
        return min(100, int(score))
```

---

## 5. 告警规则引擎详细设计

### 5.1 规则匹配引擎（Go 实现）

```go
// services/alert-engine/internal/engine/rule_engine.go

type RuleEngine struct {
    rules  []*AlertRule
    mu     sync.RWMutex
    redis  *redis.Client  // 用于滑动窗口计数
    pg     *pgxpool.Pool  // 用于读取规则
}

// AlertRule 触发条件（JSON 表达式树）
type Condition struct {
    Op       string       // AND/OR/NOT/eq/gte/lte/in/contains
    Field    string       // risk_type/confidence/app_id/tool_name 等
    Value    interface{}
    Children []*Condition // 用于 AND/OR/NOT
}

func (e *RuleEngine) ProcessRiskEvent(ctx context.Context, event *RiskEvent) error {
    e.mu.RLock()
    rules := e.rules
    e.mu.RUnlock()
    
    for _, rule := range rules {
        if !rule.Enabled {
            continue
        }
        
        // 检查规则范围（app_id 过滤）
        if !rule.MatchesApp(event.AppID) {
            continue
        }
        
        // 条件匹配
        if !e.evalCondition(rule.Conditions, event) {
            continue
        }
        
        // 滑动窗口计数（如果规则有 window 配置）
        if rule.WindowSeconds > 0 {
            count, err := e.incrementWindowCount(ctx, rule.ID, event.AppID, rule.WindowSeconds)
            if err != nil || count < rule.WindowCountThreshold {
                continue
            }
        }
        
        // 触发告警动作
        if err := e.executeActions(ctx, rule, event); err != nil {
            logger.Error("execute actions failed", "rule_id", rule.ID, "error", err)
        }
    }
    
    return nil
}

func (e *RuleEngine) evalCondition(cond *Condition, event *RiskEvent) bool {
    switch cond.Op {
    case "AND":
        for _, child := range cond.Children {
            if !e.evalCondition(child, event) {
                return false
            }
        }
        return true
    
    case "OR":
        for _, child := range cond.Children {
            if e.evalCondition(child, event) {
                return true
            }
        }
        return false
    
    case "eq":
        return getEventField(event, cond.Field) == cond.Value
    
    case "gte":
        return toFloat(getEventField(event, cond.Field)) >= toFloat(cond.Value)
    
    default:
        return false
    }
}
```

### 5.2 阻断指令下发详细设计

```go
// services/block-service/internal/block/service.go

type BlockService struct {
    redis        *redis.Client
    wsHub        *WebSocketHub  // WebSocket 连接管理
    blockLogRepo *BlockLogRepository
}

func (s *BlockService) Block(ctx context.Context, req *BlockRequest) error {
    // 1. 写入 Redis（主要路径，SDK 轮询检查）
    key := fmt.Sprintf("block:%s:%s", req.TenantID, req.SessionID)
    value, _ := json.Marshal(BlockEntry{
        Reason:    req.Reason,
        RuleID:    req.RuleID,
        BlockedAt: time.Now(),
    })
    
    if err := s.redis.SetEx(ctx, key, value, time.Hour).Err(); err != nil {
        return fmt.Errorf("failed to write block to redis: %w", err)
    }
    
    // 2. 通过 WebSocket 实时推送（辅助路径，降低延迟）
    cmd := &BlockCommand{
        Type:       "block",
        SessionID:  req.SessionID,
        TenantID:   req.TenantID,
        Reason:     req.Reason,
        TTLSeconds: 3600,
    }
    s.wsHub.BroadcastToApp(req.AppID, cmd)
    
    // 3. 记录阻断日志
    s.blockLogRepo.Insert(ctx, &BlockLog{
        TenantID:  req.TenantID,
        AppID:     req.AppID,
        SessionID: req.SessionID,
        Reason:    req.Reason,
        RuleID:    req.RuleID,
        BlockedAt: time.Now(),
    })
    
    return nil
}

// WebSocket Hub：管理所有 SDK 长连接
type WebSocketHub struct {
    // appID -> []*WebSocketConn（同一 app 的所有 SDK 实例）
    connections sync.Map
}

func (h *WebSocketHub) BroadcastToApp(appID string, cmd interface{}) {
    if conns, ok := h.connections.Load(appID); ok {
        payload, _ := json.Marshal(cmd)
        for _, conn := range conns.([]*WebSocketConn) {
            conn.SendMessage(payload) // 非阻塞发送
        }
    }
}
```

---

## 6. 查询 API 服务详细设计

### 6.1 API 接口规范

#### 6.1.1 Trace / Session 调用观测查询

```
GET /api/v1/traces/{trace_id}/spans
Authorization: Bearer {jwt_token}
Headers: X-Tenant-ID: {tenant_id}  （由 auth 中间件自动注入）

Response 200:
{
  "trace_id": "trace-abc123",
  "session_id": "sess-abc123",
  "app_id": "uuid-...",
  "total_spans": 15,
  "duration_ms": 3421,
  "anomaly_score": 72,
  "risk_events": [...],
  "spans": [
    {
      "span_id": "...",
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
    },
    ...
  ]
}
```

#### 6.1.2 时序聚合查询

```
GET /api/v1/metrics/timeseries
Authorization: Bearer {jwt_token}

Query Parameters:
  app_id: UUID (可选，不传则查询全部)
  metric: llm_calls | total_tokens | avg_latency | security_events
  from: ISO8601 (必填)
  to: ISO8601 (必填)
  granularity: 1m | 5m | 1h | 1d

Response 200:
{
  "metric": "llm_calls",
  "granularity": "5m",
  "data_points": [
    {"timestamp": "2026-03-01T12:00:00Z", "value": 42},
    {"timestamp": "2026-03-01T12:05:00Z", "value": 38},
    ...
  ]
}
```

对应 ClickHouse 查询（使用物化视图）：

```sql
SELECT
    toStartOfInterval(window_start, INTERVAL 5 MINUTE) AS ts,
    sum(llm_calls) AS value
FROM agent_spans_1m_agg
WHERE
    tenant_id = {tenant_id}
    AND app_id = {app_id}
    AND window_start BETWEEN {from} AND {to}
GROUP BY ts
ORDER BY ts
```

#### 6.1.3 风险事件查询

```
GET /api/v1/risk-events
Authorization: Bearer {jwt_token}

Query Parameters:
  risk_level: low | medium | high | critical (可多选，逗号分隔)
  trace_id: String (可选)
  span_id: String (可选)
  span_kind: llm | tool | retriever | network | db | guardrail | internal (可选)
  status: ok | blocked | error (可选)
  risk_type: prompt_injection | mcp_violation | ... (可多选)
  app_id: UUID (可选)
  status: new | in_progress | confirmed | false_positive | closed
  from: ISO8601
  to: ISO8601
  page: 1 (默认)
  page_size: 20 (默认，最大 100)

Response 200:
{
  "total": 156,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": "uuid",
      "trace_id": "trace-abc123",
  "session_id": "sess-abc123",
      "risk_type": "prompt_injection",
      "risk_level": "high",
      "confidence": 0.92,
      "evidence": {"matched_pattern": "忽略之前的指令"},
      "status": "new",
      "detected_at": "2026-03-01T12:00:00Z"
    },
    ...
  ]
}
```

### 6.2 Go 服务实现（以 query-service 为例）

```go
// 租户隔离中间件（所有查询强制过滤）
func TenantIsolationMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 从 JWT claims 中提取 tenant_id（由 auth 中间件注入）
        claims, ok := r.Context().Value(authClaimsKey).(*JWTClaims)
        if !ok {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        
        // 将 tenant_id 注入 context，后续所有 DB 查询必须使用
        ctx := context.WithValue(r.Context(), tenantIDKey, claims.TenantID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// ClickHouse 查询（强制 tenant_id 过滤）
func (r *SpanRepository) GetSessionSpans(
    ctx context.Context,
    sessionID string,
) ([]*Span, error) {
    tenantID := ctx.Value(tenantIDKey).(string)  // 必须存在，否则 panic（由中间件保障）
    
    rows, err := r.db.QueryContext(ctx, `
        SELECT * FROM agent_spans
        WHERE tenant_id = ? AND session_id = ?   -- tenant_id 过滤强制存在
        ORDER BY timestamp
        LIMIT 1000
    `, tenantID, sessionID)
    
    // ...
}
```

---

## 7. 安全运营控制台前端详细设计

### 7.1 Trace 瀑布图组件设计

#### 7.1.1 组件数据流

```
SOC 工程师点击告警 "查看证据"
  │
  ├─ 调用 useTraceSpans(trace_id) Hook
  │     → GET /api/v1/traces/{trace_id}/spans
  │     → SWR 缓存（不超过 5min 保鲜期）
  │
  ├─ 调用 useRiskEvents(span_id / trace_id) Hook
  │     → GET /api/v1/risk-events?span_id={id} 或 trace_id={id}
  │
  └─ 将 spans + risk_events 传入 ObserveWaterfall 组件
```

#### 7.1.2 ObserveWaterfall 组件核心逻辑

```typescript
interface TraceSpan {
  span_id: string;
  parent_span_id: string | null;
  span_name: string;
  span_kind: 'llm' | 'tool' | 'retriever' | 'network' | 'db' | 'guardrail' | 'internal';
  timestamp: string;
  duration_ms: number;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  risk_type?: string;
}

function TraceWaterfall({ spans, riskEvents, sessionDuration }: Props) {
  // 1. 构建树状结构（parent-child 关系）
  const tree = useMemo(() => buildSpanTree(spans), [spans]);
  
  // 2. 计算时间轴比例
  const timeScale = useCallback((timestamp: string) => {
    const offset = new Date(timestamp).getTime() - sessionStart;
    return (offset / sessionDuration) * 100; // 百分比
  }, [sessionStart, sessionDuration]);
  
  // 3. 渲染
  return (
    <div className="trace-container">
      <TimeAxis duration={sessionDuration} />
      {tree.map(node => (
        <SpanRow
          key={node.span_id}
          span={node}
          depth={node.depth}
          left={timeScale(node.timestamp)}
          width={(node.duration_ms / sessionDuration) * 100}
          riskEvent={riskEvents.find(e => e.span_id === node.span_id)}
          onClick={() => setSelectedSpan(node)}
        />
      ))}
      {selectedSpan && (
        <SpanDetailPanel span={selectedSpan} riskEvent={selectedRiskEvent} />
      )}
    </div>
  );
}

// SpanRow：单行 span 展示
function SpanRow({ span, depth, left, width, riskEvent, onClick }: SpanRowProps) {
  const colorMap = {
    llm: 'bg-blue-500',
    tool: 'bg-green-500',
    network: 'bg-orange-500',
    db: 'bg-purple-500',
  };
  
  return (
    <div className={`span-row pl-${depth * 4}`} onClick={onClick}>
      <span className="span-name truncate w-48">{span.span_name}</span>
      <div className="span-bar-container flex-1 relative h-6">
        <div
          className={`span-bar absolute h-4 rounded ${colorMap[span.span_kind]}`}
          style={{ left: `${left}%`, width: `${Math.max(width, 0.5)}%` }}
        />
        {riskEvent && (
          <RiskBadge
            level={riskEvent.risk_level}
            style={{ left: `${left}%` }}
          />
        )}
      </div>
      <span className="span-duration text-sm text-gray-500">{span.duration_ms}ms</span>
    </div>
  );
}
```

### 7.2 实时监控大盘设计

#### 7.2.1 数据刷新策略

```typescript
// 大盘页面数据刷新（30s 间隔，使用 SWR）

// 指标卡：实时刷新（30s）
const { data: stats } = useSWR('/api/v1/stats/summary', fetcher, {
  refreshInterval: 30000,
  revalidateOnFocus: true,
});

// 安全事件趋势图：5 分钟粒度，1 分钟刷新
const { data: trend } = useSWR(
  '/api/v1/metrics/timeseries?metric=security_events&granularity=5m&from=-7d',
  fetcher,
  { refreshInterval: 60000 }
);

// 最近告警列表：30s 刷新
const { data: recentAlerts } = useSWR(
  '/api/v1/risk-events?page_size=20&status=new',
  fetcher,
  { refreshInterval: 30000 }
);

// 关键优化：刷新时使用 SWR 的 stale-while-revalidate 策略
// 展示旧数据的同时后台拉新数据，避免页面闪烁
```

---

## 8. 平台基础设施详细设计

### 8.1 Helm Chart 结构

```
helm/agentsec/
├── Chart.yaml
├── values.yaml                  # 默认配置（可被用户 values 覆盖）
├── values.production.yaml       # 生产环境推荐配置
├── values.minimal.yaml          # MVP 最小部署配置
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── configmaps/
│   │   ├── collector-config.yaml
│   │   └── grafana-dashboards.yaml
│   ├── deployments/
│   │   ├── api-gateway.yaml
│   │   ├── query-service.yaml
│   │   ├── alert-engine.yaml
│   │   ├── notification-service.yaml
│   │   ├── block-service.yaml
│   │   ├── detection-prompt.yaml
│   │   ├── detection-mcp.yaml
│   │   ├── detection-behavior.yaml
│   │   └── frontend.yaml
│   ├── statefulsets/
│   │   ├── otel-collector.yaml
│   │   ├── kafka.yaml
│   │   ├── clickhouse.yaml
│   │   ├── opensearch.yaml
│   │   ├── postgresql.yaml
│   │   └── redis.yaml
│   ├── services/
│   ├── ingress/
│   │   └── main-ingress.yaml    # TLS 终止，路由配置
│   ├── hpa/                     # HPA 自动扩缩容
│   │   └── collector-hpa.yaml
│   ├── rbac/
│   └── jobs/
│       └── db-migrate.yaml      # Flyway DB 迁移 Job
└── tests/
    └── smoke-test.yaml          # helm test 冒烟测试
```

### 8.2 关键 values.yaml 配置项

```yaml
global:
  tenantIsolation: true
  platformDomain: "agentsec.example.com"
  tlsEnabled: true

collector:
  replicaCount: 3
  resources:
    requests: {cpu: "1", memory: "2Gi"}
    limits: {cpu: "4", memory: "8Gi"}
  hpa:
    enabled: true
    minReplicas: 2
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70

kafka:
  replicaCount: 3
  persistence:
    size: 100Gi
    storageClass: "ssd"
  config:
    defaultReplicationFactor: 3
    minInsyncReplicas: 2

clickhouse:
  replicaCount: 2
  persistence:
    size: 500Gi
    storageClass: "ssd"
  config:
    maxMemoryUsage: 16Gi

postgresql:
  primary:
    resources:
      requests: {cpu: "2", memory: "4Gi"}
  readReplicas:
    replicaCount: 1

detection:
  prompt:
    replicaCount: 2
    resources:
      requests: {cpu: "4", memory: "8Gi"}  # 含 NeMo 模型
  intent:
    replicaCount: 1
    maxConcurrency: 8    # LLM 调用成本控制

keycloak:
  enabled: true
  adminPassword: ""      # 必须在 install 时通过 --set 传入

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
    dashboards:
      autoImport: true   # Helm 部署后自动创建 Dashboard
```

### 8.3 数据库迁移设计（Flyway）

```sql
-- migrations/V1__init_schema.sql
-- 初始化所有表结构（见第 2 节）

-- migrations/V2__add_block_logs.sql
CREATE TABLE block_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL,
    app_id      UUID NOT NULL,
    session_id  VARCHAR(200) NOT NULL,
    reason      TEXT,
    rule_id     UUID,
    blocked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- migrations/V3__add_notification_channels.sql
CREATE TABLE notification_channels (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    name        VARCHAR(100) NOT NULL,
    type        VARCHAR(20) NOT NULL,  -- feishu/dingtalk/slack/email/sms/pagerduty
    config      JSONB NOT NULL,        -- Webhook URL / SMTP 配置等
    enabled     BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 9. 性能基准与测试策略

### 9.1 关键性能指标

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| Collector 接收 QPS | > 50,000 span/s（集群） | k6 gRPC 压测，线性增加并发 |
| ClickHouse 写入延迟 | < 5s P99（从 Collector 收到到写入） | 端到端延迟打点（span 时间戳 vs 写入时间戳） |
| Prompt 检测延迟 | < 3s P99 | Kafka 消费延迟监控 |
| Session 查询响应 | < 500ms P99（span 数 < 200） | wrk 并发 HTTP 压测 |
| 控制台首屏加载 | < 2s | Lighthouse CI 集成 |
| 告警端到端延迟 | < 10s（事件产生到飞书通知收到） | 端到端链路打点 |

### 9.2 稳定性测试

- **混沌测试**：使用 Chaos Mesh 随机 Kill Collector/Kafka/ClickHouse Pod，验证高可用切换
- **大数据量测试**：单租户写入 1 亿 span，验证 ClickHouse 查询性能不退化
- **多租户隔离测试**：自动化测试验证任何 API 请求都无法跨租户读取数据
- **阻断延迟测试**：模拟黑名单工具调用，测量端到端阻断延迟（目标 < 5s）

### 9.3 安全渗透测试

- **SQL 注入**：对所有查询 API 参数进行 SQL 注入测试
- **越权访问**：测试 SOC 工程师无法访问管理员功能，租户 A 无法访问租户 B 数据
- **API Key 安全**：验证 API Key 仅存储哈希，原文不可恢复
- **审计日志完整性**：验证审计日志表不可 DELETE/UPDATE（数据库权限验证）

---

## 10. 运维手册要点

### 10.1 关键告警配置

```yaml
# 平台运维 Prometheus 告警规则
groups:
  - name: agentsec-platform
    rules:
      - alert: CollectorDown
        expr: up{job="otel-collector"} == 0
        for: 2m
        labels: {severity: critical}

      - alert: KafkaLagHigh
        expr: kafka_consumer_lag_sum > 10000
        for: 5m
        labels: {severity: warning}

      - alert: ClickHouseWriteFailRate
        expr: rate(clickhouse_write_failures_total[5m]) > 0.01
        for: 2m
        labels: {severity: critical}

      - alert: DetectionEngineLatencyHigh
        expr: histogram_quantile(0.99, detection_latency_seconds_bucket) > 3
        for: 5m
        labels: {severity: warning}

      - alert: PostgreSQLReplicationLag
        expr: pg_replication_lag_seconds > 10
        for: 3m
        labels: {severity: warning}
```

### 10.2 日常运维操作

```bash
# 查看 Collector 集群状态
kubectl get pods -n agentsec -l app=otel-collector

# 查看 Kafka Lag
kubectl exec -n agentsec kafka-0 -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group agentsec-prompt-detector

# 手动触发 DB 迁移
kubectl create job --from=cronjob/db-migrate manual-migrate -n agentsec

# 查看检测引擎错误日志
kubectl logs -n agentsec -l app=detection-prompt --tail=100 | grep ERROR

# 清理过期 Redis 阻断 Key（通常自动 TTL，这里是手动检查）
kubectl exec -n agentsec redis-0 -- redis-cli KEYS "block:*" | wc -l
```

---

*文档结束*


