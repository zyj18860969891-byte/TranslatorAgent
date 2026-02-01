#!/usr/bin/env python3
"""
配置管理模块

基于 NotebookLM 文档驱动开发
文档: project-development-SKILL.md, tool-design-SKILL.md

功能:
- 配置文件管理
- 环境变量处理
- 配置验证
- 配置持久化
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 从项目根目录加载 .env 文件
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")
except ImportError:
    logger.warning("python-dotenv not installed. Cannot load .env file.")


class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class ModelScopeConfig:
    """ModelScope 配置"""
    api_key: Optional[str] = None
    base_url: str = "https://api.modelscope.cn"
    timeout: int = 300
    max_retries: int = 3
    retry_delay: float = 1.0
    mock_mode: bool = True  # 模拟模式（用于开发）
    
    @classmethod
    def from_env(cls) -> 'ModelScopeConfig':
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv("MODELSCOPE_API_KEY"),
            base_url=os.getenv("MODELSCOPE_BASE_URL", "https://api.modelscope.cn"),
            timeout=int(os.getenv("MODELSCOPE_TIMEOUT", "300")),
            max_retries=int(os.getenv("MODELSCOPE_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("MODELSCOPE_RETRY_DELAY", "1.0")),
            mock_mode=os.getenv("MODELSCOPE_MOCK_MODE", "true").lower() == "true"
        )


@dataclass
class VideoProcessingConfig:
    """视频处理配置"""
    frame_rate: float = 2.0
    max_frames: int = 1000
    batch_size: int = 10
    enable_cache: bool = True
    temp_dir: Optional[str] = None
    output_dir: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'VideoProcessingConfig':
        """从环境变量创建配置"""
        return cls(
            frame_rate=float(os.getenv("VIDEO_FRAME_RATE", "2.0")),
            max_frames=int(os.getenv("VIDEO_MAX_FRAMES", "1000")),
            batch_size=int(os.getenv("VIDEO_BATCH_SIZE", "10")),
            enable_cache=os.getenv("VIDEO_ENABLE_CACHE", "true").lower() == "true",
            temp_dir=os.getenv("VIDEO_TEMP_DIR"),
            output_dir=os.getenv("VIDEO_OUTPUT_DIR")
        )


@dataclass
class TranslationConfig:
    """翻译配置"""
    default_source_lang: str = "en"
    default_target_lang: str = "zh"
    enable_emotion_analysis: bool = True
    enable_post_process: bool = True
    cache_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> 'TranslationConfig':
        """从环境变量创建配置"""
        return cls(
            default_source_lang=os.getenv("TRANSLATION_SOURCE_LANG", "en"),
            default_target_lang=os.getenv("TRANSLATION_TARGET_LANG", "zh"),
            enable_emotion_analysis=os.getenv("TRANSLATION_EMOTION_ANALYSIS", "true").lower() == "true",
            enable_post_process=os.getenv("TRANSLATION_POST_PROCESS", "true").lower() == "true",
            cache_enabled=os.getenv("TRANSLATION_CACHE_ENABLED", "true").lower() == "true"
        )


@dataclass
class SubtitleProcessingConfig:
    """字幕处理配置"""
    merge_segments: bool = True
    max_segment_length: int = 80
    min_segment_length: int = 5
    min_text_length: int = 1  # 最小文本长度
    max_text_length: int = 500  # 最大文本长度
    confidence_threshold: float = 0.7
    min_confidence: float = 0.0  # 最小置信度
    max_confidence: float = 1.0  # 最大置信度
    enable_caching: bool = True
    enable_progress: bool = True  # 启用进度显示
    max_retries: int = 3  # 最大重试次数
    retry_delay: float = 1.0  # 重试延迟（秒）
    max_gap: float = 2.0  # 最大间隔（秒）
    similarity_threshold: float = 0.8  # 相似度阈值
    source_lang: str = "auto"  # 源语言
    target_lang: str = "zh"  # 目标语言
    temp_dir: Optional[str] = None
    output_dir: Optional[str] = None
    log_level: str = "INFO"
    min_duration: float = 0.1  # 最小字幕持续时间（秒）
    max_duration: float = 10.0  # 最大字幕持续时间（秒）
    
    @classmethod
    def from_env(cls) -> 'SubtitleProcessingConfig':
        """从环境变量创建配置"""
        return cls(
            merge_segments=os.getenv("SUBTITLE_MERGE_SEGMENTS", "true").lower() == "true",
            max_segment_length=int(os.getenv("SUBTITLE_MAX_SEGMENT_LENGTH", "80")),
            min_segment_length=int(os.getenv("SUBTITLE_MIN_SEGMENT_LENGTH", "5")),
            min_text_length=int(os.getenv("SUBTITLE_MIN_TEXT_LENGTH", "1")),
            max_text_length=int(os.getenv("SUBTITLE_MAX_TEXT_LENGTH", "500")),
            confidence_threshold=float(os.getenv("SUBTITLE_CONFIDENCE_THRESHOLD", "0.7")),
            min_confidence=float(os.getenv("SUBTITLE_MIN_CONFIDENCE", "0.0")),
            max_confidence=float(os.getenv("SUBTITLE_MAX_CONFIDENCE", "1.0")),
            enable_caching=os.getenv("SUBTITLE_ENABLE_CACHE", "true").lower() == "true",
            enable_progress=os.getenv("SUBTITLE_ENABLE_PROGRESS", "true").lower() == "true",
            max_retries=int(os.getenv("SUBTITLE_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("SUBTITLE_RETRY_DELAY", "1.0")),
            max_gap=float(os.getenv("SUBTITLE_MAX_GAP", "2.0")),
            similarity_threshold=float(os.getenv("SUBTITLE_SIMILARITY_THRESHOLD", "0.8")),
            source_lang=os.getenv("SUBTITLE_SOURCE_LANG", "auto"),
            target_lang=os.getenv("SUBTITLE_TARGET_LANG", "zh"),
            temp_dir=os.getenv("SUBTITLE_TEMP_DIR"),
            output_dir=os.getenv("SUBTITLE_OUTPUT_DIR"),
            min_duration=float(os.getenv("SUBTITLE_MIN_DURATION", "0.1")),
            max_duration=float(os.getenv("SUBTITLE_MAX_DURATION", "10.0"))
        )


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """从环境变量创建配置"""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )


@dataclass
class AppConfig:
    """应用配置"""
    environment: Environment = Environment.DEVELOPMENT
    app_name: str = "Translator Agent"
    version: str = "1.0.0"
    debug: bool = True
    
    modelscope: ModelScopeConfig = field(default_factory=ModelScopeConfig.from_env)
    video_processing: VideoProcessingConfig = field(default_factory=VideoProcessingConfig.from_env)
    subtitle_processing: SubtitleProcessingConfig = field(default_factory=SubtitleProcessingConfig.from_env)
    translation: TranslationConfig = field(default_factory=TranslationConfig.from_env)
    logging: LoggingConfig = field(default_factory=LoggingConfig.from_env)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """从环境变量创建配置"""
        env_str = os.getenv("ENVIRONMENT", "development")
        try:
            environment = Environment(env_str)
        except ValueError:
            environment = Environment.DEVELOPMENT
        
        return cls(
            environment=environment,
            app_name=os.getenv("APP_NAME", "Translator Agent"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            modelscope=ModelScopeConfig.from_env(),
            video_processing=VideoProcessingConfig.from_env(),
            subtitle_processing=SubtitleProcessingConfig.from_env(),
            translation=TranslationConfig.from_env(),
            logging=LoggingConfig.from_env()
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> 'AppConfig':
        """从配置文件加载配置"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Config file not found: {file_path}, using environment variables")
            return cls.from_env()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置"""
        # 处理环境
        environment = Environment.DEVELOPMENT
        if "environment" in data:
            try:
                environment = Environment(data["environment"])
            except ValueError:
                pass
        
        # 创建配置
        config = cls(
            environment=environment,
            app_name=data.get("app_name", "Translator Agent"),
            version=data.get("version", "1.0.0"),
            debug=data.get("debug", True)
        )
        
        # 设置子配置
        if "modelscope" in data:
            config.modelscope = ModelScopeConfig(**data["modelscope"])
        
        if "video_processing" in data:
            config.video_processing = VideoProcessingConfig(**data["video_processing"])
        
        if "translation" in data:
            config.translation = TranslationConfig(**data["translation"])
        
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "environment": self.environment.value,
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "modelscope": asdict(self.modelscope),
            "video_processing": asdict(self.video_processing),
            "translation": asdict(self.translation),
            "logging": asdict(self.logging)
        }
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证 ModelScope 配置
        if not self.modelscope.api_key and not self.modelscope.mock_mode:
            errors.append("ModelScope API key is required when not in mock mode")
        
        # 验证视频处理配置
        if self.video_processing.frame_rate <= 0:
            errors.append("Frame rate must be positive")
        
        if self.video_processing.max_frames <= 0:
            errors.append("Max frames must be positive")
        
        # 验证翻译配置
        if not self.translation.default_source_lang:
            errors.append("Default source language is required")
        
        if not self.translation.default_target_lang:
            errors.append("Default target language is required")
        
        return errors
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        handlers = []
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(self.logging.format))
        handlers.append(console_handler)
        
        # 文件处理器
        if self.logging.file_path:
            file_handler = logging.FileHandler(self.logging.file_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(self.logging.format))
            handlers.append(file_handler)
        
        # 配置根日志器
        logging.basicConfig(
            level=log_level,
            format=self.logging.format,
            handlers=handlers
        )
        
        logger.info(f"Logging configured: level={self.logging.level}")


class ConfigManager:
    """配置管理器"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_config(cls) -> AppConfig:
        """获取配置（单例）"""
        if cls._config is None:
            cls._config = AppConfig.from_env()
        return cls._config
    
    @classmethod
    def load_config(cls, file_path: str):
        """加载配置"""
        cls._config = AppConfig.from_file(file_path)
        logger.info(f"Configuration loaded from {file_path}")
    
    @classmethod
    def reset(cls):
        """重置配置"""
        cls._config = None
        logger.info("Configuration reset")
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证配置"""
        config = cls.get_config()
        return config.validate()
    
    @classmethod
    def get_video_config(cls):
        """获取视频处理配置"""
        config = cls.get_config()
        return config.video_processing
    
    @classmethod
    def get_subtitle_config(cls):
        """获取字幕处理配置"""
        config = cls.get_config()
        return config.subtitle_processing


# 默认配置实例
default_config = AppConfig.from_env()


# 使用示例
if __name__ == "__main__":
    # 从环境变量加载配置
    config = AppConfig.from_env()
    
    print("=== 配置信息 ===")
    print(f"环境: {config.environment.value}")
    print(f"应用名称: {config.app_name}")
    print(f"版本: {config.version}")
    print(f"调试模式: {config.debug}")
    
    print("\n=== ModelScope 配置 ===")
    print(f"API Key: {config.modelscope.api_key}")
    print(f"Base URL: {config.modelscope.base_url}")
    print(f"Mock 模式: {config.modelscope.mock_mode}")
    
    print("\n=== 视频处理配置 ===")
    print(f"帧率: {config.video_processing.frame_rate}")
    print(f"最大帧数: {config.video_processing.max_frames}")
    print(f"批处理大小: {config.video_processing.batch_size}")
    
    print("\n=== 翻译配置 ===")
    print(f"默认源语言: {config.translation.default_source_lang}")
    print(f"默认目标语言: {config.translation.default_target_lang}")
    print(f"启用情感分析: {config.translation.enable_emotion_analysis}")
    
    # 验证配置
    errors = config.validate()
    if errors:
        print(f"\n=== 配置错误 ===")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"\n=== 配置验证通过 ===")
    
    # 保存配置到文件
    config.save_to_file("./config.json")
    print(f"\n配置已保存到: ./config.json")
    
    # 使用配置管理器
    print("\n=== 使用配置管理器 ===")
    manager = ConfigManager()
    manager_config = manager.get_config()
    print(f"管理器配置: {manager_config.app_name}")
