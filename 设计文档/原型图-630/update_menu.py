import re

file_path = '/Users/adolf/Desktop/code/ai-security-platform-main/设计文档/原型图-630/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_nav = """            <!-- 导航菜单 -->
            <nav class="sidebar-nav" id="sidebarNav">
                <!-- 1. 安全总览 -->
                <div class="nav-item-top" data-page="pages/assets/dashboard.html" data-label="安全总览" onclick="loadPage('pages/assets/dashboard.html', '安全总览', this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <rect x="1" y="1" width="6" height="6" rx="1" fill="currentColor" opacity=".5" />
                        <rect x="9" y="1" width="6" height="6" rx="1" fill="currentColor" />
                        <rect x="1" y="9" width="6" height="6" rx="1" fill="currentColor" />
                        <rect x="9" y="9" width="6" height="6" rx="1" fill="currentColor" opacity=".5" />
                    </svg>
                    <span class="nav-label">安全总览</span>
                </div>

                <!-- 2. 风险事件 -->
                <div class="nav-parent" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <path d="M8 1L1 14h14L8 1z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
                        <path d="M8 6v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        <circle cx="8" cy="12" r="0.8" fill="currentColor" />
                    </svg>
                    <span class="nav-label">风险事件</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children">
                    <div class="nav-item" data-page="pages/events/event-list.html" data-label="风险事件" onclick="loadPage('pages/events/event-list.html', '风险事件', this)">风险事件</div>
                    <div class="nav-item" data-page="pages/monitor/trace-list.html" data-label="风险溯源" onclick="loadPage('pages/monitor/trace-list.html', '风险溯源', this)">风险溯源</div>
                </div>

                <!-- 3. 统一策略中心 -->
                <div class="nav-parent" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <path d="M8 1l2 4h4l-3 3 1 4-4-2-4 2 1-4-3-3h4z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
                    </svg>
                    <span class="nav-label">统一策略中心</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children">
                    <div class="nav-subgroup">
                        <div class="nav-sub-parent open" onclick="toggleSubNav(this)">
                            <span class="nav-sub-label">网关策略管理</span>
                            <span class="nav-sub-arrow"></span>
                        </div>
                        <div class="nav-sub-children show">
                            <div class="nav-item" data-page="pages/policy/access-control.html" data-label="访问控制策略" onclick="loadPage('pages/policy/access-control.html', '访问控制策略', this)">访问控制策略</div>
                            <div class="nav-item" data-page="pages/policy/traffic-governance.html" data-label="流量与服务治理" onclick="loadPage('pages/policy/traffic-governance.html', '流量与服务治理', this)">流量与服务治理</div>
                            <div class="nav-item" data-page="pages/policy/prompt-attack.html" data-label="提示词防护策略" onclick="loadPage('pages/policy/prompt-attack.html', '提示词防护策略', this)">提示词防护策略</div>
                            <div class="nav-item" data-page="pages/policy/session-audit.html" data-label="会话审计" onclick="loadPage('pages/policy/session-audit.html', '会话审计', this)">会话审计</div>
                            <div class="nav-item" data-page="pages/policy/gateway-distribution.html" data-label="绑定与下发" onclick="loadPage('pages/policy/gateway-distribution.html', '绑定与下发', this)">绑定与下发</div>
                        </div>
                    </div>
                    <div class="nav-subgroup">
                        <div class="nav-sub-parent open" onclick="toggleSubNav(this)">
                            <span class="nav-sub-label">探针策略管理</span>
                            <span class="nav-sub-arrow"></span>
                        </div>
                        <div class="nav-sub-children show">
                            <div class="nav-item" data-page="pages/policy/unified-protection.html" data-label="策略包管理" onclick="loadPage('pages/policy/unified-protection.html', '策略包管理', this)">策略包管理</div>
                            <div class="nav-item" data-page="pages/policy/distribution-status.html" data-label="绑定与下发" onclick="loadPage('pages/policy/distribution-status.html', '绑定与下发', this)">绑定与下发</div>
                        </div>
                    </div>
                    <div class="nav-item" data-page="pages/policy/notify-channel.html" data-label="通知渠道管理" onclick="loadPage('pages/policy/notify-channel.html', '通知渠道管理', this)">通知渠道管理</div>
                </div>

                <!-- 4. 资产中心 -->
                <div class="nav-parent open" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <rect x="1" y="2" width="14" height="3" rx="1" fill="currentColor" />
                        <rect x="1" y="7" width="14" height="3" rx="1" fill="currentColor" opacity=".6" />
                        <rect x="1" y="12" width="14" height="3" rx="1" fill="currentColor" opacity=".4" />
                    </svg>
                    <span class="nav-label">资产中心</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children show">
                    <div class="nav-item active" data-page="pages/assets/app-list.html" data-label="接入应用" onclick="loadPage('pages/assets/app-list.html', '接入应用', this)">接入应用</div>
                </div>

                <!-- 5. 安全扫描 -->
                <div class="nav-parent" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5" />
                        <path d="M8 4v4l3 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                    <span class="nav-label">安全扫描</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children">
                    <div class="nav-item" data-page="pages/scan/skills-scan.html" data-label="Skills扫描" onclick="loadPage('pages/scan/skills-scan.html', 'Skills扫描', this)">Skills扫描</div>
                    <div class="nav-item" data-page="pages/scan/mcp-scan.html" data-label="MCP协议检测" onclick="loadPage('pages/scan/mcp-scan.html', 'MCP协议检测', this)">MCP协议检测</div>
                    <div class="nav-item" data-page="pages/scan/prompt-scan.html" data-label="Prompt检测" onclick="loadPage('pages/scan/prompt-scan.html', 'Prompt检测', this)">Prompt检测</div>
                </div>

                <!-- 6. 报告中心 -->
                <div class="nav-parent" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.5" />
                        <path d="M5 5h6M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
                    </svg>
                    <span class="nav-label">报告中心</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children">
                    <div class="nav-item" data-page="pages/report/report-list.html" data-label="报告管理" onclick="loadPage('pages/report/report-list.html', '报告管理', this)">报告管理</div>
                    <div class="nav-item" data-page="pages/report/subscriptions.html" data-label="报告订阅" onclick="loadPage('pages/report/subscriptions.html', '报告订阅', this)">报告订阅</div>
                </div>

                <!-- 7. 系统管理 -->
                <div class="nav-parent" onclick="toggleNav(this)">
                    <svg class="nav-icon" viewBox="0 0 16 16" fill="none" width="16" height="16">
                        <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.5" />
                        <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.42 1.42M11.53 11.53l1.42 1.42M3.05 12.95l1.42-1.42M11.53 4.47l1.42-1.42" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
                    </svg>
                    <span class="nav-label">系统管理</span>
                    <span class="nav-arrow"></span>
                </div>
                <div class="nav-children">
                    <div class="nav-item" data-page="pages/system/user-list.html" data-label="用户与权限" onclick="loadPage('pages/system/user-list.html', '用户与权限', this)">用户与权限</div>
                    <div class="nav-item" data-page="pages/system/audit-log.html" data-label="操作审计日志" onclick="loadPage('pages/system/audit-log.html', '操作审计日志', this)">操作审计日志</div>
                    <div class="nav-item" data-page="pages/system/model-registry.html" data-label="模型注册管理" onclick="loadPage('pages/system/model-registry.html', '模型注册管理', this)">模型注册管理</div>
                    <div class="nav-item" data-page="pages/system/external-integration.html" data-label="外部集成配置" onclick="loadPage('pages/system/external-integration.html', '外部集成配置', this)">外部集成配置</div>
                </div>
            </nav>"""

pattern = re.compile(r'<!-- 导航菜单 -->.*?<nav class="sidebar-nav" id="sidebarNav">.*?</nav>', re.DOTALL)
new_content = pattern.sub(new_nav, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Menu updated successfully.")
