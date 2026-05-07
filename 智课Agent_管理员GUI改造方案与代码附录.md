# 智课 Agent 管理员 GUI 改造方案与代码附录

> 本文件用于一并提供给代码 Agent。  
> 目标：基于当前 `backend.zip` 与 `frontend.zip` 的实际项目结构，为“智课 Agent--一款融合向量匹配技术的智能复习辅助系统 V1.0”补齐管理员 GUI，使后台知识库构建、教材上传、向量库状态查看、检索测试、AI 服务重载等功能可以通过界面操作，并与软著用户手册形成一致对应关系。

---

## 一、给代码 Agent 的主提示词

请基于当前项目实际代码结构，实现“智课 Agent 管理员知识库控制台”。项目是 WSL 本地运行的自用 demo，不要求高并发，不需要 Celery、Redis 或复杂任务队列，功能可用、界面完整、逻辑清晰即可。

本次改造的重点不是做生产级 SaaS，而是让系统形成完整功能闭环：

```text
管理员登录
→ 查看课程知识库状态
→ 上传课程 DOCX 教材
→ 点击构建课程向量数据库
→ 查看构建状态与日志
→ 进行向量检索测试
→ 重新加载 AI 服务
→ 普通用户选择课程提问
→ 系统基于新知识库检索并生成回答
→ 保存对话历史
```

请务必阅读并参考本文后面的“代码附录”。代码附录中已经给出了后端和前端关键改造代码片段，包括 `config.py`、`models.py`、`schemas.py`、`auth.py`、`routers/admin.py`、`services/knowledge_service.py`、`ai_service.py`、前端 `store`、`router`、`api` 和管理员页面的实现框架。实际编写代码时请结合项目现有文件名、导入路径和已有接口做适配，不要机械覆盖已有可用代码。

### 重要限制

1. 第一版管理员端只支持 DOCX 教材上传，不做 PDF/OCR。
2. 不做模型训练功能，不做 TPU/XLA/RedditDataset 等训练脚本界面。
3. 不做复杂课程 CRUD。当前先管理现有 6 门课程：软件工程、操作系统、计算机网络、数据结构与算法、数据库系统、编译原理。
4. 不要求高并发。知识库构建任务可使用 FastAPI `BackgroundTasks` 或 Python 线程实现。
5. 构建向量库可能耗时较长，不要让前端请求一直阻塞等待；应返回 `task_id`，前端轮询任务状态。
6. 所有真实 API Key、数据库密码、SECRET_KEY 必须改为环境变量读取，代码中不要出现真实密钥。
7. 管理员界面风格必须与已有前端界面保持一致。当前系统整体是浅色背景、蓝紫渐变、卡片式布局、Element UI 风格，请继续沿用，不要做成完全不同的后台管理模板风格。
8. 管理员页面应使用与现有页面相同的布局语言：圆角卡片、浅灰背景、蓝紫色主按钮、统一字体、统一间距、统一导航样式。
9. 如果没有实现语音输入、课程进度、课程卡片分页/下拉刷新、实时字数提示，就不要在界面和后续用户手册中描述这些功能。
10. 构建成功后，后端应自动调用 `ai_service.ai_service.reload_course(course_id)`，让普通用户无需重启后端即可使用新构建的知识库。

---

## 二、正式源码范围调整

### 2.1 不作为正式功能使用的内容

以下目录或文件不应作为正式产品功能展示，也不建议放入软著补正源程序鉴别材料重点页：

```text
backend/models/all-MiniLM-L6-v2/
backend/process_knowledge/
backend/vector_databases/
backend/knowledge_base/*.docx
frontend/dist/
node_modules/
__pycache__/
日志文件
临时上传文件
```

说明：

- `backend/models/all-MiniLM-L6-v2/` 属于模型文件或训练相关内容，不是当前系统正式业务源码。
- `backend/process_knowledge/` 是旧版单课程 `se.docx / se.pdf / chroma_db` 处理逻辑，和当前多课程 `COURSE_CONFIG + knowledge_base + vector_databases` 架构不一致。
- `vector_databases` 和 `knowledge_base` 是运行数据或课程材料，不是源程序。
- `frontend/dist` 是构建产物，不是源码。

### 2.2 正式功能保留和强化的模块

```text
backend/main.py
backend/config.py
backend/database.py
backend/models.py
backend/schemas.py
backend/auth.py
backend/routers/auth.py
backend/routers/chat.py
backend/routers/admin.py              # 新增
backend/services/knowledge_service.py  # 新增
backend/ai_service.py
backend/course_management/course_config.py

frontend/src/views/Login.vue
frontend/src/views/Register.vue
frontend/src/views/Home.vue
frontend/src/views/Chat.vue
frontend/src/views/History.vue
frontend/src/views/admin/*             # 新增
frontend/src/api/index.js
frontend/src/router/index.js
frontend/src/store/index.js
frontend/src/App.vue
```

---

## 三、后端改造任务

### 3.1 修改 `config.py`

目的：去掉硬编码密钥，新增管理员用户名配置和路径配置。

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "course_assistant")

    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    ARK_API_KEY = os.getenv("ARK_API_KEY", "")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-seed-1-6-thinking-250715")

    ADMIN_USERNAMES = [
        item.strip()
        for item in os.getenv("ADMIN_USERNAMES", "admin").split(",")
        if item.strip()
    ]

    KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
    VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "vector_databases")

settings = Settings()
```

`.env` 示例：

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的数据库密码
MYSQL_DATABASE=course_assistant

SECRET_KEY=请改成随机字符串
ARK_API_KEY=你的豆包ARK API KEY
DOUBAO_MODEL=doubao-seed-1-6-thinking-250715

ADMIN_USERNAMES=testuser,admin
```

---

### 3.2 修改 `models.py`

给 `User` 增加管理员字段：

```python
is_admin = Column(Boolean, default=False)
```

新增知识库构建任务表：

```python
class KnowledgeBuildTask(Base):
    __tablename__ = "knowledge_build_tasks"

    id = Column(String(50), primary_key=True, index=True)
    course_id = Column(String(50), nullable=False)
    course_name = Column(String(100), nullable=True)

    status = Column(String(30), nullable=False, default="pending")
    source_file = Column(String(255), nullable=True)
    vector_db_path = Column(String(255), nullable=True)

    document_count = Column(Integer, default=0)
    log = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

注意：如果本地 MySQL 已经有旧表，`Base.metadata.create_all()` 不会自动给旧表添加字段。demo 阶段可执行：

```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

或者直接重建数据库。

---

### 3.3 修改 `schemas.py`

`UserResponse` 增加 `is_admin`：

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
```

新增管理员接口模型：

```python
from typing import Any, Dict, List, Optional

class AdminCourseStatus(BaseModel):
    course_id: str
    course_name: str
    doc_file: str
    doc_exists: bool
    doc_size: int
    vector_db_exists: bool
    vector_db_size: int
    document_count: int
    loaded: bool

class RetrievalTestRequest(BaseModel):
    course_id: str
    query: str
    top_k: int = 5

class RetrievalResultItem(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class RetrievalTestResponse(BaseModel):
    success: bool
    course_id: str
    course_name: Optional[str] = None
    original_query: str
    optimized_query: str
    results: List[RetrievalResultItem] = []
    message: Optional[str] = None

class KnowledgeBuildTaskResponse(BaseModel):
    id: str
    course_id: str
    course_name: Optional[str] = None
    status: str
    source_file: Optional[str] = None
    vector_db_path: Optional[str] = None
    document_count: int = 0
    log: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

---

### 3.4 修改 `auth.py`

新增管理员权限依赖：

```python
from fastapi import Depends, HTTPException, status
from models import User

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user
```

---

### 3.5 修改 `routers/auth.py`

注册时，如果用户名在 `settings.ADMIN_USERNAMES` 中，则设置为管理员：

```python
db_user = User(
    username=user.username,
    email=user.email,
    password=get_password_hash(user.password),
    security_question=user.security_question,
    security_answer=get_password_hash(user.security_answer) if user.security_answer else None,
    is_admin=user.username in settings.ADMIN_USERNAMES
)
```

登录返回中确保包含 `is_admin`。如果当前代码通过 `UserResponse` 返回用户对象，只要 `schemas.py` 已添加字段即可。

---

### 3.6 新增 `services/knowledge_service.py`

> 说明：该服务由原 `course_management/build_course_knowledge.py` 重构而来。  
> 第一版仅支持 DOCX，不支持 PDF/OCR。

```python
import os
import shutil
from typing import Callable, Dict, List, Optional

import docx
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from course_management.course_config import CourseManager, COURSE_CONFIG

EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"


def _log(log: Optional[Callable[[str], None]], message: str):
    print(message)
    if log:
        log(message)


def find_term_with_context(paragraphs: List[str], term: str) -> List[str]:
    contexts = []
    for i, para in enumerate(paragraphs):
        if term in para:
            start_idx = max(0, i - 2)
            end_idx = min(len(paragraphs), i + 3)
            context_paragraphs = paragraphs[start_idx:end_idx]
            full_context = "\n".join(context_paragraphs)

            if len(full_context) <= 1000:
                contexts.append(full_context)
            else:
                start_idx = max(0, i - 1)
                end_idx = min(len(paragraphs), i + 2)
                shorter_context = "\n".join(paragraphs[start_idx:end_idx])
                contexts.append(shorter_context)

    return contexts


def extract_course_content(
    course_id: str,
    docx_path: str,
    log: Optional[Callable[[str], None]] = None
) -> List[Document]:
    _log(log, f"正在提取课程内容: {course_id}")

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"课程教材文件不存在: {docx_path}")

    doc = docx.Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    _log(log, f"原始段落数: {len(paragraphs)}")

    course_config = COURSE_CONFIG.get(course_id, {})
    important_terms = course_config.get("important_terms", [])
    course_name = course_config.get("name", course_id)

    _log(log, f"课程: {course_name}")
    _log(log, f"重要术语数量: {len(important_terms)}")

    enhanced_documents = []
    for term in important_terms:
        term_contexts = find_term_with_context(paragraphs, term)
        for context in term_contexts:
            enhanced_documents.append(
                Document(
                    page_content=f"[{course_name}-关键概念-{term}] {context}",
                    metadata={
                        "source": docx_path,
                        "course_id": course_id,
                        "course_name": course_name,
                        "term": term,
                        "type": "concept_enhanced",
                        "priority": 1,
                    },
                )
            )

    _log(log, f"为重要术语创建增强文档: {len(enhanced_documents)} 个")

    paragraph_documents = []
    for i, para in enumerate(paragraphs):
        if len(para) > 30:
            context_before = paragraphs[max(0, i - 1)] if i > 0 else ""
            context_after = paragraphs[min(len(paragraphs) - 1, i + 1)] if i < len(paragraphs) - 1 else ""
            enriched_content = f"{context_before}\n\n{para}\n\n{context_after}".strip()

            paragraph_documents.append(
                Document(
                    page_content=f"[{course_name}-段落] {enriched_content}",
                    metadata={
                        "source": docx_path,
                        "course_id": course_id,
                        "course_name": course_name,
                        "paragraph_index": i,
                        "type": "paragraph_with_context",
                        "priority": 2,
                    },
                )
            )

    _log(log, f"创建段落级文档: {len(paragraph_documents)} 个")

    fine_grained_documents = []
    all_text = "\n".join(paragraphs)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        separators=["\n\n", "。", "！", "？", "\n", "，", "；"],
        length_function=len,
    )

    temp_doc = Document(page_content=all_text, metadata={"source": docx_path})
    chunks = text_splitter.split_documents([temp_doc])

    for i, chunk in enumerate(chunks):
        chunk.page_content = f"[{course_name}-细节] {chunk.page_content}"
        chunk.metadata.update(
            {
                "course_id": course_id,
                "course_name": course_name,
                "type": "fine_grained",
                "chunk_index": i,
                "priority": 3,
            }
        )
        fine_grained_documents.append(chunk)

    _log(log, f"创建细粒度文档: {len(fine_grained_documents)} 个")

    all_documents = enhanced_documents + paragraph_documents + fine_grained_documents
    _log(log, f"总计创建文档块: {len(all_documents)} 个")

    return all_documents


def build_course_vectordb(
    course_id: str,
    log: Optional[Callable[[str], None]] = None
) -> Dict:
    try:
        manager = CourseManager()

        if course_id not in COURSE_CONFIG:
            return {
                "success": False,
                "error": f"不支持的课程 ID: {course_id}",
            }

        course_config = COURSE_CONFIG[course_id]
        course_name = course_config["name"]
        doc_path = manager.get_course_doc_path(course_id)

        _log(log, f"开始构建课程向量数据库: {course_id} - {course_name}")
        _log(log, f"教材路径: {doc_path}")

        if not doc_path or not os.path.exists(doc_path):
            return {
                "success": False,
                "error": f"课程教材文件不存在: {doc_path}",
            }

        db_path = manager.get_course_vector_db_path(course_id)

        if os.path.exists(db_path):
            _log(log, f"删除旧向量数据库: {db_path}")
            shutil.rmtree(db_path)

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        documents = extract_course_content(course_id, doc_path, log=log)
        if not documents:
            return {
                "success": False,
                "error": "未能提取到有效文档内容",
            }

        _log(log, f"加载嵌入模型: {EMBEDDING_MODEL_NAME}")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        _log(log, f"创建向量数据库: {db_path}")
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=db_path,
        )

        doc_count = len(vectordb._collection.get()["documents"])
        _log(log, f"向量数据库创建成功，包含 {doc_count} 个文档块")

        return {
            "success": True,
            "course_id": course_id,
            "course_name": course_name,
            "document_count": doc_count,
            "vector_db_path": db_path,
            "source_file": doc_path,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def get_all_course_status(ai_instance=None) -> List[Dict]:
    manager = CourseManager()
    stats = manager.list_all_course_stats()

    result = []
    for course_id, item in stats.items():
        course_config = COURSE_CONFIG.get(course_id, {})
        loaded = False

        if ai_instance is not None:
            loaded = course_id in getattr(ai_instance, "course_retrievers", {})

        result.append(
            {
                "course_id": course_id,
                "course_name": course_config.get("name", item.get("course_name", course_id)),
                "doc_file": course_config.get("doc_file", ""),
                "doc_exists": item.get("doc_exists", False),
                "doc_size": item.get("doc_size", 0),
                "vector_db_exists": item.get("vector_db_exists", False),
                "vector_db_size": item.get("vector_db_size", 0),
                "document_count": item.get("document_count", 0),
                "loaded": loaded,
            }
        )

    return result


def save_course_material(course_id: str, file_bytes: bytes, filename: str) -> Dict:
    manager = CourseManager()

    if course_id not in COURSE_CONFIG:
        return {
            "success": False,
            "error": f"不支持的课程 ID: {course_id}",
        }

    if not filename.lower().endswith(".docx"):
        return {
            "success": False,
            "error": "第一版仅支持上传 .docx 教材文件",
        }

    doc_path = manager.get_course_doc_path(course_id)
    if not doc_path:
        return {
            "success": False,
            "error": "无法确定课程教材保存路径",
        }

    os.makedirs(os.path.dirname(doc_path), exist_ok=True)

    with open(doc_path, "wb") as f:
        f.write(file_bytes)

    return {
        "success": True,
        "course_id": course_id,
        "filename": filename,
        "saved_path": doc_path,
        "size": len(file_bytes),
    }
```

---

### 3.7 修改 `ai_service.py`

在 `DoubaoAIService` 类中新增方法：

```python
def reload_course(self, course_id: str) -> dict:
    course_config = COURSE_CONFIG.get(course_id)
    if not course_config:
        return {
            "success": False,
            "message": f"课程不存在: {course_id}",
        }

    course_name = course_config["name"]
    db_path = os.path.join(VECTOR_DB_BASE_PATH, course_id)

    if not os.path.exists(db_path):
        self.course_vectordbs.pop(course_id, None)
        self.course_retrievers.pop(course_id, None)
        return {
            "success": False,
            "course_id": course_id,
            "message": f"{course_name} 的向量数据库不存在",
        }

    try:
        vectordb = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings,
        )
        doc_count = len(vectordb._collection.get()["documents"])

        self.course_vectordbs[course_id] = vectordb
        self.course_retrievers[course_id] = vectordb.as_retriever(
            search_kwargs={"k": 5}
        )

        return {
            "success": True,
            "course_id": course_id,
            "course_name": course_name,
            "document_count": doc_count,
            "message": f"{course_name} 向量数据库重新加载成功",
        }
    except Exception as e:
        return {
            "success": False,
            "course_id": course_id,
            "message": str(e),
        }


def reload_all_courses(self) -> dict:
    results = {}
    for course_id in COURSE_CONFIG.keys():
        results[course_id] = self.reload_course(course_id)
    return results


def test_retrieval(self, course_id: str, query: str, top_k: int = 5) -> dict:
    course_config = COURSE_CONFIG.get(course_id)
    course_name = course_config["name"] if course_config else course_id

    if course_id not in self.course_vectordbs:
        return {
            "success": False,
            "course_id": course_id,
            "course_name": course_name,
            "original_query": query,
            "optimized_query": query,
            "results": [],
            "message": "该课程知识库尚未加载，请先构建并重新加载向量库",
        }

    optimized_query = self._optimize_query_for_course(query, course_id)

    retriever = self.course_vectordbs[course_id].as_retriever(
        search_kwargs={"k": top_k}
    )
    docs = retriever.invoke(optimized_query)

    return {
        "success": True,
        "course_id": course_id,
        "course_name": course_name,
        "original_query": query,
        "optimized_query": optimized_query,
        "results": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in docs
        ],
    }
```

---

### 3.8 新增 `routers/admin.py`

```python
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import ai_service
from auth import get_current_admin_user
from config import settings
from course_management.course_config import COURSE_CONFIG
from database import SessionLocal, get_db
from models import KnowledgeBuildTask, User
from services.knowledge_service import (
    build_course_vectordb,
    get_all_course_status,
    save_course_material,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(get_current_admin_user),
):
    ai_instance = ai_service.ai_service
    courses = get_all_course_status(ai_instance)

    total_courses = len(courses)
    doc_ready = len([c for c in courses if c["doc_exists"]])
    vector_ready = len([c for c in courses if c["vector_db_exists"]])
    loaded_courses = len([c for c in courses if c["loaded"]])

    return {
        "api_status": "running",
        "ai_status": "initialized" if ai_instance else "not_initialized",
        "model_name": settings.DOUBAO_MODEL,
        "api_key_configured": bool(settings.ARK_API_KEY),
        "total_courses": total_courses,
        "doc_ready_courses": doc_ready,
        "vector_ready_courses": vector_ready,
        "loaded_courses": loaded_courses,
        "courses": courses,
    }


@router.get("/courses")
async def admin_courses(
    current_user: User = Depends(get_current_admin_user),
):
    return get_all_course_status(ai_service.ai_service)


@router.post("/courses/{course_id}/material")
async def upload_course_material(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
):
    if course_id not in COURSE_CONFIG:
        raise HTTPException(status_code=404, detail="课程不存在")

    content = await file.read()
    result = save_course_material(course_id, content, file.filename)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/courses/{course_id}/knowledge/build")
async def build_knowledge(
    course_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if course_id not in COURSE_CONFIG:
        raise HTTPException(status_code=404, detail="课程不存在")

    course_name = COURSE_CONFIG[course_id]["name"]
    task_id = "task_" + uuid.uuid4().hex[:16]

    task = KnowledgeBuildTask(
        id=task_id,
        course_id=course_id,
        course_name=course_name,
        status="pending",
    )
    db.add(task)
    db.commit()

    background_tasks.add_task(run_build_task, task_id, course_id)

    return {
        "task_id": task_id,
        "course_id": course_id,
        "course_name": course_name,
        "status": "pending",
    }


def run_build_task(task_id: str, course_id: str):
    db = SessionLocal()
    logs = []

    def log(message: str):
        logs.append(message)

    try:
        task = db.query(KnowledgeBuildTask).filter(KnowledgeBuildTask.id == task_id).first()
        if not task:
            return

        task.status = "running"
        task.started_at = datetime.utcnow()
        task.log = "任务开始"
        db.commit()

        result = build_course_vectordb(course_id, log=log)

        task = db.query(KnowledgeBuildTask).filter(KnowledgeBuildTask.id == task_id).first()
        if not task:
            return

        if result.get("success"):
            task.status = "success"
            task.source_file = result.get("source_file")
            task.vector_db_path = result.get("vector_db_path")
            task.document_count = result.get("document_count", 0)

            if ai_service.ai_service:
                reload_result = ai_service.ai_service.reload_course(course_id)
                logs.append(f"AI 服务重载结果: {reload_result}")
        else:
            task.status = "failed"
            task.error_message = result.get("error", "构建失败")

        task.log = "\n".join(logs)
        task.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        task = db.query(KnowledgeBuildTask).filter(KnowledgeBuildTask.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.log = "\n".join(logs)
            task.finished_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.get("/knowledge/tasks")
async def list_build_tasks(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    tasks = (
        db.query(KnowledgeBuildTask)
        .order_by(KnowledgeBuildTask.created_at.desc())
        .limit(20)
        .all()
    )
    return tasks


@router.get("/knowledge/tasks/{task_id}")
async def get_build_task(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    task = db.query(KnowledgeBuildTask).filter(KnowledgeBuildTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="构建任务不存在")
    return task


@router.post("/retrieval-test")
async def retrieval_test(
    payload: dict,
    current_user: User = Depends(get_current_admin_user),
):
    course_id = payload.get("course_id")
    query = payload.get("query")
    top_k = int(payload.get("top_k", 5))

    if not course_id or not query:
        raise HTTPException(status_code=400, detail="course_id 和 query 不能为空")

    if not ai_service.ai_service:
        raise HTTPException(status_code=500, detail="AI 服务尚未初始化")

    return ai_service.ai_service.test_retrieval(course_id, query, top_k)


@router.get("/system/health")
async def admin_system_health(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    database_status = "connected"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        database_status = f"error: {e}"

    ai_instance = ai_service.ai_service

    loaded_courses = {}
    if ai_instance:
        loaded_courses = ai_instance.get_loaded_courses()

    return {
        "api_status": "running",
        "database_status": database_status,
        "ai_status": "initialized" if ai_instance else "not_initialized",
        "model_name": settings.DOUBAO_MODEL,
        "api_key_configured": bool(settings.ARK_API_KEY),
        "embedding_model": "BAAI/bge-large-zh-v1.5",
        "loaded_courses": loaded_courses,
    }


@router.post("/ai/reload")
async def reload_ai_all(
    current_user: User = Depends(get_current_admin_user),
):
    if not ai_service.ai_service:
        raise HTTPException(status_code=500, detail="AI 服务尚未初始化")

    return ai_service.ai_service.reload_all_courses()


@router.post("/ai/reload/{course_id}")
async def reload_ai_course(
    course_id: str,
    current_user: User = Depends(get_current_admin_user),
):
    if not ai_service.ai_service:
        raise HTTPException(status_code=500, detail="AI 服务尚未初始化")

    return ai_service.ai_service.reload_course(course_id)
```

> 如果 `db.execute("SELECT 1")` 在 SQLAlchemy 版本中报错，可改成：
>
> ```python
> from sqlalchemy import text
> db.execute(text("SELECT 1"))
> ```

---

### 3.9 修改 `main.py`

```python
from routers import auth, chat, admin

app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
```

---

### 3.10 修改 `requirements.txt`

确保包含：

```text
python-multipart
python-docx
chromadb
langchain-community
langchain-huggingface
sentence-transformers
```

如果项目已有其中部分依赖，不要重复也没关系。

---

## 四、前端改造任务

### 4.1 修改 `store/index.js`

增加 `isAdmin`：

```javascript
const store = new Vuex.Store({
  state: {
    user: {
      username: localStorage.getItem('username') || '',
      token: localStorage.getItem('token') || '',
      isAdmin: localStorage.getItem('isAdmin') === 'true'
    }
  },

  mutations: {
    LOGIN(state, userData) {
      state.user.username = userData.username
      state.user.token = userData.token
      state.user.isAdmin = !!userData.isAdmin

      localStorage.setItem('username', userData.username)
      localStorage.setItem('token', userData.token)
      localStorage.setItem('isAdmin', userData.isAdmin ? 'true' : 'false')
    },

    LOGOUT(state) {
      state.user.username = ''
      state.user.token = ''
      state.user.isAdmin = false

      localStorage.removeItem('username')
      localStorage.removeItem('token')
      localStorage.removeItem('isAdmin')
    }
  },

  getters: {
    isAuthenticated: state => !!state.user.token,
    currentUser: state => state.user.username,
    isAdmin: state => state.user.isAdmin
  }
})
```

结合现有 store 写法做适配，不要破坏已有功能。

---

### 4.2 修改 `Login.vue`

登录成功后保存 `is_admin`：

```javascript
this.$store.dispatch('login', {
  username: response.user.username,
  token: response.access_token,
  isAdmin: response.user.is_admin
})
```

如果现有登录响应变量名不是 `response`，请按现有代码适配。

---

### 4.3 修改 `router/index.js`

新增管理员路由：

```javascript
import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminCourses from '../views/admin/AdminCourses.vue'
import AdminRetrievalTest from '../views/admin/AdminRetrievalTest.vue'
import AdminSystem from '../views/admin/AdminSystem.vue'

const routes = [
  // 保留已有路由

  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'courses',
        name: 'AdminCourses',
        component: AdminCourses
      },
      {
        path: 'retrieval-test',
        name: 'AdminRetrievalTest',
        component: AdminRetrievalTest
      },
      {
        path: 'system',
        name: 'AdminSystem',
        component: AdminSystem
      }
    ]
  }
]
```

路由守卫增加管理员校验：

```javascript
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.isAuthenticated) {
      next('/login')
      return
    }
  }

  if (to.matched.some(record => record.meta.requiresAdmin)) {
    if (!store.getters.isAdmin) {
      next('/home')
      return
    }
  }

  next()
})
```

请结合当前项目已有路由守卫合并，不要重复定义冲突。

---

### 4.4 修改 `api/index.js`

新增 `adminAPI`：

```javascript
export const adminAPI = {
  getDashboard() {
    return api.get('/admin/dashboard')
  },

  getCourses() {
    return api.get('/admin/courses')
  },

  uploadMaterial(courseId, formData) {
    return api.post(`/admin/courses/${courseId}/material`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000
    })
  },

  buildKnowledge(courseId) {
    return api.post(`/admin/courses/${courseId}/knowledge/build`)
  },

  getBuildTask(taskId) {
    return api.get(`/admin/knowledge/tasks/${taskId}`)
  },

  getBuildTasks() {
    return api.get('/admin/knowledge/tasks')
  },

  testRetrieval(data) {
    return api.post('/admin/retrieval-test', data)
  },

  getSystemHealth() {
    return api.get('/admin/system/health')
  },

  reloadAI() {
    return api.post('/admin/ai/reload')
  },

  reloadCourse(courseId) {
    return api.post(`/admin/ai/reload/${courseId}`)
  }
}
```

在 `main.js` 中注入：

```javascript
import api, { authAPI, chatAPI, commonAPI, adminAPI } from './api'

Vue.prototype.$api = {
  authAPI,
  chatAPI,
  commonAPI,
  adminAPI
}
```

如果当前项目已经有不同的 `$api` 注入方式，请保持现有方式并添加 `adminAPI`。

---

### 4.5 修改 `App.vue`

如果管理员登录，在导航栏显示“管理员控制台”。

示例：

```vue
<el-menu-item
  v-if="isAdmin"
  index="/admin/dashboard"
  class="nav-item"
>
  <i class="el-icon-s-tools"></i>
  <span>管理员控制台</span>
</el-menu-item>
```

```javascript
computed: {
  isAdmin() {
    return this.$store.getters.isAdmin
  }
}
```

界面风格要求：

- 沿用已有蓝紫渐变视觉。
- 沿用已有顶部导航风格。
- 不要引入暗色后台模板。
- 不要使用和现有页面割裂的重型后台布局。

---

## 五、管理员页面代码框架

### 5.1 `src/views/admin/AdminLayout.vue`

```vue
<template>
  <div class="admin-layout">
    <div class="admin-header">
      <div>
        <h2>管理员控制台</h2>
        <p>课程知识库、向量数据库与系统状态管理</p>
      </div>
    </div>

    <div class="admin-body">
      <aside class="admin-sidebar">
        <el-menu
          :default-active="$route.path"
          router
          class="admin-menu"
        >
          <el-menu-item index="/admin/dashboard">
            <i class="el-icon-data-analysis"></i>
            <span>系统概览</span>
          </el-menu-item>

          <el-menu-item index="/admin/courses">
            <i class="el-icon-collection"></i>
            <span>课程知识库</span>
          </el-menu-item>

          <el-menu-item index="/admin/retrieval-test">
            <i class="el-icon-search"></i>
            <span>检索测试</span>
          </el-menu-item>

          <el-menu-item index="/admin/system">
            <i class="el-icon-setting"></i>
            <span>系统状态</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout'
}
</script>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 64px);
  background: #f5f7fb;
}

.admin-header {
  margin: 24px auto 0;
  max-width: 1180px;
  padding: 28px 32px;
  border-radius: 18px;
  background: linear-gradient(135deg, #5b8def 0%, #7b5cf0 100%);
  color: #fff;
  box-shadow: 0 12px 32px rgba(91, 141, 239, 0.24);
}

.admin-header h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
}

.admin-header p {
  margin: 0;
  opacity: 0.9;
}

.admin-body {
  max-width: 1180px;
  margin: 24px auto;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
}

.admin-sidebar {
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 8px 24px rgba(20, 40, 90, 0.08);
}

.admin-menu {
  border-right: none;
}

.admin-content {
  min-width: 0;
}

@media (max-width: 900px) {
  .admin-body {
    grid-template-columns: 1fr;
  }
}
</style>
```

---

### 5.2 `src/views/admin/AdminDashboard.vue`

```vue
<template>
  <div class="admin-page">
    <div class="page-title">
      <h3>系统概览</h3>
      <el-button type="primary" size="small" @click="loadDashboard">
        刷新
      </el-button>
    </div>

    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">课程总数</div>
          <div class="stat-value">{{ dashboard.total_courses || 0 }}</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">已上传教材</div>
          <div class="stat-value">{{ dashboard.doc_ready_courses || 0 }}</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">已构建向量库</div>
          <div class="stat-value">{{ dashboard.vector_ready_courses || 0 }}</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">AI 已加载课程</div>
          <div class="stat-value">{{ dashboard.loaded_courses || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <div slot="header">运行状态</div>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="API 状态">
          <el-tag type="success">{{ dashboard.api_status || '-' }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="AI 服务">
          <el-tag :type="dashboard.ai_status === 'initialized' ? 'success' : 'warning'">
            {{ dashboard.ai_status || '-' }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="模型名称">
          {{ dashboard.model_name || '-' }}
        </el-descriptions-item>

        <el-descriptions-item label="API Key">
          <el-tag :type="dashboard.api_key_configured ? 'success' : 'danger'">
            {{ dashboard.api_key_configured ? '已配置' : '未配置' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="section-card">
      <div slot="header">课程知识库概览</div>

      <el-table :data="dashboard.courses || []" border>
        <el-table-column prop="course_name" label="课程" width="140" />
        <el-table-column prop="doc_file" label="教材文件" />
        <el-table-column label="教材">
          <template slot-scope="{ row }">
            <el-tag :type="row.doc_exists ? 'success' : 'info'">
              {{ row.doc_exists ? '已上传' : '未上传' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="向量库">
          <template slot-scope="{ row }">
            <el-tag :type="row.vector_db_exists ? 'success' : 'info'">
              {{ row.vector_db_exists ? '已构建' : '未构建' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="document_count" label="文档块数" width="100" />
        <el-table-column label="AI 加载" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.loaded ? 'success' : 'warning'">
              {{ row.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',

  data() {
    return {
      loading: false,
      dashboard: {}
    }
  },

  created() {
    this.loadDashboard()
  },

  methods: {
    async loadDashboard() {
      this.loading = true
      try {
        const res = await this.$api.adminAPI.getDashboard()
        this.dashboard = res
      } catch (error) {
        this.$message.error('加载系统概览失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title h3 {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}

.stat-card {
  border-radius: 16px;
}

.stat-label {
  color: #7a869a;
  font-size: 14px;
}

.stat-value {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 700;
  color: #4f6bed;
}

.section-card {
  border-radius: 16px;
}
</style>
```

---

### 5.3 `src/views/admin/AdminCourses.vue`

```vue
<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>课程知识库</h3>
        <p>上传课程教材、构建向量数据库，并查看 AI 加载状态。</p>
      </div>

      <el-button type="primary" @click="loadCourses">
        刷新状态
      </el-button>
    </div>

    <el-card class="section-card">
      <el-table :data="courses" border v-loading="loading">
        <el-table-column prop="course_name" label="课程" width="130" />
        <el-table-column prop="course_id" label="课程 ID" width="180" />
        <el-table-column prop="doc_file" label="教材文件" min-width="180" />

        <el-table-column label="教材状态" width="110">
          <template slot-scope="{ row }">
            <el-tag :type="row.doc_exists ? 'success' : 'info'">
              {{ row.doc_exists ? '已上传' : '未上传' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="向量库" width="110">
          <template slot-scope="{ row }">
            <el-tag :type="row.vector_db_exists ? 'success' : 'info'">
              {{ row.vector_db_exists ? '已构建' : '未构建' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="document_count" label="文档块" width="90" />

        <el-table-column label="AI 加载" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.loaded ? 'success' : 'warning'">
              {{ row.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="330" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="mini" @click="openUpload(row)">
              上传教材
            </el-button>

            <el-button
              size="mini"
              type="primary"
              :disabled="!row.doc_exists"
              @click="buildKnowledge(row)"
            >
              构建
            </el-button>

            <el-button
              size="mini"
              type="success"
              :disabled="!row.vector_db_exists"
              @click="reloadCourse(row)"
            >
              重载
            </el-button>

            <el-button size="mini" @click="goRetrieval(row)">
              检索测试
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      title="上传课程教材"
      :visible.sync="uploadDialogVisible"
      width="520px"
    >
      <p v-if="currentCourse">
        当前课程：<strong>{{ currentCourse.course_name }}</strong>
      </p>

      <el-alert
        title="第一版仅支持上传 DOCX 文件。上传后需要点击“构建”生成向量数据库。"
        type="info"
        show-icon
        :closable="false"
        class="mb-16"
      />

      <el-upload
        drag
        action=""
        :http-request="uploadMaterial"
        :show-file-list="false"
        accept=".docx"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          将 DOCX 文件拖到此处，或 <em>点击上传</em>
        </div>
      </el-upload>
    </el-dialog>

    <el-dialog
      title="知识库构建任务"
      :visible.sync="taskDialogVisible"
      width="720px"
    >
      <div v-if="currentTask">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务 ID">
            {{ currentTask.id }}
          </el-descriptions-item>

          <el-descriptions-item label="状态">
            <el-tag :type="taskTagType(currentTask.status)">
              {{ currentTask.status }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="课程">
            {{ currentTask.course_name }}
          </el-descriptions-item>

          <el-descriptions-item label="文档块数">
            {{ currentTask.document_count || 0 }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="log-box">
          <pre>{{ currentTask.log || currentTask.error_message || '暂无日志' }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminCourses',

  data() {
    return {
      loading: false,
      courses: [],
      uploadDialogVisible: false,
      taskDialogVisible: false,
      currentCourse: null,
      currentTask: null,
      pollTimer: null
    }
  },

  created() {
    this.loadCourses()
  },

  beforeDestroy() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer)
    }
  },

  methods: {
    async loadCourses() {
      this.loading = true
      try {
        this.courses = await this.$api.adminAPI.getCourses()
      } catch (error) {
        this.$message.error('加载课程知识库状态失败')
      } finally {
        this.loading = false
      }
    },

    openUpload(row) {
      this.currentCourse = row
      this.uploadDialogVisible = true
    },

    async uploadMaterial({ file }) {
      if (!this.currentCourse) return

      const formData = new FormData()
      formData.append('file', file)

      try {
        await this.$api.adminAPI.uploadMaterial(this.currentCourse.course_id, formData)
        this.$message.success('教材上传成功')
        this.uploadDialogVisible = false
        this.loadCourses()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '教材上传失败')
      }
    },

    async buildKnowledge(row) {
      try {
        const res = await this.$confirm(
          `确认构建「${row.course_name}」的向量知识库吗？构建过程可能需要一段时间。`,
          '确认构建',
          { type: 'warning' }
        )

        if (!res) return

        const task = await this.$api.adminAPI.buildKnowledge(row.course_id)
        this.taskDialogVisible = true
        this.currentTask = {
          id: task.task_id,
          course_id: task.course_id,
          course_name: task.course_name,
          status: task.status,
          log: '任务已提交，等待后台构建...'
        }

        this.pollTask(task.task_id)
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.response?.data?.detail || '构建任务提交失败')
        }
      }
    },

    pollTask(taskId) {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
      }

      this.pollTimer = setInterval(async () => {
        try {
          const task = await this.$api.adminAPI.getBuildTask(taskId)
          this.currentTask = task

          if (task.status === 'success' || task.status === 'failed') {
            clearInterval(this.pollTimer)
            this.pollTimer = null
            this.loadCourses()

            if (task.status === 'success') {
              this.$message.success('知识库构建成功')
            } else {
              this.$message.error('知识库构建失败')
            }
          }
        } catch (error) {
          clearInterval(this.pollTimer)
          this.pollTimer = null
          this.$message.error('查询构建任务失败')
        }
      }, 2000)
    },

    async reloadCourse(row) {
      try {
        await this.$api.adminAPI.reloadCourse(row.course_id)
        this.$message.success('课程向量库已重新加载')
        this.loadCourses()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '重新加载失败')
      }
    },

    goRetrieval(row) {
      this.$router.push({
        path: '/admin/retrieval-test',
        query: { course_id: row.course_id }
      })
    },

    taskTagType(status) {
      if (status === 'success') return 'success'
      if (status === 'failed') return 'danger'
      if (status === 'running') return 'warning'
      return 'info'
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.page-title h3 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #1f2d3d;
}

.page-title p {
  margin: 0;
  color: #7a869a;
}

.section-card {
  border-radius: 16px;
}

.mb-16 {
  margin-bottom: 16px;
}

.log-box {
  margin-top: 18px;
  padding: 14px;
  background: #f7f9fc;
  border-radius: 12px;
  max-height: 320px;
  overflow: auto;
}

.log-box pre {
  margin: 0;
  white-space: pre-wrap;
  color: #344563;
  font-size: 13px;
  line-height: 1.6;
}
</style>
```

---

### 5.4 `src/views/admin/AdminRetrievalTest.vue`

```vue
<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>向量检索测试</h3>
        <p>输入课程问题，查看查询优化结果和向量库返回的教材片段。</p>
      </div>
    </div>

    <el-card class="section-card">
      <el-form :inline="true" :model="form">
        <el-form-item label="课程">
          <el-select v-model="form.course_id" placeholder="请选择课程" style="width: 220px">
            <el-option
              v-for="course in courses"
              :key="course.course_id"
              :label="course.course_name"
              :value="course.course_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Top K">
          <el-input-number v-model="form.top_k" :min="1" :max="10" />
        </el-form-item>
      </el-form>

      <el-input
        v-model="form.query"
        type="textarea"
        :rows="3"
        placeholder="请输入测试问题，例如：瀑布模型是什么？"
      />

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="testRetrieval">
          开始检索
        </el-button>
      </div>
    </el-card>

    <el-card v-if="result" class="section-card">
      <div slot="header">检索结果</div>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="原始查询">
          {{ result.original_query }}
        </el-descriptions-item>

        <el-descriptions-item label="优化后查询">
          {{ result.optimized_query }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="result-list">
        <el-card
          v-for="(item, index) in result.results"
          :key="index"
          class="result-card"
          shadow="never"
        >
          <div class="result-title">
            片段 {{ index + 1 }}
          </div>

          <div class="result-content">
            {{ item.content }}
          </div>

          <pre class="metadata">{{ formatMetadata(item.metadata) }}</pre>
        </el-card>
      </div>

      <el-empty
        v-if="!result.results || result.results.length === 0"
        description="没有检索到结果"
      />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminRetrievalTest',

  data() {
    return {
      loading: false,
      courses: [],
      form: {
        course_id: this.$route.query.course_id || '',
        query: '',
        top_k: 5
      },
      result: null
    }
  },

  created() {
    this.loadCourses()
  },

  methods: {
    async loadCourses() {
      try {
        this.courses = await this.$api.adminAPI.getCourses()
        if (!this.form.course_id && this.courses.length > 0) {
          this.form.course_id = this.courses[0].course_id
        }
      } catch (error) {
        this.$message.error('加载课程失败')
      }
    },

    async testRetrieval() {
      if (!this.form.course_id || !this.form.query.trim()) {
        this.$message.warning('请选择课程并输入测试问题')
        return
      }

      this.loading = true
      try {
        this.result = await this.$api.adminAPI.testRetrieval(this.form)
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '检索测试失败')
      } finally {
        this.loading = false
      }
    },

    formatMetadata(metadata) {
      return JSON.stringify(metadata || {}, null, 2)
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-title h3 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #1f2d3d;
}

.page-title p {
  margin: 0;
  color: #7a869a;
}

.section-card {
  border-radius: 16px;
}

.actions {
  margin-top: 16px;
  text-align: right;
}

.result-list {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.result-card {
  border-radius: 12px;
  background: #fbfcff;
}

.result-title {
  font-weight: 600;
  color: #4f6bed;
  margin-bottom: 10px;
}

.result-content {
  color: #1f2d3d;
  line-height: 1.7;
  white-space: pre-wrap;
}

.metadata {
  margin-top: 12px;
  padding: 12px;
  border-radius: 10px;
  background: #f2f5fa;
  color: #5e6c84;
  font-size: 12px;
  overflow: auto;
}
</style>
```

---

### 5.5 `src/views/admin/AdminSystem.vue`

```vue
<template>
  <div class="admin-page">
    <div class="page-title">
      <div>
        <h3>系统状态</h3>
        <p>查看后端、数据库、AI 服务和向量库加载状态。</p>
      </div>

      <div>
        <el-button @click="loadHealth">刷新</el-button>
        <el-button type="primary" :loading="reloading" @click="reloadAI">
          重新加载 AI 服务
        </el-button>
      </div>
    </div>

    <el-card class="section-card" v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="API 状态">
          <el-tag type="success">{{ health.api_status || '-' }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="数据库状态">
          <el-tag :type="databaseTagType">
            {{ health.database_status || '-' }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="AI 服务">
          <el-tag :type="health.ai_status === 'initialized' ? 'success' : 'warning'">
            {{ health.ai_status || '-' }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="豆包模型">
          {{ health.model_name || '-' }}
        </el-descriptions-item>

        <el-descriptions-item label="API Key">
          <el-tag :type="health.api_key_configured ? 'success' : 'danger'">
            {{ health.api_key_configured ? '已配置' : '未配置' }}
          </el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="嵌入模型">
          {{ health.embedding_model || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="section-card">
      <div slot="header">已加载课程</div>

      <el-table :data="loadedCourseRows" border>
        <el-table-column prop="course_id" label="课程 ID" />
        <el-table-column prop="course_name" label="课程名称" />
      </el-table>

      <el-empty
        v-if="loadedCourseRows.length === 0"
        description="暂无已加载课程"
      />
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AdminSystem',

  data() {
    return {
      loading: false,
      reloading: false,
      health: {}
    }
  },

  computed: {
    databaseTagType() {
      return String(this.health.database_status || '').startsWith('connected')
        ? 'success'
        : 'danger'
    },

    loadedCourseRows() {
      const loaded = this.health.loaded_courses || {}
      return Object.keys(loaded).map(courseId => ({
        course_id: courseId,
        course_name: loaded[courseId]
      }))
    }
  },

  created() {
    this.loadHealth()
  },

  methods: {
    async loadHealth() {
      this.loading = true
      try {
        this.health = await this.$api.adminAPI.getSystemHealth()
      } catch (error) {
        this.$message.error('加载系统状态失败')
      } finally {
        this.loading = false
      }
    },

    async reloadAI() {
      this.reloading = true
      try {
        await this.$api.adminAPI.reloadAI()
        this.$message.success('AI 服务已重新加载')
        this.loadHealth()
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '重新加载失败')
      } finally {
        this.reloading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.page-title h3 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #1f2d3d;
}

.page-title p {
  margin: 0;
  color: #7a869a;
}

.section-card {
  border-radius: 16px;
}
</style>
```

---

## 六、管理员界面风格要求

代码 Agent 实现时必须注意：

1. 管理员界面不是独立后台模板，而是“智课 Agent”的内部管理控制台。
2. 视觉应沿用已有系统风格：
   - 浅灰背景；
   - 蓝紫渐变头部；
   - 白色圆角卡片；
   - Element UI 表格、按钮、Tag、Dialog；
   - 蓝色/紫色作为主色；
   - 轻阴影；
   - 页面文案保持“智能课程助教 / 智课 Agent”风格。
3. 不要突然引入深色侧边栏、黑色后台模板、大量无关图标或与现有界面不一致的布局。
4. 管理员功能入口应放在已有顶部导航中，仅管理员可见。
5. 页面标题和说明文字应让用户能理解这些功能和“向量匹配技术”的关系。

---

## 七、验收标准

代码完成后，应满足：

1. 普通用户仍可注册、登录、选择课程、提问、查看回答、查看历史。
2. `.env` 中 `ADMIN_USERNAMES` 指定的用户登录后可看到“管理员控制台”入口。
3. 非管理员访问 `/admin/*` 会被拦截或返回首页。
4. 管理员可以进入 `/admin/dashboard` 查看课程、教材、向量库、AI 加载概览。
5. 管理员可以进入 `/admin/courses` 查看 6 门课程的教材状态和向量库状态。
6. 管理员可以为某门课程上传 `.docx` 教材。
7. 管理员可以点击“构建”生成该课程的 Chroma 向量数据库。
8. 构建任务会显示 `pending / running / success / failed` 状态。
9. 构建任务会显示日志、文档块数量和错误信息。
10. 构建成功后，后端自动重载该课程向量库。
11. 管理员可以在 `/admin/retrieval-test` 选择课程、输入问题，并看到：
    - 原始查询；
    - 优化后查询；
    - 向量检索片段；
    - metadata。
12. 管理员可以在 `/admin/system` 查看：
    - API 状态；
    - 数据库状态；
    - AI 服务状态；
    - 模型名称；
    - API Key 是否配置；
    - 已加载课程。
13. 代码中不出现真实 API Key、真实数据库密码、真实 SECRET_KEY。
14. 第一版不实现 PDF/OCR、模型训练、高并发队列、复杂动态课程 CRUD。
15. 管理员页面视觉风格与已有用户端保持一致。

---

## 八、后续用户手册应同步增加的章节

完成代码后，用户手册应增加：

```text
四、管理员功能
  4.1 管理员登录与控制台入口
  4.2 系统概览
  4.3 课程知识库状态查看
  4.4 课程教材上传
  4.5 向量知识库构建
  4.6 构建任务状态与日志查看
  4.7 向量检索测试
  4.8 AI 服务与系统状态查看

五、智能问答工作流程
  5.1 用户选择课程
  5.2 用户输入问题
  5.3 系统进行课程内查询优化
  5.4 系统从课程向量库检索教材片段
  5.5 系统调用 AI 生成回答
  5.6 系统保存对话历史
```

同时删除或避免描述未实现功能：

```text
语音提问入口
课程进度
课程卡片分页加载
课程卡片下拉刷新
实时字数提示
PDF/OCR 教材导入
模型训练
```
