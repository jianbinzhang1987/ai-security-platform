集成 Langfuse - Dify Docs
跳转到主要内容
Dify Docs home page![light logo](https://assets-docs.dify.ai/2025/05/d05cfc6ebe48f725d171dc71c64a5d16.svg)![dark logo](https://assets-docs.dify.ai/2025/05/c51f1cda47c1d9a4a162d7736f6e4c53.svg)
搜索...
Ctrl K
使用 Dify
##### 入门
* 介绍
* 30分钟快速入门
* 核心概念
##### 构建
* 工作流与对话流
  + 概述
  + 节点
  + 流程逻辑
  + 快捷键
  + 使用 MCP 工具
  + 版本控制
  + 调试
* 基础应用
* 应用工具箱
##### 发布
* 分享你的 AI 应用
* Web App
* MCP 服务器
* API 集成
* 市场
##### 监控
* 仪表盘
* 日志
* 标注系统
* 集成
  + 集成 LangSmith
  + 集成 Langfuse
  + 集成 Opik
  + 集成 W&B Weave
  + 集成 Arize
  + 集成 Phoenix
  + 集成阿里云云监控
##### 知识库
* 概述
* 创建
* 管理
* 调试
* 在应用内集成
* 请求频率限制
  CLOUD
##### 工作区
* 概述
* 模型供应商
* 插件
* 工具
* 管理应用
* 管理成员
* 个人设置
* 计费
  CLOUD
* API 扩展
##### 教程
* 工作流 101
* 简单聊天机器人
* ChatFlow 实战：搭建 Twitter 账号分析助手
* 使用知识库搭建智能客服机器人
* 如何搭建 AI 图片生成应用
* 使用文件上传搭建文章理解助手
* Changelog
* Studio
* Latest
  ![CN](https://d3gk2c5xim1je2.cloudfront.net/flags/CN.svg)
  简体中文
Dify Docs home page![light logo](https://assets-docs.dify.ai/2025/05/d05cfc6ebe48f725d171dc71c64a5d16.svg)![dark logo](https://assets-docs.dify.ai/2025/05/c51f1cda47c1d9a4a162d7736f6e4c53.svg)
Latest
![CN](https://d3gk2c5xim1je2.cloudfront.net/flags/CN.svg)
简体中文
搜索...
Ctrl K
* Changelog
* Studio
* Studio
搜索...
Navigation
集成
集成 Langfuse
集成
# 集成 Langfuse
复制页面
复制页面
⚠️ 本文档由 AI 自动翻译。如有任何不准确之处，请参考英文原版。
### ​ 什么是 Langfuse
Langfuse 是一个开源的大型语言模型工程平台，帮助团队协作调试、分析和迭代他们的应用程序。
介绍 Langfuse: https://langfuse.com/
---
### ​ 如何配置 Langfuse
1. 在官方网站注册并登录 Langfuse
2. 在 Langfuse 中创建一个项目。登录后，点击主页上的 **New** 来创建你自己的项目。该**项目**将用于与 Dify 中的**应用程序**关联，以进行数据监控。
![](https://assets-docs.dify.ai/2025/04/34ca6a973c4a1230be659b313b99fd90.png)
编辑项目名称。
![在 Langfuse 中创建项目](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/26cfbb94e312a100c39e217fdd0b4406.png)
3. 创建项目 API 凭据。在项目的左侧栏中，点击 **Settings** 打开设置。
![创建项目 API 凭据](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/2ed72a6761f2977201c29e67e5bc634c.png)
在设置中，点击 **Create API Keys** 来创建项目 API 凭据。
![创建项目 API 凭据](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/3c3fbd5392d37fbccf1f9ef76c54f0bc.png)
复制并保存 **Secret Key**、**Public Key** 和 **Host**。
![获取 API 密钥配置](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/a2ff67951ce300082d875eae8458c8c7.png)
4. 在 Dify 中配置 Langfuse。打开你需要监控的应用程序，在侧边菜单中打开 **Monitoring**，并在页面上选择 **Tracing app performance**。
![配置 Langfuse](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/ebc84b328ad37c0f6dbca6101e1f90ab.png)
点击配置后，将在 Langfuse 中创建的 **Secret Key, Public Key, Host** 粘贴到配置中并保存。
![配置 Langfuse](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/5bfa409e7a073f133f21146535401512.png)
成功保存后，你可以在当前页面查看状态。如果显示为已启动，则正在被监控。
![查看配置状态](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/1aa086a1aead0e29948e7d6d5815d5d1.png)
---
### ​ 在 Langfuse 中查看监控数据
配置完成后，可以在 Langfuse 中查看 Dify 应用程序的调试或生产数据。
![](https://assets-docs.dify.ai/2025/04/a2c02ccc559743b85b0f972aa513e47a.png)
![](https://assets-docs.dify.ai/2025/04/88f3adfb03f325d2ea800ba5685b9ec9.png)
---
### ​ 监控数据列表
#### ​ 跟踪工作流和对话流的信息
**跟踪工作流和对话流**
| Workflow | LangFuse Trace |
| --- | --- |
| workflow\_app\_log\_id/workflow\_run\_id | id |
| user\_session\_id | user\_id |
| workflow\_{id} | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| Model token consumption | usage |
| metadata | metadata |
| error | level |
| error | status\_message |
| [workflow] | tags |
| [“message”, conversation\_mode] | session\_id |
| conversion\_id | parent\_observation\_id |
**工作流跟踪信息**
* workflow\_id - 工作流的唯一 ID
* conversation\_id - 对话 ID
* workflow\_run\_id - 此运行时的工作流 ID
* tenant\_id - 租户 ID
* elapsed\_time - 此运行时的经过时间
* status - 运行时状态
* version - 工作流版本
* total\_tokens - 此运行时使用的总标记数
* file\_list - 处理文件的列表
* triggered\_from - 触发此运行时的来源
* workflow\_run\_inputs - 此工作流的输入
* workflow\_run\_outputs - 此工作流的输出
* error - 错误信息
* query - 运行时使用的查询
* workflow\_app\_log\_id - 工作流应用日志 ID
* message\_id - 相关消息 ID
* start\_time - 此运行时的开始时间
* end\_time - 此运行时的结束时间
* workflow node executions - 工作流节点运行时信息
* 元数据
  + workflow\_id - 工作流的唯一 ID
  + conversation\_id - 对话 ID
  + workflow\_run\_id - 此运行时的工作流 ID
  + tenant\_id - 租户 ID
  + elapsed\_time - 此运行时的经过时间
  + status - 操作状态
  + version - 工作流版本
  + total\_tokens - 此运行时使用的总标记数
  + file\_list - 处理文件的列表
  + triggered\_from - 触发此运行时的来源
#### ​ 消息跟踪信息
**用于跟踪大型语言模型对话**
| Message | LangFuse Generation/Trace |
| --- | --- |
| message\_id | id |
| user\_session\_id | user\_id |
| message\_{id} | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| Model token consumption | usage |
| metadata | metadata |
| error | level |
| error | status\_message |
| [“message”, conversation\_mode] | tags |
| conversation\_id | session\_id |
| conversion\_id | parent\_observation\_id |
**消息跟踪信息**
* message\_id - 消息 ID
* message\_data - 消息数据
* user\_session\_id - 用户会话 ID
* conversation\_model - 对话模型
* message\_tokens - 消息标记数
* answer\_tokens - 回答标记数
* total\_tokens - 消息和回答的总标记数
* error - 错误信息
* inputs - 输入数据
* outputs - 输出数据
* file\_list - 处理文件的列表
* start\_time - 开始时间
* end\_time - 结束时间
* message\_file\_data - 相关文件数据的消息
* conversation\_mode - 对话模式
* 元数据
  + conversation\_id - 对话 ID
  + ls\_provider - 模型提供商
  + ls\_model\_name - 模型 ID
  + status - 消息状态
  + from\_end\_user\_id - 发送用户的 ID
  + from\_account\_id - 发送账户的 ID
  + agent\_based - 是否基于智能代理
  + workflow\_run\_id - 此运行时的工作流 ID
  + from\_source - 消息来源
  + message\_id - 消息 ID
#### ​ 审核跟踪信息
**用于跟踪对话审核**
| Moderation | LangFuse Generation/Trace |
| --- | --- |
| user\_id | user\_id |
| moderation | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| metadata | metadata |
| [moderation] | tags |
| message\_id | parent\_observation\_id |
**消息跟踪信息**
* message\_id - 消息 ID
* user\_id - 用户 ID
* workflow\_app\_log\_id - 工作流应用日志 ID
* inputs - 审核输入数据
* message\_data - 消息数据
* flagged - 是否标记为关注
* action - 实施的具体动作
* preset\_response - 预设响应
* start\_time - 审核开始时间
* end\_time - 审核结束时间
* 元数据
  + message\_id - 消息 ID
  + action - 实施的具体动作
  + preset\_response - 预设响应
#### ​ 建议问题跟踪信息
**用于跟踪建议问题**
| Suggested Question | LangFuse Generation/Trace |
| --- | --- |
| user\_id | user\_id |
| suggested\_question | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| metadata | metadata |
| [suggested\_question] | tags |
| message\_id | parent\_observation\_id |
**消息跟踪信息**
* message\_id - 消息 ID
* message\_data - 消息数据
* inputs - 输入数据
* outputs - 输出数据
* start\_time - 开始时间
* end\_time - 结束时间
* total\_tokens - 总标记数
* status - 消息状态
* error - 错误信息
* from\_account\_id - 发送账户 ID
* agent\_based - 是否基于智能代理
* from\_source - 消息来源
* model\_provider - 模型提供商
* model\_id - 模型 ID
* suggested\_question - 建议问题
* level - 状态级别
* status\_message - 消息状态
* 元数据
  + message\_id - 消息 ID
  + ls\_provider - 模型提供商
  + ls\_model\_name - 模型 ID
  + status - 消息状态
  + from\_end\_user\_id - 发送用户的 ID
  + from\_account\_id - 发送账户 ID
  + workflow\_run\_id - 此运行时的工作流 ID
  + from\_source - 消息来源
#### ​ 数据集检索跟踪信息
**用于跟踪知识库检索**
| Dataset Retrieval | LangFuse Generation/Trace |
| --- | --- |
| user\_id | user\_id |
| dataset\_retrieval | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| metadata | metadata |
| [dataset\_retrieval] | tags |
| message\_id | parent\_observation\_id |
**数据集检索跟踪信息**
* message\_id - 消息 ID
* inputs - 输入消息
* documents - 文档数据
* start\_time - 开始时间
* end\_time - 结束时间
* message\_data - 消息数据
* 元数据
  + message\_id - 消息 ID
  + ls\_provider - 模型提供商
  + ls\_model\_name - 模型 ID
  + status - 模型状态
  + from\_end\_user\_id - 发送用户的 ID
  + from\_account\_id - 发送账户的 ID
  + agent\_based - 是否基于智能代理
  + workflow\_run\_id - 此运行时的工作流 ID
  + from\_source - 消息来源
#### ​ 工具跟踪信息
**用于跟踪工具调用**
| Tool | LangFuse Generation/Trace |
| --- | --- |
| user\_id | user\_id |
| tool\_name | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| metadata | metadata |
| [“tool”, tool\_name] | tags |
| message\_id | parent\_observation\_id |
**工具跟踪信息**
* message\_id - 消息 ID
* tool\_name - 工具名称
* start\_time - 开始时间
* end\_time - 结束时间
* tool\_inputs - 工具输入
* tool\_outputs - 工具输出
* message\_data - 消息数据
* error - 错误信息（如果存在）
* inputs - 消息输入
* outputs - 消息输出
* tool\_config - 工具配置
* time\_cost - 时间消耗
* tool\_parameters - 工具参数
* file\_url - 相关文件的 URL
* 元数据
  + message\_id - 消息 ID
  + tool\_name - 工具名称
  + tool\_inputs - 工具输入
  + tool\_outputs - 工具输出
  + tool\_config - 工具配置
  + time\_cost - 时间消耗
  + error - 错误信息
  + tool\_parameters - 工具参数
  + message\_file\_id - 消息文件 ID
  + created\_by\_role - 创建者角色
  + created\_user\_id - 创建者用户 ID
#### ​ 生成名称跟踪
**用于跟踪对话标题生成**
| Generate Name | LangFuse Generation/Trace |
| --- | --- |
| user\_id | user\_id |
| generate\_name | name |
| start\_time | start\_time |
| end\_time | end\_time |
| inputs | input |
| outputs | output |
| metadata | metadata |
| [generate\_name] | tags |
**生成名称跟踪信息**
* conversation\_id - 对话 ID
* inputs - 输入数据
* outputs - 生成的会话名称
* start\_time - 开始时间
* end\_time - 结束时间
* tenant\_id - 租户 ID
* 元数据
  + conversation\_id - 对话 ID
  + tenant\_id - 租户 ID
### ​ Langfuse 提示词管理
Langfuse 提示词管理插件（社区维护）让你可以在 Dify 应用程序中使用 Langfuse 中管理和版本化的提示词，增强你的大型语言模型应用程序开发工作流。主要功能包括：
* **获取提示词：** 获取在 Langfuse 中管理的特定提示词。
* **搜索提示词：** 使用各种过滤器在 Langfuse 中搜索提示词。
* **更新提示词：** 在 Langfuse 中创建提示词的新版本，并设置标签/标签。
此集成简化了管理和版本化提示词的过程，有助于更高效的开发和迭代周期。你可以在这里找到插件和安装说明。
此页面对您有帮助吗？
是否
上一页
集成 Opik
下一页
Ctrl+I
xgithublinkedin
技术支持This documentation is built and hosted on Mintlify, a developer documentation platform
在此页面
* 什么是 Langfuse
* 如何配置 Langfuse
* 在 Langfuse 中查看监控数据
* 监控数据列表
* 跟踪工作流和对话流的信息
* 消息跟踪信息
* 审核跟踪信息
* 建议问题跟踪信息
* 数据集检索跟踪信息
* 工具跟踪信息
* 生成名称跟踪
* Langfuse 提示词管理
集成 Langfuse - Dify Docs
![](https://assets-docs.dify.ai/2025/04/34ca6a973c4a1230be659b313b99fd90.png)
![在 Langfuse 中创建项目](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/26cfbb94e312a100c39e217fdd0b4406.png)
![创建项目 API 凭据](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/2ed72a6761f2977201c29e67e5bc634c.png)
![创建项目 API 凭据](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/3c3fbd5392d37fbccf1f9ef76c54f0bc.png)
![获取 API 密钥配置](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/a2ff67951ce300082d875eae8458c8c7.png)
![配置 Langfuse](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/ebc84b328ad37c0f6dbca6101e1f90ab.png)
![配置 Langfuse](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/5bfa409e7a073f133f21146535401512.png)
![查看配置状态](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/monitoring/integrate-external-ops-tools/1aa086a1aead0e29948e7d6d5815d5d1.png)
![](https://assets-docs.dify.ai/2025/04/a2c02ccc559743b85b0f972aa513e47a.png)
![](https://assets-docs.dify.ai/2025/04/88f3adfb03f325d2ea800ba5685b9ec9.png)