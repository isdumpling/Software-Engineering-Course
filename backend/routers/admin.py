"""管理员接口 —— 知识库构建、检索测试、系统状态"""

import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

import ai_service
from auth import get_current_admin_user
from config import settings
from course_management.course_config import COURSE_CONFIG
from database import SessionLocal, get_db
from models import KnowledgeBuildTask, User
from schemas import RetrievalTestRequest
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
    ai = ai_service.ai_service
    courses = get_all_course_status(ai)

    total = len(courses)
    doc_ready = len([c for c in courses if c["doc_exists"]])
    vector_ready = len([c for c in courses if c["vector_db_exists"]])
    loaded = len([c for c in courses if c["loaded"]])

    return {
        "api_status": "running",
        "ai_status": "initialized" if ai else "not_initialized",
        "model_name": settings.DOUBAO_MODEL,
        "api_key_configured": bool(settings.ARK_API_KEY),
        "total_courses": total,
        "doc_ready_courses": doc_ready,
        "vector_ready_courses": vector_ready,
        "loaded_courses": loaded,
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
        raise HTTPException(status_code=400, detail=result.get("error", "上传失败"))
    return result


def run_build_task(task_id: str, course_id: str):
    """后台执行知识库构建任务"""
    db = SessionLocal()
    logs: list = []

    def append_log(message: str):
        logs.append(message)

    try:
        task = db.query(KnowledgeBuildTask).filter(KnowledgeBuildTask.id == task_id).first()
        if not task:
            return

        task.status = "running"
        task.started_at = datetime.utcnow()
        task.log = "任务开始"
        db.commit()

        result = build_course_vectordb(course_id, log_cb=append_log)

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
                append_log(f"AI 服务重载: {reload_result}")
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
        id=task_id, course_id=course_id,
        course_name=course_name, status="pending",
    )
    db.add(task)
    db.commit()

    background_tasks.add_task(run_build_task, task_id, course_id)

    return {"task_id": task_id, "course_id": course_id, "course_name": course_name, "status": "pending"}


@router.get("/knowledge/tasks")
async def list_build_tasks(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(KnowledgeBuildTask)
        .order_by(KnowledgeBuildTask.created_at.desc())
        .limit(20)
        .all()
    )


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
    payload: RetrievalTestRequest,
    current_user: User = Depends(get_current_admin_user),
):
    if not ai_service.ai_service:
        raise HTTPException(status_code=500, detail="AI 服务尚未初始化")
    return ai_service.ai_service.test_retrieval(payload.course_id, payload.query, payload.top_k)


@router.get("/system/health")
async def admin_system_health(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    database_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        database_status = f"error: {e}"

    ai = ai_service.ai_service
    loaded = ai.get_loaded_courses() if ai else {}

    return {
        "api_status": "running",
        "database_status": database_status,
        "ai_status": "initialized" if ai else "not_initialized",
        "model_name": settings.DOUBAO_MODEL,
        "api_key_configured": bool(settings.ARK_API_KEY),
        "embedding_model": "BAAI/bge-large-zh-v1.5",
        "loaded_courses": loaded,
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
