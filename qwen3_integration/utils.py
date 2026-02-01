"""
Qwen3集成工具模块
提供各种实用工具函数
"""

import os
import json
import logging
import time
import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import base64
import re
from PIL import Image
import io

logger = logging.getLogger(__name__)

class APIUtils:
    """API工具类"""
    
    @staticmethod
    def create_headers(api_key: str, content_type: str = "application/json") -> Dict[str, str]:
        """
        创建API请求头
        
        Args:
            api_key: API密钥
            content_type: 内容类型
            
        Returns:
            请求头字典
        """
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
            "Accept": "application/json"
        }
    
    @staticmethod
    def create_payload(model: str, messages: List[Dict[str, Any]], 
                      temperature: float = 0.7, max_tokens: int = 2000,
                      stream: bool = False) -> Dict[str, Any]:
        """
        创建API请求载荷
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式传输
            
        Returns:
            载荷字典
        """
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
    
    @staticmethod
    def create_vision_payload(model: str, messages: List[Dict[str, Any]], 
                            temperature: float = 0.1, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        创建视觉API请求载荷
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            载荷字典
        """
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    
    @staticmethod
    async def async_request(session: aiohttp.ClientSession, url: str, 
                           headers: Dict[str, str], payload: Dict[str, Any],
                           timeout: int = 30) -> Dict[str, Any]:
        """
        异步API请求
        
        Args:
            session: aiohttp会话
            url: 请求URL
            headers: 请求头
            payload: 请求载荷
            timeout: 超时时间
            
        Returns:
            响应字典
        """
        try:
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {
                        "error": f"HTTP {response.status}: {error_text}",
                        "status_code": response.status
                    }
        except asyncio.TimeoutError:
            return {"error": "请求超时", "status_code": 408}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}", "status_code": 500}
    
    @staticmethod
    def sync_request(url: str, headers: Dict[str, str], payload: Dict[str, Any],
                    timeout: int = 30) -> Dict[str, Any]:
        """
        同步API请求
        
        Args:
            url: 请求URL
            headers: 请求头
            payload: 请求载荷
            timeout: 超时时间
            
        Returns:
            响应字典
        """
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
        except requests.Timeout:
            return {"error": "请求超时", "status_code": 408}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}", "status_code": 500}

class ImageUtils:
    """图像处理工具类"""
    
    @staticmethod
    def extract_frames(video_path: str, frame_interval: int = 30, 
                      max_frames: int = 100) -> List[str]:
        """
        从视频中提取帧
        
        Args:
            video_path: 视频文件路径
            frame_interval: 帧间隔
            max_frames: 最大帧数
            
        Returns:
            帧图像路径列表
        """
        try:
            import cv2
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"无法打开视频文件: {video_path}")
                return []
            
            frames = []
            frame_count = 0
            interval_count = 0
            
            while cap.isOpened() and len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                interval_count += 1
                if interval_count >= frame_interval:
                    # 保存帧
                    frame_path = f"temp_frame_{frame_count}.jpg"
                    cv2.imwrite(frame_path, frame)
                    frames.append(frame_path)
                    frame_count += 1
                    interval_count = 0
            
            cap.release()
            logger.info(f"从视频 {video_path} 提取了 {len(frames)} 帧")
            return frames
            
        except Exception as e:
            logger.error(f"提取视频帧失败: {e}")
            return []
    
    @staticmethod
    def resize_image(image_path: str, max_size: Tuple[int, int] = (1024, 1024)) -> str:
        """
        调整图像大小
        
        Args:
            image_path: 图像路径
            max_size: 最大尺寸
            
        Returns:
            调整后的图像路径
        """
        try:
            with Image.open(image_path) as img:
                # 计算新尺寸
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存调整后的图像
                resized_path = f"resized_{os.path.basename(image_path)}"
                img.save(resized_path)
                
                return resized_path
                
        except Exception as e:
            logger.error(f"调整图像大小失败: {e}")
            return image_path
    
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """
        将图像转换为Base64编码
        
        Args:
            image_path: 图像路径
            
        Returns:
            Base64编码字符串
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            logger.error(f"图像转Base64失败: {e}")
            return ""
    
    @staticmethod
    def create_image_message(image_path: str, text: str) -> Dict[str, Any]:
        """
        创建图像消息
        
        Args:
            image_path: 图像路径
            text: 文本描述
            
        Returns:
            图像消息字典
        """
        base64_image = ImageUtils.image_to_base64(image_path)
        if not base64_image:
            return {"role": "user", "content": text}
        
        return {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                },
                {
                    "type": "text",
                    "text": text
                }
            ]
        }

class TextUtils:
    """文本处理工具类"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\[\]{}"\'-]', '', text)
        
        # 标准化标点符号
        text = text.replace('。', '.').replace('，', ',').replace('！', '!').replace('？', '?')
        
        return text.strip()
    
    @staticmethod
    def split_text(text: str, max_length: int = 500) -> List[str]:
        """
        分割文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            文本片段列表
        """
        if len(text) <= max_length:
            return [text]
        
        # 按句子分割
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def extract_emotions(text: str) -> Dict[str, float]:
        """
        从文本中提取情感
        
        Args:
            text: 文本内容
            
        Returns:
            情感字典
        """
        emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "neutral": 1.0
        }
        
        # 简单的情感关键词匹配
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "delighted", "pleased", "glad", "cheerful"],
            "sadness": ["sad", "unhappy", "depressed", "disappointed", "miserable", "sorrowful"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "outraged"],
            "fear": ["afraid", "scared", "terrified", "worried", "anxious", "nervous"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "startled"],
            "disgust": ["disgusted", "revolted", "sickened", "repulsed"]
        }
        
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions[emotion] += 0.2
        
        # 归一化情感值
        total = sum(emotions.values())
        if total > 0:
            for emotion in emotions:
                emotions[emotion] /= total
        
        return emotions
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 文本内容
            
        Returns:
            语言代码
        """
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        
        if chinese_chars / total_chars > 0.3:
            return "zh"
        elif re.search(r'[a-zA-Z]', text):
            return "en"
        else:
            return "unknown"

class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def ensure_directory(directory: str):
        """
        确保目录存在
        
        Args:
            directory: 目录路径
        """
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """
        获取文件哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件哈希值
        """
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败: {e}")
            return ""
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str):
        """
        保存JSON文件
        
        Args:
            data: 数据字典
            file_path: 文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON文件保存成功: {file_path}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        加载JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            数据字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载JSON文件失败: {e}")
            return {}
    
    @staticmethod
    def clean_temp_files(file_patterns: List[str]):
        """
        清理临时文件
        
        Args:
            file_patterns: 文件模式列表
        """
        try:
            for pattern in file_patterns:
                for file_path in Path(".").glob(pattern):
                    try:
                        file_path.unlink()
                        logger.debug(f"删除临时文件: {file_path}")
                    except Exception as e:
                        logger.warning(f"删除临时文件失败 {file_path}: {e}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")

class CacheUtils:
    """缓存工具类"""
    
    @staticmethod
    def get_cache_key(prefix: str, *args) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 前缀
            *args: 参数
            
        Returns:
            缓存键
        """
        key_parts = [prefix] + [str(arg) for arg in args]
        return hashlib.md5(":".join(key_parts).encode()).hexdigest()
    
    @staticmethod
    def get_cache_file(cache_dir: str, cache_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            cache_dir: 缓存目录
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return os.path.join(cache_dir, f"{cache_key}.json")
    
    @staticmethod
    def get_from_cache(cache_dir: str, cache_key: str, max_age: int = 3600) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据
        
        Args:
            cache_dir: 缓存目录
            cache_key: 缓存键
            max_age: 最大年龄（秒）
            
        Returns:
            缓存数据或None
        """
        try:
            cache_file = CacheUtils.get_cache_file(cache_dir, cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            # 检查缓存年龄
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age > max_age:
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"从缓存获取数据失败: {e}")
            return None
    
    @staticmethod
    def save_to_cache(cache_dir: str, cache_key: str, data: Dict[str, Any]):
        """
        保存数据到缓存
        
        Args:
            cache_dir: 缓存目录
            cache_key: 缓存键
            data: 数据
        """
        try:
            FileUtils.ensure_directory(cache_dir)
            cache_file = CacheUtils.get_cache_file(cache_dir, cache_key)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存数据到缓存失败: {e}")

class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        验证API密钥
        
        Args:
            api_key: API密钥
            
        Returns:
            是否有效
        """
        if not api_key or len(api_key) < 10:
            return False
        
        # 检查格式
        if not re.match(r'^[a-zA-Z0-9\-_]+$', api_key):
            return False
        
        return True
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否有效
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    @staticmethod
    def validate_video_format(file_path: str) -> bool:
        """
        验证视频格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否有效
        """
        if not ValidationUtils.validate_file_path(file_path):
            return False
        
        # 支持的视频格式
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
        
        return any(file_path.lower().endswith(ext) for ext in video_extensions)
    
    @staticmethod
    def validate_subtitle_format(file_path: str) -> bool:
        """
        验证字幕格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否有效
        """
        if not ValidationUtils.validate_file_path(file_path):
            return False
        
        # 支持的字幕格式
        subtitle_extensions = ['.srt', '.vtt', '.ass', '.ssa']
        
        return any(file_path.lower().endswith(ext) for ext in subtitle_extensions)

class ProgressUtils:
    """进度工具类"""
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 50) -> str:
        """
        创建进度条
        
        Args:
            current: 当前进度
            total: 总数
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        if total == 0:
            return "[" + "=" * width + "]"
        
        progress = current / total
        filled_width = int(width * progress)
        
        bar = "=" * filled_width + "-" * (width - filled_width)
        percentage = progress * 100
        
        return f"[{bar}] {percentage:.1f}% ({current}/{total})"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        格式化持续时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的持续时间字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

class LoggerUtils:
    """日志工具类"""
    
    @staticmethod
    def setup_logger(name: str, level: int = logging.INFO, 
                    log_file: Optional[str] = None) -> logging.Logger:
        """
        设置日志记录器
        
        Args:
            name: 名称
            level: 日志级别
            log_file: 日志文件路径
            
        Returns:
            日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

class PerformanceUtils:
    """性能工具类"""
    
    @staticmethod
    def measure_time(func):
        """
        测量函数执行时间的装饰器
        
        Args:
            func: 函数
            
        Returns:
            装饰后的函数
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.2f}秒")
            
            return result
        
        return wrapper
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """
        获取内存使用情况
        
        Returns:
            内存使用字典
        """
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"rss": 0, "vms": 0, "percent": 0}
        except Exception as e:
            logger.error(f"获取内存使用情况失败: {e}")
            return {"rss": 0, "vms": 0, "percent": 0}

# 全局工具函数
def get_api_utils() -> APIUtils:
    """获取API工具实例"""
    return APIUtils()

def get_image_utils() -> ImageUtils:
    """获取图像工具实例"""
    return ImageUtils()

def get_text_utils() -> TextUtils:
    """获取文本工具实例"""
    return TextUtils()

def get_file_utils() -> FileUtils:
    """获取文件工具实例"""
    return FileUtils()

def get_cache_utils() -> CacheUtils:
    """获取缓存工具实例"""
    return CacheUtils()

def get_validation_utils() -> ValidationUtils:
    """获取验证工具实例"""
    return ValidationUtils()

def get_progress_utils() -> ProgressUtils:
    """获取进度工具实例"""
    return ProgressUtils()

def get_logger_utils() -> LoggerUtils:
    """获取日志工具实例"""
    return LoggerUtils()

def get_performance_utils() -> PerformanceUtils:
    """获取性能工具实例"""
    return PerformanceUtils()

# 便捷函数
def setup_logging(name: str, level: int = logging.INFO, 
                 log_file: Optional[str] = None) -> logging.Logger:
    """设置日志记录器的便捷函数"""
    return LoggerUtils.setup_logger(name, level, log_file)

def measure_time(func):
    """测量执行时间的便捷函数"""
    return PerformanceUtils.measure_time(func)

def clean_temp_files(patterns: List[str] = None):
    """清理临时文件的便捷函数"""
    if patterns is None:
        patterns = ["temp_frame_*.jpg", "resized_*.jpg", "*.tmp"]
    FileUtils.clean_temp_files(patterns)

def validate_environment() -> Dict[str, Any]:
    """验证环境的便捷函数"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # 检查必需的环境变量
    required_vars = ["DASHSCOPE_API_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            validation_result["errors"].append(f"缺少环境变量: {var}")
            validation_result["valid"] = False
    
    # 检查可选的环境变量
    optional_vars = ["DASHSCOPE_BASE_URL", "DASHSCOPE_TIMEOUT", "DASHSCOPE_MAX_RETRIES"]
    for var in optional_vars:
        if not os.getenv(var):
            validation_result["warnings"].append(f"建议设置环境变量: {var}")
    
    # 检查Python包
    try:
        import dashscope
    except ImportError:
        validation_result["errors"].append("缺少dashscope包")
        validation_result["valid"] = False
    
    try:
        import cv2
    except ImportError:
        validation_result["warnings"].append("缺少opencv-python包")
    
    try:
        import PIL
    except ImportError:
        validation_result["warnings"].append("缺少Pillow包")
    
    return validation_result