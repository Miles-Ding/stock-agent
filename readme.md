# 📊 AI 股票分析助手

> 输入股票代码，Agent 自动生成技术分析 + 新闻情绪 + 机构评级 + 操作建议

---

## ✨ 功能

- 支持多只股票同时分析（逗号分隔）
- 技术指标：MACD、RSI、成交量、均线排列
- 新闻情绪：正面 / 负面 / 中性
- 机构评级：强买 / 买入 / 持有 / 卖出 / 强卖
- 生成 Markdown 格式分析报告
- 支持 Web 界面输入 + 展示

---

## 🖥️ 技术栈

- **后端**：FastAPI + LangGraph + yfinance
- **LLM**：阿里云百炼（qwen-plus）
- **前端**：原生 HTML + CSS + JS
- **部署**：本地 / AWS EC2

---

## 🚀 快速运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

修改 `main.py` 中的配置区：

python

```
ALIYUN_API_KEY = "你的阿里云API Key"
PUSH_TOKEN = "你的pushplus token"
NEWS_API_KEY = "你的newsapi key"
```



### 3. 启动服务

bash

```
python main.py
```



### 4. 打开浏览器

访问 `http://localhost:8000`

## 📁 项目结构

text

```
v4/
├── FastAPI.py                # FastAPI 入口
├── main.py      # LangGraph Agent 核心逻辑
├── static/
│   ├── index.html         # 主页面
│   ├── style.css          # 样式
│   └── app.js             # 前端逻辑
├── requirements.txt
└── README.md
```



------

## 📌 注意事项

- 首次启动需要联网（yfinance 拉取数据、API 调用）
- 新闻情绪依赖 NewsAPI 免费额度（100 次/天）
- 财报日期依赖 yfinance，部分股票可能返回“待查”

------

## 🔮 后续计划

- 用户配置存储（股票列表 + 微信 token）
- 每日定时推送日报
- 多用户支持
- 部署到公网

## 📄 License

MIT

