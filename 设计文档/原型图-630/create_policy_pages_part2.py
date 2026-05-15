import os

base_dir = '/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/policy'

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
        <button class="btn btn-primary" onclick="toastSuccess('操作成功')">{btn_text}</button>
      </div>
    </div>

    <div class="search-bar">
      <div class="search-item">
        <span class="form-label">关键字：</span>
        <input type="text" class="form-control" placeholder="请输入...">
      </div>
      <div class="search-btns">
        <button class="btn btn-primary" onclick="toastSuccess('刷新成功')">查询</button>
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
        {{ label: '统一策略中心' }},
        {{ label: '{title}' }}
      ]);
    }}
  </script>
</body>
</html>
"""

pages = [
    {
        "filename": "traffic-governance.html",
        "title": "流量与服务治理",
        "subtitle": "管理模型路由、超时熔断、负载均衡等网关基础治理策略。",
        "btn_text": "新建治理规则",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>规则名称</th><th>目标路由</th><th>治理类型</th><th>策略详情</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>OpenAI备用容灾</td><td>/v1/chat/completions</td><td>熔断降级</td><td>失败率>50%时切换备用模型</td><td><span class="tag tag-success">启用</span></td><td><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "session-audit.html",
        "title": "会话审计",
        "subtitle": "针对敏感高价值业务的独立会话审计与录入策略配置。",
        "btn_text": "新建审计规则",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>审计规则名称</th><th>匹配应用</th><th>保存时长</th><th>审计强度</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>财务助手全局审计</td><td>app_finance_audit</td><td>180天</td><td><span class="tag tag-danger">强审计(100%)</span></td><td><span class="tag tag-success">启用</span></td><td><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "gateway-distribution.html",
        "title": "网关策略下发",
        "subtitle": "管理网关策略组合与模型路由的发布、灰度与下发状态。",
        "btn_text": "新建发布单",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>发布单名称</th><th>目标网关组</th><th>版本号</th><th>发布状态</th><th>更新时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>生产环境全量发布</td><td>Prod-Cluster-1</td><td>v2.1.4</td><td><span class="tag tag-success">发布成功</span></td><td>2026-05-13 14:00:00</td><td><button class="btn btn-link">回滚</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "distribution-status.html",
        "title": "探针策略下发",
        "subtitle": "管理端侧探针(SDK)的策略包下发与应用绑定。",
        "btn_text": "新建下发任务",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>应用名称</th><th>App ID</th><th>目标策略包</th><th>下发版本</th><th>下发状态</th><th>最后同步</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>智能客服 Copilot</td><td>app_copilot_service</td><td>基础安全包</td><td>v3.1.0</td><td><span class="tag tag-success">已同步</span></td><td>2026-05-13 14:00:00</td><td><button class="btn btn-link">变更绑定</button></td></tr>
          </tbody>
        </table>
        """
    }
]

for page in pages:
    file_path = os.path.join(base_dir, page["filename"])
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_template.format(**page))
    print(f"Created {file_path}")

