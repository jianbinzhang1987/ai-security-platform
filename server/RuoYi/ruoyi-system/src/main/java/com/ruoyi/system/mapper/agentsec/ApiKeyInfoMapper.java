package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.ApiKeyInfo;

public interface ApiKeyInfoMapper
{
    public List<ApiKeyInfo> selectApiKeyInfoList(ApiKeyInfo apiKeyInfo);
}
