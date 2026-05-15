// ==UserScript==
// @name         GLM Coding Guard
// @namespace    https://www.bigmodel.cn/
// @version      0.1.0
// @description  GLM Coding Plan 限售提醒与辅助点击脚本，保留最终人工确认。
// @author       Codex
// @match        https://www.bigmodel.cn/glm-coding*
// @run-at       document-idle
// @grant        GM_notification
// ==/UserScript==

(function () {
  'use strict';

  const STORAGE_KEY = 'glm-coding-guard-config-v1';
  const STATE_KEY = 'glm-coding-guard-runtime-v1';
  const DEFAULT_CONFIG = {
    enabled: true,
    armed: false,
    releaseHour: 10,
    releaseMinute: 0,
    warmupSeconds: 20,
    pollIntervalMs: 400,
    reloadIntervalMs: 2500,
    notificationCooldownMs: 8000,
    clickKeywords: ['立即订阅', '立即购买', '订阅', '购买', '抢购', '开通'],
    soldOutKeywords: ['明日再来', '已售罄', '售罄', '暂时缺货', '今日售罄', '排队中'],
    stopKeywords: ['支付', '确认支付', '确认订单', '收银台', '微信支付', '支付宝', '付款'],
    observeTexts: true,
    autoReloadInWindow: true,
    autoClickPrimaryButton: true,
  };

  const runtime = {
    pollTimer: null,
    reloadTimer: null,
    notifyAt: 0,
    foundAt: 0,
    lastReloadAt: 0,
  };

  const styleText = `
    #glm-coding-guard-launcher {
      position: fixed;
      right: 12px;
      bottom: 12px;
      z-index: 2147483647;
      width: 52px;
      height: 52px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 999px;
      background: linear-gradient(135deg, #2563eb, #0f172a);
      color: #fff;
      box-shadow: 0 18px 48px rgba(15, 23, 42, 0.35);
      font: 700 12px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      cursor: pointer;
    }
    #glm-coding-guard {
      position: fixed;
      top: 12px;
      right: 12px;
      z-index: 2147483647;
      width: 320px;
      background: rgba(16, 24, 40, 0.94);
      color: #f8fafc;
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 14px;
      box-shadow: 0 18px 48px rgba(15, 23, 42, 0.35);
      font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      backdrop-filter: blur(10px);
    }
    #glm-coding-guard * { box-sizing: border-box; }
    #glm-coding-guard .guard-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px 8px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.16);
    }
    #glm-coding-guard .guard-title {
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    #glm-coding-guard .guard-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      background: rgba(59, 130, 246, 0.18);
      color: #bfdbfe;
    }
    #glm-coding-guard .guard-body {
      padding: 10px 14px 14px;
      display: grid;
      gap: 10px;
    }
    #glm-coding-guard .guard-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
    }
    #glm-coding-guard .guard-row label {
      color: #cbd5e1;
      font-size: 12px;
    }
    #glm-coding-guard input[type="number"],
    #glm-coding-guard input[type="text"] {
      width: 88px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      background: rgba(15, 23, 42, 0.85);
      color: #f8fafc;
      padding: 6px 8px;
      border-radius: 8px;
      outline: none;
    }
    #glm-coding-guard input[type="text"] {
      width: 170px;
    }
    #glm-coding-guard .guard-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    #glm-coding-guard button {
      appearance: none;
      border: 0;
      border-radius: 10px;
      padding: 8px 10px;
      font-weight: 600;
      cursor: pointer;
    }
    #glm-coding-guard .btn-primary {
      background: #2563eb;
      color: white;
    }
    #glm-coding-guard .btn-secondary {
      background: rgba(148, 163, 184, 0.16);
      color: #e2e8f0;
    }
    #glm-coding-guard .guard-status {
      background: rgba(15, 23, 42, 0.72);
      border: 1px solid rgba(148, 163, 184, 0.16);
      border-radius: 10px;
      padding: 10px;
      display: grid;
      gap: 6px;
    }
    #glm-coding-guard .guard-status strong {
      color: #fef3c7;
    }
    #glm-coding-guard .guard-switches {
      display: grid;
      gap: 8px;
    }
    #glm-coding-guard .guard-switch {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    #glm-coding-guard .guard-switch input {
      width: 16px;
      height: 16px;
    }
    #glm-coding-guard .guard-hint {
      font-size: 12px;
      color: #94a3b8;
    }
    #glm-coding-guard .guard-log {
      max-height: 110px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      color: #cbd5e1;
      background: rgba(2, 6, 23, 0.55);
      border-radius: 8px;
      padding: 8px;
    }
    #glm-coding-guard.minimized .guard-body {
      display: none;
    }
  `;

  const textOf = (node) => (node?.textContent || node?.value || '').replace(/\s+/g, ' ').trim();

  const loadConfig = () => {
    try {
      return { ...DEFAULT_CONFIG, ...JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') };
    } catch {
      return { ...DEFAULT_CONFIG };
    }
  };

  const saveConfig = () => localStorage.setItem(STORAGE_KEY, JSON.stringify(config));

  const loadState = () => {
    try {
      return JSON.parse(localStorage.getItem(STATE_KEY) || '{}');
    } catch {
      return {};
    }
  };

  const saveState = (state) => localStorage.setItem(STATE_KEY, JSON.stringify(state));

  const config = loadConfig();
  const persistedState = loadState();

  function log(message) {
    const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    const nextLines = [`[${timestamp}] ${message}`, ...(persistedState.logs || [])].slice(0, 12);
    persistedState.logs = nextLines;
    saveState(persistedState);
    const logNode = document.querySelector('#glm-coding-guard .guard-log');
    if (logNode) {
      logNode.textContent = nextLines.join('\n');
    }
  }

  function notify(title, text) {
    const now = Date.now();
    if (now - runtime.notifyAt < config.notificationCooldownMs) {
      return;
    }
    runtime.notifyAt = now;
    if (typeof GM_notification === 'function') {
      GM_notification({ title, text, timeout: 6000 });
    } else if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body: text });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then((permission) => {
          if (permission === 'granted') {
            new Notification(title, { body: text });
          }
        });
      }
    }
    beep();
  }

  function beep() {
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return;
      const audio = new AudioContextClass();
      const oscillator = audio.createOscillator();
      const gain = audio.createGain();
      oscillator.type = 'triangle';
      oscillator.frequency.value = 880;
      gain.gain.value = 0.03;
      oscillator.connect(gain);
      gain.connect(audio.destination);
      oscillator.start();
      oscillator.stop(audio.currentTime + 0.15);
    } catch {
      // Ignore audio failures.
    }
  }

  function withinPurchaseWindow(now = new Date()) {
    const open = new Date(now);
    open.setHours(config.releaseHour, config.releaseMinute, 0, 0);
    const warmupStart = open.getTime() - config.warmupSeconds * 1000;
    const close = open.getTime() + 10 * 60 * 1000;
    return now.getTime() >= warmupStart && now.getTime() <= close;
  }

  function msUntilRelease(now = new Date()) {
    const target = new Date(now);
    target.setHours(config.releaseHour, config.releaseMinute, 0, 0);
    if (target <= now) {
      target.setDate(target.getDate() + 1);
    }
    return target.getTime() - now.getTime();
  }

  function formatCountdown(ms) {
    const total = Math.max(0, Math.floor(ms / 1000));
    const h = String(Math.floor(total / 3600)).padStart(2, '0');
    const m = String(Math.floor((total % 3600) / 60)).padStart(2, '0');
    const s = String(total % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
  }

  function getButtons() {
    return Array.from(document.querySelectorAll('button, a[role="button"], a[href], [class*="button"]'))
      .filter((node) => {
        const rect = node.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
  }

  function textIncludesAny(text, keywords) {
    return keywords.some((keyword) => text.includes(keyword));
  }

  function matchTargets() {
    const nodes = getButtons();
    const found = [];
    let soldOutSeen = false;
    let stopSeen = false;

    for (const node of nodes) {
      const text = textOf(node);
      if (!text) continue;
      if (textIncludesAny(text, config.soldOutKeywords)) {
        soldOutSeen = true;
      }
      if (textIncludesAny(text, config.stopKeywords)) {
        stopSeen = true;
      }
      if (textIncludesAny(text, config.clickKeywords) && !textIncludesAny(text, config.stopKeywords)) {
        found.push({ node, text });
      }
    }

    if (config.observeTexts) {
      const bodyText = textOf(document.body);
      if (textIncludesAny(bodyText, config.stopKeywords)) {
        stopSeen = true;
      }
      if (textIncludesAny(bodyText, config.soldOutKeywords)) {
        soldOutSeen = true;
      }
    }

    return { found, soldOutSeen, stopSeen };
  }

  function highlight(node) {
    node.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const previousOutline = node.style.outline;
    node.style.outline = '3px solid #f59e0b';
    setTimeout(() => {
      node.style.outline = previousOutline;
    }, 2500);
  }

  function tryAction() {
    if (!config.enabled) return;
    const status = matchTargets();

    if (status.stopSeen) {
      renderStatus('已进入确认/支付阶段，脚本停止自动点击，等待你手动确认。');
      stopLoop();
      notify('GLM Coding Guard', '已进入最终确认阶段，请你手动完成。');
      log('检测到支付或确认页面，已停止自动点击。');
      return;
    }

    if (status.found.length > 0) {
      const target = status.found[0];
      renderStatus(`发现可操作按钮：${target.text}`);
      highlight(target.node);
      notify('GLM Coding Guard', `发现按钮：${target.text}`);
      log(`发现目标按钮：${target.text}`);
      if (config.autoClickPrimaryButton && config.armed) {
        runtime.foundAt = Date.now();
        target.node.click();
        log(`已自动点击：${target.text}`);
      }
      stopReloadLoop();
      return;
    }

    if (status.soldOutSeen) {
      renderStatus('当前仍像是未开售/已售罄状态，继续等待。');
    } else {
      renderStatus('暂未识别到目标按钮，继续轮询。');
    }

    if (config.autoReloadInWindow && withinPurchaseWindow() && Date.now() - runtime.lastReloadAt >= config.reloadIntervalMs) {
      runtime.lastReloadAt = Date.now();
      log('窗口内未识别到目标按钮，刷新页面。');
      location.reload();
    }
  }

  function stopReloadLoop() {
    if (runtime.reloadTimer) {
      clearInterval(runtime.reloadTimer);
      runtime.reloadTimer = null;
    }
  }

  function stopLoop() {
    if (runtime.pollTimer) {
      clearInterval(runtime.pollTimer);
      runtime.pollTimer = null;
    }
    stopReloadLoop();
  }

  function startLoop() {
    stopLoop();
    runtime.pollTimer = setInterval(tryAction, config.pollIntervalMs);
    runtime.reloadTimer = setInterval(() => {
      if (config.autoReloadInWindow && withinPurchaseWindow() && !document.hidden) {
        tryAction();
      }
    }, Math.max(config.reloadIntervalMs, config.pollIntervalMs));
    tryAction();
  }

  function renderStatus(text) {
    const statusNode = document.querySelector('#glm-coding-guard-status');
    if (!statusNode) return;
    const countdown = formatCountdown(msUntilRelease());
    statusNode.innerHTML =
      `<div><strong>${config.armed ? '已布防' : '未布防'}</strong></div>` +
      `<div>${text}</div>` +
      `<div>距离下次 10:00 开售：${countdown}</div>`;
  }

  function updateInputsFromConfig(root) {
    root.querySelector('[data-key="releaseHour"]').value = String(config.releaseHour);
    root.querySelector('[data-key="releaseMinute"]').value = String(config.releaseMinute);
    root.querySelector('[data-key="warmupSeconds"]').value = String(config.warmupSeconds);
    root.querySelector('[data-key="pollIntervalMs"]').value = String(config.pollIntervalMs);
    root.querySelector('[data-key="reloadIntervalMs"]').value = String(config.reloadIntervalMs);
    root.querySelector('[data-key="clickKeywords"]').value = config.clickKeywords.join(',');
    root.querySelector('[data-key="soldOutKeywords"]').value = config.soldOutKeywords.join(',');
    root.querySelector('[data-key="stopKeywords"]').value = config.stopKeywords.join(',');
    root.querySelector('[data-key="enabled"]').checked = config.enabled;
    root.querySelector('[data-key="autoReloadInWindow"]').checked = config.autoReloadInWindow;
    root.querySelector('[data-key="autoClickPrimaryButton"]').checked = config.autoClickPrimaryButton;
  }

  function bindConfig(root) {
    root.addEventListener('change', (event) => {
      const target = event.target;
      const key = target?.dataset?.key;
      if (!key) return;
      if (target.type === 'checkbox') {
        config[key] = target.checked;
      } else if (['releaseHour', 'releaseMinute', 'warmupSeconds', 'pollIntervalMs', 'reloadIntervalMs'].includes(key)) {
        config[key] = Number(target.value || DEFAULT_CONFIG[key]);
      } else {
        config[key] = String(target.value || '')
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean);
      }
      saveConfig();
      renderStatus('配置已更新。');
      log(`更新配置：${key}`);
    });
  }

  function createPanel() {
    if (!document.getElementById('glm-coding-guard-launcher')) {
      const launcher = document.createElement('button');
      launcher.id = 'glm-coding-guard-launcher';
      launcher.type = 'button';
      launcher.textContent = 'GLM';
      launcher.title = '打开 GLM Coding Guard';
      launcher.addEventListener('click', () => {
        const panel = document.getElementById('glm-coding-guard');
        if (panel) {
          panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        } else {
          createPanel();
        }
      });
      (document.body || document.documentElement).appendChild(launcher);
    }

    if (document.getElementById('glm-coding-guard')) return;

    const style = document.createElement('style');
    style.textContent = styleText;
    document.head.appendChild(style);

    const panel = document.createElement('div');
    panel.id = 'glm-coding-guard';
    panel.innerHTML = `
      <div class="guard-header">
        <div class="guard-title">GLM Coding Guard</div>
        <div style="display:flex; gap:8px; align-items:center;">
          <span class="guard-badge">${config.armed ? 'ARMED' : 'SAFE'}</span>
          <button class="btn-secondary" id="glm-guard-hide">隐藏</button>
          <button class="btn-secondary" id="glm-guard-toggle-view">收起</button>
        </div>
      </div>
      <div class="guard-body">
        <div id="glm-coding-guard-status" class="guard-status"></div>
        <div class="guard-actions">
          <button class="btn-primary" id="glm-guard-arm">${config.armed ? '解除布防' : '开始布防'}</button>
          <button class="btn-secondary" id="glm-guard-check">立刻检查</button>
          <button class="btn-secondary" id="glm-guard-test">测试提醒</button>
        </div>
        <div class="guard-row">
          <label>开售小时</label>
          <input data-key="releaseHour" type="number" min="0" max="23">
        </div>
        <div class="guard-row">
          <label>开售分钟</label>
          <input data-key="releaseMinute" type="number" min="0" max="59">
        </div>
        <div class="guard-row">
          <label>提前布防秒数</label>
          <input data-key="warmupSeconds" type="number" min="0" max="300">
        </div>
        <div class="guard-row">
          <label>轮询间隔(ms)</label>
          <input data-key="pollIntervalMs" type="number" min="100" max="5000">
        </div>
        <div class="guard-row">
          <label>刷新间隔(ms)</label>
          <input data-key="reloadIntervalMs" type="number" min="500" max="10000">
        </div>
        <div class="guard-switches">
          <div class="guard-switch">
            <label>启用脚本</label>
            <input data-key="enabled" type="checkbox">
          </div>
          <div class="guard-switch">
            <label>窗口内自动刷新</label>
            <input data-key="autoReloadInWindow" type="checkbox">
          </div>
          <div class="guard-switch">
            <label>自动点击首个订阅按钮</label>
            <input data-key="autoClickPrimaryButton" type="checkbox">
          </div>
        </div>
        <div class="guard-row">
          <label>目标按钮关键词</label>
          <input data-key="clickKeywords" type="text">
        </div>
        <div class="guard-row">
          <label>售罄文案关键词</label>
          <input data-key="soldOutKeywords" type="text">
        </div>
        <div class="guard-row">
          <label>停止点击关键词</label>
          <input data-key="stopKeywords" type="text">
        </div>
        <div class="guard-hint">建议只开启到“进入订单确认前”的自动化，最终支付仍由你手动完成。</div>
        <div class="guard-log">${(persistedState.logs || []).join('\n')}</div>
      </div>
    `;
    (document.body || document.documentElement).appendChild(panel);

    updateInputsFromConfig(panel);
    bindConfig(panel);

    panel.querySelector('#glm-guard-arm').addEventListener('click', () => {
      config.armed = !config.armed;
      saveConfig();
      panel.querySelector('.guard-badge').textContent = config.armed ? 'ARMED' : 'SAFE';
      panel.querySelector('#glm-guard-arm').textContent = config.armed ? '解除布防' : '开始布防';
      renderStatus(config.armed ? '布防已开启。' : '布防已关闭。');
      log(config.armed ? '已开启布防。' : '已关闭布防。');
      if (config.armed) {
        startLoop();
      } else {
        stopLoop();
      }
    });

    panel.querySelector('#glm-guard-check').addEventListener('click', () => {
      tryAction();
    });

    panel.querySelector('#glm-guard-test').addEventListener('click', () => {
      notify('GLM Coding Guard', '提醒测试成功。');
      log('已触发测试提醒。');
    });

    panel.querySelector('#glm-guard-toggle-view').addEventListener('click', () => {
      panel.classList.toggle('minimized');
      panel.querySelector('#glm-guard-toggle-view').textContent = panel.classList.contains('minimized') ? '展开' : '收起';
    });

    panel.querySelector('#glm-guard-hide').addEventListener('click', () => {
      panel.style.display = 'none';
    });

    renderStatus('脚本已加载，等待布防。');
  }

  function boot() {
    createPanel();
    if (config.armed) {
      startLoop();
    }
    setInterval(() => {
      if (!document.getElementById('glm-coding-guard')) {
        createPanel();
      }
      if (config.armed) {
        renderStatus(withinPurchaseWindow() ? '正在抢购窗口内监控。' : '等待下次开售窗口。');
      } else {
        renderStatus('脚本已加载，等待布防。');
      }
    }, 1000);
    log('脚本启动完成。');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }

  new MutationObserver(() => {
    if (!document.getElementById('glm-coding-guard-launcher') || !document.getElementById('glm-coding-guard')) {
      createPanel();
    }
  }).observe(document.documentElement, { childList: true, subtree: true });
})();
