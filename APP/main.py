from fastapi import FastAPI
from APP.routers import dashboard

app = FastAPI(
    title="Money Game API",
    description="結合記帳與股市投資的遊戲化理財後端",
    version="0.1.0"
)

# 註冊路由器 (把 dashboard 的功能接進來)
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    return {"message": "系統核心運作中 (Refactored Structure)"}