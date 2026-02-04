"""
数据验证工具
"""

from typing import Dict, Any, List
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_task_data(task_data: Dict[str, Any]):
    """验证任务数据"""
    if not isinstance(task_data, dict):
        raise ValueError("任务数据必须是字典类型")
    
    required_fields = ["type", "module"]
    for field in required_fields:
        if field not in task_data:
            raise ValueError(f"缺少必要字段: {field}")
    
    # 验证任务类型
    valid_types = ["video-translate", "subtitle-extract", "emotion-analysis", "translation"]
    if task_data["type"] not in valid_types:
        raise ValueError(f"无效的任务类型: {task_data['type']}")
    
    # 验证模块
    valid_modules = ["video-translate", "subtitle", "translation", "emotion"]
    if task_data["module"] not in valid_modules:
        raise ValueError(f"无效的模块: {task_data['module']}")

def validate_video_data(video_data: Dict[str, Any]):
    """验证视频数据"""
    if not isinstance(video_data, dict):
        raise ValueError("视频数据必须是字典类型")
    
    if "video_url" not in video_data:
        raise ValueError("缺少视频URL")
    
    if "operation" not in video_data:
        raise ValueError("缺少操作类型")

def validate_subtitle_data(subtitle_data: Dict[str, Any]):
    """验证字幕数据"""
    if not isinstance(subtitle_data, dict):
        raise ValueError("字幕数据必须是字典类型")
    
    if "subtitle_url" not in subtitle_data:
        raise ValueError("缺少字幕URL")
    
    if "operation" not in subtitle_data:
        raise ValueError("缺少操作类型")

def validate_translate_data(translate_data: Dict[str, Any]):
    """验证翻译数据"""
    if not isinstance(translate_data, dict):
        raise ValueError("翻译数据必须是字典类型")
    
    if "text" not in translate_data:
        raise ValueError("缺少文本内容")
    
    if "target_language" not in translate_data:
        raise ValueError("缺少目标语言")