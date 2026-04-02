-- AgentSec 管理端菜单、按钮权限与超级管理员授权脚本
-- 适配当前 RuoYi sys_menu / sys_role_menu 结构
-- 执行前请确认角色 ID=2 为超级管理员角色

START TRANSACTION;

DELETE FROM sys_role_menu WHERE menu_id BETWEEN 2000 AND 2099;
DELETE FROM sys_menu WHERE menu_id BETWEEN 2000 AND 2099;

INSERT INTO sys_menu VALUES ('2000', 'AgentSec安全监测', '0',  '10', '#',                      '', 'M', '0', '1', '',                        'fa fa-shield',          'admin', sysdate(), '', NULL, 'AgentSec 一级目录');
INSERT INTO sys_menu VALUES ('2001', '安全大盘',         '2000', '1',  '/agentsec/dashboard',   '', 'C', '0', '1', 'agentsec:dashboard:view', 'fa fa-dashboard',       'admin', sysdate(), '', NULL, '安全监测总览');
INSERT INTO sys_menu VALUES ('2002', 'Agent应用',        '2000', '2',  '/agentsec/agents',      '', 'C', '0', '1', 'agentsec:app:view',       'fa fa-cubes',           'admin', sysdate(), '', NULL, 'Agent 应用管理');
INSERT INTO sys_menu VALUES ('2003', 'Session分析',      '2000', '3',  '/agentsec/sessions',    '', 'C', '0', '1', 'agentsec:session:view',   'fa fa-random',          'admin', sysdate(), '', NULL, 'Session 调用链分析');
INSERT INTO sys_menu VALUES ('2004', 'Prompt检索',       '2000', '4',  '/agentsec/prompts',     '', 'C', '0', '1', 'agentsec:prompt:view',    'fa fa-search',          'admin', sysdate(), '', NULL, 'Prompt 全文检索');
INSERT INTO sys_menu VALUES ('2005', '安全事件',         '2000', '5',  '/agentsec/events',      '', 'C', '0', '1', 'agentsec:event:view',     'fa fa-bug',             'admin', sysdate(), '', NULL, '安全事件处置');
INSERT INTO sys_menu VALUES ('2006', '告警规则',         '2000', '6',  '/agentsec/rules',       '', 'C', '0', '1', 'agentsec:rule:view',      'fa fa-bell',            'admin', sysdate(), '', NULL, '告警规则管理');
INSERT INTO sys_menu VALUES ('2007', '安全报告',         '2000', '7',  '/agentsec/reports',     '', 'C', '0', '1', 'agentsec:report:view',    'fa fa-file-pdf-o',      'admin', sysdate(), '', NULL, '安全报告中心');
INSERT INTO sys_menu VALUES ('2008', '租户管理',         '2000', '8',  '/agentsec/tenant',      '', 'C', '0', '1', 'agentsec:tenant:view',    'fa fa-users',           'admin', sysdate(), '', NULL, '租户与配额管理');
INSERT INTO sys_menu VALUES ('2009', 'API Key管理',      '2000', '9',  '/agentsec/apiKey',      '', 'C', '0', '1', 'agentsec:apiKey:view',    'fa fa-key',             'admin', sysdate(), '', NULL, '接入凭据管理');
INSERT INTO sys_menu VALUES ('2010', '平台审计',         '2000', '10', '/agentsec/audit',       '', 'C', '0', '1', 'agentsec:audit:view',     'fa fa-list-alt',        'admin', sysdate(), '', NULL, '平台审计日志');

INSERT INTO sys_menu VALUES ('2011', '看板查询', '2001', '1', '#', '', 'F', '0', '1', 'agentsec:dashboard:view', '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2012', '应用查询', '2002', '1', '#', '', 'F', '0', '1', 'agentsec:app:list',       '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2013', '应用新增', '2002', '2', '#', '', 'F', '0', '1', 'agentsec:app:add',        '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2014', '应用修改', '2002', '3', '#', '', 'F', '0', '1', 'agentsec:app:edit',       '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2015', '应用详情', '2002', '4', '#', '', 'F', '0', '1', 'agentsec:app:query',      '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2016', '实例查询', '2002', '5', '#', '', 'F', '0', '1', 'agentsec:instance:list',  '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2017', '会话查询', '2003', '1', '#', '', 'F', '0', '1', 'agentsec:session:list',   '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2018', '会话详情', '2003', '2', '#', '', 'F', '0', '1', 'agentsec:session:query',  '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2019', 'Prompt查询', '2004', '1', '#', '', 'F', '0', '1', 'agentsec:prompt:list',   '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2020', 'Prompt检索', '2004', '2', '#', '', 'F', '0', '1', 'agentsec:prompt:search', '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2021', '事件查询', '2005', '1', '#', '', 'F', '0', '1', 'agentsec:event:list',      '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2022', '事件处置', '2005', '2', '#', '', 'F', '0', '1', 'agentsec:event:edit',      '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2023', '规则查询', '2006', '1', '#', '', 'F', '0', '1', 'agentsec:rule:list',       '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2024', '规则新增', '2006', '2', '#', '', 'F', '0', '1', 'agentsec:rule:add',        '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2025', '规则测试', '2006', '3', '#', '', 'F', '0', '1', 'agentsec:rule:test',       '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2026', '报告查询', '2007', '1', '#', '', 'F', '0', '1', 'agentsec:report:list',     '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2027', '报告生成', '2007', '2', '#', '', 'F', '0', '1', 'agentsec:report:add',      '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2028', '租户查询', '2008', '1', '#', '', 'F', '0', '1', 'agentsec:tenant:list',     '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2029', 'Key查询',  '2009', '1', '#', '', 'F', '0', '1', 'agentsec:apiKey:list',     '#', 'admin', sysdate(), '', NULL, '');
INSERT INTO sys_menu VALUES ('2030', '审计查询', '2010', '1', '#', '', 'F', '0', '1', 'agentsec:audit:list',      '#', 'admin', sysdate(), '', NULL, '');

INSERT INTO sys_role_menu VALUES ('2', '2000');
INSERT INTO sys_role_menu VALUES ('2', '2001');
INSERT INTO sys_role_menu VALUES ('2', '2002');
INSERT INTO sys_role_menu VALUES ('2', '2003');
INSERT INTO sys_role_menu VALUES ('2', '2004');
INSERT INTO sys_role_menu VALUES ('2', '2005');
INSERT INTO sys_role_menu VALUES ('2', '2006');
INSERT INTO sys_role_menu VALUES ('2', '2007');
INSERT INTO sys_role_menu VALUES ('2', '2008');
INSERT INTO sys_role_menu VALUES ('2', '2009');
INSERT INTO sys_role_menu VALUES ('2', '2010');
INSERT INTO sys_role_menu VALUES ('2', '2011');
INSERT INTO sys_role_menu VALUES ('2', '2012');
INSERT INTO sys_role_menu VALUES ('2', '2013');
INSERT INTO sys_role_menu VALUES ('2', '2014');
INSERT INTO sys_role_menu VALUES ('2', '2015');
INSERT INTO sys_role_menu VALUES ('2', '2016');
INSERT INTO sys_role_menu VALUES ('2', '2017');
INSERT INTO sys_role_menu VALUES ('2', '2018');
INSERT INTO sys_role_menu VALUES ('2', '2019');
INSERT INTO sys_role_menu VALUES ('2', '2020');
INSERT INTO sys_role_menu VALUES ('2', '2021');
INSERT INTO sys_role_menu VALUES ('2', '2022');
INSERT INTO sys_role_menu VALUES ('2', '2023');
INSERT INTO sys_role_menu VALUES ('2', '2024');
INSERT INTO sys_role_menu VALUES ('2', '2025');
INSERT INTO sys_role_menu VALUES ('2', '2026');
INSERT INTO sys_role_menu VALUES ('2', '2027');
INSERT INTO sys_role_menu VALUES ('2', '2028');
INSERT INTO sys_role_menu VALUES ('2', '2029');
INSERT INTO sys_role_menu VALUES ('2', '2030');

COMMIT;
