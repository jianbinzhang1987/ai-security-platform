package com.ruoyi.web.controller.agentsec;

import java.util.List;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.system.domain.agentsec.BlockLog;
import com.ruoyi.system.service.agentsec.IBlockService;

@RestController
@RequestMapping("/agentsec")
public class BlockController extends BaseController
{
    @Autowired
    private IBlockService blockService;

    @RequiresPermissions("agentsec:block:add")
    @PostMapping("/block")
    public AjaxResult add(@RequestBody BlockLog blockLog)
    {
        blockLog.setCreateBy(getLoginName());
        return toAjax(blockService.createBlock(blockLog));
    }

    @RequiresPermissions("agentsec:blockLog:list")
    @GetMapping("/blockLog/list")
    public TableDataInfo list(BlockLog blockLog)
    {
        startPage();
        List<BlockLog> list = blockService.selectBlockLogList(blockLog);
        return getDataTable(list);
    }
}
