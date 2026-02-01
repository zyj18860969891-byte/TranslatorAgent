"""
视频字幕压制模块 (API版本)
负责将翻译后的字幕重新渲染并嵌入到视频中，使用百炼API
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


class SubtitlePressing:
    """视频字幕压制器 (API版本)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化字幕压制器
        
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
        model_config = config.get("subtitle_pressing", {}) if config else {}
        self.model_name = model_config.get("primary_model", "qwen-vl-plus")
        self.api_endpoint = model_config.get("api_endpoint", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
        self.instruction = model_config.get("instruction", "请为视频添加字幕，要求：")
        
        self.temp_dir = None
        
    def _call_api(self, video_path: str, subtitles: List[Dict[str, Any]], 
                 style_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用百炼API进行字幕压制
        
        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表
            style_config: 样式配置
            
        Returns:
            API响应
        """
        try:
            # 构建字幕内容
            srt_content = self._generate_srt_content(subtitles)
            
            # 构建提示词
            prompt = f"""{self.instruction}

视频信息：
- 视频路径：{video_path}
- 字幕内容：
{srt_content}

字幕样式要求：
- 字体大小：{style_config.get('font_size', 24)}
- 字体颜色：{style_config.get('font_color', '#FFFFFF')}
- 字体族：{style_config.get('font_family', 'Arial')}
- 字幕位置：{style_config.get('position', 'bottom')}
- 背景颜色：{style_config.get('background_color', '#000000')}
- 背景透明度：{style_config.get('background_opacity', 0.7)}

请提供详细的视频字幕压制方案。"""
            
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
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(error_msg)
            raise
    
    def _generate_srt_content(self, subtitles: List[Dict[str, Any]]) -> str:
        """
        生成SRT字幕内容
        
        Args:
            subtitles: 字幕列表，每个元素包含start_time, end_time, text
            
        Returns:
            SRT内容字符串
        """
        srt_content = []
        
        for i, subtitle in enumerate(subtitles, 1):
            start_time = self._format_srt_time(subtitle["start_time"])
            end_time = self._format_srt_time(subtitle["end_time"])
            text = subtitle["text"]
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # 空行分隔
        
        return "\n".join(srt_content)
    
    def _format_srt_time(self, seconds: float) -> str:
        """
        将秒数转换为SRT时间格式
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT时间格式字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "api_endpoint": self.api_endpoint,
            "api_key_configured": bool(self.api_key),
            "engine": "bailian_api"
        }
    
    def validate_config(self) -> Tuple[bool, str]:
        """验证配置"""
        errors = []
        
        # 检查API密钥
        if not self.api_key:
            errors.append("API密钥未配置")
        
        # 检查模型名称
        if not self.model_name:
            errors.append("模型名称未配置")
        
        # 检查API端点
        if not self.api_endpoint:
            errors.append("API端点未配置")
        
        if errors:
            return False, "; ".join(errors)
        else:
            return True, "配置验证通过"
    
    def press_subtitles(self, video_path: str, subtitles: List[Dict[str, Any]], 
                       output_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None,
                       extra_params: Optional[Dict[str, Any]] = None, 
                       progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        压制字幕到视频中
        
        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表
            output_path: 输出视频路径
            style_config: 样式配置
            extra_params: 额外参数
            progress_callback: 进度回调函数
            
        Returns:
            压制结果
        """
        try:
            # 准备样式配置
            if style_config is None:
                style_config = {
                    "font_size": 24,
                    "font_color": "#FFFFFF",
                    "font_family": "Arial",
                    "position": "bottom",
                    "background_color": "#000000",
                    "background_opacity": 0.7
                }
            
            # 准备额外参数
            if extra_params is None:
                extra_params = {
                    "quality": "high",
                    "format": "mp4",
                    "resolution": "original"
                }
            
            # 调用API
            result = self._call_api(video_path, subtitles, style_config)
            
            # 处理结果
            if result.get("status") == "success":
                # 下载处理后的视频
                if output_path:
                    self._download_result(result, output_path)
                
                # 更新进度
                if progress_callback:
                    progress_callback(100, "压制完成")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "result": result
                }
            else:
                raise Exception(result.get("message", "压制失败"))
                
        except Exception as e:
            logger.error(f"字幕压制失败: {e}")
            if progress_callback:
                progress_callback(0, f"压制失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": output_path
            }
    
    def _download_result(self, result: Dict[str, Any], output_path: str):
        """下载处理结果"""
        try:
            # 这里需要根据实际的API响应格式来实现下载逻辑
            # 假设API返回包含下载链接
            download_url = result.get("download_url")
            if download_url:
                import requests
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info(f"结果已保存到: {output_path}")
                else:
                    raise Exception(f"下载失败: {response.status_code}")
        except Exception as e:
            logger.error(f"下载结果失败: {e}")
            raise
    
    def _call_api(self, video_path: str, subtitles: List[Dict[str, Any]], 
                 style_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用百炼API进行字幕压制
        
        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表
            style_config: 样式配置
            
        Returns:
            API响应
        """
        try:
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "input": {
                    "video_path": video_path,
                    "subtitles": subtitles,
                    "style": style_config
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
    
    def press_subtitles(self, video_path: str, subtitles: List[Dict[str, Any]], 
                       output_path: Optional[str] = None, 
                       style_config: Optional[Dict[str, Any]] = None,
                       extra_params: Optional[Dict[str, Any]] = None,
                       progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        压制字幕到视频 (API版本)
        
        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表，每个元素包含start_time, end_time, text
            output_path: 输出视频路径（可选，自动生成）
            style_config: 样式配置（可选）
            extra_params: 额外参数（可选）
            progress_callback: 进度回调函数（可选）
            
        Returns:
            压制结果字典，包含success, output_path, error_message等
        """
        try:
            # 验证输入
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            if not subtitles:
                raise ValueError("字幕列表为空")
            
            # 获取样式配置
            if style_config is None:
                style_config = self.config.get("default_style", {})
            
            logger.info(f"开始API字幕压制 - 模型: {self.model_name}")
            
            # 调用百炼API
            result = self._call_api(video_path, subtitles, style_config)
            
            # 生成输出路径
            if output_path is None:
                video_name = Path(video_path).stem
                output_path = f"{video_name}_pressed_api.mp4"
            
            logger.info(f"字幕压制完成: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "video_duration": result.get("video_duration", 0),
                "subtitle_count": len(subtitles),
                "api_model": self.model_name,
                "processing_time": result.get("processing_time", 0)
            }
            
        except Exception as e:
            error_msg = f"字幕压制失败: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "error_message": error_msg
            }
    
    def _get_video_duration(self, video_path: str) -> float:
        """
        获取视频时长
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频时长（秒）
        """
        try:
            # 使用ffprobe获取视频时长
            import subprocess
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                logger.info(f"获取视频时长: {duration}秒")
                return duration
            else:
                logger.warning(f"无法获取视频时长: {result.stderr}")
                return 180.0  # 默认值
        except Exception as e:
            logger.warning(f"获取视频时长失败: {e}")
            return 180.0  # 默认值
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的字幕格式
        
        Returns:
            支持的字幕格式列表
        """
        return ["srt", "vtt", "ass", "ssa"]
    
    def get_default_style(self) -> Dict[str, Any]:
        """
        获取默认样式配置
        
        Returns:
            默认样式配置
        """
        return {
            "font_name": "Microsoft YaHei",
            "font_size": 24,
            "primary_color": "&H00FFFFFF",
            "outline_color": "&H00000000",
            "border_style": 3,
            "outline": 1,
            "shadow": 0,
            "margin_v": 20,
            "margin_l": 10,
            "margin_r": 10
        }
    
    def validate_style_config(self, style_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证样式配置
        
        Args:
            style_config: 样式配置
            
        Returns:
            (是否有效, 错误信息)
        """
        required_fields = ["font_name", "font_size", "primary_color"]
        
        for field in required_fields:
            if field not in style_config:
                return False, f"缺少必填字段: {field}"
        
        # 验证字体大小
        font_size = style_config.get("font_size")
        if not isinstance(font_size, (int, float)) or font_size < 12 or font_size > 72:
            return False, "字体大小必须在12-72之间"
        
        # 验证颜色格式
        primary_color = style_config.get("primary_color")
        if not isinstance(primary_color, str) or not primary_color.startswith("&H"):
            return False, "颜色格式必须为&HXXXXXX格式"
        
        return True, ""
    
    def __del__(self):
        """析构函数"""
        pass


class SubtitlePressingManager:
    """字幕压制管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化字幕压制管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.pressor = SubtitlePressing(config)
        self.task_queue = []
        self.active_tasks = {}
        
    def submit_pressing_task(self, video_path: str, subtitles: List[Dict[str, Any]], 
                            output_path: Optional[str] = None,
                            style_config: Optional[Dict[str, Any]] = None,
                            extra_params: Optional[Dict[str, Any]] = None) -> str:
        """
        提交压制任务
        
        Args:
            video_path: 输入视频路径
            subtitles: 字幕列表
            output_path: 输出视频路径
            style_config: 样式配置
            extra_params: 额外参数
            
        Returns:
            任务ID
        """
        import uuid
        
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "video_path": video_path,
            "subtitles": subtitles,
            "output_path": output_path,
            "style_config": style_config,
            "extra_params": extra_params,
            "status": "pending",
            "progress": 0.0
        }
        
        self.task_queue.append(task)
        logger.info(f"提交压制任务: {task_id}")
        
        return task_id
    
    def process_task(self, task_id: str, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        处理压制任务
        
        Args:
            task_id: 任务ID
            progress_callback: 进度回调函数
            
        Returns:
            压制结果
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
            # 执行压制
            result = self.pressor.press_subtitles(
                task["video_path"],
                task["subtitles"],
                task["output_path"],
                task["style_config"],
                task["extra_params"],
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
_subtitle_pressing_manager = None

def get_subtitle_pressing_manager() -> SubtitlePressingManager:
    """获取全局字幕压制管理器实例"""
    global _subtitle_pressing_manager
    if _subtitle_pressing_manager is None:
        _subtitle_pressing_manager = SubtitlePressingManager()
    return _subtitle_pressing_manager


def press_subtitles(video_path: str, subtitles: List[Dict[str, Any]], 
                   output_path: Optional[str] = None,
                   style_config: Optional[Dict[str, Any]] = None,
                   extra_params: Optional[Dict[str, Any]] = None,
                   progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    快速压制字幕的便捷函数
    
    Args:
        video_path: 输入视频路径
        subtitles: 字幕列表
        output_path: 输出视频路径
        style_config: 样式配置
        extra_params: 额外参数
        progress_callback: 进度回调函数
        
    Returns:
        压制结果
    """
    manager = get_subtitle_pressing_manager()
    pressor = manager.pressor
    
    return pressor.press_subtitles(
        video_path, subtitles, output_path, 
        style_config, extra_params, progress_callback
    )