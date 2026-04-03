package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.utils.uuid.IdUtils;
import com.ruoyi.system.domain.agentsec.AlertRule;
import com.ruoyi.system.mapper.agentsec.AlertRuleMapper;
import com.ruoyi.system.service.agentsec.IAlertRuleService;

@Service
public class AlertRuleServiceImpl implements IAlertRuleService
{
    @Autowired
    private AlertRuleMapper alertRuleMapper;

    @Override
    public List<AlertRule> selectAlertRuleList(AlertRule alertRule)
    {
        return alertRuleMapper.selectAlertRuleList(alertRule);
    }

    @Override
    public AlertRule selectAlertRuleById(String ruleId)
    {
        return alertRuleMapper.selectAlertRuleById(ruleId);
    }

    @Override
    public int insertAlertRule(AlertRule alertRule)
    {
        if (alertRule.getRuleId() == null || alertRule.getRuleId().isEmpty())
        {
            alertRule.setRuleId(IdUtils.fastSimpleUUID());
        }
        return alertRuleMapper.insertAlertRule(alertRule);
    }

    @Override
    public int updateAlertRule(AlertRule alertRule)
    {
        return alertRuleMapper.updateAlertRule(alertRule);
    }
}
