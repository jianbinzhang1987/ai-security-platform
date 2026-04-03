package com.ruoyi.web.controller.agentsec;

import java.util.Collections;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.page.TableDataInfo;

@RestController
@RequestMapping("/agentsec/audit")
public class AuditController extends BaseController
{
    @RequiresPermissions("agentsec:audit:list")
    @GetMapping("/list")
    public TableDataInfo list()
    {
        startPage();
        return getDataTable(Collections.emptyList());
    }
}
