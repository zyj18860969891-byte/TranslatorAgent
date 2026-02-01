"""
Qwen3-Omni-Flash 配置管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class Qwen3Config:
    """Qwen3-Omni-Flash 配置数据类"""
    
    # API 配置
    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    model: str = "qwen3-omni-flash-realtime"
    
    # 处理配置
    max_workers: int = 4
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # 字幕提取配置
    frame_sample_rate: int = 2  # 每秒采样帧数
    subtitle_threshold: float = 0.01  # 字幕检测阈值
    min_subtitle_duration: float = 1.0  # 最小字幕显示时间
    max_subtitle_duration: float = 10.0  # 最大字幕显示时间
    
    # 输出配置
    output_format: str = "srt"  # srt, vtt, json
    include_emotion_tags: bool = True
    include_confidence: bool = False
    
    # 文件管理配置
    temp_dir: str = "temp"
    tasks_dir: str = "tasks"
    output_dir: str = "output"
    cleanup_temp_files: bool = True
    max_task_age_hours: int = 24
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "qwen3_subtitle_extraction.log"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Qwen3Config':
        """从字典创建配置"""
        return cls(**data)
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Qwen3Config':
        """从文件加载配置"""
        if not Path(file_path).exists():
            return cls()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)

class Qwen3ConfigManager:
    """Qwen3-Omni-Flash 配置管理器"""
    
    def __init__(self, config_file: str = "qwen3_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Qwen3Config:
        """加载配置"""
        # 首先尝试从文件加载
        if self.config_file.exists():
            try:
                return Qwen3Config.load_from_file(str(self.config_file))
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 如果文件不存在或加载失败，使用默认配置
        config = Qwen3Config()
        
        # 从环境变量获取 API 密钥
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            config.api_key = api_key
        
        return config
    
    def save_config(self):
        """保存配置"""
        try:
            self.config.save_to_file(str(self.config_file))
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_config(self) -> Qwen3Config:
        """获取配置"""
        return self.config
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def get_api_key(self) -> str:
        """获取 API 密钥"""
        return self.config.api_key
    
    def set_api_key(self, api_key: str):
        """设置 API 密钥"""
        self.config.api_key = api_key
        self.save_config()
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查 API 密钥
        if not self.config.api_key:
            errors.append("API 密钥未设置")
        
        # 检查基本配置
        if self.config.max_workers <= 0:
            errors.append("最大工作线程数必须大于0")
        
        if self.config.request_timeout <= 0:
            errors.append("请求超时时间必须大于0")
        
        if self.config.frame_sample_rate <= 0:
            errors.append("帧采样率必须大于0")
        
        # 检查阈值配置
        if not (0 <= self.config.subtitle_threshold <= 1):
            warnings.append("字幕检测阈值应该在 0-1 之间")
        
        # 检查时间配置
        if self.config.min_subtitle_duration <= 0:
            errors.append("最小字幕显示时间必须大于0")
        
        if self.config.max_subtitle_duration <= 0:
            errors.append("最大字幕显示时间必须大于0")
        
        if self.config.min_subtitle_duration >= self.config.max_subtitle_duration:
            errors.append("最小字幕显示时间必须小于最大字幕显示时间")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def create_sample_config(self):
        """创建示例配置文件"""
        sample_config = Qwen3Config()
        sample_config.api_key = "your_api_key_here"
        sample_config.frame_sample_rate = 2
        sample_config.subtitle_threshold = 0.01
        sample_config.max_workers = 4
        
        try:
            sample_config.save_to_file("qwen3_config_sample.json")
            print("示例配置文件已创建: qwen3_config_sample.json")
        except Exception as e:
            print(f"创建示例配置文件失败: {e}")
    
    def print_config(self):
        """打印当前配置"""
        print("当前 Qwen3-Omni-Flash 配置:")
        print("=" * 50)
        
        config_dict = self.config.to_dict()
        for key, value in config_dict.items():
            if key == "api_key" and value:
                # 隐藏 API 密钥的部分字符
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
                print(f"{key:20}: {masked_value}")
            else:
                print(f"{key:20}: {value}")
        
        print("=" * 50)
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = Qwen3Config()
        self.save_config()
        print("配置已重置为默认值")

# 全局配置管理器实例
config_manager = Qwen3ConfigManager()

def get_qwen3_config() -> Qwen3Config:
    """获取 Qwen3 配置"""
    return config_manager.get_config()

def update_qwen3_config(**kwargs):
    """更新 Qwen3 配置"""
    config_manager.update_config(**kwargs)

def validate_qwen3_config() -> Dict[str, Any]:
    """验证 Qwen3 配置"""
    return config_manager.validate_config()

def set_qwen3_api_key(api_key: str):
    """设置 Qwen3 API 密钥"""
    config_manager.set_api_key(api_key)

def get_qwen3_api_key() -> str:
    """获取 Qwen3 API 密钥"""
    return config_manager.get_api_key()