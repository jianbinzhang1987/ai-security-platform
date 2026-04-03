package com.ruoyi.framework.shiro.web.filter.user;

import java.io.IOException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.shiro.web.filter.authc.UserFilter;
import org.apache.shiro.web.util.WebUtils;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.utils.ServletUtils;

/**
 * 兼容前后端分离场景的 user 过滤器
 */
public class AjaxUserFilter extends UserFilter
{
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @Override
    protected boolean onAccessDenied(ServletRequest request, ServletResponse response) throws Exception
    {
        if (ServletUtils.isAjaxRequest((HttpServletRequest) request))
        {
            HttpServletResponse httpServletResponse = (HttpServletResponse) response;
            httpServletResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            AjaxResult ajaxResult = AjaxResult.error("未登录或登录超时。请重新登录");
            ajaxResult.put("code", HttpServletResponse.SC_UNAUTHORIZED);
            ServletUtils.renderString(httpServletResponse,
                    OBJECT_MAPPER.writeValueAsString(ajaxResult));
            return false;
        }
        saveRequestAndRedirectToLogin(request, response);
        return false;
    }

    @Override
    protected void redirectToLogin(ServletRequest request, ServletResponse response) throws IOException
    {
        WebUtils.issueRedirect(request, response, getLoginUrl());
    }
}
