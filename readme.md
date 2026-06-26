# 📊 AI 股票分析助手

> 输入股票代码，Agent 自动生成技术分析 + 新闻情绪 + 机构评级 + 操作建议

---

## ✨ 功能

- ✅ 实时分析：输入股票代码，Agent 立即生成报告
- ✅ 日报配置：用户可设置关注的股票列表、微信推送 token、推送时间
- ✅ 配置保存：前端配置自动保存到后端，下次打开自动加载
- ✅ 多维度分析：MACD、RSI、成交量异动、均线排列、新闻情绪、机构评级
- ✅ 微信推送：分析结果可推送到微信（pushplus）

---

## 🖥️ 技术栈

- **后端**：FastAPI + LangGraph + yfinance
- **LLM**：阿里云百炼（qwen-plus）
- **前端**：原生 HTML + CSS + JS
- **部署**：本地 / AWS EC2

---

## 🚀 快速运行

### 1. 克隆项目

```bash
git clone https://github.com/Miles-Ding/stock-agent.git
cd stock-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

env

```
ALIYUN_API_KEY=你的阿里云API Key
NEWS_API_KEY=你的NewsAPI Key
PUSH_TOKEN=你的pushplus Token
```

### 4. 启动服务

bash

```
python main.py
```

### 5. 打开浏览器

访问 `http://localhost:8000`

## 📁 项目结构

text

```
v4-发布/
├── main.py                # FastAPI 入口
├── stock_agent_l3.py      # LangGraph Agent 核心
├── static/
│   ├── index.html         # 前端页面
│   ├── style.css          # 样式
│   └── app.js             # 前端逻辑
├── users.json             # 用户配置（自动生成）
├── requirements.txt
└── README.md
```



------

## 🧩 使用流程

1. **实时分析**：在页面输入股票代码（如 `AAPL,MSFT,NVDA`），点击“分析”
2. **配置日报**：在下方“日报配置”区域填写关注股票、微信 token、推送时间
3. **保存配置**：点击保存，下次打开页面自动加载

## 📌 注意事项

- 首次启动需要联网（yfinance 拉取数据）
- 新闻情绪依赖 NewsAPI 免费额度（100 次/天）
- 财报日期依赖 yfinance，部分股票可能返回“待查”
- `.env` 文件已加入 `.gitignore`，不会上传到 GitHub

------

## 🔮 后续计划

- 每日定时推送日报
- 多用户支持
- 部署到公网

## 📄 License

MIT

