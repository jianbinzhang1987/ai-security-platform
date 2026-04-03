package com.ruoyi.web.controller.agentsec;

import java.util.Collections;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.service.agentsec.ISessionQueryService;

@RestController
@RequestMapping("/agentsec/session")
public class SessionController extends BaseController
{
    @Autowired
    private ISessionQueryService sessionQueryService;

    @RequiresPermissions("agentsec:session:list")
    @GetMapping("/list")
    public TableDataInfo list()
    {
        startPage();
        return getDataTable(Collections.emptyList());
    }

    @RequiresPermissions("agentsec:session:query")
    @GetMapping("/{sessionId}")
    public AjaxResult getInfo(@PathVariable String sessionId)
    {
        return AjaxResult.success(sessionQueryService.selectSessionDetail(sessionId));
    }
}
