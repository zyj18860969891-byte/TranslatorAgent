from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    translation_router,
    video_router,
    subtitle_router,
    task_router
)
from . import routes

app = FastAPI(
    title="Translator Agent API",
    description="智能翻译系统 REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含所有路由
app.include_router(routes.router, prefix="/api/v1")  # 兼容旧版本路由
app.include_router(translation_router, prefix="/api/v1")
app.include_router(video_router, prefix="/api/v1")
app.include_router(subtitle_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Translator Agent API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }

@app.get("/health")
@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "translation": "healthy",
            "video": "healthy",
            "subtitle": "healthy",
            "task": "healthy"
        }
    }

@app.get("/api/info")
def api_info():
    """API信息"""
    return {
        "name": "Translator Agent API",
        "version": "1.0.0",
        "description": "智能翻译系统 REST API",
        "endpoints": {
            "translation": "/api/v1/translation",
            "video": "/api/v1/video",
            "subtitle": "/api/v1/subtitle",
            "task": "/api/v1/tasks",
            "health": "/health",
            "docs": "/api/docs"
        }
    }