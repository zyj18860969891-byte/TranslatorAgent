#!/usr/bin/env python3
"""
API 路由器模块

包含所有API路由
"""

from .translation import router as translation_router
from .video import router as video_router
from .subtitle import router as subtitle_router
from .task import router as task_router

__all__ = [
    'translation_router',
    'video_router',
    'subtitle_router',
    'task_router'
]
