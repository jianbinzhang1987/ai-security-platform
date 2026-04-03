package com.ruoyi.system.service.impl.agentsec;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.utils.uuid.IdUtils;
import com.ruoyi.system.domain.agentsec.BlockLog;
import com.ruoyi.system.mapper.agentsec.BlockLogMapper;
import com.ruoyi.system.service.agentsec.IBlockService;

@Service
public class BlockServiceImpl implements IBlockService
{
    @Autowired
    private BlockLogMapper blockLogMapper;

    @Override
    public int createBlock(BlockLog blockLog)
    {
        if (blockLog.getBlockLogId() == null || blockLog.getBlockLogId().isEmpty())
        {
            blockLog.setBlockLogId(IdUtils.fastSimpleUUID());
        }
        return blockLogMapper.insertBlockLog(blockLog);
    }

    @Override
    public List<BlockLog> selectBlockLogList(BlockLog blockLog)
    {
        return blockLogMapper.selectBlockLogList(blockLog);
    }
}
