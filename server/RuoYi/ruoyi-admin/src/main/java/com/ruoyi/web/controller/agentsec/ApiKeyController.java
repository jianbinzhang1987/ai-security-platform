package com.ruoyi.web.controller.agentsec;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.ApiKeyInfo;
import com.ruoyi.system.service.agentsec.IApiKeyInfoService;

@RestController
@RequestMapping("/agentsec/apiKey")
public class ApiKeyController extends BaseController
{
    @Autowired
    private IApiKeyInfoService apiKeyInfoService;

    @RequiresPermissions("agentsec:apiKey:list")
    @GetMapping("/list")
    public TableDataInfo list(ApiKeyInfo apiKeyInfo)
    {
        startPage();
        return getDataTable(apiKeyInfoService.selectApiKeyInfoList(apiKeyInfo));
    }
}
