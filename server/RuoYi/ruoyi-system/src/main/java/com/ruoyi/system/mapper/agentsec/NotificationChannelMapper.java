package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.NotificationChannel;

public interface NotificationChannelMapper
{
    public List<NotificationChannel> selectNotificationChannelList(NotificationChannel notificationChannel);
}
