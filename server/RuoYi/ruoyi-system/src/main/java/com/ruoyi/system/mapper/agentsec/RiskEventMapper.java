package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.RiskEvent;

/**
 * 风险事件 Mapper
 */
public interface RiskEventMapper
{
    public List<RiskEvent> selectRiskEventList(RiskEvent riskEvent);

    public RiskEvent selectRiskEventById(String eventId);

    public int updateRiskEvent(RiskEvent riskEvent);
}
