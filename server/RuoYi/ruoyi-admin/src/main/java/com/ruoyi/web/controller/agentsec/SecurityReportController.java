package com.ruoyi.web.controller.agentsec;

import java.util.List;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.SecurityReport;
import com.ruoyi.system.service.agentsec.ISecurityReportService;

@RestController
@RequestMapping("/agentsec/report")
public class SecurityReportController extends BaseController
{
    @Autowired
    private ISecurityReportService securityReportService;

    @RequiresPermissions("agentsec:report:list")
    @GetMapping("/list")
    public TableDataInfo list(SecurityReport securityReport)
    {
        startPage();
        List<SecurityReport> list = securityReportService.selectSecurityReportList(securityReport);
        return getDataTable(list);
    }

    @RequiresPermissions("agentsec:report:add")
    @PostMapping
    public AjaxResult add(@RequestBody SecurityReport securityReport)
    {
        securityReport.setCreateBy(getLoginName());
        return toAjax(securityReportService.createSecurityReport(securityReport));
    }
}
