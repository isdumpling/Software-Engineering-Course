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

### 5.5 Bug 修复实录

> 以下记录从零构建管理员 GUI 及其后端过程中遇到的每一个 bug，包含完整排查过程。

#### Bug 索引

| # | 问题 | 分类 | 根因一句话 |
|---|------|------|-----------|
| 1 | 后端启动崩溃 `python-multipart` | 依赖缺失 | FastAPI `UploadFile` 需要此包但未安装 |
| 2 | `is_admin` 列不存在 | 数据库迁移 | SQLAlchemy `create_all` 不修改已有表 |
| 3 | 前端启动 `EISDIR: illegal operation on a directory` | WSL 兼容 | Plan 9 网络文件系统不支持 `fs.watch` |
| 4 | `options has an unknown property 'watchOptions'` | API 版本 | webpack-dev-server v5 不再接受此配置项 |
| 5 | 豆包 AI 返回 fallback 提示"不可用" | API 端点 | 模型名过时 + API 格式需迁移到 v3 |
| 6 | v3 API 响应 `'Response' object has no attribute 'output_text'` | API 适配 | v3 响应结构是 `output[1].content[0].text` |
| 7 | DOCX 上传 422 | 数据构造 | FormData 被嵌套包装，文件内容变成 `[object FormData]` |
| 8 | 管理员面板首次加载 30+ 秒 | 性能 | `get_course_stats()` 每门课加载一次 1.3GB BGE 模型 |
| 9 | CORS 预检失败被缓存，后端重启后请求全被拦截 | 浏览器缓存 | `max-age: 600` 会缓存失败的预检 |
| 10 | Element UI `<el-table>` 数据已加载但显示"暂无数据" | 前端渲染 | `v-loading` 指令在表格上的已知 bug |

---

#### Bug 1：`python-multipart` 缺失导致后端完全无法启动

**现象**：
```
RuntimeError: Form data requires "python-multipart" to be installed.
```

整个后端进程崩溃，无法启动。错误发生在模块导入阶段——`routers/admin.py` 中 `upload_course_material` 函数签名包含 `file: UploadFile = File(...)`，FastAPI 在注册路由时检测到 `File()` 依赖但找不到 `python-multipart`。

**排查**：
```bash
# 查看完整错误栈
wsl -d Ubuntu -- bash -c "cd /home/scvsalsgn/se_practice/backend && ./venv/bin/python main.py"

# 关键输出：Traceback → routers/admin.py → ensure_multipart_is_installed()
# 错误发生在 "from routers import auth, chat, admin" 这一行
```

**为什么是"启动时"而非"调用时"报错**：FastAPI 在装饰器 `@router.post(...)` 执行时就解析函数签名中的依赖，发现 `UploadFile` 需要 multipart 支持，立即抛异常。**这和大多数 Python 依赖错误不同——不是在运行时调用函数时报错，而是在 import 模块时报错。**

**修复**：
```bash
# 安装到 venv
./venv/bin/pip install python-multipart
```

**后续预防**：在 `requirements.txt` 中加入 `python-multipart`。

---

#### Bug 2：`is_admin` 列不存在

**现象**：后端日志中出现 SQL 错误，`users` 表没有 `is_admin` 列。

**排查**：
```bash
# 用 venv Python 直接查数据库
/home/scvsalsgn/se_practice/backend/venv/bin/python -c "
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='12345678', database='course_assistant')
cur = conn.cursor()
cur.execute(\"SHOW COLUMNS FROM users LIKE 'is_admin'\")
print(cur.fetchone())  # → None，列不存在
conn.close()
"
```

**根因**：SQLAlchemy 的 `Base.metadata.create_all()` 只会创建**不存在的表**，不会修改**已存在的表**。`users` 表在之前就已创建，新增的 `is_admin` 字段不会被自动添加。

**修复**：
```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

> 💡 **通用原则**：SQLAlchemy 的 `create_all` 适合新项目初始化。已有数据库的 schema 变更需用 Alembic 等迁移工具，或手动执行 SQL。

---

#### Bug 3 & 4：WSL 文件监听 + watchOptions 位置错误

**现象**（对应 Bug 3）：
```
Error: EISDIR: illegal operation on a directory, watch 'Z:/home/scvsalsgn/se_practice/frontend/public'
```

前端 dev server 启动后立即崩溃。错误来自 `chokidar`（webpack 使用的文件监听库）。

**排查**：
- 用户是从 Windows PowerShell 运行 `npm run serve`，项目在 `Z:\` 盘
- `Z:` 盘是 `\\wsl.localhost\Ubuntu` 的网络映射
- WSL 的 Plan 9 网络文件系统**不支持 `fs.watch` 系统调用**
- chokidar 默认使用 `fs.watch` 来监听文件变更

**第一次修复尝试——放错位置**：
```javascript
// vue.config.js — 错误位置（webpack-dev-server v5 不接受）
devServer: {
    watchOptions: { poll: 1000, ignored: /node_modules/ }  // ← 这里不行
}
```

**现象**（对应 Bug 4）：
```
ValidationError: options has an unknown property 'watchOptions'.
```

**根因**：`watchOptions` 是 **webpack** 的配置项，不是 **webpack-dev-server** 的。vue.config.js 中：
- `devServer` → 传给 webpack-dev-server
- `configureWebpack` → 传给 webpack

在 webpack-dev-server v4 中，`devServer.watchOptions` 是有效的。但用户环境是 v5，该配置项已移除。

**正确修复**：
```javascript
// vue.config.js — 正确位置
configureWebpack: {
    watchOptions: {
        poll: 1000,         // 每 1000ms 轮询一次文件变更
        ignored: /node_modules/
    }
}
```

---

#### Bug 5 & 6：豆包 AI 端点迁移到 v3 API

**现象**（Bug 5）：AI 聊天返回 fallback 回复——"抱歉，AI服务暂时不可用。"

**排查**：
```bash
# 查看后端日志中的 AI 调用错误
grep -E '调用豆包|Error code' /tmp/backend.log
```

输出：
```
调用豆包AI失败: Error code: 404 - {
  'error': {
    'code': 'InvalidEndpointOrModel.NotFound',
    'message': 'The model or endpoint doubao-seed-1-6-thinking-250715 does not exist...'
  }
}
```

**根因**：`.env` 中的模型端点 `doubao-seed-1-6-thinking-250715` 已不存在。用户在火山引擎控制台创建了新接入点 `ep-20260506231534-p9wm4`，需要：
1. 更换模型名
2. 新接入点使用 v3 API（`responses.create`），而旧代码用 `chat.completions.create`
3. 需要指定 `base_url`

**第一次修复——更新 `.env` 和客户端初始化**：
```python
# ai_service.py
self.client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=self.api_key
)
```

```env
# .env
DOUBAO_MODEL=ep-20260506231534-p9wm4
```

**现象**（Bug 6）：修改后仍返回 fallback。日志显示：
```
'Response' object has no attribute 'output_text'
```

**排查过程**——直接在 Python 中探查 v3 Response 对象结构：

```python
from volcenginesdkarkruntime import Ark
client = Ark(base_url='...', api_key='...')
resp = client.responses.create(
    model='ep-20260506231534-p9wm4',
    input=[{'role': 'user', 'content': '你好'}]
)

# 探查对象属性
print([a for a in dir(resp) if not a.startswith('_')])
# → ['output', 'text', 'model', 'usage', ...]

print(type(resp.output), len(resp.output))
# → <class 'list'>, 2

# output[0] → ResponseReasoningItem (思考过程)
# output[1] → ResponseOutputMessage (实际回答)
print(resp.output[1].content[0].text)
# → "你好呀！😊 很高兴和你打招呼~"
```

**正确修复**：
```python
# 遍历 output 列表，提取 ResponseOutputMessage 中的文本
ai_response = ""
for item in completion.output:
    content = getattr(item, "content", [])
    for c in content:
        if getattr(c, "text", None):
            ai_response += c.text
```

> 💡 **探查未知对象的方法**：`dir(obj)` 看属性名 → `type(obj.attr)` 看类型 → `repr(obj.attr)` 看内容。逐层深入直到拿到数据。

---

#### Bug 7：DOCX 上传返回 422

**现象**：前端上传文件返回 `422 Unprocessable Entity`，后端日志显示 422。

**排查——先确认后端是否正常**：
```bash
# 用 curl 模拟 multipart 上传，绕开前端
curl -X POST "http://localhost:8000/api/admin/courses/database/material" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test.docx"
# → 200 OK ✓  后端没问题
```

**然后追踪前端调用链**——发现数据被重复包装：
```
AdminCourses.vue: new FormData().append('file', rawFile)  → FormData ✓
    ↓ 传给
adminAPI.uploadMaterial(courseId, formData)
    ↓ 内部又
new FormData().append('file', formData)  → FormData 被 toString() 成字符串 ✗
```

**修复**：`adminAPI.uploadMaterial` 直接发送调用方传入的 FormData，不再重复 `new FormData()`。

---

#### Bug 8：管理员面板 API 响应 30+ 秒

**详见第七章完整排查过程。** 根因：`course_config.py:get_course_stats()` 每门课加载一次 1.3GB BGE 嵌入模型。

---

#### Bug 9：CORS 预检失败缓存

**现象**：后端 uvicorn 重启后，浏览器中所有 admin API 请求状态显示 `ERR_ABORTED`，后端日志完全看不到这些请求。

**根因**：后端重启期间，浏览器发出 OPTIONS 预检请求但得不到响应（超时/连接拒绝）。`Access-Control-Max-Age: 600` 意味着浏览器把这个**失败结果缓存了 10 分钟**。10 分钟内所有跨域请求直接被浏览器拦截，根本不发送。

**修复**：`CORSMiddleware` 加 `max_age=0`，开发阶段禁止预检缓存。

---

#### Bug 10：Element UI 表格首次加载不渲染数据

**现象**：Vue data 中 `courses` 数组有 6 个元素，但 `<el-table>` 始终显示"暂无数据"。点击刷新按钮后正常。

**排查**——确认数据确实在 Vue 中：
```javascript
// 浏览器 Console
const app = document.querySelector('#app').__vue__
const comp = findComponent(app, 'AdminCourses')
console.log(comp.courses)            // → Array(6)，数据完整 ✓
console.log(comp.courses.length)     // → 6 ✓
console.log(comp.loading)            // → false ✓
// 但 DOM 中表格显示 "暂无数据"
```

**根因**：Element UI 的 `v-loading` 指令直接放在 `<el-table>` 上时，loading 状态从 `true` 切换到 `false` 的过渡动画会阻塞表格数据的响应式更新。这是一个已知的 Element UI bug。

**修复**：
```html
<!-- 修复前 -->
<el-table :data="courses" v-loading="loading" border>

<!-- 修复后：v-loading 移到外层 div，表格加 v-if 条件渲染 -->
<div v-loading="loading">
  <el-table v-if="courses.length" :data="courses" border>
  <el-empty v-else />
</div>
```

---

## 六、待办事项

- [ ] 完善邮件发送功能（密码重置当前依赖打印 Token 到控制台）
- [ ] 添加 API 限频保护
- [ ] 生产环境使用 Gunicorn + Uvicorn Worker 部署
- [ ] 向量库构建进度细化（当前仅日志文本，可增加百分比进度）
- [ ] 支持 PDF 教材上传（当前仅 DOCX）

---

## 七、管理员面板问题排查实录（深度剖析）

> 本节完整记录"管理员面板四个栏目一直转圈加载"问题的排查全过程。  
> 目标：让读者理解排查思路，掌握可复用的诊断方法。

### 7.1 初始现象

用户反馈：
- 前端其他功能正常（登录、聊天、历史记录）
- **管理员控制台四个栏目均无法加载**，页面长时间转圈后提示"加载失败"
- 检索测试页面的课程下拉框直接显示"无数据"
- 后端终端看不到 admin API 请求，只看到 `/api/auth/login` 和 `/api/chat/stats`

### 7.2 排查思维框架

遇到"前端部分功能不正常"时，按以下层次逐级隔离：

```
用户浏览器 → 前端代码（JS/Vue）→ HTTP 请求 → 后端代码（Python/FastAPI）
                                                      ↓
用户看到结果 ← 前端渲染 ← HTTP 响应 ←                数据库/外部服务
```

**核心原则**：每一层都分别验证，找到最先断掉的环节。

### 7.3 第一轮：确认后端 API 本身是否正常

**思路**：绕开前端，直接用 curl 调用后端 API。如果 curl 也失败 → 后端问题。如果 curl 成功 → 前端或网络问题。

**命令**（在 WSL 终端中执行）：

```bash
# 1. 先登录获取 Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 测试管理员 API
curl -s -w '\nHTTP %{http_code}\n' \
  http://localhost:8000/api/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"

curl -s -w '\nHTTP %{http_code}\n' \
  http://localhost:8000/api/admin/courses \
  -H "Authorization: Bearer $TOKEN"
```

**结果**：返回 200，JSON 数据正确（6 门课程，3 门已加载向量库）。

**结论**：后端 API 本身正常运作，问题在前端侧。

> 💡 **你面对类似问题时**：永远先从后端入手。用 curl 或 Postman 直接调 API，确认后端没挂。90% 的"前端加载不出来"其实都是后端问题（进程挂了、数据库断连、接口报错）。

### 7.4 第二轮：确认前端代码是否被加载执行

**思路**：前端的 admin 页面是我们新写的代码。需要确认浏览器加载的是最新版本，并且 admin 组件确实在执行。

**方法**：在 Vue 组件中临时添加 `console.log` 诊断日志：

```javascript
// AdminDashboard.vue
created() {
  console.log('[AdminDashboard] created, $api keys:', Object.keys(this.$api))
  this.loadDashboard()
},
methods: {
  async loadDashboard() {
    console.log('[AdminDashboard] loadDashboard called')
    // ...
  }
}
```

**现象**（用户浏览器 Console 输出）：
```
[AdminDashboard] created, $api keys: ['authAPI', 'chatAPI', 'commonAPI', 'adminAPI']
[AdminDashboard] loadDashboard called
```

**结论**：
- `$api.adminAPI` 注入成功 ✓
- `created()` 正常触发 ✓
- `loadDashboard()` 被调用 ✓
- 但之后没有 `result` 或 `error` 日志 → **API 调用挂起（hang），既不 resolve 也不 reject**

> 💡 **你面对类似问题时**：在组件关键生命周期（`created`、`mounted`）和 API 调用前后加 `console.log`，确认执行到了哪一步。如果某一步之后没有任何输出，说明卡在这一步。

### 7.5 第三轮：定位 HTTP 请求卡在哪里

**思路**：API 调用挂起，可能是：
- A) 请求根本**没发出去**（JS 报错、被拦截）
- B) 发出去了但**没到达后端**（代理未转发、CORS 拦截）
- C) 到达后端但**响应没回来**（后端处理中、连接断开）
- D) 响应回来了但**前端没处理**（axios 拦截器异常）

**关键发现——后端日志比对**：

用户后端日志中完全没有 `/api/admin/` 开头的请求！只有 `/api/auth/login` 和 `/api/chat/stats`。

这意味着 admin 请求要么没发出去，要么在代理层丢失了。

**进阶诊断——浏览器 Network 面板**：

打开 F12 → Network 标签，刷新管理员页面，观察 `/api/admin/` 请求的状态：

- 请求出现但状态显示 `(pending)` → 卡在发送或等待响应中
- 请求出现但状态显示红色 `(failed)` → CORS 或网络错误
- 请求根本没有出现 → JS 代码未执行或请求被 abort

**此时的现象**：请求以 `ERR_ABORTED` 失败，或处于 `(pending)` 永不完成。

> 💡 **你面对类似问题时**：打开 F12 → Network 面板是关键。过滤只看 XHR/Fetch 请求，观察每个 `/api/` 请求的状态码和时间线。

### 7.6 第四轮：跨请求对比——为什么 chat 正常但 admin 异常？

这是整个排查中最关键的一步。chat API 和 admin API 使用同样的 axios 实例、同样的 baseURL、同样的认证方式，为什么一个正常一个异常？

**对比测试（在浏览器 Console 中执行）**：

```javascript
// 测试 1：fetch 方式调用 admin API（绕过 axios）
const headers = {}
headers['Authorization'] = 'Bearer ' + localStorage.getItem('token')
const resp = await fetch('http://localhost:8000/api/admin/dashboard', { headers })
// → 200 OK ✓

// 测试 2：XHR 方式调用 admin API（模拟 axios 内部行为）
const xhr = new XMLHttpRequest()
xhr.open('GET', 'http://localhost:8000/api/admin/dashboard')
xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('token'))
xhr.timeout = 5000
xhr.send()
// → TIMEOUT ✗

// 测试 3：XHR 方式调用 chat API（对照组）
xhr.open('GET', 'http://localhost:8000/api/chat/history')
// → 200 OK ✓
```

**结果矩阵**：

| 请求方式 | `/api/chat/` | `/api/admin/` |
|----------|:---:|:---:|
| `fetch()` | ✓ 200 | ✓ 200 |
| `XMLHttpRequest` | ✓ 200 | ✗ **超时** |

**关键洞察**：同样是 XHR，chat 路径正常，admin 路径超时。说明问题不在 axios/XHR 本身，而在**请求的响应速度**。

### 7.7 第五轮：计时分析——锁定真凶

**最终诊断（在浏览器 Console 中执行）**：

```javascript
// 计时对比：chat vs admin 的响应速度
const results = []
for (const path of ['/api/chat/stats', '/api/admin/dashboard', '/api/admin/courses']) {
  const t0 = Date.now()
  await fetch('http://localhost:8000' + path, { headers })
  results.push({ path, time: Date.now() - t0 })
}
console.table(results)
```

**结果**：

| path | time |
|------|-----:|
| `/api/chat/stats` | **331ms** |
| `/api/admin/dashboard` | **31,379ms** |
| `/api/admin/courses` | **32,944ms** |

**Admin API 比 chat API 慢 100 倍！** 请求并没有挂起——它在等待响应，只是响应需要 30+ 秒。前端 axios 超时设为 180 秒所以不会报错，但用户看到的就是"一直转圈"。

### 7.8 追溯代码：找到慢的根因

admin dashboard 和 courses 端点都调用了 `get_all_course_status()`：

```
routers/admin.py: get_all_course_status(ai_instance)
  → services/knowledge_service.py: get_all_course_status()
    → course_management/course_config.py: CourseManager.list_all_course_stats()
      → course_management/course_config.py: get_course_stats()  ← 每个课程调用一次
```

`get_course_stats()` 中对有向量库的课程执行了：

```python
# course_config.py 第 222-224 行（修复前）
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")
vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)
stats["document_count"] = len(vectordb._collection.get()['documents'])
```

这段代码只是要**统计文档数量**，但它做了两件极其昂贵的事：
1. `HuggingFaceEmbeddings(...)` — 从磁盘加载 1.3GB 的 BGE 中文嵌入模型到内存
2. `Chroma(persist_directory=..., embedding_function=...)` — 用该模型初始化 ChromaDB 连接

3 门有向量库的课程 × 每门 ~10 秒 = **总计 ~31 秒**。

### 7.9 修复

只需统计文档数，不需要嵌入模型。ChromaDB 底层使用 SQLite 存储，可以用 `chromadb.PersistentClient` 直连：

```python
# 修复后（course_config.py）
import chromadb
client = chromadb.PersistentClient(path=db_path)
collections = client.list_collections()
if collections:
    stats["document_count"] = collections[0].count()
```

**效果**：31,379ms → 322ms，**快 97 倍**。

### 7.10 附：排查过程中发现的其他问题

| 问题 | 原因 | 修复 |
|------|------|------|
| Element UI `v-loading` 用在 `<el-table>` 上首次渲染不显示数据 | Element UI 已知 bug，`v-loading` 过渡动画阻塞表格数据绑定更新 | 移除外层 `<div v-loading>` + 表格加 `v-if` 条件渲染 |
| 后端 uvicorn `reload=True` 在文件变更后自动重启时卡住 | AI 服务初始化（加载 BGE 模型）过程中响应极慢，重启期间请求全部挂起 | 开发期间的已知副作用，生产环境关闭 reload |
| CORS 预检失败被浏览器缓存 10 分钟 | 后端挂了期间浏览器发出 OPTIONS 预检失败，`max-age=600` 导致失败结果被缓存 | `CORSMiddleware` 加 `max_age=0` 禁用预检缓存 |
| WSL Plan 9 文件系统不支持 `fs.watch` | Node.js chokidar 在 WSL 网络盘上无法监听文件变更 | `vue.config.js` 启用 `watchOptions.poll: 1000` |
| 豆包 API 模型端点 404 | 旧端点 `doubao-seed-1-6-thinking-250715` 已不存在 | 改为新接入点 ID `ep-20260506231534-p9wm4`，API 切换到 v3 `responses.create` |

### 7.11 排查方法论总结

```
第1步：后端自检
   curl 直接调 API → 确认后端是否正常
   看后端日志 → 确认请求是否到达、是否报错

第2步：前端功能确认  
   打开浏览器 F12 → Console → 看 JS 错误
   在关键代码加 console.log → 确认执行到了哪一步

第3步：网络层检查
   F12 → Network 面板 → 只看 XHR/Fetch
   对比正常请求和异常请求的状态码、耗时

第4步：隔离变量
   对比不同路径（chat vs admin）
   对比不同调用方式（fetch vs XHR）
   通过交叉对比找到差异

第5步：计时定位
   在 Console 中手动发起请求并计时
   哪个请求慢，就跟踪哪个请求对应的后端代码

第6步：代码追溯
   从 API 路由 → service 层 → 底层函数
   找到耗时操作 → 优化或替换
```

### 7.12 可复用的诊断命令速查

```bash
# === 后端诊断 ===
# 检查进程是否运行
fuser 8000/tcp                              # WSL/Linux: 查看端口占用
netstat -ano | findstr ":8000"              # Windows: 查看端口占用

# 直接测试 API
curl -s -w '\n%{http_code}\n' http://localhost:8000/api/health
curl -s http://localhost:8000/openapi.json | python3 -c \
  "import sys,json; [print(p) for p in json.load(sys.stdin)['paths'] if 'admin' in p]"

# 查看后端日志中特定路径的请求
grep -E 'GET|POST.*admin' /tmp/backend.log   # 查找 admin API 请求
grep -E 'error|Error|ERROR' /tmp/backend.log # 查找错误日志

# 杀掉卡住的进程
fuser -k 8000/tcp                            # 终止占用 8000 端口的进程
pkill -f "python main.py"                    # 按进程名终止
```

```javascript
// === 浏览器 Console 诊断 ===
// 1. 检查 localStorage 认证状态
console.log('token:', !!localStorage.getItem('token'), 
            'isAdmin:', localStorage.getItem('isAdmin'))

// 2. 手动调用 API（绕过 axios 和所有拦截器）
const headers = {}
const t = localStorage.getItem('token')
if (t) headers['Authorization'] = 'Bearer ' + t
// 计时测试
const t0 = Date.now()
const resp = await fetch('http://localhost:8000/api/admin/dashboard', { headers })
console.log('Status:', resp.status, 'Time:', Date.now() - t0, 'ms')
const data = await resp.json()
console.log(data)

// 3. 对比 XHR 和 fetch 的行为差异
// XHR 版本
const xhr = new XMLHttpRequest()
xhr.open('GET', 'http://localhost:8000/api/admin/dashboard')
xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('token'))
xhr.timeout = 10000
xhr.onload = () => console.log('XHR:', xhr.status)
xhr.ontimeout = () => console.log('XHR TIMEOUT')
xhr.send()

// 4. 访问 Vue 组件内部状态
const app = document.querySelector('#app').__vue__
// 递归查找指定名称的组件实例
function findC(vm, name) {
  if (!vm) return null
  if (vm.$options.name === name) return vm
  for (const c of (vm.$children || [])) { 
    const f = findC(c, name); if (f) return f 
  }
  return null
}
const dashboard = findC(app, 'AdminDashboard')
console.log('loading:', dashboard.loading, 'courses:', dashboard.courses)
```

---

**更新记录**：
- v1.0: 初始版本（单课程架构）
- v2.0: 多课程 RAG 架构升级（课程配置、查询优化、三层索引）
- v2.1: 管理员 GUI 改造（知识库管理控制台、安全配置优化、WSL 兼容性修复）
- v2.2: 管理员面板性能修复（chromadb 直连替代 HuggingFace 嵌入模型加载） + 完整排查实录

---

## 八、排查中涉及的关键技术概念详解

> 第七章的排查过程中，有几个技术点反复出现且对定位问题至关重要。
> 本章逐一展开讲解，帮助读者深入理解"为什么这么排查"。

### 8.1 fetch API vs XMLHttpRequest vs axios —— 三种 HTTP 调用方式的差异

#### 8.1.1 架构层次

```
┌──────────────────────────────────────────────┐
│  Vue 组件代码                                 │
│  this.$api.adminAPI.getDashboard()            │
├──────────────────────────────────────────────┤
│  axios (XHR)          │  fetchApi (fetch)     │  ← 我们封装的两套调用方式
│  XMLHttpRequest       │  Fetch API            │  ← 浏览器底层 API
├──────────────────────────────────────────────┤
│              浏览器网络栈                      │
│         (HTTP/1.1, CORS, 缓存, Cookie)        │
└──────────────────────────────────────────────┘
```

#### 8.1.2 为什么同一 URL 有时 fetch 通而 XHR 不通

两者的**网络请求本身完全相同**——都是 HTTP GET，都带 Authorization header。区别在于错误处理和底层实现：

| 维度 | `fetch()` | `XMLHttpRequest` |
|------|-----------|-------------------|
| Promise 支持 | 原生支持 | 需 axios 封装 |
| 超时处理 | 用 `AbortController` | 有 `timeout` 属性 |
| CORS 错误 | 默认不抛异常（`type: 'opaque'`） | 明确报 `onerror` |
| 连接复用 | 独立连接池 | 独立连接池 |
| 预检行为 | 相同 | 相同 |

**真实原因**（本次排查发现）：两者的行为实际上一致。fetch 在 30 秒后才返回是因为响应本来就慢（`get_course_stats()` 加载 BGE 模型）。XHR 的 `timeout=180000`（180 秒）远大于 30 秒，所以也不会超时报错。之前误判"fetch 通 XHR 不通"是因为**没有等到响应完成**——在 8 秒时检查了还在 pending 的请求。

#### 8.1.3 排查启示

**同时用 fetch 和 XHR 测试同一 URL 是有效的交叉验证手段。** 如果两者表现不同，问题在"调用之前"（如拦截器、请求头差异）。如果两者表现相同，问题在"调用之后"（网络、后端处理）。

### 8.2 CORS 预检机制与 `max-age` 缓存陷阱

#### 8.2.1 CORS 预检（Preflight）流程

当前端代码运行在 `localhost:8080`，向后端 `localhost:8000` 发请求时：

```
  浏览器 (origin: localhost:8080)
      │
      │  ① OPTIONS /api/admin/dashboard        ← 预检请求
      │     Headers:                           
      │       Origin: http://localhost:8080
      │       Access-Control-Request-Method: GET
      │       Access-Control-Request-Headers: authorization
      │
      ▼
  后端 (localhost:8000) ── CORSMiddleware 处理
      │
      │  ② 200 OK
      │     Headers:
      │       Access-Control-Allow-Origin: http://localhost:8080
      │       Access-Control-Allow-Methods: GET, POST, ...
      │       Access-Control-Allow-Headers: authorization
      │       Access-Control-Max-Age: 600              ← 缓存 600 秒！
      │
      ▼
  浏览器：预检通过，缓存此结果 600 秒
      │
      │  ③ GET /api/admin/dashboard             ← 实际请求
      │     Headers: Authorization: Bearer xxx
      │
      ▼
  后端：处理请求，返回数据
```

#### 8.2.2 `max-age` 的双面性

- **`max-age: 600`**（默认）：浏览器缓存预检结果 10 分钟。后续同源请求跳过预检，**性能好**。
- **`max-age: 0`**：每次请求都先发预检，**实时性好**。

**关键陷阱**：如果后端在某个时刻不可用（例如 uvicorn 重启），浏览器发出预检请求失败——**这个 FAILURE 结果也被缓存了！** 接下来的 10 分钟内，所有跨域请求都将被浏览器直接拦截，根本不发送。

这就是用户之前遇到的现象：后端重启后，前端所有 admin API 请求状态都是 `ERR_ABORTED`（被浏览器直接终止），后端日志完全看不到请求。

#### 8.2.3 如何验证是否是 CORS 缓存问题

```javascript
// 在浏览器 Console 中手动发预检请求
fetch('http://localhost:8000/api/admin/dashboard', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'http://localhost:8080',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'authorization'
  }
}).then(r => console.log('OPTIONS status:', r.status))

// 查看响应头
// 如果返回非 200 或缺少 Access-Control-* 头 → CORS 配置有问题
// 如果返回 200 且头完整 → CORS 工作正常，问题在别处
```

#### 8.2.4 修复方案

```python
# main.py — 开发阶段设置 max_age=0，禁止缓存预检结果
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=0,  # 关键：开发环境不缓存预检
)
```

### 8.3 ChromaDB 嵌入模型的加载时机与性能影响

#### 8.3.1 ChromaDB 存储架构

```
vector_databases/software-engineering/
├── chroma.sqlite3          ← SQLite 数据库（存元数据、文档文本、向量）
└── index/                  ← 向量索引文件（HNSW 图结构）
```

> ChromaDB 底层是 SQLite + 向量索引。**元数据和文档文本存在 SQLite 中，不需要嵌入模型就能读取。**

#### 8.3.2 LangChain Chroma 包装器的问题

```python
# 方式 A：通过 LangChain 的 Chroma 包装器（需要嵌入模型）
from langchain_community.vectorstores import Chroma
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")
vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)
# ↑ 这一行加载了 1.3GB 模型到内存！但 count() 只是查 SQLite，根本不需要模型。

# 方式 B：直接用 chromadb 原生客户端（不需要嵌入模型）
import chromadb
client = chromadb.PersistentClient(path=db_path)
collections = client.list_collections()
doc_count = collections[0].count()
# ↑ 只读 SQLite，毫秒级完成。
```

**什么时候需要嵌入模型？**
- 添加新文档（需要将文本转为向量）
- 查询相似文档（需要将查询文本转为向量，在向量空间中搜索）
- **读取元数据/计数/列名——不需要。**

#### 8.3.3 性能对比

| 操作 | LangChain Chroma 包装器 | chromadb.PersistentClient |
|------|:-:|:-:|
| 统计文档数（3 门课） | ~31,000ms | ~10ms |
| 检索 Top 5 文档 | ~200ms | ~100ms |
| 添加 100 个文档 | ~5,000ms | ~5,000ms（都需要模型） |

> **原则**：只有需要"语义理解"的操作才加载嵌入模型。纯数据操作（统计、列名、读取元数据）用 chromadb 原生 API。

### 8.4 FormData 嵌套上传的排查

#### 8.4.1 问题现象

前端上传 DOCX 文件，后端返回 `422 Unprocessable Entity`。

#### 8.4.2 排查过程

**第 1 步：确认后端是否正常**（用 curl 模拟 multipart 上传）
```bash
curl -X POST "http://localhost:8000/api/admin/courses/database/material" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test.docx"
# → 200 OK ✓  后端正常
```

**第 2 步：追踪前端数据流**

调用链：
```
AdminCourses.vue: uploadMaterial({ file })
  → formData = new FormData()
  → formData.append('file', file)      // file 是浏览器原生的 File 对象
  → adminAPI.uploadMaterial(courseId, formData)
    → 内部又 new FormData().append('file', formData)  // ← BUG！
```

第二次 `append('file', formData)` 时，`formData` 作为普通 JS 对象被序列化为字符串 `"[object FormData]"`。后端 FastAPI 收到 `file` 字段的内容是字符串而非文件二进制，`UploadFile` 验证失败 → 422。

#### 8.4.3 修复

```javascript
// 修复前：API 层重复包装 FormData
async uploadMaterial(courseId, file) {
    const formData = new FormData()
    formData.append('file', file)   // file 本身已是 FormData！
}

// 修复后：API 层直接发送调用方传入的 FormData
async uploadMaterial(courseId, formData) {
    // 不要再 new FormData()，直接发送
    const resp = await fetch(url, { method: 'POST', body: formData })
}
```

#### 8.4.4 排查启示

- `422 Unprocessable Entity` 在 FastAPI 中通常是请求体格式校验失败
- 先用 curl `-F` 确认后端能正确处理，再排查前端数据构造
- FormData 的 `append` 不会递归展开——如果把 FormData 对象作为值 append，它会被 `toString()` 成字符串

---

**更新记录**：
- v1.0: 初始版本（单课程架构）
- v2.0: 多课程 RAG 架构升级（课程配置、查询优化、三层索引）
- v2.1: 管理员 GUI 改造（知识库管理控制台、安全配置优化、WSL 兼容性修复）
- v2.2: 管理员面板性能修复（chromadb 直连替代 HuggingFace 嵌入模型加载） + 完整排查实录
- v2.3: DOCX 上传修复 + 排查关键技术概念详解章节
