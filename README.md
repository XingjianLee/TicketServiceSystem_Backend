# 蓝天航空票务系统 - 后端

这是蓝天航空票务系统的后端 API 服务，基于 FastAPI 框架开发。

## 功能特性

- 🔐 用户认证与授权（JWT Token）
- 👤 用户注册、登录、信息管理
- ✈️ 航班搜索和查询
- 📋 订单创建、支付、管理
- 📢 系统通知管理
- 🔒 密码加密存储
- 🌐 CORS 跨域支持

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL
- **认证**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt
- **数据验证**: Pydantic
- **API 文档**: Swagger UI (自动生成)

## 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+
- pip

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 数据库配置

1. 确保 MySQL 服务正在运行
2. 创建数据库：
   ```sql
   CREATE DATABASE ticket_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. 运行数据库初始化脚本：

   ```bash
   # 进入数据库配置目录
   cd database_configure

   # 创建表结构
   mysql -u root -p ticket_service < create_tables.sql

   # 初始化示例数据
   mysql -u root -p ticket_service < init_sample_data.sql
   ```

### 4. 环境变量配置

创建 `.env` 文件（可选）：

```env
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=ticket_service
DATABASE_USER=root
DATABASE_PASSWORD=123456

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=true
```

## 运行服务

### 开发模式

```bash
# 启动开发服务器
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动服务后，可以通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 认证相关 (`/api/auth`)

- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /logout` - 用户登出
- `GET /me` - 获取当前用户信息
- `POST /refresh` - 刷新访问令牌

### 用户管理 (`/api/users`)

- `GET /` - 获取用户列表（管理员）
- `GET /{user_id}` - 获取用户详情
- `PUT /me` - 更新当前用户信息
- `PUT /{user_id}` - 更新指定用户信息（管理员）
- `DELETE /{user_id}` - 删除用户（管理员）

### 航班管理 (`/api/flights`)

- `GET /search` - 搜索航班
- `GET /{flight_id}` - 获取航班详情
- `GET /` - 获取所有航班

### 订单管理 (`/api/orders`)

- `POST /` - 创建订单
- `GET /` - 获取用户订单列表
- `GET /{order_id}` - 获取订单详情
- `POST /{order_id}/pay` - 支付订单
- `POST /{order_id}/cancel` - 取消订单

### 通知管理 (`/api/notices`)

- `GET /` - 获取所有活跃通知
- `GET /{notice_id}` - 获取通知详情

## 测试

运行 API 测试脚本：

```bash
python test_api.py
```

## 数据库表结构

### 用户表 (users)

```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  nickname VARCHAR(50),
  avatar VARCHAR(255),
  signature VARCHAR(255),
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  phone VARCHAR(20),
  id_card VARCHAR(30) NOT NULL UNIQUE,
  real_name VARCHAR(100),
  gender ENUM('男', '女', '未知') DEFAULT '未知',
  age TINYINT UNSIGNED DEFAULT NULL,
  vip_level TINYINT DEFAULT 0 CHECK (vip_level BETWEEN 0 AND 4),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/schemas/` 中定义数据模型
2. 在 `app/routers/` 中创建路由
3. 在 `main.py` 中注册路由

### 数据库操作

- 使用 `app/database/models.py` 中定义的模型类
- 所有数据库操作都通过模型类进行

### 认证和授权

- 使用 `@Depends(get_current_user)` 装饰器保护需要认证的端点
- JWT token 通过 Authorization header 传递：`Bearer <token>`

## 部署

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量

生产环境中请设置以下环境变量：

- `SECRET_KEY`: 强随机密钥
- `DATABASE_PASSWORD`: 数据库密码
- `DEBUG`: false

## 故障排除

### 常见问题

1. **数据库连接失败**

   - 检查 MySQL 服务是否运行
   - 验证数据库连接配置
   - 确认数据库用户权限

2. **JWT Token 无效**

   - 检查 SECRET_KEY 配置
   - 确认 token 格式正确
   - 验证 token 是否过期

3. **CORS 错误**
   - 检查 allowed_origins 配置
   - 确认前端 URL 在允许列表中

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
