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

    window.addEventListener('load', () => {
        setTimeout(analyze, 500);
    });
})();