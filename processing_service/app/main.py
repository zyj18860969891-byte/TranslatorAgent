"""
Python处理服务主应用
提供基于Qwen3的真实任务处理能力
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加app目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.routes import router as processing_router
from app.models.task_processor import TaskProcessor
from app.config.settings import Settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化配置
settings = Settings()

# 初始化FastAPI应用
app = FastAPI(
    title="Translator Agent Processing Service",
    description="基于Qwen3的真实任务处理服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化任务处理器
task_processor = TaskProcessor(settings)

# 包含处理路由
app.include_router(processing_router, prefix="/api/v1/process", tags=["processing"])

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "processing-service",
        "timestamp": "2026-02-04T00:00:00Z"
    }

@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "Translator Agent Processing Service",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )