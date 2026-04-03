package com.ruoyi.web.controller.agentsec;

import java.util.List;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.AlertRule;
import com.ruoyi.system.service.agentsec.IAlertRuleService;

@RestController
@RequestMapping("/agentsec/rule")
public class AlertRuleController extends BaseController
{
    @Autowired
    private IAlertRuleService alertRuleService;

    @RequiresPermissions("agentsec:rule:list")
    @GetMapping("/list")
    public TableDataInfo list(AlertRule alertRule)
    {
        startPage();
        List<AlertRule> list = alertRuleService.selectAlertRuleList(alertRule);
        return getDataTable(list);
    }

    @RequiresPermissions("agentsec:rule:add")
    @PostMapping
    public AjaxResult add(@RequestBody AlertRule alertRule)
    {
        alertRule.setCreateBy(getLoginName());
        return toAjax(alertRuleService.insertAlertRule(alertRule));
    }

    @RequiresPermissions("agentsec:rule:test")
    @PostMapping("/test/{ruleId}")
    public AjaxResult test(@PathVariable String ruleId)
    {
        return AjaxResult.success("规则测试接口骨架已创建", ruleId);
    }
}
