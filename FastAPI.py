from fastapi import FastAPI
from pydantic import BaseModel
from main import app as agent_app
from fastapi.staticfiles import StaticFiles

# 创建 FastAPI 实例
api = FastAPI(title="炒股Agent API")

# 定义请求体结构（前端传股票列表）
class AnalyzeRequest(BaseModel):
    tickers: str   # 例如 "AAPL,MSFT,NVDA"

# 定义响应体结构（你返回的报告）
class AnalyzeResponse(BaseModel):
    report: str
    status: str

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

# 托管 static 目录，访问 http://localhost:8000 直接打开 index.html
api.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)