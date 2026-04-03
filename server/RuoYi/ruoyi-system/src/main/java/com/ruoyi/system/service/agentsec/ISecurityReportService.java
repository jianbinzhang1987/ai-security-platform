package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.SecurityReport;

public interface ISecurityReportService
{
    public List<SecurityReport> selectSecurityReportList(SecurityReport securityReport);

    public int createSecurityReport(SecurityReport securityReport);
}
