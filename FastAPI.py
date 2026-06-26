from fastapi import FastAPI
from pydantic import BaseModel
from main import app as agent_app
from fastapi.staticfiles import StaticFiles
import json
import os

USERS_FILE = "users.json"
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 创建 FastAPI 实例
api = FastAPI(title="炒股Agent API")

# 定义请求体结构（前端传股票列表）
class AnalyzeRequest(BaseModel):
    tickers: str   # 例如 "AAPL,MSFT,NVDA"

# 定义响应体结构（你返回的报告）
class AnalyzeResponse(BaseModel):
    report: str
    status: str

class SubscribeRequest(BaseModel):
    user_id: str
    stocks: list[str]
    wechat_token: str
    push_time: str = "08:00"

@api.get("/ping")
def ping():
    """测试接口是否活着"""
    return {"status": "ok", "message": "Agent is running"}

@api.post("/analyze")
def analyze(req: AnalyzeRequest):
    """核心接口：传股票代码，返回分析报告"""
    user_input = f"分析 {req.tickers}，生成日报"
    result = agent_app.invoke({"messages": [("user", user_input)]})
    report = result["messages"][-1].content
    return AnalyzeResponse(report=report, status="success")

@api.post("/subscribe")
def subscribe(req: SubscribeRequest):
    """保存用户配置（股票列表 + 微信token + 推送时间）"""
    users = load_users()
    users[req.user_id] = {
        "stocks": req.stocks,
        "wechat_token": req.wechat_token,
        "push_time": req.push_time
    }
    save_users(users)
    return {"status": "ok", "message": f"用户 {req.user_id} 配置已保存"}

@api.get("/config/{user_id}")
def get_config(user_id: str):
    """获取用户配置"""
    users = load_users()
    if user_id not in users:
        return {"status": "error", "message": "用户不存在"}
    return {"status": "ok", "config": users[user_id]}
# 托管 static 目录，访问 http://localhost:8000 直接打开 index.html
api.mount("/", StaticFiles(directory="static", html=True), name="static")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)