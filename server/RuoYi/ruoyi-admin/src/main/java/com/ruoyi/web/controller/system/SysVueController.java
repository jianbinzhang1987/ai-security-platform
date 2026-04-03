package com.ruoyi.web.controller.system;

import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.imageio.ImageIO;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import com.google.code.kaptcha.Constants;
import com.google.code.kaptcha.Producer;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysMenu;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.text.Convert;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.common.utils.uuid.IdUtils;
import com.ruoyi.system.service.ISysConfigService;
import com.ruoyi.system.service.ISysMenuService;
import com.ruoyi.system.service.ISysRoleService;

/**
 * RuoYi-Vue3 兼容接口
 */
@RestController
public class SysVueController extends BaseController
{
    private static final Map<String, String> COMPONENT_MAPPING = new HashMap<>();

    static
    {
        COMPONENT_MAPPING.put("/monitor/data", "monitor/druid/index");
        COMPONENT_MAPPING.put("/tool/build", "tool/build/index");
        COMPONENT_MAPPING.put("/tool/gen", "tool/gen/index");
        COMPONENT_MAPPING.put("/tool/swagger", "tool/swagger/index");
    }

    @Resource(name = "captchaProducer")
    private Producer captchaProducer;

    @Resource(name = "captchaProducerMath")
    private Producer captchaProducerMath;

    @Autowired
    private ISysMenuService menuService;

    @Autowired
    private ISysRoleService roleService;

    @Autowired
    private ISysConfigService configService;

    @Value("${shiro.user.captchaEnabled:true}")
    private boolean captchaEnabled;

    @Value("${shiro.user.captchaType:math}")
    private String captchaType;

    @GetMapping("/captchaImage")
    public AjaxResult captchaImage(HttpServletRequest request) throws IOException
    {
        AjaxResult ajax = AjaxResult.success();
        ajax.put("captchaEnabled", captchaEnabled);
        if (!captchaEnabled)
        {
            ajax.put("img", "");
            ajax.put("uuid", IdUtils.fastSimpleUUID());
            return ajax;
        }

        HttpSession session = request.getSession();
        String type = request.getParameter("type");
        if (StringUtils.isEmpty(type))
        {
            type = captchaType;
        }

        String capStr;
        String code;
        BufferedImage image;
        if ("math".equals(type))
        {
            String capText = captchaProducerMath.createText();
            capStr = capText.substring(0, capText.lastIndexOf("@"));
            code = capText.substring(capText.lastIndexOf("@") + 1);
            image = captchaProducerMath.createImage(capStr);
        }
        else
        {
            capStr = captchaProducer.createText();
            code = capStr;
            image = captchaProducer.createImage(capStr);
        }

        session.setAttribute(Constants.KAPTCHA_SESSION_KEY, code);
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        ImageIO.write(image, "jpg", stream);
        ajax.put("img", Base64.getEncoder().encodeToString(stream.toByteArray()));
        ajax.put("uuid", IdUtils.fastSimpleUUID());
        return ajax;
    }

    @GetMapping("/getInfo")
    public AjaxResult getInfo()
    {
        SysUser user = getSysUser();
        if (StringUtils.isNull(user))
        {
            AjaxResult ajax = AjaxResult.error("未登录或登录超时，请重新登录");
            ajax.put("code", 401);
            return ajax;
        }

        Map<String, Object> userInfo = new LinkedHashMap<>();
        userInfo.put("userId", user.getUserId());
        userInfo.put("userName", user.getLoginName());
        userInfo.put("nickName", StringUtils.defaultString(user.getUserName(), user.getLoginName()));
        userInfo.put("avatar", user.getAvatar());
        userInfo.put("dept", user.getDept());

        Set<String> permissions = user.isAdmin() ? Set.of("*:*:*") : menuService.selectPermsByUserId(user.getUserId());
        Set<String> roles = user.isAdmin() ? Set.of("admin") : roleService.selectRoleKeys(user.getUserId());

        AjaxResult ajax = AjaxResult.success();
        ajax.put("user", userInfo);
        ajax.put("roles", roles);
        ajax.put("permissions", permissions);
        ajax.put("isDefaultModifyPwd", initPasswordIsModify(user));
        ajax.put("isPasswordExpired", passwordIsExpiration(user));
        return ajax;
    }

    @GetMapping("/getRouters")
    public AjaxResult getRouters()
    {
        SysUser user = getSysUser();
        if (StringUtils.isNull(user))
        {
            AjaxResult ajax = AjaxResult.error("未登录或登录超时，请重新登录");
            ajax.put("code", 401);
            return ajax;
        }

        List<SysMenu> menus = menuService.selectMenusByUser(user);
        List<RouterVo> routes = buildMenus(menus);
        return AjaxResult.success(routes);
    }

    private List<RouterVo> buildMenus(List<SysMenu> menus)
    {
        List<RouterVo> routes = new ArrayList<>();
        for (SysMenu menu : menus)
        {
            if (!"M".equals(menu.getMenuType()) && !"C".equals(menu.getMenuType()))
            {
                continue;
            }
            routes.add(buildMenuRoute(menu));
        }
        return routes;
    }

    private RouterVo buildMenuRoute(SysMenu menu)
    {
        RouterVo router = new RouterVo();
        router.setHidden("1".equals(menu.getVisible()));
        router.setName(routeName(menu));
        router.setPath(routerPath(menu));
        router.setComponent(routerComponent(menu));
        router.setQuery(null);
        router.setMeta(new MetaVo(menu.getMenuName(), normalizeIcon(menu.getIcon()), noCache(menu), innerLink(menu)));

        List<SysMenu> children = visibleChildren(menu.getChildren());
        if (!children.isEmpty() && "M".equals(menu.getMenuType()))
        {
            router.setAlwaysShow(children.size() > 1);
            router.setRedirect("noRedirect");
            List<RouterVo> childRoutes = new ArrayList<>();
            for (SysMenu child : children)
            {
                if (!"M".equals(child.getMenuType()) && !"C".equals(child.getMenuType()))
                {
                    continue;
                }
                childRoutes.add(buildMenuRoute(child));
            }
            router.setChildren(childRoutes);
        }
        else if (isMenuFrame(menu))
        {
            router.setMeta(new MetaVo(menu.getMenuName(), normalizeIcon(menu.getIcon()), noCache(menu), null));
            RouterVo child = new RouterVo();
            child.setPath(lastSegment(menu.getUrl()));
            child.setName(routeName(menu));
            child.setComponent(resolveComponent(menu.getUrl()));
            child.setQuery(null);
            child.setMeta(new MetaVo(menu.getMenuName(), normalizeIcon(menu.getIcon()), noCache(menu), null));
            router.setMeta(null);
            router.setName(null);
            router.setAlwaysShow(false);
            router.setRedirect(null);
            router.setChildren(List.of(child));
        }

        if (isInnerLink(menu))
        {
            router.setComponent("InnerLink");
            router.setMeta(new MetaVo(menu.getMenuName(), normalizeIcon(menu.getIcon()), noCache(menu), menu.getUrl()));
        }

        return router;
    }

    private String routerPath(SysMenu menu)
    {
        String url = StringUtils.defaultString(menu.getUrl(), "");
        List<SysMenu> children = visibleChildren(menu.getChildren());
        if (("#".equals(url) || StringUtils.isEmpty(url)) && !children.isEmpty())
        {
            if (menu.getParentId() == 0L)
            {
                String childUrl = StringUtils.defaultString(children.get(0).getUrl(), "");
                String topPath = StringUtils.substringBetween(childUrl + "/", "/", "/");
                return StringUtils.isEmpty(topPath) ? "/menu-" + menu.getMenuId() : "/" + topPath;
            }
            return "menu-" + menu.getMenuId();
        }
        if (menu.getParentId() == 0L && isInnerLink(menu))
        {
            return "/";
        }
        if (menu.getParentId() == 0L || isInnerLink(menu))
        {
            return url;
        }
        if (isMenuFrame(menu))
        {
            return "/";
        }
        return lastSegment(url);
    }

    private String routerComponent(SysMenu menu)
    {
        if (menu.getParentId() == 0L && "M".equals(menu.getMenuType()))
        {
            return "Layout";
        }
        if (hasVisibleChildren(menu))
        {
            return "ParentView";
        }
        if (isInnerLink(menu))
        {
            return "InnerLink";
        }
        if (isMenuFrame(menu))
        {
            return "Layout";
        }
        return resolveComponent(menu.getUrl());
    }

    private String resolveComponent(String url)
    {
        if (StringUtils.isEmpty(url))
        {
            return "index";
        }
        String mapped = COMPONENT_MAPPING.get(url);
        if (StringUtils.isNotEmpty(mapped))
        {
            return mapped;
        }
        String normalized = url.startsWith("/") ? url.substring(1) : url;
        return normalized + "/index";
    }

    private String routeName(SysMenu menu)
    {
        String url = StringUtils.defaultIfEmpty(menu.getUrl(), menu.getMenuName());
        if ("#".equals(url))
        {
            url = menu.getMenuName();
        }
        String[] parts = url.replaceFirst("^/+", "").split("[/_-]");
        StringBuilder builder = new StringBuilder();
        for (String part : parts)
        {
            if (StringUtils.isEmpty(part))
            {
                continue;
            }
            builder.append(Character.toUpperCase(part.charAt(0)));
            if (part.length() > 1)
            {
                builder.append(part.substring(1));
            }
        }
        if (builder.length() == 0)
        {
            builder.append("Menu").append(menu.getMenuId());
        }
        return builder.toString();
    }

    private List<SysMenu> visibleChildren(List<SysMenu> children)
    {
        List<SysMenu> visibleChildren = new ArrayList<>();
        if (children == null)
        {
            return visibleChildren;
        }
        for (SysMenu child : children)
        {
            if ("F".equals(child.getMenuType()) || "1".equals(child.getVisible()))
            {
                continue;
            }
            visibleChildren.add(child);
        }
        return visibleChildren;
    }

    private boolean hasVisibleChildren(SysMenu menu)
    {
        return !visibleChildren(menu.getChildren()).isEmpty();
    }

    private boolean isMenuFrame(SysMenu menu)
    {
        return menu.getParentId() == 0L && "C".equals(menu.getMenuType()) && !isInnerLink(menu);
    }

    private boolean isInnerLink(SysMenu menu)
    {
        return StringUtils.isNotEmpty(menu.getUrl())
                && (menu.getUrl().startsWith("http://") || menu.getUrl().startsWith("https://"));
    }

    private String innerLink(SysMenu menu)
    {
        return isInnerLink(menu) ? menu.getUrl() : null;
    }

    private boolean noCache(SysMenu menu)
    {
        return "1".equals(menu.getIsRefresh());
    }

    private String lastSegment(String url)
    {
        String path = StringUtils.substringAfterLast(url, "/");
        return StringUtils.isEmpty(path) ? url : path;
    }

    private String normalizeIcon(String icon)
    {
        if (StringUtils.isEmpty(icon) || "#".equals(icon))
        {
            return "list";
        }
        if (icon.startsWith("fa "))
        {
            return StringUtils.substringAfterLast(icon, "fa-");
        }
        return icon;
    }

    private boolean initPasswordIsModify(SysUser user)
    {
        Integer initPasswordModify = Convert.toInt(configService.selectConfigByKey("sys.account.initPasswordModify"));
        return initPasswordModify != null && initPasswordModify == 1 && user.getPwdUpdateDate() == null;
    }

    private boolean passwordIsExpiration(SysUser user)
    {
        Integer passwordValidateDays = Convert.toInt(configService.selectConfigByKey("sys.account.passwordValidateDays"));
        if (passwordValidateDays != null && passwordValidateDays > 0)
        {
            if (user.getPwdUpdateDate() == null)
            {
                return true;
            }
            long diff = System.currentTimeMillis() - user.getPwdUpdateDate().getTime();
            return diff > passwordValidateDays * 24L * 60L * 60L * 1000L;
        }
        return false;
    }

    public static class RouterVo
    {
        private String name;
        private String path;
        private boolean hidden;
        private String redirect;
        private String component;
        private boolean alwaysShow;
        private String query;
        private MetaVo meta;
        private List<RouterVo> children;

        public String getName()
        {
            return name;
        }

        public void setName(String name)
        {
            this.name = name;
        }

        public String getPath()
        {
            return path;
        }

        public void setPath(String path)
        {
            this.path = path;
        }

        public boolean isHidden()
        {
            return hidden;
        }

        public void setHidden(boolean hidden)
        {
            this.hidden = hidden;
        }

        public String getRedirect()
        {
            return redirect;
        }

        public void setRedirect(String redirect)
        {
            this.redirect = redirect;
        }

        public String getComponent()
        {
            return component;
        }

        public void setComponent(String component)
        {
            this.component = component;
        }

        public boolean isAlwaysShow()
        {
            return alwaysShow;
        }

        public void setAlwaysShow(boolean alwaysShow)
        {
            this.alwaysShow = alwaysShow;
        }

        public String getQuery()
        {
            return query;
        }

        public void setQuery(String query)
        {
            this.query = query;
        }

        public MetaVo getMeta()
        {
            return meta;
        }

        public void setMeta(MetaVo meta)
        {
            this.meta = meta;
        }

        public List<RouterVo> getChildren()
        {
            return children;
        }

        public void setChildren(List<RouterVo> children)
        {
            this.children = children;
        }
    }

    public static class MetaVo
    {
        private String title;
        private String icon;
        private boolean noCache;
        private String link;

        public MetaVo(String title, String icon, boolean noCache, String link)
        {
            this.title = title;
            this.icon = icon;
            this.noCache = noCache;
            this.link = link;
        }

        public String getTitle()
        {
            return title;
        }

        public void setTitle(String title)
        {
            this.title = title;
        }

        public String getIcon()
        {
            return icon;
        }

        public void setIcon(String icon)
        {
            this.icon = icon;
        }

        public boolean isNoCache()
        {
            return noCache;
        }

        public void setNoCache(boolean noCache)
        {
            this.noCache = noCache;
        }

        public String getLink()
        {
            return link;
        }

        public void setLink(String link)
        {
            this.link = link;
        }
    }
}
