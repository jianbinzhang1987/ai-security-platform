package com.ruoyi.web.controller.agentsec;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.TenantInfo;
import com.ruoyi.system.service.agentsec.ITenantInfoService;

@RestController
@RequestMapping("/agentsec/tenant")
public class TenantController extends BaseController
{
    @Autowired
    private ITenantInfoService tenantInfoService;

    @RequiresPermissions("agentsec:tenant:list")
    @GetMapping("/list")
    public TableDataInfo list(TenantInfo tenantInfo)
    {
        startPage();
        return getDataTable(tenantInfoService.selectTenantInfoList(tenantInfo));
    }
}
