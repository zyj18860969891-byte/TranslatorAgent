#!/usr/bin/env python3
"""数据处理模块测试"""

import pytest
from translator_agent.data.video_processor import VideoProcessor
from translator_agent.data.subtitle_processor import SubtitleProcessor


class TestVideoProcessor:
    """视频处理器测试类"""
    
    def test_video_processor_initialization(self):
        """测试视频处理器初始化"""
        processor = VideoProcessor()
        assert processor is not None
        # 确保配置对象存在
        assert hasattr(processor, 'config')
        assert processor.config is not None
    
    def test_video_processor_config(self):
        """测试视频处理器配置"""
        processor = VideoProcessor()
        # 确保配置属性存在且值合理
        assert hasattr(processor.config, 'frame_rate')
        assert hasattr(processor.config, 'max_frames') 
        assert hasattr(processor.config, 'batch_size')
        assert processor.config.frame_rate > 0
        assert processor.config.max_frames > 0
        assert processor.config.batch_size > 0


class TestSubtitleProcessor:
    """字幕处理器测试类"""
    
    def test_subtitle_processor_initialization(self):
        """测试字幕处理器初始化"""
        processor = SubtitleProcessor()
        assert processor is not None
        # 确保配置对象存在
        assert hasattr(processor, 'config')
        assert processor.config is not None
        # 确保统计信息存在
        assert hasattr(processor, 'stats')
        assert processor.stats is not None
    
    def test_subtitle_processor_config(self):
        """测试字幕处理器配置"""
        processor = SubtitleProcessor()
        # 确保配置属性存在且值合理
        assert hasattr(processor.config, 'source_lang')
        assert hasattr(processor.config, 'target_lang')
        assert hasattr(processor.config, 'min_confidence')
        assert hasattr(processor.config, 'max_confidence')
        assert hasattr(processor.config, 'max_duration')
        assert hasattr(processor.config, 'min_duration')
        assert hasattr(processor.config, 'max_text_length')
        assert hasattr(processor.config, 'min_text_length')
        assert hasattr(processor.config, 'enable_caching')
        assert hasattr(processor.config, 'max_retries')
        assert processor.config.source_lang in ['en', 'zh', 'ja', 'ko']
        assert processor.config.target_lang in ['en', 'zh', 'ja', 'ko']
        assert 0.0 <= processor.config.min_confidence <= 1.0
        assert 0.0 <= processor.config.max_confidence <= 1.0
        assert processor.config.min_duration > 0
        assert processor.config.max_duration > processor.config.min_duration
        assert processor.config.min_text_length > 0
        assert processor.config.max_text_length > processor.config.min_text_length
        assert processor.config.max_retries >= 0
    
    def test_subtitle_processor_custom_config(self):
        """测试自定义配置"""
        from translator_agent.data.subtitle_processor import SubtitleProcessingConfig
        
        custom_config = SubtitleProcessingConfig(
            source_lang="ja",
            target_lang="zh",
            min_confidence=0.8,
            max_confidence=1.0,
            enable_caching=False,
            max_retries=5
        )
        
        processor = SubtitleProcessor(custom_config)
        assert processor.config.source_lang == "ja"
        assert processor.config.target_lang == "zh"
        assert processor.config.min_confidence == 0.8
        assert processor.config.max_confidence == 1.0
        assert processor.config.enable_caching == False
        assert processor.config.max_retries == 5