package com.ruoyi.system.domain.agentsec;

import java.math.BigDecimal;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 风险事件对象 risk_event
 */
public class RiskEvent extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String eventId;

    private String appId;

    private String sessionId;

    private String riskType;

    private String riskLevel;

    private BigDecimal confidence;

    private String status;

    public String getEventId()
    {
        return eventId;
    }

    public void setEventId(String eventId)
    {
        this.eventId = eventId;
    }

    public String getAppId()
    {
        return appId;
    }

    public void setAppId(String appId)
    {
        this.appId = appId;
    }

    public String getSessionId()
    {
        return sessionId;
    }

    public void setSessionId(String sessionId)
    {
        this.sessionId = sessionId;
    }

    public String getRiskType()
    {
        return riskType;
    }

    public void setRiskType(String riskType)
    {
        this.riskType = riskType;
    }

    public String getRiskLevel()
    {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel)
    {
        this.riskLevel = riskLevel;
    }

    public BigDecimal getConfidence()
    {
        return confidence;
    }

    public void setConfidence(BigDecimal confidence)
    {
        this.confidence = confidence;
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
            .append("eventId", getEventId())
            .append("appId", getAppId())
            .append("sessionId", getSessionId())
            .append("riskType", getRiskType())
            .append("riskLevel", getRiskLevel())
            .append("confidence", getConfidence())
            .append("status", getStatus())
            .toString();
    }
}
