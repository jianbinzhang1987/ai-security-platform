package com.ruoyi.system.domain.agentsec;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 租户对象 agentsec_tenant
 */
public class TenantInfo extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String tenantId;

    private String tenantName;

    private String planCode;

    private Integer maxAgents;

    private Integer dataRetentionDays;

    private String status;

    public String getTenantId()
    {
        return tenantId;
    }

    public void setTenantId(String tenantId)
    {
        this.tenantId = tenantId;
    }

    public String getTenantName()
    {
        return tenantName;
    }

    public void setTenantName(String tenantName)
    {
        this.tenantName = tenantName;
    }

    public String getPlanCode()
    {
        return planCode;
    }

    public void setPlanCode(String planCode)
    {
        this.planCode = planCode;
    }

    public Integer getMaxAgents()
    {
        return maxAgents;
    }

    public void setMaxAgents(Integer maxAgents)
    {
        this.maxAgents = maxAgents;
    }

    public Integer getDataRetentionDays()
    {
        return dataRetentionDays;
    }

    public void setDataRetentionDays(Integer dataRetentionDays)
    {
        this.dataRetentionDays = dataRetentionDays;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    @Override
    public String toString()
    {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("tenantId", getTenantId())
            .append("tenantName", getTenantName())
            .append("planCode", getPlanCode())
            .append("maxAgents", getMaxAgents())
            .append("dataRetentionDays", getDataRetentionDays())
            .append("status", getStatus())
            .toString();
    }
}
