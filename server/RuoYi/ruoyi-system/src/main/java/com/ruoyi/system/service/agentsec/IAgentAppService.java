package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.AgentApp;

public interface IAgentAppService
{
    public List<AgentApp> selectAgentAppList(AgentApp agentApp);

    public AgentApp selectAgentAppById(String appId);

    public int insertAgentApp(AgentApp agentApp);

    public int updateAgentApp(AgentApp agentApp);
}
