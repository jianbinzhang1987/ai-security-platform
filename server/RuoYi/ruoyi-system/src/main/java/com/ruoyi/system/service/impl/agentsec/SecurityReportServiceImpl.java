package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.utils.uuid.IdUtils;
import com.ruoyi.system.domain.agentsec.SecurityReport;
import com.ruoyi.system.mapper.agentsec.SecurityReportMapper;
import com.ruoyi.system.service.agentsec.ISecurityReportService;

@Service
public class SecurityReportServiceImpl implements ISecurityReportService
{
    @Autowired
    private SecurityReportMapper securityReportMapper;

    @Override
    public List<SecurityReport> selectSecurityReportList(SecurityReport securityReport)
    {
        return securityReportMapper.selectSecurityReportList(securityReport);
    }

    @Override
    public int createSecurityReport(SecurityReport securityReport)
    {
        if (securityReport.getReportId() == null || securityReport.getReportId().isEmpty())
        {
            securityReport.setReportId(IdUtils.fastSimpleUUID());
        }
        return securityReportMapper.insertSecurityReport(securityReport);
    }
}
