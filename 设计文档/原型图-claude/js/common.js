/**
 * 大模型安全监测平台 - 管理端原型图共享 JS 工具库
 * 提供：弹窗管理、提示通知、确认对话框、Tab 切换、分页、导航等
 */

/* =============================================
   全局状态
   ============================================= */
window._confirmCallback = null;

/* =============================================
   弹窗（Modal）管理
   ============================================= */

/**
 * 打开弹窗
 * @param {string} id - 弹窗 overlay 的元素 ID
 */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
}

/**
 * 关闭弹窗
 * @param {string} id - 弹窗 overlay 的元素 ID
 */
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove('show');
    // 检查是否还有其他打开的弹窗
    const anyOpen = document.querySelectorAll('.modal-overlay.show, .confirm-overlay.show');
    if (anyOpen.length === 0) {
      document.body.style.overflow = '';
    }
  }
}

/**
 * 点击遮罩层关闭弹窗
 */
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('show');
    const anyOpen = document.querySelectorAll('.modal-overlay.show, .confirm-overlay.show');
    if (anyOpen.length === 0) {
      document.body.style.overflow = '';
    }
  }
});

/* =============================================
   右侧抽屉面板
   ============================================= */

/**
 * 打开抽屉面板
 * @param {string} overlayId - 遮罩层 ID
 * @param {string} panelId   - 面板 ID
 */
function openDrawer(overlayId, panelId) {
  const overlay = document.getElementById(overlayId);
  const panel = document.getElementById(panelId);
  if (overlay) overlay.classList.add('show');
  if (panel) panel.classList.add('show');
  document.body.style.overflow = 'hidden';
}

/**
 * 关闭抽屉面板
 * @param {string} overlayId - 遮罩层 ID
 * @param {string} panelId   - 面板 ID
 */
function closeDrawer(overlayId, panelId) {
  const overlay = document.getElementById(overlayId);
  const panel = document.getElementById(panelId);
  if (overlay) overlay.classList.remove('show');
  if (panel) panel.classList.remove('show');
  document.body.style.overflow = '';
}

/* =============================================
   提示通知（Toast）
   ============================================= */

/**
 * 显示提示通知
 * @param {'success'|'error'|'warning'|'info'} type - 类型
 * @param {string} title   - 标题
 * @param {string} message - 消息内容
 * @param {number} duration - 显示时长（毫秒），默认 3000
 */
function showToast(type, title, message, duration) {
  duration = duration || 3000;

  let container = document.getElementById('__toast_container__');
  if (!container) {
    container = document.createElement('div');
    container.id = '__toast_container__';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const iconMap = {
    success: '✓',
    error: '✕',
    warning: '!',
    info: 'i'
  };

  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.innerHTML =
    '<div class="toast-icon">' + (iconMap[type] || 'i') + '</div>' +
    '<div class="toast-content">' +
    '<div class="toast-title">' + title + '</div>' +
    (message ? '<div class="toast-msg">' + message + '</div>' : '') +
    '</div>';

  container.appendChild(toast);

  setTimeout(function () {
    toast.classList.add('fade-out');
    setTimeout(function () {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, duration);
}

/** 快捷方法 */
function toastSuccess(msg) { showToast('success', '操作成功', msg); }
function toastError(msg) { showToast('error', '操作失败', msg); }
function toastWarning(msg) { showToast('warning', '警告', msg); }
function toastInfo(msg) { showToast('info', '提示', msg); }

/* =============================================
   确认对话框
   ============================================= */

/**
 * 显示确认对话框
 * @param {string}   message  - 提示内容
 * @param {Function} callback - 点击"确认"后执行的回调
 * @param {string}   title    - 标题，默认"操作确认"
 * @param {string}   type     - 类型 'danger'|'warning'，影响确认按钮样式
 */
function showConfirm(message, callback, title, type) {
  title = title || '操作确认';
  type = type || 'warning';

  let overlay = document.getElementById('__global_confirm__');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = '__global_confirm__';
    overlay.className = 'confirm-overlay';
    overlay.innerHTML =
      '<div class="confirm-box">' +
      '  <div class="confirm-header">' +
      '    <span class="confirm-icon" id="__confirm_icon__">!</span>' +
      '    <span class="confirm-title" id="__confirm_title__"></span>' +
      '  </div>' +
      '  <div class="confirm-message" id="__confirm_msg__"></div>' +
      '  <div class="confirm-footer">' +
      '    <button class="btn btn-default" onclick="hideConfirm()">取 消</button>' +
      '    <button class="btn" id="__confirm_ok__" onclick="execConfirm()">确 认</button>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(overlay);
  }

  document.getElementById('__confirm_title__').textContent = title;
  document.getElementById('__confirm_msg__').textContent = message;

  const okBtn = document.getElementById('__confirm_ok__');
  if (type === 'danger') {
    okBtn.className = 'btn btn-danger';
  } else {
    okBtn.className = 'btn btn-warning';
  }

  window._confirmCallback = callback;
  overlay.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function hideConfirm() {
  const overlay = document.getElementById('__global_confirm__');
  if (overlay) overlay.classList.remove('show');
  document.body.style.overflow = '';
  window._confirmCallback = null;
}

function execConfirm() {
  hideConfirm();
  if (typeof window._confirmCallback === 'function') {
    window._confirmCallback();
  }
}

/**
 * 删除确认快捷方法
 * @param {string}   itemName - 被删除项名称
 * @param {Function} callback - 确认后回调
 */
function confirmDelete(itemName, callback) {
  showConfirm(
    '确定要删除"' + itemName + '"吗？删除后无法恢复。',
    callback,
    '删除确认',
    'danger'
  );
}

/* =============================================
   选项卡（Tab）切换
   ============================================= */

/**
 * 切换选项卡
 * @param {string} navSelector  - 选项卡导航容器的选择器或 ID
 * @param {string} paneSelector - 选项卡内容容器的选择器或 ID
 * @param {string} tabName      - 要激活的 tab 名（data-tab 属性值）
 */
function switchTab(navContainerId, paneContainerId, tabName) {
  // 处理导航
  const navContainer = document.getElementById(navContainerId) ||
    document.querySelector(navContainerId);
  if (navContainer) {
    navContainer.querySelectorAll('.tab-item').forEach(function (item) {
      if (item.dataset.tab === tabName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  // 处理内容面板
  const paneContainer = document.getElementById(paneContainerId) ||
    document.querySelector(paneContainerId);
  if (paneContainer) {
    paneContainer.querySelectorAll('.tab-pane').forEach(function (pane) {
      if (pane.dataset.tab === tabName) {
        pane.classList.add('show');
      } else {
        pane.classList.remove('show');
      }
    });
  }
}

/**
 * 初始化选项卡（自动绑定点击事件）
 * @param {string} navContainerId  - 导航容器 ID
 * @param {string} paneContainerId - 内容容器 ID
 * @param {string} defaultTab      - 默认激活的 tab 名
 */
function initTabs(navContainerId, paneContainerId, defaultTab) {
  const navContainer = document.getElementById(navContainerId);
  if (!navContainer) return;

  navContainer.querySelectorAll('.tab-item').forEach(function (item) {
    item.addEventListener('click', function () {
      switchTab(navContainerId, paneContainerId, item.dataset.tab);
    });
  });

  if (defaultTab) {
    switchTab(navContainerId, paneContainerId, defaultTab);
  } else {
    const first = navContainer.querySelector('.tab-item');
    if (first && first.dataset.tab) {
      switchTab(navContainerId, paneContainerId, first.dataset.tab);
    }
  }
}

/* =============================================
   分页组件
   ============================================= */

/**
 * 渲染分页
 * @param {string} containerId - 分页容器 ID
 * @param {number} total       - 总条数
 * @param {number} current     - 当前页
 * @param {number} pageSize    - 每页条数
 * @param {Function} onChange  - 页码变化回调，参数为新页码
 */
function renderPagination(containerId, total, current, pageSize, onChange) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  current = Math.max(1, Math.min(current, totalPages));

  // 信息文字
  const start = (current - 1) * pageSize + 1;
  const end = Math.min(current * pageSize, total);

  let infoHtml = '<span class="pagination-info">共 ' + total + ' 条，第 ' + start + '-' + end + ' 条</span>';

  // 生成页码
  let pages = [];
  pages.push(1);
  if (current > 3) pages.push('...');
  for (let i = Math.max(2, current - 1); i <= Math.min(totalPages - 1, current + 1); i++) {
    pages.push(i);
  }
  if (current < totalPages - 2) pages.push('...');
  if (totalPages > 1) pages.push(totalPages);

  let pagesHtml = '';
  // 上一页
  pagesHtml += '<button class="page-btn" ' + (current === 1 ? 'disabled' : '') +
    ' onclick="__pgChange(\'' + containerId + '\',' + (current - 1) + ',' + total + ',' + pageSize + ')">&#8249;</button>';

  pages.forEach(function (p) {
    if (p === '...') {
      pagesHtml += '<span style="padding:0 4px;color:#C0C4CC;">...</span>';
    } else {
      pagesHtml += '<button class="page-btn ' + (p === current ? 'active' : '') + '" ' +
        'onclick="__pgChange(\'' + containerId + '\',' + p + ',' + total + ',' + pageSize + ')">' + p + '</button>';
    }
  });

  // 下一页
  pagesHtml += '<button class="page-btn" ' + (current === totalPages ? 'disabled' : '') +
    ' onclick="__pgChange(\'' + containerId + '\',' + (current + 1) + ',' + total + ',' + pageSize + ')">&#8250;</button>';

  container.innerHTML =
    '<div class="pagination-wrapper">' +
    infoHtml +
    '<div class="pagination">' + pagesHtml + '</div>' +
    '</div>';

  // 保存回调
  container._pgCallback = onChange;
}

function __pgChange(containerId, page, total, pageSize) {
  const container = document.getElementById(containerId);
  if (container && typeof container._pgCallback === 'function') {
    container._pgCallback(page);
  }
  renderPagination(containerId, total, page, pageSize, container ? container._pgCallback : null);
}

/* =============================================
   复选框全选
   ============================================= */

/**
 * 全选/反选表格复选框
 * @param {HTMLElement} masterCheckbox - 全选复选框元素
 * @param {string}      tableId        - 表格 ID
 */
function toggleAllCheckbox(masterCheckbox, tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
  checkboxes.forEach(function (cb) {
    cb.checked = masterCheckbox.checked;
  });
}

/**
 * 获取表格中已勾选的行数据（通过 data-id 属性）
 * @param {string} tableId - 表格 ID
 * @returns {string[]}
 */
function getCheckedIds(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return [];
  const checked = table.querySelectorAll('tbody input[type="checkbox"]:checked');
  return Array.from(checked).map(function (cb) {
    return cb.dataset.id || cb.closest('tr').dataset.id;
  }).filter(Boolean);
}

/* =============================================
   导航（iframe 内页面跳转）
   ============================================= */

/**
 * 从 iframe 内部触发父页面导航
 * @param {string} path - 相对路径，如 'pages/assets/server-detail.html'
 */
function navigateTo(path) {
  if (window.parent && window.parent !== window && typeof window.parent.loadPage === 'function') {
    window.parent.loadPage(path);
  } else {
    window.location.href = path;
  }
}

/**
 * 更新父页面面包屑
 * @param {Array} items - [{label, path?}]
 */
function updateBreadcrumb(items) {
  if (window.parent && window.parent !== window && typeof window.parent.setBreadcrumb === 'function') {
    window.parent.setBreadcrumb(items);
  }
}

/* =============================================
   表单工具
   ============================================= */

/**
 * 简单表单验证
 * @param {string} formId - 表单 ID
 * @returns {boolean} 是否通过验证
 */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  let valid = true;
  // 清除旧错误
  form.querySelectorAll('.form-error').forEach(function (el) { el.remove(); });
  form.querySelectorAll('.form-control.error, .form-select.error').forEach(function (el) {
    el.classList.remove('error');
  });

  // 检查 required
  form.querySelectorAll('[required]').forEach(function (input) {
    const val = input.value.trim();
    if (!val) {
      valid = false;
      input.classList.add('error');
      const err = document.createElement('div');
      err.className = 'form-error';
      err.textContent = '该字段不能为空';
      if (input.parentNode) {
        input.parentNode.appendChild(err);
      }
    }
  });

  return valid;
}

/* =============================================
   代码块复制
   ============================================= */

/**
 * 复制代码块内容
 * @param {HTMLElement} btn - 复制按钮元素
 * @param {string}      codeId - 代码块 ID
 */
function copyCode(btn, codeId) {
  const codeEl = document.getElementById(codeId);
  if (!codeEl) return;
  const text = codeEl.innerText || codeEl.textContent;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(function () {
      const orig = btn.textContent;
      btn.textContent = '已复制';
      setTimeout(function () { btn.textContent = orig; }, 2000);
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    const orig = btn.textContent;
    btn.textContent = '已复制';
    setTimeout(function () { btn.textContent = orig; }, 2000);
  }
}

/* =============================================
   侧边栏折叠（供 index.html 使用）
   ============================================= */

/**
 * 切换侧边栏展开/折叠
 */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const wrapper = document.getElementById('layoutWrapper');
  if (!sidebar) return;
  sidebar.classList.toggle('collapsed');
  if (wrapper) wrapper.classList.toggle('sidebar-collapsed');
}

/* =============================================
   日期格式化工具
   ============================================= */

/**
 * 格式化日期
 * @param {Date|string|number} date
 * @param {string} fmt - 格式字符串，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string}
 */
function formatDate(date, fmt) {
  fmt = fmt || 'YYYY-MM-DD HH:mm:ss';
  const d = date instanceof Date ? date : new Date(date);
  const map = {
    YYYY: d.getFullYear(),
    MM: String(d.getMonth() + 1).padStart(2, '0'),
    DD: String(d.getDate()).padStart(2, '0'),
    HH: String(d.getHours()).padStart(2, '0'),
    mm: String(d.getMinutes()).padStart(2, '0'),
    ss: String(d.getSeconds()).padStart(2, '0')
  };
  return fmt.replace(/YYYY|MM|DD|HH|mm|ss/g, function (k) { return map[k]; });
}

/* =============================================
   模拟数据生成工具
   ============================================= */

/** 生成随机整数 */
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/** 从数组中随机取一个元素 */
function randItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

/** 生成模拟日期字符串（最近 N 天内） */
function randDate(daysAgo) {
  daysAgo = daysAgo || 30;
  const d = new Date(Date.now() - randInt(0, daysAgo) * 86400000 - randInt(0, 86400000));
  return formatDate(d, 'YYYY-MM-DD HH:mm:ss');
}

/* =============================================
   CSS 辅助
   ============================================= */

/** 添加 error 样式到 input */
function form_control_error(el) {
  if (typeof el === 'string') el = document.getElementById(el);
  if (el) el.style.borderColor = '#F56C6C';
}

/** 清除 error 样式 */
function form_control_clear(el) {
  if (typeof el === 'string') el = document.getElementById(el);
  if (el) el.style.borderColor = '';
}

/* =============================================
   初始化通用行为
   ============================================= */
document.addEventListener('DOMContentLoaded', function () {
  // 给所有 .modal-close 按钮绑定关闭事件
  document.querySelectorAll('.modal-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const overlay = btn.closest('.modal-overlay');
      if (overlay) {
        overlay.classList.remove('show');
        const anyOpen = document.querySelectorAll('.modal-overlay.show');
        if (anyOpen.length === 0) document.body.style.overflow = '';
      }
    });
  });

  // 给所有 .drawer-close 按钮绑定关闭事件
  document.querySelectorAll('.drawer-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const panel = btn.closest('.drawer-panel');
      const panelId = panel ? panel.id : null;
      document.querySelectorAll('.drawer-overlay').forEach(function (o) { o.classList.remove('show'); });
      document.querySelectorAll('.drawer-panel').forEach(function (p) { p.classList.remove('show'); });
      document.body.style.overflow = '';
    });
  });

  // 点击抽屉遮罩关闭
  document.querySelectorAll('.drawer-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function () {
      document.querySelectorAll('.drawer-overlay').forEach(function (o) { o.classList.remove('show'); });
      document.querySelectorAll('.drawer-panel').forEach(function (p) { p.classList.remove('show'); });
      document.body.style.overflow = '';
    });
  });
});
