package com.ruoyi.system.domain.agentsec;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * Agent 应用对象 agent_app
 */
public class AgentApp extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String appId;

    private String tenantId;

    private String appName;

    private String status;

    private String tokenStatus;

    private String sdkVersion;

    public String getAppId()
    {
        return appId;
    }

    public void setAppId(String appId)
    {
        this.appId = appId;
    }

    public String getTenantId()
    {
        return tenantId;
    }

    public void setTenantId(String tenantId)
    {
        this.tenantId = tenantId;
    }

    public String getAppName()
    {
        return appName;
    }

    public void setAppName(String appName)
    {
        this.appName = appName;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    public String getTokenStatus()
    {
        return tokenStatus;
    }

    public void setTokenStatus(String tokenStatus)
    {
        this.tokenStatus = tokenStatus;
    }

    public String getSdkVersion()
    {
        return sdkVersion;
    }

    public void setSdkVersion(String sdkVersion)
    {
        this.sdkVersion = sdkVersion;
    }

    @Override
    public String toString()
    {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("appId", getAppId())
            .append("tenantId", getTenantId())
            .append("appName", getAppName())
            .append("status", getStatus())
            .append("tokenStatus", getTokenStatus())
            .append("sdkVersion", getSdkVersion())
            .append("createBy", getCreateBy())
            .append("createTime", getCreateTime())
            .append("updateBy", getUpdateBy())
            .append("updateTime", getUpdateTime())
            .append("remark", getRemark())
            .toString();
    }
}
