package com.ruoyi.web.controller.agentsec;

import java.util.Collections;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.AgentInstance;

@RestController
@RequestMapping("/agentsec/instance")
public class AgentInstanceController extends BaseController
{
    @RequiresPermissions("agentsec:instance:list")
    @GetMapping("/list")
    public TableDataInfo list(AgentInstance agentInstance)
    {
        startPage();
        return getDataTable(Collections.emptyList());
    }
}
