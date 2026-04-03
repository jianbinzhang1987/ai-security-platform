package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.domain.agentsec.TenantInfo;
import com.ruoyi.system.mapper.agentsec.TenantInfoMapper;
import com.ruoyi.system.service.agentsec.ITenantInfoService;

@Service
public class TenantInfoServiceImpl implements ITenantInfoService
{
    @Autowired
    private TenantInfoMapper tenantInfoMapper;

    @Override
    public List<TenantInfo> selectTenantInfoList(TenantInfo tenantInfo)
    {
        return tenantInfoMapper.selectTenantInfoList(tenantInfo);
    }
}
