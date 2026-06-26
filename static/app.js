(function() {
    const tickerInput = document.getElementById('tickerInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const reportContainer = document.getElementById('reportContainer');

    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false
    });

    async function analyze() {
        const tickers = tickerInput.value.trim();
        if (!tickers) {
            reportContainer.innerHTML = `<div class="error-msg">⚠️ 请至少输入一只股票代码</div>`;
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = '⏳ 分析中...';
        loadingIndicator.classList.add('active');
        reportContainer.innerHTML = '';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers }),
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                const html = marked.parse(data.report);
                reportContainer.innerHTML = `<div class="markdown-body">${html}</div>`;
            } else {
                reportContainer.innerHTML = `<div class="error-msg">❌ 分析失败：${data.detail || data.message || '未知错误'}</div>`;
            }
        } catch (error) {
            reportContainer.innerHTML = `<div class="error-msg">❌ 网络错误：${error.message}</div>`;
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = '🔍 分析';
            loadingIndicator.classList.remove('active');
        }
    }

    analyzeBtn.addEventListener('click', analyze);
    tickerInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            analyze();
        }
    });

})();

// ===== 配置相关 =====
const configStocks = document.getElementById('configStocks');
const configToken = document.getElementById('configToken');
const configTime = document.getElementById('configTime');
const saveConfigBtn = document.getElementById('saveConfigBtn');
const configStatus = document.getElementById('configStatus');

// 固定用户 ID（后续可改为登录）
const USER_ID = 'user_001';

// 加载配置
async function loadConfig() {
    try {
        const res = await fetch(`/config/${USER_ID}`);
        const data = await res.json();
        if (data.status === 'ok' && data.config) {
            const cfg = data.config;
            if (cfg.stocks) configStocks.value = cfg.stocks.join(',');
            if (cfg.wechat_token) configToken.value = cfg.wechat_token;
            if (cfg.push_time) configTime.value = cfg.push_time;
        }
    } catch (e) {
        // 配置不存在或加载失败，忽略，用户自己填写
    }
}

// 保存配置
async function saveConfig() {
    const stocksRaw = configStocks.value.trim();
    const stocks = stocksRaw ? stocksRaw.split(',').map(s => s.trim().toUpperCase()).filter(Boolean) : [];
    const wechat_token = configToken.value.trim();
    const push_time = configTime.value || '08:00';

    if (!stocks.length) {
        setConfigStatus('❌ 请至少添加一只股票', 'error');
        return;
    }
    if (!wechat_token) {
        setConfigStatus('❌ 请输入微信推送 Token', 'error');
        return;
    }

    try {
        const res = await fetch('/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: USER_ID,
                stocks: stocks,
                wechat_token: wechat_token,
                push_time: push_time
            })
        });
        const data = await res.json();
        if (data.status === 'ok') {
            setConfigStatus('✅ 配置保存成功！', 'success');
        } else {
            setConfigStatus('❌ 保存失败：' + (data.message || '未知错误'), 'error');
        }
    } catch (e) {
        setConfigStatus('❌ 网络错误：' + e.message, 'error');
    }
}

function setConfigStatus(msg, type) {
    configStatus.textContent = msg;
    configStatus.className = 'config-status ' + type;
}

// 绑定保存按钮
saveConfigBtn.addEventListener('click', saveConfig);

// 页面加载时加载配置
loadConfig();