package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.utils.uuid.IdUtils;
import com.ruoyi.system.domain.agentsec.AgentApp;
import com.ruoyi.system.mapper.agentsec.AgentAppMapper;
import com.ruoyi.system.service.agentsec.IAgentAppService;

@Service
public class AgentAppServiceImpl implements IAgentAppService
{
    @Autowired
    private AgentAppMapper agentAppMapper;

    @Override
    public List<AgentApp> selectAgentAppList(AgentApp agentApp)
    {
        return agentAppMapper.selectAgentAppList(agentApp);
    }

    @Override
    public AgentApp selectAgentAppById(String appId)
    {
        return agentAppMapper.selectAgentAppById(appId);
    }

    @Override
    public int insertAgentApp(AgentApp agentApp)
    {
        if (agentApp.getAppId() == null || agentApp.getAppId().isEmpty())
        {
            agentApp.setAppId(IdUtils.fastSimpleUUID());
        }
        return agentAppMapper.insertAgentApp(agentApp);
    }

    @Override
    public int updateAgentApp(AgentApp agentApp)
    {
        return agentAppMapper.updateAgentApp(agentApp);
    }
}
