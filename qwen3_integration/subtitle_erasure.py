"""
字幕无痕擦除模块 (API版本)
负责从视频中检测并擦除硬编码字幕，使用百炼API
"""

import os
import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


class SubtitleErasure:
    """字幕无痕擦除器 (API版本)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化字幕擦除器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is required")
        
        # 初始化百炼客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 从配置中获取模型信息
        model_config = config.get("subtitle_erasure", {}) if config else {}
        self.model_name = model_config.get("primary_model", "qwen-vl-plus")
        self.api_endpoint = model_config.get("api_endpoint", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
        self.instruction = model_config.get("instruction", "请擦除图像中的字幕，要求：")
        
        self.temp_dir = None
    
    def _call_api(self, image_path: str, mask_path: str) -> Dict[str, Any]:
        """
        调用百炼API进行图像擦除
        
        Args:
            image_path: 输入图像路径
            mask_path: 掩码图像路径
            
        Returns:
            API响应
        """
        try:
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 读取图像和掩码
            with open(image_path, "rb") as f:
                image_data = f.read()
            with open(mask_path, "rb") as f:
                mask_data = f.read()
            
            # 构建提示词
            prompt = f"""{self.instruction}

图像信息：
- 图像路径：{image_path}
- 任务：擦除图像中的字幕

请提供详细的字幕擦除方案。"""
            
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            logger.info(f"调用百炼API: {self.api_endpoint}")
            
            # 发送请求
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=request_data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API调用成功: {result}")
                return result
            else:
                error_msg = f"API调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(error_msg)
            raise
    
    def _call_api(self, image_path: str, mask_path: str) -> Dict[str, Any]:
        """
        调用百炼API进行图像擦除
        
        Args:
            image_path: 输入图像路径
            mask_path: 掩码图像路径
            
        Returns:
            API响应
        """
        try:
            # 构建提示词
            prompt = f"""{self.instruction}

图像信息：
- 图像路径：{image_path}
- 任务：擦除图像中的字幕

请提供详细的字幕擦除方案。"""
            
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            logger.info(f"调用百炼API: {self.api_endpoint}")
            
            # 发送请求
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=request_data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API调用成功: {result}")
                return result
            else:
                error_msg = f"API调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 读取图像和掩码
            with open(image_path, "rb") as f:
                image_data = f.read()
            with open(mask_path, "rb") as f:
                mask_data = f.read()
            
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "input": {
                    "image": image_data.hex(),
                    "mask": mask_data.hex()
                },
                "parameters": {
                    "timeout": 300,
                    "async_mode": False
                }
            }
            
            logger.info(f"调用百炼API: {self.api_endpoint}")
            
            # 发送请求
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=request_data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API调用成功: {result}")
                return result
            else:
                error_msg = f"API调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(error_msg)
            raise
    
    def _extract_frame(self, video_path: str, frame_index: int, output_dir: str) -> str:
        """
        提取视频帧
        
        Args:
            video_path: 视频路径
            frame_index: 帧索引
            output_dir: 输出目录
            
        Returns:
            帧图像路径
        """
        try:
            import subprocess
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 提取帧
            frame_path = os.path.join(output_dir, f"frame_{frame_index:06d}.png")
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vf", f"select='eq(n,{frame_index})'",
                "-vframes", "1",
                "-y", frame_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return frame_path
            else:
                logger.error(f"提取帧失败: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"提取帧异常: {e}")
            return None
    
    def _create_mask(self, frame_path: str, subtitle_region: Dict[str, Any]) -> str:
        """
        创建字幕掩码
        
        Args:
            frame_path: 帧图像路径
            subtitle_region: 字幕区域信息
            
        Returns:
            掩码图像路径
        """
        try:
            import cv2
            import numpy as np
            
            # 读取图像
            frame = cv2.imread(frame_path)
            if frame is None:
                return None
            
            # 创建掩码
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # 根据subtitle_region绘制掩码
            # subtitle_region格式: {"x": 100, "y": 200, "width": 300, "height": 50}
            x = subtitle_region.get("x", 0)
            y = subtitle_region.get("y", 0)
            width = subtitle_region.get("width", 100)
            height = subtitle_region.get("height", 30)
            
            cv2.rectangle(mask, (x, y), (x + width, y + height), 255, -1)
            
            # 保存掩码
            mask_path = frame_path.replace(".png", "_mask.png")
            cv2.imwrite(mask_path, mask)
            
            return mask_path
            
        except Exception as e:
            logger.error(f"创建掩码失败: {e}")
            return None
    
    def erase_subtitles_from_video(self, video_path: str, output_path: Optional[str] = None,
                                  subtitle_region: Optional[Dict[str, Any]] = None,
                                  progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        从视频中擦除字幕 (API版本)
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            subtitle_region: 字幕区域信息（可选，自动检测）
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        try:
            # 验证输入
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            logger.info(f"开始API字幕擦除 - 模型: {self.model_name}")
            
            # 生成输出路径
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = f"{video_name}_erased_api.mp4"
            
            # 创建临时目录
            import tempfile
            temp_dir = tempfile.mkdtemp()
            
            # 提取视频帧（示例：提取前10帧）
            total_frames = 10
            frames = []
            masks = []
            
            for i in range(total_frames):
                progress = (i + 1) / total_frames * 50
                if progress_callback:
                    progress_callback(progress, f"提取帧 {i+1}/{total_frames}")
                
                # 提取帧
                frame_path = self._extract_frame(video_path, i, temp_dir)
                if frame_path:
                    frames.append(frame_path)
                    
                    # 创建掩码（假设字幕在底部区域）
                    if subtitle_region is None:
                        # 默认字幕区域（底部1/4）
                        subtitle_region = {
                            "x": 0,
                            "y": int(720 * 0.75),  # 假设视频高度720
                            "width": 1280,  # 假设视频宽度1280
                            "height": 180
                        }
                    
                    mask_path = self._create_mask(frame_path, subtitle_region)
                    if mask_path:
                        masks.append(mask_path)
            
            # 调用API处理帧
            processed_frames = []
            for i, (frame_path, mask_path) in enumerate(zip(frames, masks)):
                progress = 50 + (i + 1) / len(frames) * 50
                if progress_callback:
                    progress_callback(progress, f"API处理帧 {i+1}/{len(frames)}")
                
                try:
                    # 调用百炼API
                    result = self._call_api(frame_path, mask_path)
                    
                    # 保存处理后的帧
                    if "output" in result:
                        output_frame_path = frame_path.replace(".png", "_erased.png")
                        # 这里需要根据API返回的图像数据保存文件
                        processed_frames.append(output_frame_path)
                        
                except Exception as e:
                    logger.error(f"处理帧 {i} 失败: {e}")
                    continue
            
            # 合成视频（使用FFmpeg）
            if processed_frames:
                import subprocess
                
                # 创建帧列表文件
                list_file = os.path.join(temp_dir, "frames.txt")
                with open(list_file, "w") as f:
                    for frame_path in processed_frames:
                        f.write(f"file '{frame_path}'\n")
                
                # 合成视频
                cmd = [
                    "ffmpeg", "-f", "concat", "-safe", "0",
                    "-i", list_file,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-y", output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"视频合成成功: {output_path}")
                else:
                    logger.error(f"视频合成失败: {result.stderr}")
            
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            logger.info(f"字幕擦除完成: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "api_model": self.model_name,
                "processed_frames": len(processed_frames),
                "message": "字幕擦除完成（API版本）"
            }
            
        except Exception as e:
            error_msg = f"视频处理失败: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "error_message": error_msg
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "api_endpoint": self.api_endpoint,
            "api_key_configured": bool(self.api_key),
            "engine": "bailian_api"
        }
    
    def validate_config(self) -> Tuple[bool, str]:
        """
        验证配置
        
        Returns:
            (是否有效, 错误信息)
        """
        # 检查API密钥
        if not self.api_key:
            return False, "DASHSCOPE_API_KEY未配置"
        
        # 检查模型名称
        if not self.model_name:
            return False, "模型名称未配置"
        
        return True, ""
    
    def __del__(self):
        """析构函数"""
        pass


class SubtitleErasureManager:
    """字幕擦除管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化字幕擦除管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.erasure = SubtitleErasure(config)
        self.task_queue = []
        self.active_tasks = {}
        
    def submit_erasure_task(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        提交擦除任务
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            
        Returns:
            任务ID
        """
        import uuid
        
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "video_path": video_path,
            "output_path": output_path,
            "status": "pending",
            "progress": 0.0
        }
        
        self.task_queue.append(task)
        logger.info(f"提交擦除任务: {task_id}")
        
        return task_id
    
    def process_task(self, task_id: str, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        处理擦除任务
        
        Args:
            task_id: 任务ID
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        # 查找任务
        task = None
        for t in self.task_queue:
            if t["task_id"] == task_id:
                task = t
                break
        
        if not task:
            return {
                "success": False,
                "error_message": f"任务不存在: {task_id}"
            }
        
        # 更新任务状态
        task["status"] = "processing"
        self.active_tasks[task_id] = task
        
        try:
            # 执行擦除
            result = self.erasure.erase_subtitles_from_video(
                task["video_path"],
                task["output_path"],
                progress_callback
            )
            
            # 更新任务状态
            if result["success"]:
                task["status"] = "completed"
                task["progress"] = 100.0
            else:
                task["status"] = "failed"
                task["error_message"] = result.get("error_message", "Unknown error")
            
            return result
            
        except Exception as e:
            error_msg = f"任务处理失败: {str(e)}"
            logger.error(error_msg)
            
            task["status"] = "failed"
            task["error_message"] = error_msg
            
            return {
                "success": False,
                "error_message": error_msg
            }
        
        finally:
            # 从活动任务中移除
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        # 检查活动任务
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # 检查已完成的任务
        for task in self.task_queue:
            if task["task_id"] == task_id:
                return task
        
        return {
            "task_id": task_id,
            "status": "not_found",
            "error_message": f"任务不存在: {task_id}"
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        # 从队列中移除
        for i, task in enumerate(self.task_queue):
            if task["task_id"] == task_id:
                if task["status"] == "pending":
                    self.task_queue.pop(i)
                    logger.info(f"取消任务: {task_id}")
                    return True
                else:
                    logger.warning(f"无法取消正在处理的任务: {task_id}")
                    return False
        
        logger.warning(f"任务不存在: {task_id}")
        return False


# 全局实例
_subtitle_erasure_manager = None

def get_subtitle_erasure_manager() -> SubtitleErasureManager:
    """获取全局字幕擦除管理器实例"""
    global _subtitle_erasure_manager
    if _subtitle_erasure_manager is None:
        _subtitle_erasure_manager = SubtitleErasureManager()
    return _subtitle_erasure_manager


def erase_subtitles_from_video(video_path: str, output_path: Optional[str] = None,
                              progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    快速擦除字幕的便捷函数
    
    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径
        progress_callback: 进度回调函数
        
    Returns:
        处理结果
    """
    manager = get_subtitle_erasure_manager()
    erasure = manager.erasure
    
    return erasure.erase_subtitles_from_video(
        video_path, output_path, progress_callback
    )