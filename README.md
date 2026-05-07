# 智课 Agent —— 融合向量匹配技术的智能复习辅助系统 V1.0

> 基于 RAG（检索增强生成）架构的多课程 AI 助教系统，支持 6 门计算机科学课程的智能问答、知识库管理与向量检索。

---

## 一、操作指南

### 1.1 环境要求

| 组件 | 版本/说明 |
|------|-----------|
| Python | 3.10+（已在 WSL 内配置 venv） |
| Node.js | 14+（Windows 端运行前端） |
| MySQL | 5.7+（WSL 内运行，端口 3306） |
| WSL | Ubuntu 2 |
| 磁盘空间 | 向量库约需 2-4 GB |

### 1.2 启动方式

#### 后端启动（在 WSL 内）

```bash
# 进入 WSL
wsl -d Ubuntu

# 激活虚拟环境并进入项目
cd /home/scvsalsgn/se_practice/backend

# 确保 MySQL 已启动
sudo service mysql start

# 安装依赖（仅首次需要）
./venv/bin/pip install -r requirements.txt

# 启动后端
./venv/bin/python main.py
```

后端启动后：
- API 服务：`http://localhost:8000`
- API 文档（Swagger）：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

#### 前端启动（在 Windows PowerShell）

```powershell
# 进入前端目录（Z: 盘为 WSL 映射盘）
cd Z:\home\scvsalsgn\se_practice\frontend

# 安装依赖（仅首次需要）
npm install

# 启动开发服务器
npm run serve
```

前端启动后：
- 用户页面：`http://localhost:8080`
- 管理员控制台：`http://localhost:8080/admin/dashboard`

#### 一键启动（从 Windows）

在 Windows 终端中同时启动前后端：

```powershell
# 终端1 - 启动后端
wsl -d Ubuntu -- bash -c "cd /home/scvsalsgn/se_practice/backend && sudo service mysql start && ./venv/bin/python main.py"

# 终端2 - 启动前端
cd Z:\home\scvsalsgn\se_practice\frontend && npm run serve
```

### 1.3 账号说明

#### 管理员账号

管理员通过 `.env` 文件中的三项配置自动管理（位于 `backend/.env`）：

```env
ADMIN_USERNAMES=admin
ADMIN_DEFAULT_PASSWORD=admin123
ADMIN_DEFAULT_EMAIL=admin@local.dev
```

**后端启动时自动创建**：如果设定了 `ADMIN_DEFAULT_PASSWORD`，系统会在每次启动时扫描 `ADMIN_USERNAMES` 列表，对不存在的用户名自动创建管理员账号。无需手动注册，启动后直接用配置的密码登录即可。

**手动方式（备选）**：如果未设定 `ADMIN_DEFAULT_PASSWORD`，则需要在前端注册页面手动注册与 `ADMIN_USERNAMES` 中匹配的用户名，系统将自动赋予管理员权限。

**多个管理员**：`ADMIN_USERNAMES=admin,teacher1,teacher2`（逗号分隔）

#### 普通用户账号

在前端注册页面正常注册即可。普通用户无管理员控制台入口，无法访问 `/admin/*` 路由。

### 1.4 管理员功能操作指南

管理员控制台包含 4 个功能页面：

#### 系统概览（`/admin/dashboard`）

- 查看所有 6 门课程的整体状态
- 查看课程总数、已上传教材数、已构建向量库数、AI 已加载课程数
- 查看运行状态：API 状态、AI 服务状态、模型名称、API Key 配置状态

#### 课程知识库（`/admin/courses`）

**上传教材**：
1. 点击某课程的「上传教材」按钮
2. 在弹出的对话框中拖入或选择 `.docx` 教材文件
3. 上传成功后教材状态变为「已上传」

**构建向量库**：
1. 确保教材已上传（「已上传」状态）
2. 点击「构建」按钮
3. 确认后弹出任务状态弹窗，实时显示构建进度
4. 构建成功后系统自动重载该课程，用户可立即使用

**重载向量库**：
- 如果向量库已构建但 AI 服务未加载（例如重启后），点击「重载」

**检索测试**：
- 点击「检索」跳转到检索测试页面，输入查询词验证向量检索效果

#### 检索测试（`/admin/retrieval-test`）

1. 选择课程
2. 输入测试问题（如"瀑布模型是什么？"）
3. 点击「开始检索」
4. 查看：
   - 原始查询 → 优化后查询（展示查询优化规则效果）
   - 检索到的教材片段（含 metadata）

#### 系统状态（`/admin/system`）

- 查看 API、数据库、AI 服务运行状态
- 查看当前使用的 AI 模型和嵌入模型
- 查看已加载的课程列表
- 「重新加载 AI 服务」按钮：从磁盘重新加载所有已构建课程的向量数据库

### 1.5 知识库构建流程

```
管理员登录 → 上传课程 DOCX 教材
           → 点击「构建」生成向量数据库
           → 系统自动重载该课程
           → 普通用户选择该课程提问
           → 系统基于新知识库检索并生成回答
```

### 1.6 配置文件说明

后端配置文件 `backend/.env`：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=course_assistant

# JWT 安全配置
SECRET_KEY=你的随机密钥
ARK_API_KEY=你的豆包ARK_API_KEY
DOUBAO_MODEL=doubao-seed-1-6-thinking-250715

# 管理员用户名列表（逗号分隔）
ADMIN_USERNAMES=admin
```

---

## 二、系统架构

### 2.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI | Python 异步 Web 框架 |
| 数据库 | MySQL + SQLAlchemy ORM | 用户、会话、消息持久化存储 |
| 向量数据库 | ChromaDB | 课程知识库向量存储与语义检索 |
| 嵌入模型 | BAAI/bge-large-zh-v1.5 | 中文文本向量化（HuggingFace） |
| AI 模型 | 豆包 Doubao-seed-1.6 | 火山引擎 Ark API（大语言模型生成回答） |
| 前端框架 | Vue 2 + Vuex + Vue Router | 单页应用 |
| UI 组件库 | Element UI | 企业级 UI 组件 |
| 认证 | JWT + pbkdf2_sha256 | Bearer Token 认证 + 密码哈希 |

### 2.2 项目结构

```
se_practice/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理（从 .env 读取）
│   ├── database.py          # SQLAlchemy 数据库连接
│   ├── models.py            # 数据模型（User/ChatSession/ChatMessage/KnowledgeBuildTask）
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── auth.py              # JWT 认证、密码哈希、权限依赖
│   ├── ai_service.py        # RAG AI 服务（向量检索 + 豆包 AI 调用）
│   ├── .env                 # 环境变量（不入 git）
│   ├── requirements.txt     # Python 依赖
│   ├── routers/
│   │   ├── auth.py          # 用户认证 API（注册/登录/密码重置）
│   │   ├── chat.py          # 聊天 API（消息发送/历史/统计）
│   │   └── admin.py         # 管理员 API（知识库构建/检索测试/系统状态）
│   ├── services/
│   │   └── knowledge_service.py  # 知识库管理服务（教材提取/向量库构建）
│   ├── course_management/
│   │   ├── course_config.py      # 6 门课程配置（术语/查询优化规则）
│   │   ├── build_course_knowledge.py  # 命令行构建脚本
│   │   └── build_all_courses.py       # 批量构建脚本
│   ├── knowledge_base/      # 教材文件存放目录（DOCX）
│   └── vector_databases/    # ChromaDB 向量数据库持久化目录
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue    # 登录页
│   │   │   ├── Register.vue # 注册页
│   │   │   ├── Home.vue     # 课程主页
│   │   │   ├── Chat.vue     # AI 对话页
│   │   │   ├── History.vue  # 历史记录页
│   │   │   └── admin/
│   │   │       ├── AdminLayout.vue      # 管理员布局
│   │   │       ├── AdminDashboard.vue   # 系统概览
│   │   │       ├── AdminCourses.vue     # 课程知识库管理
│   │   │       ├── AdminRetrievalTest.vue # 检索测试
│   │   │       └── AdminSystem.vue      # 系统状态
│   │   ├── store/index.js   # Vuex 状态管理
│   │   ├── router/index.js  # 路由配置（含管理员权限守卫）
│   │   ├── api/index.js     # Axios API 封装
│   │   ├── App.vue          # 根组件（含导航栏）
│   │   └── main.js          # 应用入口
│   ├── vue.config.js        # Webpack 配置（WSL 轮询模式）
│   └── package.json
└── 旧版本/                   # 历史文档归档
```

### 2.3 数据库设计

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 用户表 | id, username, email, password(哈希), is_admin, is_active |
| `chat_sessions` | 聊天会话表 | id, user_id, course_id, course_name, title |
| `chat_messages` | 聊天消息表 | id, session_id, user_id, role(user/assistant), content |
| `reset_tokens` | 密码重置令牌表 | id, user_id, token, expires_at, is_used |
| `knowledge_build_tasks` | 知识库构建任务表 | id, course_id, status, log, document_count |

### 2.4 API 接口一览

#### 认证接口（`/api/auth`）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| POST | `/auth/register` | 用户注册 | - |
| POST | `/auth/login` | 用户登录 | - |
| GET | `/auth/me` | 获取当前用户信息 | Bearer |
| POST | `/auth/forgot-password` | 发送密码重置邮件 | - |
| POST | `/auth/reset-password` | 重置密码 | - |
| POST | `/auth/validate-reset-token` | 验证重置令牌 | - |
| POST | `/auth/security-question` | 获取安全问题 | - |
| POST | `/auth/verify-security-answer` | 验证安全答案 | - |

#### 聊天接口（`/api/chat`）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| POST | `/chat/` | 发送聊天消息 | Bearer |
| GET | `/chat/history` | 获取聊天历史列表 | Bearer |
| GET | `/chat/history/{id}` | 获取具体聊天详情 | Bearer |
| DELETE | `/chat/history/{id}` | 删除聊天记录 | Bearer |
| GET | `/chat/stats` | 获取聊天统计 | Bearer |

#### 管理员接口（`/api/admin`）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/admin/dashboard` | 系统概览 | Admin |
| GET | `/admin/courses` | 课程知识库状态列表 | Admin |
| POST | `/admin/courses/{id}/material` | 上传教材（DOCX） | Admin |
| POST | `/admin/courses/{id}/knowledge/build` | 构建向量知识库 | Admin |
| GET | `/admin/knowledge/tasks` | 构建任务列表 | Admin |
| GET | `/admin/knowledge/tasks/{id}` | 查询构建任务状态 | Admin |
| POST | `/admin/retrieval-test` | 向量检索测试 | Admin |
| GET | `/admin/system/health` | 系统健康状态 | Admin |
| POST | `/admin/ai/reload` | 重载全部课程向量库 | Admin |
| POST | `/admin/ai/reload/{id}` | 重载指定课程向量库 | Admin |

---

## 三、核心功能说明

### 3.1 RAG 智能问答流程

```
用户选择课程并输入问题
        ↓
课程特定查询优化（如"瀑布模型" → "瀑布模型 软件开发模型"）
        ↓
从该课程 ChromaDB 向量库中检索 Top 5 相关教材片段
        ↓
将检索到的教材片段作为上下文，构造 RAG Prompt
        ↓
调用豆包大语言模型生成基于教材内容的回答
        ↓
返回回答，保存对话历史
```

### 3.2 知识库三层索引策略

系统对教材文档采用三层索引策略以提高检索质量：

| 层级 | 类型 | 优先级 | 说明 |
|------|------|:---:|------|
| 概念增强层 | `concept_enhanced` | 1 | 围绕课程重要术语提取上下文窗口（前后 2-3 段） |
| 段落上下文层 | `paragraph_with_context` | 2 | 每个段落附带前后段落作为上下文 |
| 细粒度分块层 | `fine_grained` | 3 | RecursiveCharacterTextSplitter 按 300 字符切分，100 字符重叠 |

### 3.3 课程查询优化

每门课程配置了专用查询优化规则。例如：

| 课程 | 用户输入 | 系统优化查询 |
|------|----------|-------------|
| 软件工程 | "生命周期" | "软件开发生命周期 软件过程" |
| 操作系统 | "进程管理" | "进程 进程调度 进程同步" |
| 计算机网络 | "OSI模型" | "OSI七层模型 网络协议栈" |

### 3.4 管理员知识库管理

- **教材上传**：支持 DOCX 格式教材文件上传
- **异步构建**：后台线程执行向量库构建，前端轮询任务状态
- **自动热重载**：构建完成后自动重载课程向量库，无需重启服务
- **检索测试**：输入查询词即可验证向量检索效果和查询优化规则

---

## 四、支持的课程

| 课程 ID | 课程名称 | 教材文件 |
|---------|----------|----------|
| `software-engineering` | 软件工程 | software-engineering.docx |
| `operating-system` | 操作系统 | operating-system.docx |
| `computer-network` | 计算机网络 | computer-network.docx |
| `data-structure` | 数据结构与算法 | data-structure.docx |
| `database` | 数据库系统 | database.docx |
| `compiler` | 编译原理 | compiler.docx |

---

## 五、本次改造内容（2026-05-06）

### 5.1 改造目标

为软著补正补齐管理员 GUI，使后台知识库构建、教材上传、向量库状态查看、检索测试、AI 服务重载等功能可通过界面操作，并修复安全配置问题。

### 5.2 后端改造

| 文件 | 操作 | 说明 |
|------|:---:|------|
| `config.py` | 修改 | 移除硬编码密钥和密码；新增 `ADMIN_USERNAMES`、`KNOWLEDGE_BASE_DIR`、`VECTOR_DB_DIR` 配置项；所有敏感配置改为从 `.env` 环境变量读取 |
| `models.py` | 修改 | `User` 表新增 `is_admin` 字段；新增 `KnowledgeBuildTask` 表（知识库构建任务记录） |
| `schemas.py` | 修改 | `UserResponse` 增加 `is_admin` 字段；新增 5 个管理员接口 Pydantic 模型 |
| `auth.py` | 修改 | 新增 `get_current_admin_user` 依赖函数（非管理员返回 403） |
| `routers/auth.py` | 修改 | 注册时自动根据 `ADMIN_USERNAMES` 设置管理员权限 |
| `ai_service.py` | 修改 | 新增三个方法：`reload_course()` 重载单课程、`reload_all_courses()` 重载全部（含汇总统计）、`test_retrieval()` 检索测试 |
| `main.py` | 修改 | 注册 `admin.router` |
| `requirements.txt` | 修改 | 新增 `langchain-huggingface`、`chromadb`、`python-docx`、`python-multipart`、`sentence-transformers` |
| `.env` | **新建** | 所有敏感配置抽离到此文件（不入 git） |
| `services/__init__.py` | **新建** | 服务包初始化 |
| `services/knowledge_service.py` | **新建** | 知识库管理核心服务：教材提取（`extract_course_content`）、向量库构建（`build_course_vectordb`）、课程状态查询（`get_all_course_status`）、教材保存（`save_course_material`） |
| `routers/admin.py` | **新建** | 12 个管理员 API 端点：系统概览、课程列表、教材上传、知识库构建（BackgroundTasks 异步）、任务状态轮询、检索测试（使用 Pydantic 模型校验）、系统健康、AI 服务重载 |

### 5.3 前端改造

| 文件 | 操作 | 说明 |
|------|:---:|------|
| `store/index.js` | 修改 | state/mutations/getters 增加 `isAdmin`；登录/登出时同步持久化 |
| `api/index.js` | 修改 | 新增 `adminAPI`（11 个接口方法） |
| `main.js` | 修改 | `$api` 注入 `adminAPI` |
| `Login.vue` | 修改 | 登录成功时传递 `isAdmin` 到 store |
| `router/index.js` | 修改 | 新增 `/admin/*` 嵌套路由（4 个子页面）；路由守卫增加管理员权限校验 |
| `App.vue` | 修改 | 管理员可见「管理员控制台」导航入口（`isAdmin` 计算属性） |
| `vue.config.js` | 修改 | `configureWebpack.watchOptions` 启用 `poll: 1000` 轮询模式（修复 WSL 网络文件系统 `fs.watch` 不兼容问题） |
| `views/admin/AdminLayout.vue` | **新建** | 管理员控制台布局：蓝紫渐变头部 + 侧边栏导航（4 项）+ `<router-view>` 内容区 |
| `views/admin/AdminDashboard.vue` | **新建** | 系统概览页：4 统计卡片 + 运行状态描述 + 课程知识库概览表格 |
| `views/admin/AdminCourses.vue` | **新建** | 课程知识库管理页：课程状态表格 → 上传教材（拖拽 Dialog） → 构建向量库（确认 + 后台任务轮询弹窗） → 重载 → 检索跳转 |
| `views/admin/AdminRetrievalTest.vue` | **新建** | 向量检索测试页：选课 + 输入查询 + Top K 设置 → 展示原始查询/优化查询/检索片段/metadata |
| `views/admin/AdminSystem.vue` | **新建** | 系统状态页：API/DB/AI 状态描述 + 已加载课程表格 + 重载 AI 服务按钮 |

### 5.4 数据库迁移

```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

`knowledge_build_tasks` 表由 SQLAlchemy `Base.metadata.create_all()` 在启动时自动创建。

### 5.5 Bug 修复记录

| 问题 | 现象 | 修复 |
|------|------|------|
| 缺少 `python-multipart` | 后端启动时报 `RuntimeError: Form data requires "python-multipart"` | 安装到 venv |
| `watchOptions` 位置错误 | 前端启动时报 `options has an unknown property 'watchOptions'` | 从 `devServer` 移至 `configureWebpack`（webpack-dev-server v5 不支持此选项） |
| WSL 文件监听不兼容 | 前端启动时报 `Error: EISDIR: illegal operation on a directory, watch` | 启用 webpack `watchOptions.poll: 1000` 轮询模式 |
| `is_admin` 列不存在 | 后端查询 users 表报错 | 执行 `ALTER TABLE` 手动添加字段 |

---

## 六、待办事项

- [ ] 完善邮件发送功能（密码重置当前依赖打印 Token 到控制台）
- [ ] 添加 API 限频保护
- [ ] 生产环境使用 Gunicorn + Uvicorn Worker 部署
- [ ] 向量库构建进度细化（当前仅日志文本，可增加百分比进度）
- [ ] 支持 PDF 教材上传（当前仅 DOCX）

---

**更新记录**：
- v1.0: 初始版本（单课程架构）
- v2.0: 多课程 RAG 架构升级（课程配置、查询优化、三层索引）
- v2.1: 管理员 GUI 改造（知识库管理控制台、安全配置优化、WSL 兼容性修复）
