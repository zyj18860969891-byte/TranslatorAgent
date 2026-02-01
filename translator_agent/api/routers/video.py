#!/usr/bin/env python3
"""
视频处理API路由

提供视频处理相关的REST API接口
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pathlib import Path

from ...data.video_processor import VideoProcessor, VideoProcessingConfig
from ...core.modelscope_integration import ModelScopeClient
from ..schemas import (
    VideoProcessingRequest,
    VideoProcessingResponse,
    VideoTranslationRequest,
    VideoTranslationResponse,
    TaskInfo,
    TaskStatus,
    ErrorResponse
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/video", tags=["video"])

# 任务存储
_tasks: Dict[str, TaskInfo] = {}


@router.get("/health", response_model=dict)
async def health_check():
    """视频处理服务健康检查"""
    return {
        "status": "healthy",
        "service": "video_processing",
        "timestamp": time.time()
    }


@router.post("/process", response_model=VideoProcessingResponse)
async def process_video(request: VideoProcessingRequest):
    """处理视频（同步方式）"""
    start_time = time.time()
    
    try:
        # 验证视频文件
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=400, detail=f"Video file not found: {request.video_path}")
        
        # 创建配置
        config = VideoProcessingConfig(
            frame_rate=request.frame_rate,
            max_frames=request.max_frames,
            batch_size=request.batch_size,
            output_dir=str(video_path.parent / "output"),
            temp_dir=str(video_path.parent / "temp")
        )
        
        # 创建ModelScope客户端
        model_client = ModelScopeClient()
        
        # 创建视频处理器
        processor = VideoProcessor(config, model_client=model_client)
        
        # 执行处理
        results = await processor.process_video(
            video_path=str(video_path),
            enable_subtitle_extraction=request.enable_subtitle_extraction,
            enable_subtitle_erasure=request.enable_subtitle_erasure,
            enable_visual_analysis=request.enable_visual_analysis
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建响应
        response = VideoProcessingResponse(
            success=True,
            task_id=None,
            video_path=results.get('video_path'),
            extracted_frames=results.get('extracted_frames', []),
            subtitle_path=results.get('subtitle_path'),
            analysis_path=results.get('analysis_path'),
            processing_time=processing_time,
            frame_count=results.get('frame_count', 0),
            subtitle_count=results.get('subtitle_count', 0),
            errors=results.get('errors', []),
            metadata=results.get('metadata', {})
        )
        
        logger.info(f"Video processing completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        processing_time = time.time() - start_time
        
        error_response = ErrorResponse(
            success=False,
            error_code="VIDEO_PROCESSING_FAILED",
            error_message=str(e),
            details={"video_path": request.video_path},
            timestamp=time.time()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@router.post("/process/async", response_model=TaskInfo)
async def process_video_async(request: VideoProcessingRequest, background_tasks: BackgroundTasks):
    """处理视频（异步方式）"""
    task_id = str(uuid.uuid4())
    
    try:
        # 验证视频文件
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=400, detail=f"Video file not found: {request.video_path}")
        
        # 创建任务
        task = TaskInfo(
            task_id=task_id,
            task_type="video_processing",
            status=TaskStatus.PENDING,
            created_at=time.time(),
            progress=0.0,
            metadata=request.dict()
        )
        
        # 存储任务
        _tasks[task_id] = task
        
        # 添加后台任务
        background_tasks.add_task(
            _process_video_background,
            task_id=task_id,
            request=request
        )
        
        logger.info(f"Video processing task created: {task_id}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to create video processing task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {e}")


async def _process_video_background(task_id: str, request: VideoProcessingRequest):
    """后台处理视频"""
    start_time = time.time()
    
    try:
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.PROCESSING
        _tasks[task_id].started_at = time.time()
        _tasks[task_id].progress = 0.1
        
        # 验证视频文件
        video_path = Path(request.video_path)
        
        # 创建配置
        config = VideoProcessingConfig(
            frame_rate=request.frame_rate,
            max_frames=request.max_frames,
            batch_size=request.batch_size,
            output_dir=str(video_path.parent / "output"),
            temp_dir=str(video_path.parent / "temp")
        )
        
        # 创建ModelScope客户端
        model_client = ModelScopeClient()
        
        # 创建视频处理器
        processor = VideoProcessor(config, model_client=model_client)
        
        # 执行处理
        results = await processor.process_video(
            video_path=str(video_path),
            enable_subtitle_extraction=request.enable_subtitle_extraction,
            enable_subtitle_erasure=request.enable_subtitle_erasure,
            enable_visual_analysis=request.enable_visual_analysis
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.COMPLETED
        _tasks[task_id].completed_at = time.time()
        _tasks[task_id].progress = 1.0
        _tasks[task_id].result = {
            'success': True,
            'video_path': results.get('video_path'),
            'extracted_frames': results.get('extracted_frames', []),
            'subtitle_path': results.get('subtitle_path'),
            'analysis_path': results.get('analysis_path'),
            'processing_time': processing_time,
            'frame_count': results.get('frame_count', 0),
            'subtitle_count': results.get('subtitle_count', 0),
            'errors': results.get('errors', []),
            'metadata': results.get('metadata', {})
        }
        
        logger.info(f"Video processing task completed: {task_id} in {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Video processing task failed: {task_id} - {e}")
        
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.FAILED
        _tasks[task_id].completed_at = time.time()
        _tasks[task_id].progress = 1.0
        _tasks[task_id].error = str(e)


@router.post("/translate", response_model=VideoTranslationResponse)
async def translate_video(request: VideoTranslationRequest):
    """翻译视频（兼容旧版本）"""
    start_time = time.time()
    
    try:
        # 验证视频文件
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=400, detail=f"Video file not found: {request.video_path}")
        
        # 创建配置
        config = VideoProcessingConfig(
            frame_rate=2.0,
            max_frames=100,
            batch_size=10,
            output_dir=str(video_path.parent / "output"),
            temp_dir=str(video_path.parent / "temp")
        )
        
        # 创建ModelScope客户端
        model_client = ModelScopeClient()
        
        # 创建视频处理器
        processor = VideoProcessor(config, model_client=model_client)
        
        # 执行处理
        results = await processor.process_video(
            video_path=str(video_path),
            enable_subtitle_extraction=request.enable_subtitle_extraction,
            enable_subtitle_erasure=request.enable_subtitle_erasure,
            enable_visual_analysis=False
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建响应
        response = VideoTranslationResponse(
            success=True,
            video_path=results.get('video_path', str(video_path)),
            extracted_frames=results.get('extracted_frames', []),
            translated_subtitles=results.get('subtitle_path'),
            processing_time=processing_time,
            frame_count=results.get('frame_count', 0),
            subtitle_count=results.get('subtitle_count', 0),
            errors=results.get('errors', []),
            metadata=results.get('metadata', {})
        )
        
        logger.info(f"Video translation completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Video translation failed: {e}")
        processing_time = time.time() - start_time
        
        error_response = ErrorResponse(
            success=False,
            error_code="VIDEO_TRANSLATION_FAILED",
            error_message=str(e),
            details={"video_path": request.video_path},
            timestamp=time.time()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@router.get("/tasks/{task_id}", response_model=TaskInfo)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    return _tasks[task_id]


@router.get("/tasks", response_model=list[TaskInfo])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="任务状态过滤"),
    limit: int = Query(20, description="返回的任务数量限制")
):
    """列出任务"""
    tasks = list(_tasks.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    # 按创建时间倒序排序
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    return tasks[:limit]


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    task = _tasks[task_id]
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        raise HTTPException(status_code=400, detail=f"Task cannot be cancelled: {task.status}")
    
    task.status = TaskStatus.CANCELLED
    task.completed_at = time.time()
    
    logger.info(f"Task cancelled: {task_id}")
    return {"success": True, "task_id": task_id, "status": "cancelled"}
