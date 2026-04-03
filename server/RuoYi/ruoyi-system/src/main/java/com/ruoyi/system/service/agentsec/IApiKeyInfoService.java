package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.ApiKeyInfo;

public interface IApiKeyInfoService
{
    public List<ApiKeyInfo> selectApiKeyInfoList(ApiKeyInfo apiKeyInfo);
}
