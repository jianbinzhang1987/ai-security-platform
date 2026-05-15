import os

files_to_create = [
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/assets/dashboard.html",
        "title": "安全总览",
        "subtitle": "提供全局视角的资产运行状态、风险拦截与趋势统计大盘。",
        "btn_text": "刷新看板",
        "table_content": """
        <div class="stat-cards" style="margin-bottom:20px;">
          <div class="stat-card">
            <div class="stat-card-label">总接入应用</div>
            <div class="stat-card-value blue">132</div>
            <div class="stat-card-footer">较上周 +4</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-label">近24小时告警</div>
            <div class="stat-card-value orange">58</div>
            <div class="stat-card-footer">高危 12</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-label">成功阻断次数</div>
            <div class="stat-card-value green">214</div>
            <div class="stat-card-footer">拦截率 100%</div>
          </div>
        </div>
        <div style="background:#f5f7fa; padding:40px; text-align:center; color:#909399; border-radius:8px; border: 1px dashed #dcdfe6; margin-bottom: 20px;">
          [ 数据趋势折线图占位区: 显示过去30天的拦截和告警趋势 ]
        </div>
        <h3 style="margin-bottom:12px; font-size:16px; color:#303133;">最新高风险事件</h3>
        <table class="data-table">
          <thead><tr><th>发生时间</th><th>风险类型</th><th>应用</th><th>风险等级</th><th>动作</th></tr></thead>
          <tbody>
            <tr><td>2026-05-13 14:00</td><td>工具越权调用</td><td>智能客服 Copilot</td><td><span class="tag tag-danger">极高风险</span></td><td><span class="tag tag-danger">阻断</span></td></tr>
            <tr><td>2026-05-13 13:20</td><td>敏感数据输出</td><td>财务小助手</td><td><span class="tag tag-warning">高风险</span></td><td><span class="tag tag-info">告警</span></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/report/report-list.html",
        "title": "报告管理",
        "subtitle": "查看和下载由系统定期生成或手动触发的安全运营分析报告。",
        "btn_text": "生成即时报告",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>报告名称</th><th>报告类型</th><th>生成周期</th><th>生成时间</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>全局安全态势月报_202604</td><td>安全态势</td><td>月度</td><td>2026-05-01 08:00:00</td><td><span class="tag tag-success">已生成</span></td><td><button class="btn btn-link">预览</button><button class="btn btn-link">下载PDF</button></td></tr>
            <tr><td>2</td><td>智能客服安全周报</td><td>应用专属</td><td>周度</td><td>2026-05-11 08:00:00</td><td><span class="tag tag-success">已生成</span></td><td><button class="btn btn-link">预览</button><button class="btn btn-link">下载PDF</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/report/subscriptions.html",
        "title": "报告订阅",
        "subtitle": "配置定期生成的报告模板、发送周期以及邮件/Webhook接收方。",
        "btn_text": "新建订阅任务",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>任务名称</th><th>报告模板</th><th>发送周期</th><th>收件人/渠道</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>每周应用合规巡检推报</td><td>应用合规基线</td><td>每周一 09:00</td><td>security-team@example.com</td><td><span class="tag tag-success">运行中</span></td><td><button class="btn btn-link">执行记录</button><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/system/user-list.html",
        "title": "用户与权限",
        "subtitle": "管理控制台的登录账号、部门组织架构及基于 RBAC 的访问角色。",
        "btn_text": "新增用户",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>账号</th><th>姓名</th><th>部门</th><th>角色</th><th>状态</th><th>最后登录时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>admin</td><td>系统管理员</td><td>安全部</td><td>超级管理员</td><td><span class="tag tag-success">正常</span></td><td>2026-05-13 10:00:00</td><td><button class="btn btn-link">分配角色</button></td></tr>
            <tr><td>2</td><td>zhoumin</td><td>周敏</td><td>客服中心</td><td>应用管理员</td><td><span class="tag tag-success">正常</span></td><td>2026-05-13 14:15:00</td><td><button class="btn btn-link">分配角色</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/system/audit-log.html",
        "title": "操作审计日志",
        "subtitle": "记录管理控制台内的所有高敏感配置变更及数据访问操作，满足等保合规要求。",
        "btn_text": "导出日志",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>操作时间</th><th>操作人</th><th>操作IP</th><th>功能模块</th><th>操作内容</th><th>结果</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>2026-05-13 14:02:11</td><td>admin</td><td>10.0.1.5</td><td>策略包管理</td><td>发布新版本 v3.1.0</td><td><span class="tag tag-success">成功</span></td><td><button class="btn btn-link">详情</button></td></tr>
            <tr><td>2</td><td>2026-05-13 13:45:00</td><td>zhang_sec</td><td>10.0.2.11</td><td>风险事件</td><td>对 EVT-001 进行处置登记</td><td><span class="tag tag-success">成功</span></td><td><button class="btn btn-link">详情</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/system/model-registry.html",
        "title": "模型注册管理",
        "subtitle": "登记企业正在使用的大模型服务（LLM/Embeddings），供策略网关进行路由和容灾调度。",
        "btn_text": "注册新模型",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>模型别名</th><th>提供方</th><th>Endpoint</th><th>状态</th><th>关联策略</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>GPT-4-Turbo</td><td>OpenAI</td><td>https://api.openai.com/...</td><td><span class="tag tag-success">健康</span></td><td>3个路由</td><td><button class="btn btn-link">编辑</button></td></tr>
            <tr><td>2</td><td>Qwen-Max-Local</td><td>自研部署</td><td>http://10.20.1.1:8000/v1</td><td><span class="tag tag-warning">高延迟</span></td><td>备用容灾</td><td><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "path": "/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/system/external-integration.html",
        "title": "外部集成配置",
        "subtitle": "管理与企业现有 IT 设施（如 LDAP、SSO、SIEM/SOC系统）的集成对接参数。",
        "btn_text": "添加集成项",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>集成类型</th><th>集成名称</th><th>状态</th><th>最后同步/调用</th><th>说明</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>SSO 登录</td><td>公司内网 OAuth2 认证</td><td><span class="tag tag-success">已启用</span></td><td>2026-05-13 15:00</td><td>允许员工使用内网账号一键登录控制台</td><td><button class="btn btn-link">配置</button><button class="btn btn-link danger">停用</button></td></tr>
            <tr><td>SIEM 对接</td><td>日志推送到 Splunk</td><td><span class="tag tag-info">未启用</span></td><td>-</td><td>将告警事件以 Syslog/Webhook 形式转发至安全运营中心</td><td><button class="btn btn-link">配置</button></td></tr>
          </tbody>
        </table>
        """
    }
]

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body class="page-content">
  <div class="sub-page">
    <div class="page-header">
      <div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-primary" onclick="toastSuccess('操作触发')">{btn_text}</button>
      </div>
    </div>

    <!-- 简化版搜索区 -->
    <div class="search-bar">
      <div class="search-item">
        <span class="form-label">关键字检索：</span>
        <input type="text" class="form-control" placeholder="请输入...">
      </div>
      <div class="search-btns">
        <button class="btn btn-primary" onclick="toastSuccess('数据刷新完毕')">查询</button>
        <button class="btn btn-default">重置</button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrapper">
        {table_content}
      </div>
    </div>
  </div>
  <script src="../../js/common.js"></script>
  <script>
    if (typeof updateBreadcrumb === 'function') {{
      updateBreadcrumb([
        {{ label: '控制台菜单' }},
        {{ label: '{title}' }}
      ]);
    }}
  </script>
</body>
</html>
"""

for page in files_to_create:
    os.makedirs(os.path.dirname(page["path"]), exist_ok=True)
    with open(page["path"], "w", encoding="utf-8") as f:
        f.write(html_template.format(**page))
    print(f"Created {page['path']}")

