package com.ruoyi.system.domain.agentsec;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * Agent 实例对象 agent_instance
 */
public class AgentInstance extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String instanceId;

    private String appId;

    private String hostName;

    private String ipAddress;

    private String status;

    public String getInstanceId()
    {
        return instanceId;
    }

    public void setInstanceId(String instanceId)
    {
        this.instanceId = instanceId;
    }

    public String getAppId()
    {
        return appId;
    }

    public void setAppId(String appId)
    {
        this.appId = appId;
    }

    public String getHostName()
    {
        return hostName;
    }

    public void setHostName(String hostName)
    {
        this.hostName = hostName;
    }

    public String getIpAddress()
    {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress)
    {
        this.ipAddress = ipAddress;
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
            .append("instanceId", getInstanceId())
            .append("appId", getAppId())
            .append("hostName", getHostName())
            .append("ipAddress", getIpAddress())
            .append("status", getStatus())
            .toString();
    }
}
