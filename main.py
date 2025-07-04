from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, flights, orders, auth
from app.core.config import settings

app = FastAPI(
    title="蓝天航空票务系统 API",
    description="提供航班查询、订票、用户管理等功能",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(flights.router, prefix="/api/flights", tags=["航班"])
app.include_router(orders.router, prefix="/api/orders", tags=["订单"])

@app.get("/")
async def root():
    return {"message": "蓝天航空票务系统 API 服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 