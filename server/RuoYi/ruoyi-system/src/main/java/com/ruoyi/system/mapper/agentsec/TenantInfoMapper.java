package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.TenantInfo;

public interface TenantInfoMapper
{
    public List<TenantInfo> selectTenantInfoList(TenantInfo tenantInfo);
}
