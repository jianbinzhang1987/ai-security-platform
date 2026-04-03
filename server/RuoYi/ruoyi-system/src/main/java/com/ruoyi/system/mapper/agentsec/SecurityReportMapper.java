package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.SecurityReport;

public interface SecurityReportMapper
{
    public List<SecurityReport> selectSecurityReportList(SecurityReport securityReport);

    public int insertSecurityReport(SecurityReport securityReport);
}
