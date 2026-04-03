package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.domain.agentsec.NotificationChannel;
import com.ruoyi.system.mapper.agentsec.NotificationChannelMapper;
import com.ruoyi.system.service.agentsec.INotificationService;

@Service
public class NotificationServiceImpl implements INotificationService
{
    @Autowired
    private NotificationChannelMapper notificationChannelMapper;

    @Override
    public List<NotificationChannel> selectNotificationChannelList(NotificationChannel notificationChannel)
    {
        return notificationChannelMapper.selectNotificationChannelList(notificationChannel);
    }
}
