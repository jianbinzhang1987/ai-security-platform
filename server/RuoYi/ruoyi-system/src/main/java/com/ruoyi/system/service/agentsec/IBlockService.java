package com.ruoyi.system.service.agentsec;

import java.util.List;
import com.ruoyi.system.domain.agentsec.BlockLog;

public interface IBlockService
{
    public int createBlock(BlockLog blockLog);

    public List<BlockLog> selectBlockLogList(BlockLog blockLog);
}
