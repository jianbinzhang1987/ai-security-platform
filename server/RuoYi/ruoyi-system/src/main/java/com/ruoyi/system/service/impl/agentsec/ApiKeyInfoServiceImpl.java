package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.domain.agentsec.ApiKeyInfo;
import com.ruoyi.system.mapper.agentsec.ApiKeyInfoMapper;
import com.ruoyi.system.service.agentsec.IApiKeyInfoService;

@Service
public class ApiKeyInfoServiceImpl implements IApiKeyInfoService
{
    @Autowired
    private ApiKeyInfoMapper apiKeyInfoMapper;

    @Override
    public List<ApiKeyInfo> selectApiKeyInfoList(ApiKeyInfo apiKeyInfo)
    {
        return apiKeyInfoMapper.selectApiKeyInfoList(apiKeyInfo);
    }
}
