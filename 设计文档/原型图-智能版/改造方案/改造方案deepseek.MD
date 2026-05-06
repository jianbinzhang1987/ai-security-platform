Let me first explore both directories to understand their

Let me read the key system design and prototype design documents to perform

Now let me look at the actual HTML prototype files and the remaining design docs to compare implementation vs design

Let me now read the key HTML prototype files to compare implementation against the design specifications.

Now I have a thorough understanding of both the system design documents and the prototype implementation. Here is my comprehensive analysis:

---

# 原型设计问题分析报告

基于对概要设计文档（`系统设计/` 共13篇）和原型实现（`原型图-智能版/` 共41个HTML页面 + 6篇原型说明）的交叉比对，当前原型存在以下核心问题：

---

## 一、分期边界严重混乱（Scope Creep）

这是最根本的问题。设计文档 `01-智能化改造原型设计范围与页面清单.md` 明确约定"**分期页面只展示该期次可交付能力**"，但 [index.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/index.html:0:0-0:0) 导航中：

| 期次    | 页面                                                                  | 实际状态                               |
| ------- | --------------------------------------------------------------------- | -------------------------------------- |
| P1      | 知识库管理全部5个子页                                                 | **已暴露**，无 `nav-hidden-p0` |
| P2a/P2b | SOC分析驾驶舱、人员风险分析、风险关联分析、行为基线管理、组织风险态势 | **已暴露**，无 `nav-hidden-p0` |
| P3      | 自动响应规则                                                          | **已暴露**，无 `nav-hidden-p0` |

`nav-hidden-p0` 仅对资产管理子页面生效，而对更后期的智能化页面全部可见。这直接违反了设计原则第5条："不在 P0.5a 页面中提前承诺完整 RAG、完整知识库或自动响应"。

**[event-detail.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/events/event-detail.html:0:0-0:0) 同样存在范围蔓延**：AI处置建议卡片和自动执行台账（含L1-L3动作级别、TTL倒计时）均属于P3能力，却被塞进了P0.5a的核心闭环页面。

---

## 二、信息架构错位

1. **文件路径与导航分组不对应**：

   - [model-registry.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/system/model-registry.html:0:0-0:0)、[prompt-template.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/system/prompt-template.html:0:0-0:0) 放在 [pages/system/](cci:9://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/system:0:0-0:0) 下，但导航归入"AI模型治理"
   - [ai-service-monitor.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/ops/ai-service-monitor.html:0:0-0:0) 放在 [pages/ops/](cci:9://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/ops:0:0-0:0) 下，但导航挂在"安全监控"下（`index.html:458`）
   - [data-classification.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/system/data-classification.html:0:0-0:0) 放在 [pages/system/](cci:9://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/system:0:0-0:0) 下，但导航挂在"统一策略中心"下
2. **安全监控导航膨胀**：9个平级子菜单（`index.html:374-467`），日常高频操作（溯源、会话追踪）与低频分析页面（SOC驾驶舱、组织态势）平铺，无优先级区分。
3. **策略中心三级嵌套**：用户需先理解"网关策略"和"探针策略"的技术区别才能找到配置入口，而非按"防什么"（提示词攻击？数据泄露？）组织。

---

## 三、事件详情页——UX重灾区

[event-detail.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/events/event-detail.html:0:0-0:0) 是P0.5a核心页面，但存在严重的可用性问题：

### 3.1 信息过载

单页包含 **8个卡片区域 + 6个弹窗**，17个基础字段 + 5个证据Tab + 3个右侧操作卡片。核心问题"这个事件是不是真的风险？我该做什么？"被淹没在信息海洋中。

### 3.2 三套操作区无流程引导

右侧同时存在三组强操作属性的按钮群：

- AI研判卡片：确认 / 修正 / 拒绝
- AI处置建议：采纳并执行 / 修改后执行 / 拒绝并记录 / 转人工
- 处置动作：下发限制 / 标记误报 / 接受风险 / 处置登记

用户面临逻辑死锁：如果认为事件是误报，该点"拒绝AI研判"还是"标记误报"？"对AI的反馈"与"对事件的处置"在工作流上未合并。

### 3.3 证据与结论物理拆散

- AI为什么命中（命中片段、判断理由）藏在左侧"证据工作区 → AI检测结果Tab"
- AI对全局的看法（攻击手法、影响面）放在右侧"AI辅助研判卡片"

用户必须在左侧切Tab看证据，再跳到右侧看结论，打断"证据→结论"的连贯思考。

### 3.4 首屏被开发态术语占领

`trace_id`、`span_id`、`source_field: tool.input`、`evidence_offset`、`model_version`、`prompt_template_version` 等字段占据首屏黄金位置。这些对模型调优重要，但对运营人员是严重的视觉噪音。

---

## 四、AI状态术语晦涩

标题区同时展示三套独立状态机（`event-detail.html:67-71`）：

- 事件状态（高风险/处理中）
- AI检测状态：`success` / `timeout` / `error` / `circuit_open` / `skipped_by_policy`
- AI研判状态：`generated` / `confirmed` / `modified` / `rejected`

`circuit_open`（熔断）、`skipped_by_policy`（策略跳过）是工程术语，安全运营人员不理解。15种状态组合让用户无法快速判断"这个事件的AI结果能不能信"。

---

## 五、图表交互能力不足

- 安全总览 [dashboard.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/pages/assets/dashboard.html:0:0-0:0) 保留"P2改进：引入ECharts"注释，脚本仍为注释状态
- 人员风险趋势用CSS柱状块模拟（`persona-analysis.html:23`）
- AI服务监控大量使用 `chart-mock`（`ai-service-monitor.html:471`）
- 趋势图缺少tooltip、区间缩放、点击联动筛选、导出和异常点解释

---

## 六、AI结论标识不全局一致

- 关联分析页有"AI分析"标签（`correlation-analysis.html:108`）
- SOC驾驶舱预测链路只标"预测"，无统一"AI分析/需人工确认"表达（`soc-dashboard.html:87`）
- 设计文档要求"所有AI分析结论必须标注AI分析标识"，但实现不一致

---

## 七、其他问题

- **优先级标记矛盾**：`01-页面清单`中内容安全策略标P0、风险事件列表标P1，但系统设计中期次分别为P0.5b和P0.5a
- **默认首页不合理**：[index.html](cci:7://file:///E:/code/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E7%9B%91%E6%B5%8B%E5%B9%B3%E5%8F%B0/%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3/%E5%8E%9F%E5%9E%8B%E5%9B%BE-%E6%99%BA%E8%83%BD%E7%89%88/index.html:0:0-0:0) 默认加载"接入应用管理"，安全监测平台应以"安全总览"为首页
- **缺少引导和空状态**：大部分页面无首次使用引导、无有意义的空状态提示、无预置模板
- **页面间缺少上下文**：从安全总览下钻到事件列表，筛选上下文丢失；从人员分析跳转事件详情，不知来源路径
- **L4强控制约束不够显性**：自动响应页L4"不可自动执行"的约束仅在页面说明中，未形成强约束交互

---

## 核心结论

当前原型设计的根本矛盾是：**它更像是"数据模型字段的UI堆砌版"，而非以安全运营人员工作流为中心的设计**。系统设计的分期规划、信息架构原则、状态机分层和UX原则在原型实现中出现了明显的偏离。改造方向应从"以字段为中心"转向"以工作流为中心"——模型运行状态沉底、操作按钮业务归并、首屏聚焦风险事实与处置引导。
