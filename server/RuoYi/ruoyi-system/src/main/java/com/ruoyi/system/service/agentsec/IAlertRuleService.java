package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.AlertRule;

public interface IAlertRuleService
{
    public List<AlertRule> selectAlertRuleList(AlertRule alertRule);

    public AlertRule selectAlertRuleById(String ruleId);

    public int insertAlertRule(AlertRule alertRule);

    public int updateAlertRule(AlertRule alertRule);
}
