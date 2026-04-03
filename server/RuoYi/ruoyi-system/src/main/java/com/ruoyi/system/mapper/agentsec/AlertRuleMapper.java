package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.AlertRule;

/**
 * 告警规则 Mapper
 */
public interface AlertRuleMapper
{
    public List<AlertRule> selectAlertRuleList(AlertRule alertRule);

    public AlertRule selectAlertRuleById(String ruleId);

    public int insertAlertRule(AlertRule alertRule);

    public int updateAlertRule(AlertRule alertRule);
}
