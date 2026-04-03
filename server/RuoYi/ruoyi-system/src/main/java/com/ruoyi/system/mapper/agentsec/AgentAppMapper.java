package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.AgentApp;

/**
 * Agent 应用 Mapper
 */
public interface AgentAppMapper
{
    public List<AgentApp> selectAgentAppList(AgentApp agentApp);

    public AgentApp selectAgentAppById(String appId);

    public int insertAgentApp(AgentApp agentApp);

    public int updateAgentApp(AgentApp agentApp);
}
