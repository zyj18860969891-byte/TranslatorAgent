#!/usr/bin/env python3
"""
数据处理模块单元测试

测试视频处理和字幕处理功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from translator_agent.data.video_processor import VideoProcessor
from translator_agent.data.subtitle_processor import SubtitleProcessor
from translator_agent.data.subtitle_processor import SRTSegment


def test_subtitle_processor_init():
    """测试字幕处理器初始化"""
    processor = SubtitleProcessor()
    assert isinstance(processor, SubtitleProcessor)


def test_video_processor_init():
    """测试视频处理器初始化"""
    processor = VideoProcessor()
    assert isinstance(processor, VideoProcessor)


def test_srt_segment():
    """测试 SRT 段结构"""
    segment = SRTSegment(
        index=1,
        text="Hello, world!",
        start_time=1.0,
        end_time=3.0
    )
    assert segment.index == 1
    assert segment.text == "Hello, world!"
    assert segment.start_time == 1.0
    assert segment.end_time == 3.0


if __name__ == "__main__":
    pytest.main([__file__])