"""
CLI 命令行模块

提供命令行接口用于翻译和视频处理服务
"""

from .main import main
from .commands import cli

__all__ = [
    'main',
    'cli'
]