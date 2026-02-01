"""
Qwen3批量处理器
支持批量视频翻译、字幕提取和情感分析的高效处理工具
"""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

from .subtitle_extractor import SubtitleExtractor
from .video_translator import VideoTranslator
from .emotion_analyzer import EmotionAnalyzer

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型枚举"""
    SUBTITLE_EXTRACTION = "subtitle_extraction"
    VIDEO_TRANSLATION = "video_translation"
    EMOTION_ANALYSIS = "emotion_analysis"
    BATCH_PROCESSING = "batch_processing"

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BatchTask:
    """批量任务数据类"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    input_path: str
    output_path: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "parameters": self.parameters,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "progress": self.progress
        }

class BatchProcessor:
    """批量处理器类"""
    
    def __init__(self, 
                 max_workers: int = 4,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大工作线程数
            config: 配置字典
        """
        self.max_workers = max_workers
        self.config = config or self._load_default_config()
        
        # 初始化组件
        self.subtitle_extractor = SubtitleExtractor(self.config)
        self.video_translator = VideoTranslator(self.config)
        self.emotion_analyzer = EmotionAnalyzer(self.config)
        
        # 任务管理
        self.tasks: Dict[str, BatchTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0
        }
        
        logger.info(f"批量处理器初始化完成，最大工作线程数: {max_workers}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "max_workers": 4,
            "batch_size": 10,
            "enable_progress_tracking": True,
            "enable_error_recovery": True,
            "max_retries": 3,
            "retry_delay": 1.0,
            "timeout": 300,
            "cache_enabled": True,
            "cache_ttl": 3600
        }
    
    async def process_video_files(self,
                                video_files: List[str],
                                task_type: TaskType = TaskType.VIDEO_TRANSLATION,
                                target_language: str = "zh",
                                output_dir: str = "output",
                                **kwargs) -> List[Dict[str, Any]]:
        """
        批量处理视频文件
        
        Args:
            video_files: 视频文件路径列表
            task_type: 任务类型
            target_language: 目标语言（翻译任务）
            output_dir: 输出目录
            **kwargs: 额外参数
            
        Returns:
            处理结果列表
        """
        logger.info(f"开始批量处理 {len(video_files)} 个视频文件，任务类型: {task_type.value}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建任务
        tasks = []
        for i, video_file in enumerate(video_files):
            if not os.path.exists(video_file):
                logger.warning(f"视频文件不存在: {video_file}")
                continue
            
            # 生成输出文件路径
            video_name = Path(video_file).stem
            output_file = os.path.join(output_dir, f"{video_name}_result.json")
            
            # 创建任务
            task = BatchTask(
                task_id=f"batch_{task_type.value}_{i}_{int(time.time())}",
                task_type=task_type,
                status=TaskStatus.PENDING,
                input_path=video_file,
                output_path=output_file,
                parameters={
                    "target_language": target_language,
                    **kwargs
                }
            )
            
            tasks.append(task)
            self.tasks[task.task_id] = task
        
        # 更新统计信息
        self.stats["total_tasks"] = len(tasks)
        
        # 执行任务
        results = await self._execute_tasks(tasks)
        
        # 更新统计信息
        self.stats["completed_tasks"] = len([r for r in results if r.get("success", False)])
        self.stats["failed_tasks"] = len([r for r in results if not r.get("success", False)])
        
        # 计算平均处理时间
        if self.stats["completed_tasks"] > 0:
            self.stats["average_processing_time"] = self.stats["total_processing_time"] / self.stats["completed_tasks"]
        
        logger.info(f"批量处理完成: {self.stats['completed_tasks']}/{self.stats['total_tasks']} 成功")
        return results
    
    async def _execute_tasks(self, tasks: List[BatchTask]) -> List[Dict[str, Any]]:
        """执行任务列表"""
        results = []
        
        # 创建任务队列
        for task in tasks:
            await self.task_queue.put(task)
        
        # 启动任务处理器
        workers = []
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._task_worker(f"worker_{i}"))
            workers.append(worker)
        
        # 等待所有任务完成
        await self.task_queue.join()
        
        # 停止工作线程
        for worker in workers:
            worker.cancel()
        
        # 收集结果
        for task in tasks:
            results.append(task.to_dict())
        
        return results
    
    async def _task_worker(self, worker_name: str):
        """任务工作线程"""
        logger.info(f"任务工作线程 {worker_name} 启动")
        
        while True:
            try:
                # 获取任务
                task = await self.task_queue.get()
                
                # 执行任务
                await self._execute_single_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info(f"任务工作线程 {worker_name} 被取消")
                break
            except Exception as e:
                logger.error(f"任务工作线程 {worker_name} 出错: {e}")
    
    async def _execute_single_task(self, task: BatchTask):
        """执行单个任务"""
        logger.info(f"开始执行任务: {task.task_id}")
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        task.progress = 0.1
        
        try:
            # 根据任务类型执行
            if task.task_type == TaskType.SUBTITLE_EXTRACTION:
                result = await self._execute_subtitle_extraction(task)
            elif task.task_type == TaskType.VIDEO_TRANSLATION:
                result = await self._execute_video_translation(task)
            elif task.task_type == TaskType.EMOTION_ANALYSIS:
                result = await self._execute_emotion_analysis(task)
            elif task.task_type == TaskType.BATCH_PROCESSING:
                result = await self._execute_batch_processing(task)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")
            
            # 更新任务结果
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            
            # 保存结果
            if result and result.get("success"):
                self._save_task_result(task)
            
            logger.info(f"任务 {task.task_id} 执行完成")
            
        except Exception as e:
            # 更新任务状态
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.progress = 0.0
            
            logger.error(f"任务 {task.task_id} 执行失败: {e}")
            
            # 尝试错误恢复
            if self.config.get("enable_error_recovery", True):
                await self._error_recovery(task)
        
        finally:
            # 更新结束时间
            task.end_time = time.time()
            
            # 更新统计信息
            if task.start_time and task.end_time:
                processing_time = task.end_time - task.start_time
                self.stats["total_processing_time"] += processing_time
    
    async def _execute_subtitle_extraction(self, task: BatchTask) -> Dict[str, Any]:
        """执行字幕提取任务"""
        logger.info(f"执行字幕提取任务: {task.task_id}")
        
        # 更新进度
        task.progress = 0.3
        
        # 提取字幕
        loop = asyncio.get_event_loop()
        subtitles = await loop.run_in_executor(
            self.executor, 
            self.subtitle_extractor.extract, 
            task.input_path
        )
        
        # 更新进度
        task.progress = 0.8
        
        # 获取统计信息
        stats = self.subtitle_extractor.get_statistics(subtitles)
        
        # 保存字幕文件
        output_srt = task.output_path.replace('.json', '.srt')
        output_json = task.output_path
        
        success = True
        if not self.subtitle_extractor._save_srt(subtitles, output_srt):
            logger.error(f"保存SRT文件失败: {output_srt}")
            success = False
        
        if not self.subtitle_extractor._save_json(subtitles, output_json):
            logger.error(f"保存JSON文件失败: {output_json}")
            success = False
        
        # 更新进度
        task.progress = 1.0
        
        return {
            "success": success,
            "task_type": "subtitle_extraction",
            "video_path": task.input_path,
            "subtitle_count": len(subtitles),
            "statistics": stats,
            "output_files": [output_srt, output_json],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _execute_video_translation(self, task: BatchTask) -> Dict[str, Any]:
        """执行视频翻译任务"""
        logger.info(f"执行视频翻译任务: {task.task_id}")
        
        # 更新进度
        task.progress = 0.2
        
        # 翻译视频
        target_language = task.parameters.get("target_language", "zh")
        include_emotions = task.parameters.get("include_emotions", True)
        cultural_adaptation = task.parameters.get("cultural_adaptation", True)
        
        result = await self.video_translator.translate(
            video_path=task.input_path,
            target_language=target_language,
            include_emotions=include_emotions,
            cultural_adaptation=cultural_adaptation
        )
        
        # 更新进度
        task.progress = 0.8
        
        # 保存翻译结果
        output_srt = task.output_path.replace('.json', '_translated.srt')
        output_json = task.output_path
        
        success = True
        if result["success"]:
            if not self.video_translator._save_translations_srt(result["translations"], output_srt):
                logger.error(f"保存翻译SRT文件失败: {output_srt}")
                success = False
            
            if not self.video_translator._save_translations_json(result, output_json):
                logger.error(f"保存翻译JSON文件失败: {output_json}")
                success = False
        else:
            success = False
        
        # 更新进度
        task.progress = 1.0
        
        return {
            "success": success,
            "task_type": "video_translation",
            "video_path": task.input_path,
            "target_language": target_language,
            "translation_count": len(result.get("translations", [])),
            "emotions": result.get("emotions"),
            "output_files": [output_srt, output_json] if success else [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _execute_emotion_analysis(self, task: BatchTask) -> Dict[str, Any]:
        """执行情感分析任务"""
        logger.info(f"执行情感分析任务: {task.task_id}")
        
        # 首先提取字幕
        loop = asyncio.get_event_loop()
        subtitles = await loop.run_in_executor(
            self.executor, 
            self.subtitle_extractor.extract, 
            task.input_path
        )
        
        # 更新进度
        task.progress = 0.5
        
        # 分析情感
        emotions = await self.emotion_analyzer.analyze_subtitles(subtitles)
        
        # 更新进度
        task.progress = 0.8
        
        # 保存情感分析结果
        output_json = task.output_path
        
        success = True
        if emotions["success"]:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(emotions, f, ensure_ascii=False, indent=2)
        else:
            success = False
        
        # 更新进度
        task.progress = 1.0
        
        return {
            "success": success,
            "task_type": "emotion_analysis",
            "video_path": task.input_path,
            "subtitle_count": len(subtitles),
            "emotion_analysis": emotions,
            "output_files": [output_json] if success else [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _execute_batch_processing(self, task: BatchTask) -> Dict[str, Any]:
        """执行批量处理任务"""
        logger.info(f"执行批量处理任务: {task.task_id}")
        
        # 这里可以实现更复杂的批量处理逻辑
        # 例如：先提取字幕，再翻译，最后分析情感
        
        # 简化实现：只执行字幕提取
        return await self._execute_subtitle_extraction(task)
    
    async def _error_recovery(self, task: BatchTask):
        """错误恢复"""
        logger.info(f"尝试错误恢复任务: {task.task_id}")
        
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"错误恢复尝试 {attempt + 1}/{max_retries}")
                
                # 等待重试延迟
                await asyncio.sleep(retry_delay * (2 ** attempt))
                
                # 重新执行任务
                await self._execute_single_task(task)
                
                if task.status == TaskStatus.COMPLETED:
                    logger.info(f"任务 {task.task_id} 错误恢复成功")
                    break
                
            except Exception as e:
                logger.error(f"错误恢复尝试 {attempt + 1} 失败: {e}")
                continue
    
    def _save_task_result(self, task: BatchTask):
        """保存任务结果"""
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(task.output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存任务结果
            with open(task.output_path, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"任务结果已保存: {task.output_path}")
            
        except Exception as e:
            logger.error(f"保存任务结果失败: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.CANCELLED
            task.progress = 0.0
            logger.info(f"任务 {task_id} 已取消")
            return True
        return False
    
    def clear_completed_tasks(self):
        """清除已完成的任务"""
        completed_tasks = [
            task_id for task_id, task in self.tasks.items() 
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        
        for task_id in completed_tasks:
            del self.tasks[task_id]
        
        logger.info(f"清除了 {len(completed_tasks)} 个已完成的任务")
    
    async def process_directory(self,
                                input_dir: str,
                                output_dir: str,
                                task_type: TaskType = TaskType.VIDEO_TRANSLATION,
                                target_language: str = "zh",
                                file_extensions: List[str] = None,
                                **kwargs) -> List[Dict[str, Any]]:
        """
        处理目录中的所有视频文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            task_type: 任务类型
            target_language: 目标语言
            file_extensions: 文件扩展名列表
            **kwargs: 额外参数
            
        Returns:
            处理结果列表
        """
        if file_extensions is None:
            file_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        # 查找所有视频文件
        video_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in file_extensions):
                    video_files.append(os.path.join(root, file))
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        # 批量处理
        return await self.process_video_files(
            video_files=video_files,
            task_type=task_type,
            target_language=target_language,
            output_dir=output_dir,
            **kwargs
        )
    
    def create_custom_task(self,
                          task_id: str,
                          task_type: TaskType,
                          input_path: str,
                          output_path: str,
                          process_func: Callable,
                          parameters: Dict[str, Any] = None) -> str:
        """
        创建自定义任务
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            input_path: 输入路径
            output_path: 输出路径
            process_func: 处理函数
            parameters: 参数
            
        Returns:
            任务ID
        """
        task = BatchTask(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters or {}
        )
        
        self.tasks[task_id] = task
        
        # 添加到队列
        asyncio.create_task(self.task_queue.put(task))
        
        logger.info(f"创建自定义任务: {task_id}")
        return task_id
    
    async def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        等待所有任务完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否所有任务都完成
        """
        try:
            await asyncio.wait_for(self.task_queue.join(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.warning(f"等待任务完成超时: {timeout}秒")
            return False
    
    def shutdown(self):
        """关闭批量处理器"""
        logger.info("关闭批量处理器...")
        
        # 停止任务队列
        self.is_running = False
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        logger.info("批量处理器已关闭")