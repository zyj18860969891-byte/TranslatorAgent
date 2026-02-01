"""
Qwen3-Omni-Flash 字幕提取服务
集成到 OpenManus TranslatorAgent 中
"""

import os
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..core.config import Config
from ..utils.file_utils import ensure_directory, cleanup_temp_files
from ..models.subtitle import SubtitleSegment, SubtitleTask
from .enhanced_qwen3_subtitle_extractor import EnhancedQwen3SubtitleExtractor

logger = logging.getLogger(__name__)

class Qwen3SubtitleService:
    """Qwen3-Omni-Flash 字幕提取服务"""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.get_qwen3_api_key()
        self.extractor = EnhancedQwen3SubtitleExtractor(self.api_key)
        self.tasks_dir = Path("tasks")
        self.output_dir = Path("output")
        
        # 确保目录存在
        ensure_directory(self.tasks_dir)
        ensure_directory(self.output_dir)
        
        # 任务状态跟踪
        self.active_tasks: Dict[str, SubtitleTask] = {}
        
    async def extract_subtitles(self, video_path: str, 
                              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        异步提取字幕
        
        Args:
            video_path: 视频文件路径
            options: 处理选项
            
        Returns:
            处理结果
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())
        task_dir = self.tasks_dir / task_id
        
        # 创建任务对象
        task = SubtitleTask(
            task_id=task_id,
            video_path=video_path,
            status="processing",
            created_at=datetime.now(),
            options=options or {}
        )
        
        # 保存任务信息
        self._save_task_info(task)
        
        try:
            # 异步处理
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self._extract_subtitles_sync,
                video_path, 
                task_id,
                options
            )
            
            # 更新任务状态
            task.status = "completed" if result["success"] else "failed"
            task.completed_at = datetime.now()
            task.result = result
            
            self._save_task_info(task)
            self.active_tasks[task_id] = task
            
            return result
            
        except Exception as e:
            logger.error(f"字幕提取失败: {e}")
            
            # 更新任务状态
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            self._save_task_info(task)
            self.active_tasks[task_id] = task
            
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def _extract_subtitles_sync(self, video_path: str, task_id: str, 
                               options: Dict[str, Any]) -> Dict[str, Any]:
        """同步提取字幕（在线程池中执行）"""
        try:
            # 生成输出路径
            output_filename = f"subtitles_{task_id}.srt"
            output_path = self.output_dir / output_filename
            
            # 执行字幕提取
            result = self.extractor.extract_subtitles_from_video(
                video_path, 
                str(output_path),
                task_id
            )
            
            # 添加任务相关信息
            result["task_id"] = task_id
            result["output_filename"] = output_filename
            result["output_path"] = str(output_path)
            
            return result
            
        except Exception as e:
            logger.error(f"同步字幕提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "video_path": task.video_path,
                "error": task.error,
                "result": task.result
            }
        
        # 从文件加载任务信息
        task_file = self.tasks_dir / task_id / "task_info.json"
        if task_file.exists():
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                return task_data
            except Exception as e:
                logger.error(f"加载任务信息失败: {e}")
        
        return None
    
    def list_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出最近的任务"""
        tasks = []
        
        # 从活动任务中获取
        for task_id, task in list(self.active_tasks.items())[-limit:]:
            tasks.append({
                "task_id": task.task_id,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "video_path": task.video_path,
                "error": task.error
            })
        
        return tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status == "processing":
                task.status = "cancelled"
                task.completed_at = datetime.now()
                self._save_task_info(task)
                return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的任务"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=max_age_hours)
        
        for task_id, task in list(self.active_tasks.items()):
            if (task.status in ["completed", "failed", "cancelled"] and 
                task.completed_at and 
                task.completed_at < cutoff_time):
                
                # 删除任务文件
                task_dir = self.tasks_dir / task_id
                if task_dir.exists():
                    import shutil
                    shutil.rmtree(task_dir)
                
                # 从活动任务中移除
                del self.active_tasks[task_id]
                logger.info(f"已清理任务: {task_id}")
    
    def _save_task_info(self, task: SubtitleTask):
        """保存任务信息"""
        task_dir = self.tasks_dir / task.task_id
        ensure_directory(task_dir)
        
        task_file = task_dir / "task_info.json"
        task_data = {
            "task_id": task.task_id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "video_path": task.video_path,
            "error": task.error,
            "result": task.result
        }
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务信息失败: {e}")
    
    def get_task_output(self, task_id: str) -> Optional[str]:
        """获取任务输出文件路径"""
        task = self.active_tasks.get(task_id)
        if task and task.status == "completed" and task.result:
            return task.result.get("output_path")
        return None
    
    def get_processing_progress(self, task_id: str) -> Dict[str, Any]:
        """获取处理进度"""
        task = self.active_tasks.get(task_id)
        if not task:
            return {"progress": 0, "status": "not_found"}
        
        if task.status == "processing":
            # 这里可以添加更详细的进度信息
            return {
                "progress": 50,  # 简化的进度显示
                "status": "processing",
                "message": "正在处理中..."
            }
        elif task.status == "completed":
            return {
                "progress": 100,
                "status": "completed",
                "message": "处理完成"
            }
        elif task.status == "failed":
            return {
                "progress": 0,
                "status": "failed",
                "message": f"处理失败: {task.error}"
            }
        else:
            return {
                "progress": 0,
                "status": task.status,
                "message": f"状态: {task.status}"
            }

class SubtitleTask:
    """字幕任务数据类"""
    
    def __init__(self, task_id: str, video_path: str, status: str, 
                 created_at: datetime, options: Dict[str, Any] = None):
        self.task_id = task_id
        self.video_path = video_path
        self.status = status
        self.created_at = created_at
        self.completed_at = None
        self.error = None
        self.result = None
        self.options = options or {}