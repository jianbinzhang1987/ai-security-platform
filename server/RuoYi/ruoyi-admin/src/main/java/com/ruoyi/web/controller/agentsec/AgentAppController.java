package com.ruoyi.web.controller.agentsec;

import java.util.List;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.AgentApp;
import com.ruoyi.system.service.agentsec.IAgentAppService;

@RestController
@RequestMapping("/agentsec/app")
public class AgentAppController extends BaseController
{
    @Autowired
    private IAgentAppService agentAppService;

    @RequiresPermissions("agentsec:app:list")
    @GetMapping("/list")
    public TableDataInfo list(AgentApp agentApp)
    {
        startPage();
        List<AgentApp> list = agentAppService.selectAgentAppList(agentApp);
        return getDataTable(list);
    }

    @RequiresPermissions("agentsec:app:query")
    @GetMapping("/{appId}")
    public AjaxResult getInfo(@PathVariable String appId)
    {
        return AjaxResult.success(agentAppService.selectAgentAppById(appId));
    }

    @RequiresPermissions("agentsec:app:add")
    @PostMapping
    public AjaxResult add(@RequestBody AgentApp agentApp)
    {
        agentApp.setCreateBy(getLoginName());
        return toAjax(agentAppService.insertAgentApp(agentApp));
    }

    @RequiresPermissions("agentsec:app:edit")
    @PutMapping("/config/{appId}")
    public AjaxResult updateConfig(@PathVariable String appId, @RequestBody AgentApp agentApp)
    {
        agentApp.setAppId(appId);
        agentApp.setUpdateBy(getLoginName());
        return toAjax(agentAppService.updateAgentApp(agentApp));
    }

    @RequiresPermissions("agentsec:app:add")
    @PostMapping("/autoRegister")
    public AjaxResult autoRegister(@RequestBody AgentApp agentApp)
    {
        agentApp.setCreateBy(getLoginName());
        return AjaxResult.success("自动注册接口骨架已创建", agentApp);
    }
}
