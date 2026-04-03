package com.ruoyi.system.service.agentsec;

import java.util.Map;

public interface ISessionQueryService
{
    public Map<String, Object> selectSessionDetail(String sessionId);
}
