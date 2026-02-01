#!/usr/bin/env python3
"""
字幕处理API路由

提供字幕处理相关的REST API接口
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pathlib import Path

from ...data.subtitle_processor import (
    SubtitleProcessor,
    SubtitleProcessingConfig,
    AlignmentConfig,
    SyncConfig
)
from ..schemas import (
    SubtitleProcessingRequest,
    SubtitleProcessingResponse,
    SubtitleTranslationRequest,
    SubtitleTranslationResponse,
    TaskInfo,
    TaskStatus,
    ErrorResponse
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/subtitle", tags=["subtitle"])

# 任务存储
_tasks: Dict[str, TaskInfo] = {}


@router.get("/health", response_model=dict)
async def health_check():
    """字幕处理服务健康检查"""
    return {
        "status": "healthy",
        "service": "subtitle_processing",
        "timestamp": time.time()
    }


@router.post("/process", response_model=SubtitleProcessingResponse)
async def process_subtitle(request: SubtitleProcessingRequest):
    """处理字幕（同步方式）"""
    start_time = time.time()
    
    try:
        # 验证字幕文件
        subtitle_path = Path(request.subtitle_path)
        if not subtitle_path.exists():
            raise HTTPException(status_code=400, detail=f"Subtitle file not found: {request.subtitle_path}")
        
        # 创建配置
        config = SubtitleProcessingConfig(
            source_lang=request.source_language,
            target_lang=request.target_language,
            enable_ocr=False,
            enable_alignment=request.enable_alignment,
            enable_sync=request.enable_sync
        )
        
        # 设置对齐配置
        if request.enable_alignment:
            config.alignment_config = AlignmentConfig(
                alignment_method=request.alignment_method
            )
        
        # 设置同步配置
        if request.enable_sync:
            config.sync_config = SyncConfig(
                sync_method=request.sync_method
            )
        
        # 创建字幕处理器
        processor = SubtitleProcessor(config)
        
        # 加载字幕
        segments = await processor.load_srt(str(subtitle_path))
        
        # 翻译字幕
        if request.enable_translation:
            from ...core.translator import TranslatorFactory, TranslationEngine
            translator = TranslatorFactory.create_translator(TranslationEngine.MIMO)
            segments = await processor.translate_subtitles(segments, translator)
        
        # 对齐时间轴
        if request.enable_alignment and request.reference_segments:
            # 将参考段转换为SRTSegment
            from ...data.subtitle_processor import SRTSegment
            reference_segments = [
                SRTSegment(
                    index=seg.get('index', i + 1),
                    start_time=seg.get('start_time', 0),
                    end_time=seg.get('end_time', 1),
                    text=seg.get('text', '')
                )
                for i, seg in enumerate(request.reference_segments)
            ]
            segments = await processor.align_timestamps(segments, reference_segments)
        
        # 同步字幕
        if request.enable_sync:
            segments = await processor.sync_subtitles(segments, request.reference_audio)
        
        # 检查冲突
        conflicts_found = 0
        conflicts_fixed = 0
        if request.enable_conflict_check:
            conflicts = processor.check_conflicts(segments)
            conflicts_found = len(conflicts['overlaps']) + len(conflicts['gaps'])
            
            if request.enable_conflict_fix and conflicts_found > 0:
                segments = await processor.fix_conflicts(segments, conflicts)
                conflicts_fixed = conflicts_found
        
        # 清理字幕
        segments = await processor.clean_subtitles(segments)
        
        # 保存处理后的字幕
        output_path = request.output_path
        if not output_path:
            output_path = str(subtitle_path.parent / f"{subtitle_path.stem}_processed.srt")
        
        await processor.save_srt(segments, output_path)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建响应
        response = SubtitleProcessingResponse(
            success=True,
            task_id=None,
            original_subtitle_path=str(subtitle_path),
            processed_subtitle_path=output_path,
            subtitle_count=len(segments),
            processing_time=processing_time,
            aligned_count=processor.stats.get('aligned_segments', 0),
            synced_count=processor.stats.get('synced_segments', 0),
            conflicts_found=conflicts_found,
            conflicts_fixed=conflicts_fixed,
            errors=[],
            metadata={
                'stats': processor.stats,
                'config': config.__dict__
            }
        )
        
        logger.info(f"Subtitle processing completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Subtitle processing failed: {e}")
        processing_time = time.time() - start_time
        
        error_response = ErrorResponse(
            success=False,
            error_code="SUBTITLE_PROCESSING_FAILED",
            error_message=str(e),
            details={"subtitle_path": request.subtitle_path},
            timestamp=time.time()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@router.post("/process/async", response_model=TaskInfo)
async def process_subtitle_async(request: SubtitleProcessingRequest, background_tasks: BackgroundTasks):
    """处理字幕（异步方式）"""
    task_id = str(uuid.uuid4())
    
    try:
        # 验证字幕文件
        subtitle_path = Path(request.subtitle_path)
        if not subtitle_path.exists():
            raise HTTPException(status_code=400, detail=f"Subtitle file not found: {request.subtitle_path}")
        
        # 创建任务
        task = TaskInfo(
            task_id=task_id,
            task_type="subtitle_processing",
            status=TaskStatus.PENDING,
            created_at=time.time(),
            progress=0.0,
            metadata=request.dict()
        )
        
        # 存储任务
        _tasks[task_id] = task
        
        # 添加后台任务
        background_tasks.add_task(
            _process_subtitle_background,
            task_id=task_id,
            request=request
        )
        
        logger.info(f"Subtitle processing task created: {task_id}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to create subtitle processing task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {e}")


async def _process_subtitle_background(task_id: str, request: SubtitleProcessingRequest):
    """后台处理字幕"""
    start_time = time.time()
    
    try:
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.PROCESSING
        _tasks[task_id].started_at = time.time()
        _tasks[task_id].progress = 0.1
        
        # 验证字幕文件
        subtitle_path = Path(request.subtitle_path)
        
        # 创建配置
        config = SubtitleProcessingConfig(
            source_lang=request.source_language,
            target_lang=request.target_language,
            enable_ocr=False,
            enable_alignment=request.enable_alignment,
            enable_sync=request.enable_sync
        )
        
        # 设置对齐配置
        if request.enable_alignment:
            config.alignment_config = AlignmentConfig(
                alignment_method=request.alignment_method
            )
        
        # 设置同步配置
        if request.enable_sync:
            config.sync_config = SyncConfig(
                sync_method=request.sync_method
            )
        
        # 创建字幕处理器
        processor = SubtitleProcessor(config)
        
        # 加载字幕
        segments = await processor.load_srt(str(subtitle_path))
        
        # 翻译字幕
        if request.enable_translation:
            from ...core.translator import TranslatorFactory, TranslationEngine
            translator = TranslatorFactory.create_translator(TranslationEngine.MIMO)
            segments = await processor.translate_subtitles(segments, translator)
        
        # 对齐时间轴
        if request.enable_alignment and request.reference_segments:
            from ...data.subtitle_processor import SRTSegment
            reference_segments = [
                SRTSegment(
                    index=seg.get('index', i + 1),
                    start_time=seg.get('start_time', 0),
                    end_time=seg.get('end_time', 1),
                    text=seg.get('text', '')
                )
                for i, seg in enumerate(request.reference_segments)
            ]
            segments = await processor.align_timestamps(segments, reference_segments)
        
        # 同步字幕
        if request.enable_sync:
            segments = await processor.sync_subtitles(segments, request.reference_audio)
        
        # 检查冲突
        conflicts_found = 0
        conflicts_fixed = 0
        if request.enable_conflict_check:
            conflicts = processor.check_conflicts(segments)
            conflicts_found = len(conflicts['overlaps']) + len(conflicts['gaps'])
            
            if request.enable_conflict_fix and conflicts_found > 0:
                segments = await processor.fix_conflicts(segments, conflicts)
                conflicts_fixed = conflicts_found
        
        # 清理字幕
        segments = await processor.clean_subtitles(segments)
        
        # 保存处理后的字幕
        output_path = request.output_path
        if not output_path:
            output_path = str(subtitle_path.parent / f"{subtitle_path.stem}_processed.srt")
        
        await processor.save_srt(segments, output_path)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.COMPLETED
        _tasks[task_id].completed_at = time.time()
        _tasks[task_id].progress = 1.0
        _tasks[task_id].result = {
            'success': True,
            'original_subtitle_path': str(subtitle_path),
            'processed_subtitle_path': output_path,
            'subtitle_count': len(segments),
            'processing_time': processing_time,
            'aligned_count': processor.stats.get('aligned_segments', 0),
            'synced_count': processor.stats.get('synced_segments', 0),
            'conflicts_found': conflicts_found,
            'conflicts_fixed': conflicts_fixed,
            'errors': [],
            'metadata': {
                'stats': processor.stats,
                'config': config.__dict__
            }
        }
        
        logger.info(f"Subtitle processing task completed: {task_id} in {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Subtitle processing task failed: {task_id} - {e}")
        
        # 更新任务状态
        _tasks[task_id].status = TaskStatus.FAILED
        _tasks[task_id].completed_at = time.time()
        _tasks[task_id].progress = 1.0
        _tasks[task_id].error = str(e)


@router.post("/translate", response_model=SubtitleTranslationResponse)
async def translate_subtitle(request: SubtitleTranslationRequest):
    """翻译字幕（兼容旧版本）"""
    start_time = time.time()
    
    try:
        # 验证字幕文件
        subtitle_path = Path(request.subtitle_path)
        if not subtitle_path.exists():
            raise HTTPException(status_code=400, detail=f"Subtitle file not found: {request.subtitle_path}")
        
        # 创建配置
        config = SubtitleProcessingConfig(
            source_lang=request.source_language,
            target_lang=request.target_language,
            enable_ocr=False
        )
        
        # 创建字幕处理器
        processor = SubtitleProcessor(config)
        
        # 加载字幕
        segments = await processor.load_srt(str(subtitle_path))
        
        # 翻译字幕
        from ...core.translator import TranslatorFactory, TranslationEngine
        translator = TranslatorFactory.create_translator(TranslationEngine.MIMO)
        segments = await processor.translate_subtitles(segments, translator)
        
        # 合并字幕段
        if request.merge_segments:
            segments = await processor.merge_segments(segments)
        
        # 保存翻译后的字幕
        output_path = request.output_path
        if not output_path:
            output_path = str(subtitle_path.parent / f"{subtitle_path.stem}_translated.srt")
        
        await processor.save_srt(segments, output_path)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建响应
        response = SubtitleTranslationResponse(
            success=True,
            original_subtitle_path=str(subtitle_path),
            translated_subtitle_path=output_path,
            subtitle_count=len(segments),
            processing_time=processing_time,
            errors=[],
            metadata={
                'stats': processor.stats,
                'config': config.__dict__
            }
        )
        
        logger.info(f"Subtitle translation completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Subtitle translation failed: {e}")
        processing_time = time.time() - start_time
        
        error_response = ErrorResponse(
            success=False,
            error_code="SUBTITLE_TRANSLATION_FAILED",
            error_message=str(e),
            details={"subtitle_path": request.subtitle_path},
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
