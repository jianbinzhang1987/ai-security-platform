import os

base_dir = '/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/pages/policy'
os.makedirs(base_dir, exist_ok=True)

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
        "filename": "access-control.html",
        "title": "访问控制策略",
        "subtitle": "管理模型 API 网关的 IP 黑白名单、身份鉴权与并发限制策略。",
        "btn_text": "新建访问控制",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>策略名称</th><th>规则类型</th><th>匹配对象</th><th>动作</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>测试环境内网访问</td><td>IP 白名单</td><td>192.168.*.*</td><td><span class="tag tag-success">放行</span></td><td><span class="tag tag-success">启用</span></td><td><button class="btn btn-link">编辑</button></td></tr>
            <tr><td>2</td><td>异常请求拦截</td><td>并发控制</td><td>>100qps</td><td><span class="tag tag-warning">限流</span></td><td><span class="tag tag-success">启用</span></td><td><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "prompt-attack.html",
        "title": "提示词防护策略",
        "subtitle": "配置大模型输入输出护栏，包括敏感词、正则过滤、LLM语义判别等。",
        "btn_text": "新建护栏策略",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>护栏策略名称</th><th>生效阶段</th><th>检测类型</th><th>动作</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>禁止政治敏感话题</td><td><span class="tag tag-warning">Input(Prompt)</span></td><td>LLM 评分</td><td><span class="tag tag-danger">阻断</span></td><td><input type="checkbox" checked disabled></td><td><button class="btn btn-link">编辑</button></td></tr>
            <tr><td>2</td><td>拦截竞品名称输出</td><td><span class="tag tag-success">Output(Response)</span></td><td>正则匹配</td><td><span class="tag tag-danger">阻断</span></td><td><input type="checkbox" checked disabled></td><td><button class="btn btn-link">编辑</button></td></tr>
            <tr><td>3</td><td>内网IP探测行为</td><td><span class="tag tag-warning">Input(Prompt)</span></td><td>语义相似度</td><td><span class="tag tag-info">仅告警</span></td><td><input type="checkbox" disabled></td><td><button class="btn btn-link">编辑</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "unified-protection.html",
        "title": "策略包管理",
        "subtitle": "对安全策略、防护基线和检测规则集进行版本化打包管理。",
        "btn_text": "创建策略包",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>策略包名称</th><th>当前版本</th><th>包含规则数</th><th>绑定应用数</th><th>状态</th><th>更新时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>基础安全包</td><td>v3.1.0</td><td>125</td><td>8</td><td><span class="tag tag-success">已发布</span></td><td>2026-05-13 10:00:00</td><td><button class="btn btn-link">版本管理</button></td></tr>
            <tr><td>2</td><td>增强审计包</td><td>v2.0.0</td><td>48</td><td>3</td><td><span class="tag tag-success">已发布</span></td><td>2026-05-12 11:30:00</td><td><button class="btn btn-link">版本管理</button></td></tr>
          </tbody>
        </table>
        """
    },
    {
        "filename": "notify-channel.html",
        "title": "通知渠道管理",
        "subtitle": "配置并管理风险告警和事件分发渠道，如 Webhook、钉钉、飞书、邮件等。",
        "btn_text": "新增通知渠道",
        "table_content": """
        <table class="data-table">
          <thead><tr><th>序号</th><th>渠道名称</th><th>渠道类型</th><th>目标地址/群组</th><th>触发条件</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>安全团队飞书群</td><td>飞书机器人</td><td>https://open.feishu.cn/open-apis/bot/v2/...</td><td>高危风险、阻断事件</td><td><span class="tag tag-success">正常</span></td><td><button class="btn btn-link">测试连通性</button><button class="btn btn-link">编辑</button></td></tr>
            <tr><td>2</td><td>SOC 告警邮箱</td><td>邮件</td><td>soc-alert@example.com</td><td>极高风险</td><td><span class="tag tag-success">正常</span></td><td><button class="btn btn-link">测试连通性</button><button class="btn btn-link">编辑</button></td></tr>
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

