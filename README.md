# 蓝天航空票务系统后端

基于 FastAPI 开发的航空票务系统后端 API。

## 功能特性

- 用户注册/登录/认证
- 航班搜索和查询
- 订单创建和管理
- 支付状态管理
- JWT 身份验证

## 技术栈

- FastAPI
- PyMySQL
- JWT (python-jose)
- 密码加密 (passlib)
- Pydantic 数据验证

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

### 3. 启动服务

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python main.py
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 用户相关

- `GET /api/users/profile` - 获取用户资料
- `PUT /api/users/profile` - 更新用户资料
- `GET /api/users/orders` - 获取用户订单列表

### 航班相关

- `GET /api/flights/search` - 搜索航班
- `GET /api/flights/{flight_id}` - 获取航班详情
- `GET /api/flights/` - 获取所有航班

### 订单相关

- `POST /api/orders/` - 创建订单
- `GET /api/orders/{order_id}` - 获取订单详情
- `PUT /api/orders/{order_id}/pay` - 支付订单

## 数据库

确保 MySQL 数据库已启动，并创建了相应的表结构。

## 开发

项目结构：

```
backend/
├── main.py              # 主应用入口
├── app/
│   ├── core/           # 核心配置
│   │   ├── config.py   # 配置管理
│   │   └── database.py # 数据库连接
│   ├── models/         # 数据模型
│   │   └── schemas.py  # Pydantic 模型
│   └── routers/        # 路由模块
│       ├── auth.py     # 认证路由
│       ├── users.py    # 用户路由
│       ├── flights.py  # 航班路由
│       └── orders.py   # 订单路由
└── requirements.txt    # 依赖包
```
