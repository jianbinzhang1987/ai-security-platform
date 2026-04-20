基于所有参考资料和现有设计规范，以下是关于"网关+探针策略二合一"的分析和设计建议：

---

# 网关与探针策略合并方案分析

## 一、两者安全扫描的核心区别与联系

### 区别

| 维度               | 网关安全扫描                          | 探针安全扫描                                 |
| ------------------ | ------------------------------------- | -------------------------------------------- |
| **扫描位置** | 网络边界，HTTP 请求/响应级别          | 进程内，Agent 运行时上下文级别               |
| **可见数据** | HTTP Body/Header/Params               | Tool 参数、Session 上下文、RAG 检索结果      |
| **延迟约束** | 极低延迟（<<10ms），倾向快速规则匹配  | 可容忍较重检测（语义分析、参数校验）         |
| **阻断粒度** | 整请求级别（拦截 HTTP 请求/覆写响应） | 细粒度（拦截单个 Tool 调用、暂停执行转审批） |
| **脱敏方式** | 网关层内容替换/截断（数据已出进程）   | 端侧本地脱敏（数据不出进程，更安全）         |
| **流控范围** | 全局限流/配额/ACL（租户/应用维度）    | 单实例限流/熔断/死循环中断                   |
| **典型场景** | Prompt注入、敏感内容过滤、访问控制    | 凭证防泄露、PII脱敏、工具越权、RAG污染       |

### 联系

* **同一风险可能双端触发** ：如"敏感内容过滤"既可在网关拦截（快速规则），也可在探针深度检测（语义分析）
* **纵深防御互补** ：网关是第一道防线（粗筛），探针是第二道防线（精筛），两者协同形成纵深
* **共享检测能力** ：Guardrail（关键词/正则/LLM评分）可作为公共校验库被两端策略引用
* **告警统一** ：无论哪个执行面触发的告警，最终都汇聚到同一个告警体系

---

## 二、合并方案设计

### 核心思路：**统一列表 + 执行面标签化 + 智能推荐**

不是简单地把两个列表拼在一起，而是通过**执行面标签**和**策略类型分类**让用户在一个视图中管理所有策略，同时清晰区分每条策略的生效位置和能力差异。

### 1. 菜单架构调整

<pre class="no-fadeIn"><div class=" panel-bg panel-border rounded-[6px] shadow-step"><div class="relative flex min-h-7 flex-shrink-0 flex-row items-center justify-between pl-2 pr-0.5 rounded-t-[6px]"><div class="flex min-w-0 items-center gap-1.5 overflow-hidden"><div class="truncate font-sans text-sm text-ide-text-color opacity-60"></div></div><div><div class="flex flex-row items-center gap-0.5"><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-at-sign h-3 w-3" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"></path></svg></span></div><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy h-3 w-3" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg></span></div></div></div></div><div class="relative overflow-hidden bg-ide-editor-background rounded-b-[6px]" aria-label="highlighted-code-"><pre><div class="group/hscroll relative flex min-w-0 flex-1 flex-col bg-ide-editor-background"><div class="min-w-0 flex-1"><div class="min-w-fit p-[1em]"><div><div class="monaco-tokenized-source"><div><span class="mtk1">▼ 统一策略中心 /policies</span></div><div><span class="mtk1">   ├─ 安全防护策略 /policies/protection          ← 合并后的统一入口</span></div><div><span class="mtk1">   │    ├─ 全部策略 (默认视图)                     ← 不分执行面，统一列表</span></div><div><span class="mtk1">   │    ├─ 网关防护策略 (筛选视图)                 ← target=gateway 筛选</span></div><div><span class="mtk1">   │    └─ 探针运行时策略 (筛选视图)               ← target=probe 筛选</span></div><div><span class="mtk1">   ├─ 通知渠道管理 /policies/channels</span></div><div><span class="mtk1">   └─ 策略发布与下发 /policies/release</span></div></div></div></div></div></div></pre></div></div></pre>

 **关键变化** ：网关和探针不再是两个独立子菜单，而是 **同一个列表的两种筛选视图** 。默认展示全部策略，用户可按执行面筛选。

### 2. 策略列表设计（区分执行面的关键交互）

| 列名                 | 说明                                                  | 区分作用                                          |
| -------------------- | ----------------------------------------------------- | ------------------------------------------------- |
| **生效节点**   | 标签样式：🟢网关 / 🔵探针 / 🟡双端                    | **最核心的区分标识** ，一眼看出策略在哪生效 |
| **策略类型**   | content_safety / dlp / tool_control / guardrail / ... | 按安全能力分类                                    |
| **Hook Point** | gw-request-in / probe-tool-before / ...               | 精确到拦截锚点                                    |
| **处置动作**   | block / mask / alert / allow / ...                    | 策略的行为语义                                    |
| **优先级**     | 数字                                                  | 执行顺序                                          |
| **发布状态**   | draft / published                                     | 生命周期                                          |
| **下发状态**   | 已同步 / 下发中 / 部分失败                            | 同步情况                                          |

### 3. 策略编辑表单设计（合并后的核心交互）

<pre class="no-fadeIn"><div class=" panel-bg panel-border rounded-[6px] shadow-step"><div class="relative flex min-h-7 flex-shrink-0 flex-row items-center justify-between pl-2 pr-0.5 rounded-t-[6px]"><div class="flex min-w-0 items-center gap-1.5 overflow-hidden"><div class="truncate font-sans text-sm text-ide-text-color opacity-60"></div></div><div><div class="flex flex-row items-center gap-0.5"><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-at-sign h-3 w-3" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"></path></svg></span></div><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy h-3 w-3" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg></span></div></div></div></div><div class="relative overflow-hidden bg-ide-editor-background rounded-b-[6px]" aria-label="highlighted-code-"><pre><div class="group/hscroll relative flex min-w-0 flex-1 flex-col bg-ide-editor-background"><div class="min-w-0 flex-1"><div class="min-w-fit p-[1em]"><div><div class="monaco-tokenized-source"><div><span class="mtk1">┌─────────────────────────────────────────────────┐</span></div><div><span class="mtk1">│ 策略编辑                                         │</span></div><div><span class="mtk1">├─────────────────────────────────────────────────┤</span></div><div><span class="mtk1">│ 基础信息区                                       │</span></div><div><span class="mtk1">│  策略名称: [____________]                        │</span></div><div><span class="mtk1">│  策略类型: [内容安全 ▼]                           │</span></div><div><span class="mtk1">│  ★ 生效节点: [网关] [探针] [双端]  ← 必选，核心区分 │</span></div><div><span class="mtk1">│                                                  │</span></div><div><span class="mtk1">│  ┌─ 执行面能力提示（选择后动态展示）──────────┐    │</span></div><div><span class="mtk1">│  │ 🟢 网关模式：                              │    │</span></div><div><span class="mtk1">│  │   · 可用Hook: gw-request-in, gw-response-out│   │</span></div><div><span class="mtk1">│  │   · 适用场景: 流量级快速拦截、全局访问控制    │    │</span></div><div><span class="mtk1">│  │   · 延迟约束: 低延迟，倾向规则匹配           │    │</span></div><div><span class="mtk1">│  │                                            │    │</span></div><div><span class="mtk1">│  │ 🔵 探针模式：                               │    │</span></div><div><span class="mtk1">│  │   · 可用Hook: probe-llm-before/after,      │    │</span></div><div><span class="mtk1">│  │     probe-tool-before/after, probe-rag-after │    │</span></div><div><span class="mtk1">│  │   · 适用场景: 行为级精细管控、本地脱敏        │    │</span></div><div><span class="mtk1">│  │   · 延迟约束: 可做语义分析等较重检测          │    │</span></div><div><span class="mtk1">│  └────────────────────────────────────────────┘    │</span></div><div><span class="mtk1">│                                                  │</span></div><div><span class="mtk1">│  Hook Point: [gw-request-in ▼]  ← 级联过滤       │</span></div><div><span class="mtk1">│  处置动作:   [☑block ☐mask ☐alert ☐allow]        │</span></div><div><span class="mtk1">│  优先级:     [100]                                │</span></div><div><span class="mtk1">├─────────────────────────────────────────────────┤</span></div><div><span class="mtk1">│ 条件配置区                                       │</span></div><div><span class="mtk1">│  ...                                             │</span></div><div><span class="mtk1">├─────────────────────────────────────────────────┤</span></div><div><span class="mtk1">│ 动作配置区（选择 alert 时展开告警配置）             │</span></div><div><span class="mtk1">│  ...                                             │</span></div><div><span class="mtk1">├─────────────────────────────────────────────────┤</span></div><div><span class="mtk1">│ 作用域区                                         │</span></div><div><span class="mtk1">│  ...                                             │</span></div><div><span class="mtk1">└─────────────────────────────────────────────────┘</span></div></div></div></div></div></div></pre></div></div></pre>

### 4. 智能推荐机制（防止用户混淆的关键）

当用户选择策略类型时，系统**自动推荐**最合适的执行面：

| 策略类型       | 推荐执行面 | 推荐理由                  | 是否允许切换   |
| -------------- | ---------- | ------------------------- | -------------- |
| Prompt注入防御 | 🟢 网关    | 需要在请求入站时快速拦截  | 可切换为双端   |
| 敏感内容过滤   | 🟡 双端    | 网关快速规则+探针深度语义 | 可切换单端     |
| 凭证防泄露     | 🔵 探针    | 端侧扫描，数据不出进程    | 不建议切网关   |
| PII脱敏        | 🔵 探针    | 端侧本地替换更安全        | 可切换为双端   |
| 工具白黑名单   | 🔵 探针    | 探针拦截Tool调用          | 不建议切网关   |
| 工具参数约束   | 🔵 探针    | 探针校验Tool入参          | 不建议切网关   |
| 高危操作审批   | 🔵 探针    | 探针暂停执行转审批        | 不建议切网关   |
| 全局频控配额   | 🟢 网关    | 全局限流/配额             | 不建议切换探针 |
| 访问控制ACL    | 🟢 网关    | IP/Token/地理位置控制     | 不建议切换探针 |
| Guardrail护栏  | 🟢 网关    | 快速关键词/正则匹配       | P1支持双端     |
| RAG污染防护    | 🔵 探针    | 检索结果注入风险检测      | 不建议切网关   |

 **交互** ：选择策略类型后，"生效节点"自动填入推荐值，并显示推荐理由气泡。用户仍可手动切换，但切换到不推荐组合时弹出 **风险提示** （如："凭证防泄露策略部署到网关时，敏感凭证会先经过网络传输再被检测，存在泄露风险。建议保持探针模式或选择双端部署。"）

### 5. 双端策略的拆分与联动（P1）

当用户选择 `<span>target=both</span>` 时，系统在后台**自动拆分**为两条策略：

<pre class="no-fadeIn"><div class=" panel-bg panel-border rounded-[6px] shadow-step"><div class="relative flex min-h-7 flex-shrink-0 flex-row items-center justify-between pl-2 pr-0.5 rounded-t-[6px]"><div class="flex min-w-0 items-center gap-1.5 overflow-hidden"><div class="truncate font-sans text-sm text-ide-text-color opacity-60"></div></div><div><div class="flex flex-row items-center gap-0.5"><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-at-sign h-3 w-3" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"></path></svg></span></div><div class="rounded p-1 cursor-pointer opacity-60 hover:bg-neutral-500/25 hover:opacity-100"><span class="text-ide-text-color" data-state="closed"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy h-3 w-3" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg></span></div></div></div></div><div class="relative overflow-hidden bg-ide-editor-background rounded-b-[6px]" aria-label="highlighted-code-"><pre><div class="group/hscroll relative flex min-w-0 flex-1 flex-col bg-ide-editor-background"><div class="min-w-0 flex-1"><div class="min-w-fit p-[1em]"><div><div class="monaco-tokenized-source"><div><span class="mtk1">用户创建: "敏感内容过滤" target=both</span></div><div><span class="mtk1">  ↓ 自动拆分</span></div><div><span class="mtk1">  ├── 策略A: "敏感内容过滤(网关)" target=gateway, hook=gw-request-in</span></div><div><span class="mtk1">  │     动作: block（快速规则匹配拦截明显违规）</span></div><div><span class="mtk1">  │     优先级: 50（先执行，粗筛）</span></div><div><span class="mtk1">  └── 策略B: "敏感内容过滤(探针)" target=probe, hook=probe-llm-before</span></div><div><span class="mtk1">        动作: mask（语义分析后脱敏/打码）</span></div><div><span class="mtk1">        优先级: 100（后执行，精筛）</span></div></div></div></div></div></div></pre></div></div></pre>

 **用户视角** ：在列表中看到的是一条策略，标签为🟡双端；点击展开可看到两个执行面的具体配置。

### 6. 防混淆的视觉设计规范

| 设计元素       | 网关策略              | 探针策略                | 双端策略              |
| -------------- | --------------------- | ----------------------- | --------------------- |
| 标签颜色       | 🟢 绿色               | 🔵 蓝色                 | 🟡 黄色               |
| 标签文字       | `<span>网关</span>` | `<span>探针</span>`   | `<span>双端</span>` |
| 图标           | 🛡️ 盾牌             | 🔍 放大镜               | 🔗 链接               |
| Hook Point前缀 | `<span>gw-</span>`  | `<span>probe-</span>` | 两者都有              |
| 列表行背景     | 微绿色底              | 微蓝色底                | 微黄色底              |

---

## 三、与现有设计规范的差异对照

| 维度                         | 现有规范（分离方案）      | 合并方案                   | 影响               |
| ---------------------------- | ------------------------- | -------------------------- | ------------------ |
| 菜单结构                     | 网关/探针为两个独立子菜单 | 统一入口+筛选视图          | 减少页面跳转       |
| 策略列表                     | 分属两个页面              | 同一列表，执行面标签区分   | 信息密度增加       |
| 策略编辑                     | 各自独立表单              | 统一表单+执行面动态切换    | 需要智能推荐防混淆 |
| `<span>target=both</span>` | P0不开放                  | P1开放，自动拆分           | 需要拆分联动机制   |
| 冲突检测                     | P1/P2                     | 更重要（合并后同列表可见） | 应提升优先级       |

---

## 四、建议的落地节奏

* **P0** ：统一列表 + 执行面标签 + 智能推荐（策略类型→推荐执行面）+ 筛选视图；`<span>target=both</span>` 前端隐藏后端拒绝
* **P1** ：`<span>target=both</span>` 开放 + 自动拆分联动 + 执行面矛盾冲突检测 + 执行面能力提示气泡
* **P2** ：双端策略深度协同（网关粗筛结果传递给探针精筛，避免重复检测）

 **核心原则** ：合并的是 **管理视图** ，不是 **执行逻辑** 。用户在一个地方管理所有策略，但每条策略的执行面、Hook Point、动作仍然严格区分——这是防止混淆的根本。
