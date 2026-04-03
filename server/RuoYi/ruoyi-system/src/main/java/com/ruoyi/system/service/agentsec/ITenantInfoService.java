package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.TenantInfo;

public interface ITenantInfoService
{
    public List<TenantInfo> selectTenantInfoList(TenantInfo tenantInfo);
}
