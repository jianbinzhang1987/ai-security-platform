-- AgentSec 管理端业务表初始化脚本
-- 适配 RuoYi 管理端扩展场景，使用独立业务表前缀避免与若依内置表冲突

DROP TABLE IF EXISTS agentsec_api_key;
DROP TABLE IF EXISTS agentsec_security_report;
DROP TABLE IF EXISTS agentsec_notification_channel;
DROP TABLE IF EXISTS agentsec_block_log;
DROP TABLE IF EXISTS agentsec_alert_rule;
DROP TABLE IF EXISTS agentsec_risk_event;
DROP TABLE IF EXISTS agentsec_app_token;
DROP TABLE IF EXISTS agentsec_agent_instance;
DROP TABLE IF EXISTS agentsec_agent_app;
DROP TABLE IF EXISTS agentsec_tenant;

CREATE TABLE agentsec_tenant (
    tenant_id              VARCHAR(36)  NOT NULL COMMENT '租户ID',
    tenant_name            VARCHAR(100) NOT NULL COMMENT '租户名称',
    plan_code              VARCHAR(20)  NOT NULL DEFAULT 'basic' COMMENT '套餐编码',
    max_agents             INT          NOT NULL DEFAULT 10 COMMENT '最大Agent数',
    data_retention_days    INT          NOT NULL DEFAULT 30 COMMENT '数据保留天数',
    status                 CHAR(1)      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    create_by              VARCHAR(64)  DEFAULT '' COMMENT '创建者',
    create_time            DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)  DEFAULT '' COMMENT '更新者',
    update_time            DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500) DEFAULT '' COMMENT '备注',
    PRIMARY KEY (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AgentSec租户表';

CREATE TABLE agentsec_agent_app (
    app_id                 VARCHAR(36)  NOT NULL COMMENT '应用ID',
    tenant_id              VARCHAR(36)  NOT NULL COMMENT '租户ID',
    app_name               VARCHAR(100) NOT NULL COMMENT '应用名称',
    status                 CHAR(1)      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    token_status           CHAR(1)      NOT NULL DEFAULT '0' COMMENT 'Token状态（0有效 1失效）',
    sdk_version            VARCHAR(50)  DEFAULT '' COMMENT 'SDK版本',
    description            VARCHAR(500) DEFAULT '' COMMENT '描述',
    create_by              VARCHAR(64)  DEFAULT '' COMMENT '创建者',
    create_time            DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)  DEFAULT '' COMMENT '更新者',
    update_time            DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500) DEFAULT '' COMMENT '备注',
    PRIMARY KEY (app_id),
    KEY idx_agentsec_app_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent应用表';

CREATE TABLE agentsec_agent_instance (
    instance_id            VARCHAR(36)  NOT NULL COMMENT '实例ID',
    app_id                 VARCHAR(36)  NOT NULL COMMENT '应用ID',
    host_name              VARCHAR(100) DEFAULT '' COMMENT '主机名',
    ip_address             VARCHAR(64)  DEFAULT '' COMMENT 'IP地址',
    status                 CHAR(1)      NOT NULL DEFAULT '0' COMMENT '状态（0在线 1离线）',
    create_time            DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time            DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (instance_id),
    KEY idx_agentsec_instance_app (app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent实例表';

CREATE TABLE agentsec_app_token (
    token_id               VARCHAR(36)  NOT NULL COMMENT 'Token ID',
    app_id                 VARCHAR(36)  NOT NULL COMMENT '应用ID',
    token_name             VARCHAR(100) NOT NULL COMMENT 'Token名称',
    token_hash             VARCHAR(128) NOT NULL COMMENT 'Token哈希',
    status                 CHAR(1)      NOT NULL DEFAULT '0' COMMENT '状态（0有效 1失效）',
    create_by              VARCHAR(64)  DEFAULT '' COMMENT '创建者',
    create_time            DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)  DEFAULT '' COMMENT '更新者',
    update_time            DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500) DEFAULT '' COMMENT '备注',
    PRIMARY KEY (token_id),
    KEY idx_agentsec_token_app (app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用Token表';

CREATE TABLE agentsec_risk_event (
    event_id               VARCHAR(36)   NOT NULL COMMENT '风险事件ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    app_id                 VARCHAR(36)   NOT NULL COMMENT '应用ID',
    session_id             VARCHAR(64)   DEFAULT '' COMMENT '会话ID',
    span_id                VARCHAR(64)   DEFAULT '' COMMENT 'Span ID',
    risk_type              VARCHAR(50)   DEFAULT '' COMMENT '风险类型',
    risk_level             VARCHAR(20)   DEFAULT '' COMMENT '风险等级',
    confidence             DECIMAL(5,4)  DEFAULT NULL COMMENT '置信度',
    evidence               TEXT          COMMENT '证据JSON',
    explanation            VARCHAR(1000) DEFAULT '' COMMENT '解释',
    status                 VARCHAR(20)   NOT NULL DEFAULT 'new' COMMENT '事件状态',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (event_id),
    KEY idx_agentsec_event_app (app_id),
    KEY idx_agentsec_event_session (session_id),
    KEY idx_agentsec_event_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='风险事件表';

CREATE TABLE agentsec_alert_rule (
    rule_id                VARCHAR(36)   NOT NULL COMMENT '规则ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    rule_name              VARCHAR(100)  NOT NULL COMMENT '规则名称',
    risk_level             VARCHAR(20)   DEFAULT '' COMMENT '规则目标等级',
    status                 CHAR(1)       NOT NULL DEFAULT '0' COMMENT '状态（0启用 1停用）',
    condition_json         TEXT          COMMENT '规则条件JSON',
    action_json            TEXT          COMMENT '动作配置JSON',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (rule_id),
    KEY idx_agentsec_rule_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则表';

CREATE TABLE agentsec_block_log (
    block_log_id           VARCHAR(36)   NOT NULL COMMENT '阻断日志ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    target_type            VARCHAR(20)   NOT NULL COMMENT '目标类型',
    target_id              VARCHAR(64)   NOT NULL COMMENT '目标ID',
    reason                 VARCHAR(1000) DEFAULT '' COMMENT '阻断原因',
    status                 CHAR(1)       NOT NULL DEFAULT '0' COMMENT '状态（0成功 1失败）',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (block_log_id),
    KEY idx_agentsec_block_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='阻断日志表';

CREATE TABLE agentsec_notification_channel (
    channel_id             VARCHAR(36)   NOT NULL COMMENT '渠道ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    channel_name           VARCHAR(100)  NOT NULL COMMENT '渠道名称',
    channel_type           VARCHAR(30)   NOT NULL COMMENT '渠道类型',
    status                 CHAR(1)       NOT NULL DEFAULT '0' COMMENT '状态（0启用 1停用）',
    config_json            TEXT          COMMENT '配置JSON',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (channel_id),
    KEY idx_agentsec_channel_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知渠道表';

CREATE TABLE agentsec_security_report (
    report_id              VARCHAR(36)   NOT NULL COMMENT '报告ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    report_name            VARCHAR(100)  NOT NULL COMMENT '报告名称',
    report_type            VARCHAR(30)   NOT NULL COMMENT '报告类型',
    status                 CHAR(1)       NOT NULL DEFAULT '0' COMMENT '状态（0生成中 1完成 2失败）',
    file_url               VARCHAR(500)  DEFAULT '' COMMENT '文件地址',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (report_id),
    KEY idx_agentsec_report_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安全报告表';

CREATE TABLE agentsec_api_key (
    api_key_id             VARCHAR(36)   NOT NULL COMMENT 'API Key ID',
    tenant_id              VARCHAR(36)   NOT NULL COMMENT '租户ID',
    app_id                 VARCHAR(36)   DEFAULT '' COMMENT '关联应用ID',
    api_key_name           VARCHAR(100)  NOT NULL COMMENT 'Key名称',
    api_key_hash           VARCHAR(128)  NOT NULL COMMENT 'Key哈希',
    status                 CHAR(1)       NOT NULL DEFAULT '0' COMMENT '状态（0有效 1失效）',
    expire_time            DATETIME      DEFAULT NULL COMMENT '过期时间',
    create_by              VARCHAR(64)   DEFAULT '' COMMENT '创建者',
    create_time            DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by              VARCHAR(64)   DEFAULT '' COMMENT '更新者',
    update_time            DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                 VARCHAR(500)  DEFAULT '' COMMENT '备注',
    PRIMARY KEY (api_key_id),
    KEY idx_agentsec_apikey_tenant (tenant_id),
    KEY idx_agentsec_apikey_app (app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API Key表';

INSERT INTO agentsec_tenant (tenant_id, tenant_name, plan_code, max_agents, data_retention_days, status, create_by, remark)
VALUES
('tenant_demo_001', '演示租户', 'enterprise', 200, 180, '0', 'admin', '初始化演示租户');

INSERT INTO agentsec_agent_app (app_id, tenant_id, app_name, status, token_status, sdk_version, description, create_by)
VALUES
('app_demo_001', 'tenant_demo_001', '客服智能体', '0', '0', '0.1.0', '用于演示的Agent应用', 'admin'),
('app_demo_002', 'tenant_demo_001', '运营Copilot', '0', '0', '0.1.0', '运营辅助智能体', 'admin');

INSERT INTO agentsec_api_key (api_key_id, tenant_id, app_id, api_key_name, api_key_hash, status, expire_time, create_by)
VALUES
('key_demo_001', 'tenant_demo_001', 'app_demo_001', '客服环境Key', 'hashed_demo_key_001', '0', DATE_ADD(NOW(), INTERVAL 90 DAY), 'admin');

INSERT INTO agentsec_alert_rule (rule_id, tenant_id, rule_name, risk_level, status, condition_json, action_json, create_by)
VALUES
('rule_demo_001', 'tenant_demo_001', '高危Prompt注入告警', 'high', '0', '{"riskType":"prompt_injection","riskLevel":"high"}', '{"notify":["feishu"],"block":true}', 'admin');

INSERT INTO agentsec_risk_event (event_id, tenant_id, app_id, session_id, span_id, risk_type, risk_level, confidence, evidence, explanation, status, create_by)
VALUES
('event_demo_001', 'tenant_demo_001', 'app_demo_001', 'sess_demo_001', 'span_demo_001', 'prompt_injection', 'high', 0.9200, '{"matchedPattern":"忽略之前的指令"}', '检测到疑似Prompt注入行为', 'new', 'system');

INSERT INTO agentsec_block_log (block_log_id, tenant_id, target_type, target_id, reason, status, create_by)
VALUES
('block_demo_001', 'tenant_demo_001', 'session', 'sess_demo_001', '命中高危规则自动阻断', '0', 'system');

INSERT INTO agentsec_notification_channel (channel_id, tenant_id, channel_name, channel_type, status, config_json, create_by)
VALUES
('channel_demo_001', 'tenant_demo_001', '飞书安全群', 'feishu', '0', '{"webhook":"https://example.invalid/webhook"}', 'admin');

INSERT INTO agentsec_security_report (report_id, tenant_id, report_name, report_type, status, file_url, create_by)
VALUES
('report_demo_001', 'tenant_demo_001', '2026年03月安全周报', 'weekly', '1', '/reports/2026-03-weekly.pdf', 'admin');
