package com.ruoyi.system.mapper.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.BlockLog;

public interface BlockLogMapper
{
    public int insertBlockLog(BlockLog blockLog);

    public List<BlockLog> selectBlockLogList(BlockLog blockLog);
}
