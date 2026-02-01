"""
Translator Agent - 智能翻译系统

基于 NotebookLM 文档驱动开发
支持多模态翻译、视频处理、字幕翻译等功能
"""

__version__ = "1.0.0"
__author__ = "Translator Agent Team"

from .core.agent import TranslatorAgent
from .core.modelscope_integration import ModelScopeClient
from .core.translator import Translator
from .data.video_processor import VideoProcessor
from .data.subtitle_processor import SubtitleProcessor
from .config.settings import ConfigManager

__all__ = [
    "TranslatorAgent",
    "ModelScopeClient",
    "Translator",
    "VideoProcessor",
    "SubtitleProcessor",
    "ConfigManager",
    "__version__",
    "__author__",
]