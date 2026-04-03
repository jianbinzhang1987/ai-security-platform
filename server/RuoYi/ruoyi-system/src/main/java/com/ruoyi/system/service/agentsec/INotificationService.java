package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.NotificationChannel;

public interface INotificationService
{
    public List<NotificationChannel> selectNotificationChannelList(NotificationChannel notificationChannel);
}
