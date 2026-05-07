from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import settings
from database import init_db
from routers import auth, chat, admin
from ai_service import get_ai_service  # 导入get_ai_service函数
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="智能课程助教聊天机器人 API",
    description="基于AI的课程助教后端服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=0,  # 禁用预检缓存，避免后端重启后浏览器缓存失效预检结果
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("正在初始化数据库...")
    try:
        init_db()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

    # 自动创建管理员账号
    if settings.ADMIN_DEFAULT_PASSWORD:
        from database import SessionLocal
        from models import User
        from auth import get_password_hash
        db = SessionLocal()
        try:
            for username in settings.ADMIN_USERNAMES:
                existing = db.query(User).filter(User.username == username).first()
                if existing:
                    if not existing.is_admin:
                        existing.is_admin = True
                        db.commit()
                        print(f"✅ 用户 '{username}' 已升级为管理员")
                else:
                    db.add(User(
                        username=username,
                        email=settings.ADMIN_DEFAULT_EMAIL,
                        password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
                        is_admin=True,
                    ))
                    db.commit()
                    print(f"✅ 管理员 '{username}' 已自动创建，密码为 .env 中 ADMIN_DEFAULT_PASSWORD")
        except Exception as e:
            print(f"⚠️ 管理员账号初始化失败: {e}")
        finally:
            db.close()
    else:
        print("💡 ADMIN_DEFAULT_PASSWORD 未设置，管理员需通过注册页面创建（用户名须在 ADMIN_USERNAMES 中）")

    # 在应用启动时强制创建新的AI服务实例
    print("正在初始化AI服务...")
    import ai_service
    ai_service.ai_service = get_ai_service()
    print("✅ AI服务初始化完成！")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能课程助教聊天机器人 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "API服务正常运行"}

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发环境启用热重载
        log_level="info"
    )