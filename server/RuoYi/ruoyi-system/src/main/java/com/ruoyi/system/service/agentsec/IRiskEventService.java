package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.RiskEvent;

public interface IRiskEventService
{
    public List<RiskEvent> selectRiskEventList(RiskEvent riskEvent);

    public RiskEvent selectRiskEventById(String eventId);

    public int updateRiskEvent(RiskEvent riskEvent);
}
