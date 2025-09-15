from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import init_db
from routers import auth, chat
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
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("正在初始化数据库...")
    try:
        init_db()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

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