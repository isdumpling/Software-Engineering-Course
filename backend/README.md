# 智能课程助教聊天机器人 - 后端

基于FastAPI + MySQL的后端API服务，为智能课程助教聊天机器人提供用户认证、聊天记录存储等功能。

## 📋 功能特性

### 用户认证系统
- ✅ **用户注册**: 用户名、邮箱、密码、安全问题
- ✅ **用户登录**: JWT令牌认证
- ✅ **密码重置**: 邮件重置链接（支持安全问题验证）
- ✅ **用户信息**: 获取当前用户资料

### 聊天记录系统  
- ✅ **消息发送**: 保存用户消息和AI回答
- ✅ **历史记录**: 按课程查看聊天历史
- ✅ **会话管理**: 创建、查看、删除聊天会话
- ✅ **统计信息**: 各课程聊天数量统计

## 🛠️ 技术栈

- **Web框架**: FastAPI 0.104.1
- **数据库**: MySQL + SQLAlchemy 2.0.23
- **认证**: JWT + passlib (bcrypt)
- **数据验证**: Pydantic 2.5.0
- **数据库驱动**: PyMySQL 1.1.0

## 📁 项目结构

```
backend/
├── routers/            # API路由
│   ├── auth.py        # 用户认证相关API
│   └── chat.py        # 聊天相关API
├── models.py          # 数据库模型
├── schemas.py         # Pydantic模式
├── database.py        # 数据库连接配置
├── auth.py           # 认证和密码处理
├── config.py         # 配置管理
├── main.py           # 主应用文件
├── init_db.py        # 数据库初始化脚本
├── start.py          # 启动脚本
├── requirements.txt   # 依赖列表
└── README.md         # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

**Python要求**: Python 3.8+

**MySQL要求**: MySQL 5.7+ 或 MySQL 8.0+

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

修改 `config.py` 中的数据库配置：

```python
class Settings:
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "你的MySQL密码"  # 修改这里
    MYSQL_DATABASE = "course_assistant"
```

### 4. 初始化数据库

```bash
# 运行数据库初始化脚本
python init_db.py
```

### 5. 启动服务

**方法一：使用启动脚本（推荐）**

```bash
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh
```

**方法二：手动启动**

```bash
python start.py
# 或者
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 验证服务

- 🌐 **API服务**: http://localhost:8000
- 📖 **API文档**: http://localhost:8000/docs
- 🔍 **健康检查**: http://localhost:8000/api/health

## 📊 数据库设计

### users (用户表)
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| username | VARCHAR(50) | 用户名 |
| email | VARCHAR(100) | 邮箱 |
| password | VARCHAR(255) | 加密密码 |
| security_question | VARCHAR(255) | 安全问题 |
| security_answer | VARCHAR(255) | 加密的安全答案 |
| is_active | BOOLEAN | 账户状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### chat_sessions (聊天会话表)
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | VARCHAR(50) | 会话ID (前端生成) |
| user_id | INT | 用户ID (外键) |
| course_id | VARCHAR(50) | 课程ID |
| course_name | VARCHAR(100) | 课程名称 |
| title | VARCHAR(255) | 会话标题 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### chat_messages (聊天消息表)
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| session_id | VARCHAR(50) | 会话ID (外键) |
| user_id | INT | 用户ID (外键) |
| role | VARCHAR(20) | 消息角色 (user/assistant) |
| content | TEXT | 消息内容 |
| created_at | DATETIME | 创建时间 |

### reset_tokens (密码重置令牌表)
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID (外键) |
| token | VARCHAR(255) | 重置令牌 |
| expires_at | DATETIME | 过期时间 |
| is_used | BOOLEAN | 是否已使用 |
| created_at | DATETIME | 创建时间 |

## 🔌 API接口

### 认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/auth/forgot-password` | 发送密码重置邮件 |
| POST | `/api/auth/reset-password` | 重置密码 |
| POST | `/api/auth/validate-reset-token` | 验证重置令牌 |
| POST | `/api/auth/security-question` | 获取安全问题 |
| POST | `/api/auth/verify-security-answer` | 验证安全答案 |

### 聊天相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/` | 发送聊天消息 |
| GET | `/api/chat/history` | 获取聊天历史列表 |
| GET | `/api/chat/history/{session_id}` | 获取具体聊天记录 |
| DELETE | `/api/chat/history/{session_id}` | 删除聊天记录 |
| GET | `/api/chat/stats` | 获取聊天统计信息 |

## 🔧 配置说明

### 环境变量支持

可以创建 `.env` 文件来配置环境变量：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=course_assistant

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件配置（密码重置功能）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password
```

### 安全配置

1. **修改JWT密钥**: 生产环境务必修改 `SECRET_KEY`
2. **数据库权限**: 使用专门的数据库用户，避免使用root
3. **HTTPS部署**: 生产环境启用HTTPS

## 🧪 测试

### API测试

启动服务后，访问 http://localhost:8000/docs 使用Swagger UI测试API。

### 测试用例示例

```bash
# 用户注册
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "test_user",
       "email": "test@example.com",
       "password": "123456",
       "security_question": "您的小学名称？",
       "security_answer": "阳光小学"
     }'

# 用户登录
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "test_user",
       "password": "123456"
     }'
```

## 🚀 部署

### 生产环境部署

1. **使用Gunicorn**:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **使用Docker**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. **使用Nginx反向代理**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛡️ 安全注意事项

- 🔐 生产环境必须修改默认的SECRET_KEY
- 🏗️ 使用HTTPS保护API通信
- 👤 创建专门的MySQL用户，避免使用root
- 📧 配置真实的SMTP服务进行邮件发送
- 🔒 定期更新依赖包版本

## 📝 待办事项

- [ ] 集成真实的AI模型（如ChatGLM、Qwen等）
- [ ] 实现邮件发送功能
- [ ] 添加API限频保护
- [ ] 实现文件上传功能
- [ ] 添加日志记录系统
- [ ] 性能优化和缓存

## 🤝 贡献

欢迎提交Issue和Pull Request来完善这个项目！

---

**注意**: 这是课设项目的后端部分，需要配合前端Vue.js项目一起使用。