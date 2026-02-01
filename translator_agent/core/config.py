"""
配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class Config:
    """配置数据类"""
    
    # 基础配置
    app_name: str = "OpenManus TranslatorAgent"
    version: str = "1.0.0"
    debug: bool = False
    
    # API 配置
    modelscope_api_key: str = ""
    dashscope_api_key: str = ""
    openai_api_key: str = ""
    
    # LLM 配置
    llm_provider: str = "modelscope"
    llm_model: str = "qwen3-omni-flash-realtime"
    llm_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.7
    
    # 字幕提取配置
    subtitle_enabled: bool = True
    subtitle_sample_rate: int = 2
    subtitle_threshold: float = 0.01
    subtitle_min_duration: float = 1.0
    subtitle_max_duration: float = 10.0
    
    # 文件处理配置
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_formats: list = None
    temp_dir: str = "temp"
    output_dir: str = "output"
    tasks_dir: str = "tasks"
    
    # 性能配置
    max_workers: int = 4
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "translator_agent.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """初始化后处理"""
        if self.allowed_formats is None:
            self.allowed_formats = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # API 密钥
        if os.getenv("MODELSCOPE_API_KEY"):
            self.modelscope_api_key = os.getenv("MODELSCOPE_API_KEY")
        if os.getenv("DASHSCOPE_API_KEY"):
            self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        if os.getenv("OPENAI_API_KEY"):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # 调试模式
        if os.getenv("DEBUG"):
            self.debug = os.getenv("DEBUG").lower() == "true"
        
        # 日志级别
        if os.getenv("LOG_LEVEL"):
            self.log_level = os.getenv("LOG_LEVEL")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典创建配置"""
        return cls(**data)
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Config':
        """从文件加载配置"""
        if not Path(file_path).exists():
            return cls()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def get_qwen3_api_key(self) -> str:
        """获取 Qwen3 API 密钥"""
        return self.dashscope_api_key
    
    def get_modelscope_api_key(self) -> str:
        """获取 ModelScope API 密钥"""
        return self.modelscope_api_key
    
    def get_openai_api_key(self) -> str:
        """获取 OpenAI API 密钥"""
        return self.openai_api_key
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查 API 密钥
        if not self.modelscope_api_key and not self.dashscope_api_key:
            errors.append("至少需要设置一个 API 密钥（ModelScope 或 DashScope）")
        
        # 检查基础配置
        if self.max_workers <= 0:
            errors.append("最大工作线程数必须大于0")
        
        if self.request_timeout <= 0:
            errors.append("请求超时时间必须大于0")
        
        if self.llm_max_tokens <= 0:
            errors.append("LLM 最大令牌数必须大于0")
        
        if not (0 <= self.llm_temperature <= 1):
            warnings.append("LLM 温度应该在 0-1 之间")
        
        # 检查字幕配置
        if self.subtitle_enabled:
            if self.subtitle_sample_rate <= 0:
                errors.append("字幕采样率必须大于0")
            
            if not (0 <= self.subtitle_threshold <= 1):
                warnings.append("字幕检测阈值应该在 0-1 之间")
            
            if self.subtitle_min_duration <= 0:
                errors.append("最小字幕显示时间必须大于0")
            
            if self.subtitle_max_duration <= 0:
                errors.append("最大字幕显示时间必须大于0")
            
            if self.subtitle_min_duration >= self.subtitle_max_duration:
                errors.append("最小字幕显示时间必须小于最大字幕显示时间")
        
        # 检查文件配置
        if self.max_file_size <= 0:
            errors.append("最大文件大小必须大于0")
        
        if not self.allowed_formats:
            errors.append("允许的文件格式不能为空")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# 全局配置实例
_config_instance = None

def get_config() -> Config:
    """获取配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def load_config_from_file(file_path: str):
    """从文件加载配置"""
    global _config_instance
    _config_instance = Config.load_from_file(file_path)

def save_config_to_file(file_path: str):
    """保存配置到文件"""
    config = get_config()
    config.save_to_file(file_path)

def update_config(**kwargs):
    """更新配置"""
    config = get_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

def get_qwen3_api_key() -> str:
    """获取 Qwen3 API 密钥"""
    return get_config().get_qwen3_api_key()

def get_modelscope_api_key() -> str:
    """获取 ModelScope API 密钥"""
    return get_config().get_modelscope_api_key()

def get_openai_api_key() -> str:
    """获取 OpenAI API 密钥"""
    return get_config().get_openai_api_key()