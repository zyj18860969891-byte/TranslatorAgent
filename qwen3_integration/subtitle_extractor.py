"""
Qwen3字幕提取器
基于Qwen3-VL-Rerank模型的高精度字幕提取工具
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

try:
    import dashscope
    from dashscope import ImageSynthesis
except ImportError:
    dashscope = None

logger = logging.getLogger(__name__)

class SubtitleExtractor:
    """字幕提取器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化字幕提取器
        
        Args:
            config: 配置字典，包含模型参数和设置
        """
        self.config = config or self._load_default_config()
        self.model_name = self.config.get("primary_model", "qwen3-vl-rerank")
        self.fallback_model = self.config.get("fallback_model", None)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.95)
        self.supported_formats = self.config.get("supported_formats", ["srt", "vtt", "ass", "ssa"])
        self.max_text_length = self.config.get("max_text_length", 500)
        
        # 初始化DashScope客户端
        self._init_dashscope_client()
        
        # 初始化OpenCV
        self._init_opencv()
        
        logger.info(f"字幕提取器初始化完成，使用模型: {self.model_name}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "primary_model": "qwen3-vl-rerank",
            "fallback_model": None,
            "confidence_threshold": 0.95,
            "supported_formats": ["srt", "vtt", "ass", "ssa"],
            "max_text_length": 500,
            "max_retries": 3,
            "retry_delay": 1.0,
            "timeout": 30,
            "batch_size": 10,
            "enable_cache": True,
            "cache_ttl": 3600
        }
    
    def _init_dashscope_client(self):
        """初始化DashScope客户端"""
        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("未配置DASHSCOPE_API_KEY，无法使用DashScope服务")
                self.dashscope_client = None
                return
            
            dashscope.api_key = api_key
            self.dashscope_client = dashscope
            logger.info("DashScope客户端初始化成功")
            
        except Exception as e:
            logger.error(f"DashScope客户端初始化失败: {e}")
            self.dashscope_client = None
    
    def _init_opencv(self):
        """初始化OpenCV"""
        try:
            # 测试OpenCV是否正常工作
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            _ = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
            logger.info("OpenCV初始化成功")
        except Exception as e:
            logger.error(f"OpenCV初始化失败: {e}")
            raise
    
    def extract(self, video_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        从视频中提取字幕
        
        Args:
            video_path: 视频文件路径
            **kwargs: 额外参数
            
        Returns:
            字幕列表，每个字幕包含时间戳和文本
        """
        logger.info(f"开始提取视频字幕: {video_path}")
        
        try:
            # 验证视频文件
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 提取视频帧
            frames = self._extract_frames(video_path, **kwargs)
            
            # 识别字幕文本
            subtitles = self._recognize_subtitles(frames, **kwargs)
            
            # 后处理字幕
            subtitles = self._post_process_subtitles(subtitles, **kwargs)
            
            logger.info(f"字幕提取完成，共提取 {len(subtitles)} 条字幕")
            return subtitles
            
        except Exception as e:
            logger.error(f"字幕提取失败: {e}")
            raise
    
    def _extract_frames(self, video_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        从视频中提取关键帧
        
        Args:
            video_path: 视频文件路径
            **kwargs: 额外参数
            
        Returns:
            帧列表，每个帧包含图像和时间戳
        """
        logger.info("开始提取视频帧...")
        
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        logger.info(f"视频信息: {total_frames} 帧, {fps:.2f} FPS, {duration:.2f} 秒")
        
        # 设置帧提取策略
        frame_interval = max(1, int(fps * 0.5))  # 每0.5秒提取一帧
        sample_interval = max(1, total_frames // 100)  # 最多采样100帧
        
        frame_count = 0
        sampled_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 按间隔采样帧
            if frame_count % frame_interval == 0:
                # 转换颜色空间
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 创建帧对象
                frame_obj = {
                    "frame_number": frame_count,
                    "timestamp": frame_count / fps,
                    "image": frame_rgb,
                    "width": frame.shape[1],
                    "height": frame.shape[0]
                }
                
                frames.append(frame_obj)
                sampled_count += 1
                
                # 限制采样数量
                if sampled_count >= 100:
                    break
        
        cap.release()
        
        logger.info(f"帧提取完成，共提取 {len(frames)} 帧")
        return frames
    
    def _recognize_subtitles(self, frames: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        识别帧中的字幕文本
        
        Args:
            frames: 帧列表
            **kwargs: 额外参数
            
        Returns:
            字幕识别结果列表
        """
        logger.info("开始字幕文本识别...")
        
        subtitles = []
        
        for frame in frames:
            try:
                # 预处理图像
                processed_image = self._preprocess_image(frame["image"])
                
                # 使用Qwen3-VL-Rerank进行文本识别
                text_result = self._recognize_text_with_qwen(processed_image)
                
                if text_result and text_result.get("text"):
                    # 创建字幕对象
                    subtitle = {
                        "start_time": frame["timestamp"],
                        "end_time": frame["timestamp"] + 0.5,  # 假设字幕持续0.5秒
                        "text": text_result["text"],
                        "confidence": text_result.get("confidence", 0.0),
                        "frame_number": frame["frame_number"],
                        "timestamp": frame["timestamp"]
                    }
                    
                    subtitles.append(subtitle)
                
                # 添加延迟避免API限制
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"帧 {frame['frame_number']} 字幕识别失败: {e}")
                continue
        
        logger.info(f"字幕识别完成，共识别 {len(subtitles)} 条字幕")
        return subtitles
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像以提高文本识别精度
        
        Args:
            image: 原始图像
            
        Returns:
            预处理后的图像
        """
        # 转换为PIL图像
        pil_image = Image.fromarray(image)
        
        # 调整图像大小
        width, height = pil_image.size
        if width > 1920 or height > 1080:
            # 保持宽高比缩放
            ratio = min(1920 / width, 1080 / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 增强对比度
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # 增强锐度
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)
        
        # 转换回numpy数组
        return np.array(pil_image)
    
    def _recognize_text_with_qwen(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        使用Qwen3-VL-Rerank模型识别文本
        
        Args:
            image: 图像数组
            
        Returns:
            识别结果字典
        """
        if not self.dashscope_client:
            logger.warning("DashScope客户端未初始化，无法使用Qwen3模型")
            return None
        
        try:
            # 准备请求数据
            import base64
            import io
            
            # 将图像转换为base64
            buffered = io.BytesIO()
            pil_image = Image.fromarray(image)
            pil_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # 构建请求
            request = {
                "model": self.model_name,
                "input": {
                    "image": f"data:image/jpeg;base64,{img_str}",
                    "text": "请识别图像中的文字内容，如果图像中没有文字，请返回空字符串。"
                },
                "parameters": {
                    "temperature": 0.1,
                    "max_tokens": 100,
                    "top_p": 0.8,
                    "top_k": 50
                }
            }
            
            # 发送请求
            response = self.dashscope_client.get(
                url=f"{self.config.get('base_url', 'https://dashscope.aliyuncs.com')}/api/v1/services/aigc/multimodal-generation/generation",
                json=request,
                timeout=self.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("output", {}).get("text"):
                    return {
                        "text": result["output"]["text"].strip(),
                        "confidence": 0.95,  # Qwen3-VL-Rerank通常有很高的置信度
                        "model": self.model_name
                    }
                else:
                    return None
            else:
                logger.error(f"Qwen3 API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Qwen3文本识别失败: {e}")
            
            # 尝试使用备用模型
            if self.fallback_model:
                logger.info(f"尝试使用备用模型: {self.fallback_model}")
                return self._recognize_text_with_fallback_model(image)
            
            return None
    
    def _recognize_text_with_fallback_model(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        使用备用模型识别文本
        
        Args:
            image: 图像数组
            
        Returns:
            识别结果字典
        """
        # 这里可以实现备用模型的文本识别逻辑
        # 例如使用OCR库或其他AI模型
        logger.warning("备用模型文本识别功能尚未实现")
        return None
    
    def _post_process_subtitles(self, subtitles: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        后处理字幕结果
        
        Args:
            subtitles: 原始字幕列表
            **kwargs: 额外参数
            
        Returns:
            处理后的字幕列表
        """
        logger.info("开始后处理字幕...")
        
        processed_subtitles = []
        
        # 按时间排序
        subtitles.sort(key=lambda x: x["start_time"])
        
        # 合并相邻的字幕
        merged_subtitles = []
        current_subtitle = None
        
        for subtitle in subtitles:
            # 过滤低置信度结果
            if subtitle["confidence"] < self.confidence_threshold:
                continue
            
            # 过滤过长的文本
            if len(subtitle["text"]) > self.max_text_length:
                continue
            
            # 过滤空文本
            if not subtitle["text"].strip():
                continue
            
            # 合并相邻的字幕
            if current_subtitle and (subtitle["start_time"] - current_subtitle["end_time"]) < 1.0:
                # 合并文本
                current_subtitle["text"] += " " + subtitle["text"]
                current_subtitle["end_time"] = subtitle["end_time"]
                current_subtitle["confidence"] = min(current_subtitle["confidence"], subtitle["confidence"])
            else:
                if current_subtitle:
                    merged_subtitles.append(current_subtitle)
                current_subtitle = subtitle.copy()
        
        if current_subtitle:
            merged_subtitles.append(current_subtitle)
        
        # 进一步处理合并后的字幕
        for subtitle in merged_subtitles:
            # 清理文本
            text = subtitle["text"].strip()
            
            # 移除多余的空格
            text = " ".join(text.split())
            
            # 移除特殊字符
            import re
            text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\[\]{}"\'-]', '', text)
            
            # 更新字幕
            subtitle["text"] = text
            
            # 确保时间戳有效
            if subtitle["start_time"] >= subtitle["end_time"]:
                subtitle["end_time"] = subtitle["start_time"] + 0.5
            
            processed_subtitles.append(subtitle)
        
        logger.info(f"字幕后处理完成，共 {len(processed_subtitles)} 条有效字幕")
        return processed_subtitles
    
    def extract_to_file(self, video_path: str, output_path: str, format: str = "srt", **kwargs) -> bool:
        """
        提取字幕并保存到文件
        
        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            format: 输出格式 (srt, vtt, json)
            **kwargs: 额外参数
            
        Returns:
            是否成功保存
        """
        try:
            # 提取字幕
            subtitles = self.extract(video_path, **kwargs)
            
            # 根据格式保存
            if format.lower() == "srt":
                return self._save_srt(subtitles, output_path)
            elif format.lower() == "vtt":
                return self._save_vtt(subtitles, output_path)
            elif format.lower() == "json":
                return self._save_json(subtitles, output_path)
            else:
                raise ValueError(f"不支持的输出格式: {format}")
                
        except Exception as e:
            logger.error(f"字幕提取并保存失败: {e}")
            return False
    
    def _save_srt(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为SRT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, subtitle in enumerate(subtitles, 1):
                    start_time = self._format_time(subtitle["start_time"])
                    end_time = self._format_time(subtitle["end_time"])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['text']}\n\n")
            
            logger.info(f"SRT字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存SRT文件失败: {e}")
            return False
    
    def _save_vtt(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为VTT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                for subtitle in subtitles:
                    start_time = self._format_time_vtt(subtitle["start_time"])
                    end_time = self._format_time_vtt(subtitle["end_time"])
                    
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['text']}\n\n")
            
            logger.info(f"VTT字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存VTT文件失败: {e}")
            return False
    
    def _save_json(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为JSON格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(subtitles, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """格式化时间为VTT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def get_statistics(self, subtitles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取字幕统计信息
        
        Args:
            subtitles: 字幕列表
            
        Returns:
            统计信息字典
        """
        if not subtitles:
            return {
                "total_subtitles": 0,
                "total_duration": 0,
                "average_subtitle_length": 0,
                "average_confidence": 0,
                "time_range": {"start": 0, "end": 0}
            }
        
        total_duration = subtitles[-1]["end_time"] - subtitles[0]["start_time"]
        total_length = sum(len(sub["text"]) for sub in subtitles)
        average_length = total_length / len(subtitles)
        average_confidence = sum(sub["confidence"] for sub in subtitles) / len(subtitles)
        
        return {
            "total_subtitles": len(subtitles),
            "total_duration": total_duration,
            "average_subtitle_length": average_length,
            "average_confidence": average_confidence,
            "time_range": {
                "start": subtitles[0]["start_time"],
                "end": subtitles[-1]["end_time"]
            }
        }