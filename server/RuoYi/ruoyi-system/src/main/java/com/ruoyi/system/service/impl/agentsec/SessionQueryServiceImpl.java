package com.ruoyi.system.service.impl.agentsec;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.stereotype.Service;
import com.ruoyi.system.service.agentsec.ISessionQueryService;

@Service
public class SessionQueryServiceImpl implements ISessionQueryService
{
    @Override
    public Map<String, Object> selectSessionDetail(String sessionId)
    {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sessionId", sessionId);
        result.put("totalSpans", 0);
        result.put("durationMs", 0);
        result.put("riskEvents", new ArrayList<>());
        result.put("spans", new ArrayList<>());
        return result;
    }
}
