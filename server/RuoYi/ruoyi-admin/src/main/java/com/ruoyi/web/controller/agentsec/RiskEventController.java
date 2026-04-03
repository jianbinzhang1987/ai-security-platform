package com.ruoyi.web.controller.agentsec;

import java.util.List;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.RiskEvent;
import com.ruoyi.system.service.agentsec.IRiskEventService;

@RestController
@RequestMapping("/agentsec/event")
public class RiskEventController extends BaseController
{
    @Autowired
    private IRiskEventService riskEventService;

    @RequiresPermissions("agentsec:event:list")
    @GetMapping("/list")
    public TableDataInfo list(RiskEvent riskEvent)
    {
        startPage();
        List<RiskEvent> list = riskEventService.selectRiskEventList(riskEvent);
        return getDataTable(list);
    }

    @RequiresPermissions("agentsec:event:edit")
    @PutMapping("/{eventId}")
    public AjaxResult update(@PathVariable String eventId, @RequestBody RiskEvent riskEvent)
    {
        riskEvent.setEventId(eventId);
        riskEvent.setUpdateBy(getLoginName());
        return toAjax(riskEventService.updateRiskEvent(riskEvent));
    }
}
