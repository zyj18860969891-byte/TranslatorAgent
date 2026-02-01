"""
API 接口模块

提供 REST API 接口用于翻译和视频处理服务
"""

from .main import app
from .routers import (
    translation_router,
    video_router,
    subtitle_router,
    task_router
)
from .schemas import (
    TranslationRequest,
    TranslationResponse,
    VideoTranslationRequest,
    VideoTranslationResponse,
    SubtitleTranslationRequest,
    SubtitleTranslationResponse,
    VideoProcessingRequest,
    VideoProcessingResponse,
    SubtitleProcessingRequest,
    SubtitleProcessingResponse,
    TaskInfo,
    TaskStatus,
    TaskStatusResponse,
    TaskListResponse,
    HealthResponse,
    ModelInfo,
    ErrorResponse
)
try:
    from .middleware import setup_middleware
except ImportError:
    setup_middleware = None

__all__ = [
    'app',
    'translation_router',
    'video_router',
    'subtitle_router',
    'task_router',
    'TranslationRequest',
    'TranslationResponse', 
    'VideoTranslationRequest',
    'VideoTranslationResponse',
    'SubtitleTranslationRequest',
    'SubtitleTranslationResponse',
    'VideoProcessingRequest',
    'VideoProcessingResponse',
    'SubtitleProcessingRequest',
    'SubtitleProcessingResponse',
    'TaskInfo',
    'TaskStatus',
    'TaskStatusResponse',
    'TaskListResponse',
    'HealthResponse',
    'ModelInfo',
    'ErrorResponse',
    'setup_middleware'
]