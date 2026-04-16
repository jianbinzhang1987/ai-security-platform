# Phase 03 / 3.2 LangChain SDK 当前遥测能力说明

## 1. 文档目的

本文档用于面向项目相关同事，说明当前 Python SDK 在 `LangChain` 场景下已经具备的遥测能力、当前 Demo 的验证情况，以及当前能力边界。

本文档聚焦客户端侧当前实现，不代表管理端查证、落库、展示能力已经全部完成。

---

## 2. 当前结论

当前 SDK 已经能够对 `LangChain Agent` 主链路中的以下对象进行无侵入式自动遥测：

1. `LLM 调用`
2. `Tool / Skill 调用`
3. `风险检测与阻断结果`
4. `trace / span 关系`
5. `本地时间线主证据展示`

在当前 Demo 中，SDK 已能采集并展示：

1. `Prompt`
2. `LLM 回复`
3. `Tool 名称`
4. `Tool 入参`
5. `Tool 响应`
6. `风险等级`
7. `阻断原因`
8. `blocked / error / ok` 状态

---

## 3. 当前 LangChain 可采集对象

### 3.1 LLM 调用

对 `LangChain ChatModel` 调用，当前可采集：

1. `agentsec.span_type=llm_call`
2. `gen_ai.framework=langchain`
3. `gen_ai.vendor`
4. `gen_ai.model`（如可获得）
5. `gen_ai.prompt`
6. `gen_ai.completion`
7. `agentsec.llm.input`
8. `agentsec.llm.output`
9. `agentsec.node.display_name`
10. `agentsec.node.method_name`
11. `start_time / end_time / duration`
12. `error.type`

对应理解：

1. `gen_ai.prompt` / `agentsec.llm.input`：输入给 LLM 的 Prompt
2. `gen_ai.completion` / `agentsec.llm.output`：LLM 返回内容
3. `display_name`：页面展示名，例如：
   - `ChatModel: Scenario Chat Model`
   - `ChatModel: Remote Summary`

---

### 3.2 Tool / Skill 调用

对 `LangChain tool` 调用，当前可采集：

1. `agentsec.span_type=tool_call`
2. `gen_ai.framework=langchain`
3. `agentsec.tool.kind=skill`
4. `agentsec.tool.name`
5. `agentsec.tool.input`
6. `agentsec.tool.output`
7. `agentsec.node.display_name`
8. `agentsec.node.class_name`
9. `agentsec.node.method_name`
10. `start_time / end_time / duration`
11. `error.type`

对应理解：

1. `agentsec.tool.name`：工具名称
2. `agentsec.tool.input`：工具真实入参
3. `agentsec.tool.output`：工具真实出参或返回内容

在当前 Demo 中，已经可以看到例如：

1. `Tool: parse_material`
2. `Tool: extract_key_points`
3. `Tool: apply_selected_skill`
4. `Tool: send_message_outside`

---

### 3.3 风险检测与阻断结果

在 LangChain 主链路中，当前还能沉淀以下安全相关字段：

1. `security.risk.level`
2. `security.block_reason`
3. `agentsec.block.action`
4. `status`

当前可表达的运行状态包括：

1. `ok`
2. `blocked`
3. `error`

在异常 tool 场景下，当前时间线中可以看到例如：

1. `status=blocked`
2. `security.risk.level=high`
3. `security.block_reason=detection_rule:...`

---

### 3.4 Trace / Span 关系

当前还可采集和输出：

1. `trace_id`
2. `span_id`
3. `parent_span_id`

因此当前可支撑：

1. 执行时间线展示
2. 父子调用关系还原
3. 同一条 Agent 执行链路的多节点串联

---

## 4. 当前本地时间线可展示内容

当前本地 API / Demo 主时间线，已可展示以下字段摘要：

1. `llm_input_preview`
2. `llm_output_preview`
3. `tool_input_preview`
4. `tool_output_preview`
5. `tool_kind`
6. `duration_ms`

同时在 Demo 主视图中，当前也可读取更完整的详情字段：

1. `llm_input_text`
2. `llm_output_text`
3. `tool_input_text`
4. `tool_output_text`

这意味着在当前 Demo 页面中，已经可以直接看到：

1. Prompt 内容
2. LLM 回复内容
3. Tool 名称
4. Tool 入参
5. Tool 响应

---

## 5. 当前 Demo 中已验证到的 LangChain 遥测节点

当前 Demo 的主链路已经验证到以下 LangChain 遥测节点：

1. `ChatModel: Scenario Chat Model`
2. `Tool: parse_material`
3. `Tool: extract_key_points`
4. `Tool: apply_selected_skill`
5. `Tool: send_message_outside`
6. `ChatModel: Remote Summary`

说明：

1. `Scenario Chat Model`：主智能体的流程调度模型，用于决定下一步调用哪个 tool
2. `Remote Summary`：摘要生成模型，当前也已收敛为走 `LangChain BaseChatModel` 路径

这意味着当前 Demo 中的核心 LLM / Tool 遥测，已经尽量统一到 `LangChain` 框架侧，由 SDK 自动采集，而不是在 Demo 里手工埋 LLM 或 Tool 遥测点。

---

## 6. 当前已经验证成立的能力点

当前已验证成立的点包括：

1. `LangChain LLM 调用` 能采到 Prompt 与输出
2. `LangChain Tool 调用` 能采到工具名、入参、出参
3. `异常 Tool` 可在 pre-call 阶段被识别并阻断
4. `阻断结果` 可在时间线中形成 `blocked` 主证据
5. `远端摘要模型调用` 已纳入 LangChain 遥测链路
6. `本地时间线` 可直接展示 LLM 与 Tool 关键内容

---

## 7. 适合对外汇报的一句话

可直接使用以下表述：

> 当前 SDK 已经能够对 LangChain Agent 的 LLM 调用与 Tool 调用进行无侵入式自动遥测，能够采集 Prompt、LLM 回复、Tool 名称、Tool 入参/出参、风险等级、阻断原因以及 trace/span 关系，并在本地时间线中形成可直接查看的主证据。

---

## 8. 当前能力边界

为避免误解，当前还需明确以下边界：

### 8.1 不是任意 Python 方法都能自动采到

当前稳定覆盖的是：

1. `LangChain LLM 调用`
2. `LangChain Tool 调用`
3. 少量显式业务 span（仅用于辅助说明业务步骤）

因此当前不能表述为：

1. “任意 Python 方法级全量自动追踪”

---

### 8.2 当前以 LangChain 为首批重点适配框架

当前对 `LangChain` 的支持最成熟。
其他框架如 `LangGraph`、更广泛的第三方生态接入，仍应在后续“框架采集增强层”中单独推进。

---

-

## 9. 当前证据来源

当前结论的主证据来自：

1. 本地 trace store / local API 输出
3. SDK 自动化测试
4. Demo 实际运行后的当前执行时间线

当前不以 Demo 自己的 stdout 或辅助步骤文案作为主证据。

---

## 10. 推荐对齐口径

建议项目内统一口径如下：

1. Demo 中的 `LLM / Tool` 遥测，优先应由 SDK 对 `LangChain` 自动插桩获得
2. Demo 不应手工埋 `LLM 调用`、`Tool 调用`、`MCP/Skill 调用` 的遥测点
3. Demo 可保留少量业务级辅助 span，用于说明业务步骤，但不替代框架遥测主证据
4. 当前最适合优先对外强调的是：`LangChain` 场景下的无侵入式自动采集能力

---

## 11. 当前状态结论

截至当前代码状态，可以认为：

1. `LangChain` 已是当前 SDK 遥测能力最成熟、最适合对外汇报的首批框架
2. 当前 SDK 已能对 LangChain Agent 的关键主链路形成可复核的本地遥测证据
3. 当前 Demo 已能够作为“异常 Tool 调用阻断 + 时间线证据展示”的有效验证场景
