import os
from dotenv import load_dotenv
load_dotenv()
import yfinance as yf   #雅虎的包，用来获取股票数据
import requests  #作用是把消息打包成HTTP请求，发送到微信的接口上
import pandas as pd
import json
from datetime import datetime
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages  #
from langchain_openai import ChatOpenAI   #阿里云兼容OpenAI接口
from langchain_core.tools import tool
#-------------配置区---------------
#自选股列表
ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
PUSH_TOKEN = os.getenv("PUSH_TOKEN")
if not ALIYUN_API_KEY:
    raise ValueError("❌ ALIYUN_API_KEY 未设置，请检查 .env 文件")
if not NEWS_API_KEY:
    raise ValueError("❌ NEWS_API_KEY 未设置，请检查 .env 文件")
if not PUSH_TOKEN:
    raise ValueError("❌ PUSH_TOKEN 未设置，请检查 .env 文件")
total_tokens = 0
total_prompt_tokens = 0
total_completion_tokens = 0
#-------------工作区---------------

@tool
def get_price(tickers: str) -> str:
    """获取股票最新价，输入如 AAPL,MSFT"""
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    # 一次下载所有股票
    df = yf.download(ticker_list, period="1d", progress=False)
    results = []
    for ticker in ticker_list:
        try:
            price = float(df['Close'][ticker].iloc[-1])
            results.append(f"{ticker}: ${price:.2f}")
        except:
            results.append(f"{ticker}: 查询失败")
    return " | ".join(results)
@tool
def analyze_technical(tickers: str) -> str:
    """综合分析技术指标:MACD金叉、RSI、成交量异动、均线排列,输入如 AAPL,MSFT"""
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    # 一次下载所有股票
    df = yf.download(ticker_list, period="120d", progress=False)
    # df['Close'] 是多列 DataFrame，每列是一只股票
    closes = df['Close']  # shape: (120, n)
    volumes = df['Volume']  # shape: (120, n)
    results = []
    for ticker in ticker_list:
        try:
            close = closes[ticker]
            volume = volumes[ticker]
            
            # 1. MACD 金叉
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            dif = ema12 - ema26
            dea = dif.ewm(span=9).mean()
            golden_cross = (dif.iloc[-1] > dea.iloc[-1]) and (dif.iloc[-2] <= dea.iloc[-2])
            
            # 2. RSI（14天）
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
            
            # 3. 成交量异动
            avg_volume = volume.rolling(20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1
            volume_surge = volume_ratio > 1.5
            
            # 4. 均线排列（MA5 > MA20 > MA60）
            ma5 = close.rolling(5).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            ma_bullish = (ma5 > ma20 > ma60)
            ma_bearish = (ma5 < ma20 < ma60)
            ma_status = "多头排列" if ma_bullish else "空头排列" if ma_bearish else "震荡"
            
            price = float(close.iloc[-1])
            
            result = f"""**{ticker}** 技术分析:
- 价格: ${price:.2f}
- MACD金叉: {'✅' if golden_cross else '❌'}
- RSI({rsi:.1f}): {rsi_status}
- 成交量: {'🔥 放量' if volume_surge else '正常'} (均量比 {volume_ratio:.1f}x)
- 均线排列: {ma_status}
"""
            results.append(result)
        except Exception as e:
            results.append(f"**{ticker}** 技术分析失败: {e}")
    return "\n".join(results)    #注意这里的join和上面的result=[]，是为了把每次循环的结果拼在一起显示出来，防止被覆盖
@tool
def get_analyst_rating(ticker: str) -> str:
    """获取机构评级，输入股票代码如 AAPL"""
    try:
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations
        
        if recommendations is not None and not recommendations.empty:
            # 取最新一行（period = 0m）
            latest = recommendations.iloc[0]
            strong_buy = int(latest.get('strongBuy', 0))
            buy = int(latest.get('buy', 0))
            hold = int(latest.get('hold', 0))
            sell = int(latest.get('sell', 0))
            strong_sell = int(latest.get('strongSell', 0))
            
            total = strong_buy + buy + hold + sell + strong_sell
            if total > 0:
                # 计算买入比例（强买+买入）
                buy_ratio = (strong_buy + buy) / total * 100
                return f"{ticker} 机构评级: {strong_buy}强买 / {buy}买入 / {hold}持有 / {sell}卖出 / {strong_sell}强卖 (买入比例 {buy_ratio:.0f}%)"
        
        return f"{ticker} 机构评级数据暂不可用"
    except Exception as e:
        return f"{ticker} 机构评级获取失败: {e}"
@tool
def send_wechat(message: str) -> str:
    """发送消息到微信"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSH_TOKEN,
        "title": "Agent日报",
        "content": message,
        "template": "markdown"  # 让微信以 Markdown 格式显示
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"微信推送响应: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                return "推送成功"
            else:
                return f"推送失败: {result.get('msg', '未知错误')}"
        else:
            return f"推送失败: HTTP {response.status_code}"
    except Exception as e:
        return f"推送异常: {e}"
@tool
def get_news_sentiment(ticker: str) -> str:
    """获取股票近期新闻情绪，输入股票代码如 AAPL"""
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}&pageSize=5"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if not articles:
                return f"{ticker} 暂无相关新闻"
            
            # 简单情绪判断（基于标题关键词）
            positive = 0
            negative = 0
            for article in articles:
                title = article['title'].lower()
                if any(word in title for word in ['rise', 'gain', 'surge', 'positive', 'up']):
                    positive += 1
                elif any(word in title for word in ['fall', 'drop', 'loss', 'negative', 'down']):
                    negative += 1
            
            sentiment = "偏正面" if positive > negative else "偏负面" if negative > positive else "中性"
            return f"{ticker} 近期新闻情绪 {sentiment}（最新：{articles[0]['title'][:50]}...）"
        else:
            return f"{ticker} 新闻获取失败"
    except Exception as e:
        return f"{ticker} 新闻接口异常: {e}"
@tool
def get_earning_date(ticker: str) -> str:
    """获取股票下次财报日期，输入股票代码如 AAPL"""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        
        if calendar and isinstance(calendar, dict):
            earnings_dates = calendar.get('Earnings Date')
            if earnings_dates:
                # 可能是列表或单个日期
                if isinstance(earnings_dates, (list, tuple)) and len(earnings_dates) > 0:
                    earnings_date = earnings_dates[0]
                else:
                    earnings_date = earnings_dates
                
                if hasattr(earnings_date, 'strftime'):
                    date_str = earnings_date.strftime('%Y-%m-%d')
                else:
                    date_str = str(earnings_date)
                
                return f"{ticker} 下次财报日期: {date_str}"
        return f"{ticker} 财报日期待查"
    except Exception as e:
        return f"{ticker} 财报获取失败: {e}"
# 绑定 Tool
tools = [get_price, analyze_technical, get_analyst_rating,send_wechat, get_news_sentiment, get_earning_date]
llm = ChatOpenAI(api_key=ALIYUN_API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model="qwen-plus")
llm_with_tools = llm.bind_tools(tools)
# 定义状态
class State(TypedDict):
    messages: Annotated[List, add_messages]  #这里定义message应该是一个列表

# Agent 节点
def call_model(state):
    global total_tokens, total_prompt_tokens, total_completion_tokens
    response = llm_with_tools.invoke(state["messages"])
    if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
        usage = response.response_metadata['token_usage']
        total_tokens += usage.get('total_tokens', 0)
        total_prompt_tokens += usage.get('prompt_tokens', 0)
        total_completion_tokens += usage.get('completion_tokens', 0)
    return {"messages": [response]}
# 条件边：判断是否要调 Tool
def should_continue(state):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

# 建图
from langgraph.prebuilt import ToolNode
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")
app = workflow.compile()

today = datetime.now().strftime('%Y-%m-%d')

# 运行
if __name__ == "__main__":
    # 让 Agent 自己决定怎么分析、怎么汇总、怎么输出
    user_input = f"""
【重要规则】
- 每只股票的每个指标（股价、技术面、新闻、财报、评级）只能调用一次工具
- 如果某个工具已经返回了数据，不要再重复调用
- 所有数据收集完成后，立即生成日报，不要再调用任何工具
- 禁止重复调用任何工具

今天是 {today}

请分析以下股票:AAPL、MSFT、NVDA、TSLA、GOOGL。

对每只股票，你需要：
1. 查最新股价
2. 判断 MACD 金叉
3. 查新闻情绪
4. 查财报日期
5. 查机构评级
并决定其中哪些信息值得关注，给出你的操作建议（如买入、卖出、持有），并说明理由。

最后，请生成一份 Markdown 格式的日报，包含：
- 今天的日期 {today}
- 你认为每只股票需要关注的信息（如果一切如常，这个指标就不用显示了）
- 底部加上免责声明

重要指令：
- 所有股票分析完成后，必须调用 send_wechat 工具推送日报。
- 不允许在未推送的情况下结束任务。
"""
    
    result = app.invoke({"messages": [("user", user_input)]})
    print(result)
    print("\n" + "="*50)
    print("Agent 执行完成")
    print("="*50)
    
    # 只打印最后一条消息的内容
    last_message = result["messages"][-1]
    if hasattr(last_message, "content") and last_message.content:
        print("\n最终回复:")
        print(last_message.content)
    else:
        print("\n无文本回复")
         # 可选：打印所有 Tool 调用记录（调试用）
    print("\n工具调用记录:")
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🔧 {tc['name']}: {tc['args']}")
    print("\n" + "="*50)
    print("📊 Token 消耗统计")
    print("="*50)
    print(f"  - Prompt Tokens: {total_prompt_tokens}")
    print(f"  - Completion Tokens: {total_completion_tokens}")
    print(f"  - Total Tokens: {total_tokens}")
    print(f"  - 预估成本 (qwen-plus): ${total_tokens * 0.0000012:.4f}") 