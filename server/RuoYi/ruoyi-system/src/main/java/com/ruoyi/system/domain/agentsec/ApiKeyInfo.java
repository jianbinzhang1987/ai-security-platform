package com.ruoyi.system.domain.agentsec;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * API Key 对象 agentsec_api_key
 */
public class ApiKeyInfo extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String apiKeyId;

    private String tenantId;

    private String apiKeyName;

    private String appId;

    private String status;

    private String expireTimeText;

    public String getApiKeyId()
    {
        return apiKeyId;
    }

    public void setApiKeyId(String apiKeyId)
    {
        this.apiKeyId = apiKeyId;
    }

    public String getTenantId()
    {
        return tenantId;
    }

    public void setTenantId(String tenantId)
    {
        this.tenantId = tenantId;
    }

    public String getApiKeyName()
    {
        return apiKeyName;
    }

    public void setApiKeyName(String apiKeyName)
    {
        this.apiKeyName = apiKeyName;
    }

    public String getAppId()
    {
        return appId;
    }

    public void setAppId(String appId)
    {
        this.appId = appId;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    public String getExpireTimeText()
    {
        return expireTimeText;
    }

    public void setExpireTimeText(String expireTimeText)
    {
        this.expireTimeText = expireTimeText;
    }

    @Override
    public String toString()
    {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("apiKeyId", getApiKeyId())
            .append("tenantId", getTenantId())
            .append("apiKeyName", getApiKeyName())
            .append("appId", getAppId())
            .append("status", getStatus())
            .append("expireTimeText", getExpireTimeText())
            .toString();
    }
}
