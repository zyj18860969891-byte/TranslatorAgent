"""
处理服务配置
"""

import os
import json
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    SERVICE_NAME: str = "processing-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = []
    
    # Qwen3配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com")
    DASHSCOPE_TIMEOUT: int = int(os.getenv("DASHSCOPE_TIMEOUT", "30"))
    DASHSCOPE_MAX_RETRIES: int = int(os.getenv("DASHSCOPE_MAX_RETRIES", "3"))
    DASHSCOPE_RETRY_DELAY: int = int(os.getenv("DASHSCOPE_RETRY_DELAY", "1"))
    
    # 模型配置
    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "qwen3-omni-flash-realtime")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "qwen3-embedding")
    SUBTITLE_MODEL: str = os.getenv("SUBTITLE_MODEL", "qwen3-vl-rerank")
    
    # 处理配置
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # 路径配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 处理ALLOWED_ORIGINS环境变量
        origins = os.getenv("ALLOWED_ORIGINS", "")
        if origins:
            try:
                # 尝试解析JSON格式
                self.ALLOWED_ORIGINS = json.loads(origins)
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试按逗号分割
                self.ALLOWED_ORIGINS = [origin.strip() for origin in origins.split(",") if origin.strip()]
        else:
            # 默认值
            self.ALLOWED_ORIGINS = [
                "http://localhost:3000",
                "https://translator-agent-*.vercel.app",
                "http://localhost:8080"
            ]
    
    class Config:
        env_file = ".env"

# 全局配置实例
settings = Settings()