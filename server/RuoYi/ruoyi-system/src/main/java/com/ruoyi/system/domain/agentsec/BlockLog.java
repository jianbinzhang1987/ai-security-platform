package com.ruoyi.system.domain.agentsec;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 阻断日志对象 block_log
 */
public class BlockLog extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private String blockLogId;

    private String targetType;

    private String targetId;

    private String reason;

    private String status;

    public String getBlockLogId()
    {
        return blockLogId;
    }

    public void setBlockLogId(String blockLogId)
    {
        this.blockLogId = blockLogId;
    }

    public String getTargetType()
    {
        return targetType;
    }

    public void setTargetType(String targetType)
    {
        this.targetType = targetType;
    }

    public String getTargetId()
    {
        return targetId;
    }

    public void setTargetId(String targetId)
    {
        this.targetId = targetId;
    }

    public String getReason()
    {
        return reason;
    }

    public void setReason(String reason)
    {
        this.reason = reason;
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
            .append("blockLogId", getBlockLogId())
            .append("targetType", getTargetType())
            .append("targetId", getTargetId())
            .append("reason", getReason())
            .append("status", getStatus())
            .toString();
    }
}
