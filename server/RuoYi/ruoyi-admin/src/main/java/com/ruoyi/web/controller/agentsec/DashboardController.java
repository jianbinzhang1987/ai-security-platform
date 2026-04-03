package com.ruoyi.web.controller.agentsec;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.domain.AjaxResult;

@RestController
@RequestMapping("/agentsec/dashboard")
public class DashboardController
{
    @RequiresPermissions("agentsec:dashboard:view")
    @GetMapping("/summary")
    public AjaxResult summary()
    {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("appCount", 0);
        data.put("eventCount", 0);
        data.put("criticalCount", 0);
        data.put("blockedCount", 0);
        return AjaxResult.success(data);
    }

    @RequiresPermissions("agentsec:dashboard:view")
    @GetMapping("/timeseries")
    public AjaxResult timeseries()
    {
        return AjaxResult.success(new ArrayList<>());
    }
}
