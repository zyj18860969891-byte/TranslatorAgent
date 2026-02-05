"""
处理服务路由
定义任务处理相关的API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import logging

# 添加app目录到路径
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# 安全导入OpenCV，处理缺失的系统库
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError as e:
    CV2_AVAILABLE = False
    print(f"OpenCV导入失败: {e}")

from processing_service.models.task_processor import TaskProcessor
from processing_service.utils.validators import validate_task_data

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局任务处理器实例（在main.py中初始化）
task_processor = None

@router.post("/tasks/{task_id}")
async def process_task(task_id: str, task_data: Dict[str, Any]):
    """处理任务"""
    try:
        logger.info(f"开始处理任务: {task_id}")
        
        # 验证任务数据
        validate_task_data(task_data)
        
        # 调用任务处理器
        result = await task_processor.process_task(task_id, task_data)
        
        logger.info(f"任务处理完成: {task_id}")
        return {
            "success": True,
            "message": "任务处理成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"任务处理失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/video")
async def process_video(task_id: str, video_data: Dict[str, Any]):
    """处理视频"""
    try:
        logger.info(f"开始处理视频: {task_id}")
        
        result = await task_processor.process_video(task_id, video_data)
        
        logger.info(f"视频处理完成: {task_id}")
        return {
            "success": True,
            "message": "视频处理成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"视频处理失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/subtitle")
async def process_subtitle(task_id: str, subtitle_data: Dict[str, Any]):
    """处理字幕"""
    try:
        logger.info(f"开始处理字幕: {task_id}")
        
        result = await task_processor.process_subtitle(task_id, subtitle_data)
        
        logger.info(f"字幕处理完成: {task_id}")
        return {
            "success": True,
            "message": "字幕处理成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"字幕处理失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/translate")
async def translate_text(task_id: str, translate_data: Dict[str, Any]):
    """翻译文本"""
    try:
        logger.info(f"开始翻译文本: {task_id}")
        
        result = await task_processor.translate_text(
            translate_data.get("text", ""),
            translate_data.get("target_language", "zh"),
            translate_data.get("source_language", "auto")
        )
        
        logger.info(f"文本翻译完成: {task_id}")
        return {
            "success": True,
            "message": "翻译成功",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"翻译失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务处理状态"""
    try:
        status = task_processor.get_task_status(task_id)
        return {
            "success": True,
            "message": "状态获取成功",
            "data": status
        }
    except Exception as e:
        logger.error(f"获取状态失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    try:
        result = task_processor.cancel_task(task_id)
        return {
            "success": True,
            "message": "任务取消成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"取消任务失败 {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))