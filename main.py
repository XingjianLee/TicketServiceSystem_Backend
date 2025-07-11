import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import users, flights, orders, auth, notices
from app.core.config import settings
from app.database.connection import test_database_connection, get_database_info
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动蓝天航空票务系统...")
    
    # 测试数据库连接
    logger.info("测试数据库连接...")
    if test_database_connection():
        db_info = get_database_info()
        logger.info(f"✅ 数据库连接成功")
        logger.info(f"   数据库: {db_info['database_name']}")
        logger.info(f"   版本: {db_info['version']}")
        logger.info(f"   表数量: {db_info['table_count']}")
    else:
        logger.error("❌ 数据库连接失败")
        logger.error("请检查数据库配置和连接信息")
        logger.error("可以尝试运行: python init_database.py")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭蓝天航空票务系统...")


app = FastAPI(
    title="蓝天航空票务系统 API",
    description="提供航班查询、订票、用户管理等功能",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 从配置文件读取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(flights.router, prefix="/api/flights", tags=["航班"])
app.include_router(orders.router, prefix="/api/orders", tags=["订单"])
app.include_router(notices.router, prefix="/api/notices", tags=["通知"])


@app.get("/")
async def root():
    return {"message": "蓝天航空票务系统 API 服务运行中"
            }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)