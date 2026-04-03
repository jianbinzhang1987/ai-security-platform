package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.domain.agentsec.RiskEvent;
import com.ruoyi.system.mapper.agentsec.RiskEventMapper;
import com.ruoyi.system.service.agentsec.IRiskEventService;

@Service
public class RiskEventServiceImpl implements IRiskEventService
{
    @Autowired
    private RiskEventMapper riskEventMapper;

    @Override
    public List<RiskEvent> selectRiskEventList(RiskEvent riskEvent)
    {
        return riskEventMapper.selectRiskEventList(riskEvent);
    }

    @Override
    public RiskEvent selectRiskEventById(String eventId)
    {
        return riskEventMapper.selectRiskEventById(eventId);
    }

    @Override
    public int updateRiskEvent(RiskEvent riskEvent)
    {
        return riskEventMapper.updateRiskEvent(riskEvent);
    }
}
