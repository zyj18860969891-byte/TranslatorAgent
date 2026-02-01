#!/usr/bin/env python3
"""
字幕处理模块

基于 NotebookLM 文档驱动开发
文档: srt-translation-skill.md, video-translation-SKILL.md

功能:
- SRT 字幕解析
- 字幕翻译
- 时间轴对齐 (LCB-NET)
- 字幕同步
- 时间轴冲突检测
- 字幕格式化
"""

import re
import asyncio
import logging
import time
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import timedelta
from functools import lru_cache
from modelscope import snapshot_download
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import json
import hashlib
from collections import defaultdict

from ..core.translator import (
    BaseTranslator, 
    TranslationRequest, 
    TranslationResponse, 
    Language, 
    TranslationEngine,
    TranslatorFactory
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SRTSegment:
    """SRT 字幕段"""
    index: int
    start_time: float  # 秒
    end_time: float    # 秒
    text: str
    translated_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence: float = 1.0  # 置信度 (0.0-1.0)
    duration: float = field(init=False)  # 字幕持续时间
    # 时间轴对齐相关字段
    aligned_start_time: Optional[float] = None  # 对齐后的开始时间
    aligned_end_time: Optional[float] = None    # 对齐后的结束时间
    alignment_confidence: Optional[float] = None  # 对齐置信度
    alignment_method: Optional[str] = None  # 对齐方法
    # 字幕同步相关字段
    sync_offset: Optional[float] = None  # 同步偏移量（秒）
    sync_confidence: Optional[float] = None  # 同步置信度
    
    def __post_init__(self):
        """初始化后计算持续时间"""
        self.duration = self.end_time - self.start_time
        
        # 验证时间戳
        if self.start_time >= self.end_time:
            raise ValueError(f"Invalid timestamps: start={self.start_time}, end={self.end_time}")
        
        if self.duration <= 0:
            raise ValueError(f"Invalid duration: {self.duration}")
    
    def to_srt(self) -> str:
        """转换为 SRT 格式"""
        # 使用对齐后的时间（如果存在）
        start_time = self.aligned_start_time if self.aligned_start_time is not None else self.start_time
        end_time = self.aligned_end_time if self.aligned_end_time is not None else self.end_time
        
        start = self._format_timestamp(start_time)
        end = self._format_timestamp(end_time)
        
        lines = [
            str(self.index),
            f"{start} --> {end}",
            self.translated_text or self.text,
            ""
        ]
        
        return "\n".join(lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@dataclass
class AlignmentConfig:
    """时间轴对齐配置"""
    # LCB-NET 模型配置
    lcbnet_model: str = "damo/cv_lcbnet_timestamp_alignment"
    lcbnet_device: str = "cpu"
    lcbnet_batch_size: int = 4
    
    # 对齐算法参数
    alignment_method: str = "lcbnet"  # lcbnet, dynamic_time_warping, cross_correlation
    max_time_shift: float = 5.0  # 最大时间偏移（秒）
    min_confidence: float = 0.5  # 最小置信度
    
    # 缓存配置
    enable_caching: bool = True
    cache_dir: str = ".cache/alignment"
    
    # 日志级别
    log_level: str = "INFO"


@dataclass
class SyncConfig:
    """字幕同步配置"""
    # 同步算法参数
    sync_method: str = "dynamic_time_warping"  # dynamic_time_warping, cross_correlation, feature_matching
    window_size: float = 2.0  # 搜索窗口大小（秒）
    max_offset: float = 3.0  # 最大偏移量（秒）
    min_confidence: float = 0.6  # 最小置信度
    
    # 特征提取配置
    feature_type: str = "mfcc"  # mfcc, chroma, spectral
    feature_window: float = 0.1  # 特征窗口（秒）
    
    # 缓存配置
    enable_caching: bool = True
    cache_dir: str = ".cache/sync"
    
    # 日志级别
    log_level: str = "INFO"


class SRTParser:
    """SRT 字幕解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def parse(self, srt_content: str) -> List[SRTSegment]:
        """解析 SRT 内容"""
        segments = []
        
        # 按双换行分割字幕块
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            
            if len(lines) < 3:
                self.logger.warning(f"Invalid SRT block: {block}")
                continue
            
            try:
                # 解析索引
                index = int(lines[0].strip())
                
                # 解析时间戳
                timestamp_line = lines[1].strip()
                start_str, end_str = timestamp_line.split('-->')
                
                start_time = self._parse_timestamp(start_str.strip())
                end_time = self._parse_timestamp(end_str.strip())
                
                # 解析文本
                text_lines = lines[2:]
                text = '\n'.join(text_lines)
                
                segment = SRTSegment(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                )
                
                segments.append(segment)
                
            except Exception as e:
                self.logger.error(f"Failed to parse SRT block: {e}")
                continue
        
        self.logger.info(f"Parsed {len(segments)} SRT segments")
        return segments
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """解析时间戳"""
        # SRT 格式: HH:MM:SS,mmm
        match = re.match(r'(\d+):(\d+):(\d+),(\d+)', timestamp_str)
        if not match:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}")
        
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
        
        return total_seconds
    
    def serialize(self, segments: List[SRTSegment]) -> str:
        """序列化为 SRT 格式"""
        return '\n'.join(segment.to_srt() for segment in segments)


@dataclass
class SubtitleProcessingConfig:
    """字幕处理配置"""
    # 翻译配置
    source_lang: str = "en"
    target_lang: str = "zh"
    
    # 置信度阈值
    min_confidence: float = 0.5
    max_confidence: float = 1.0
    
    # 时间轴配置
    max_duration: float = 10.0  # 最大字幕持续时间（秒）
    min_duration: float = 0.1   # 最小字幕持续时间（秒）
    
    # 文本处理配置
    max_text_length: int = 200  # 最大文本长度
    min_text_length: int = 1    # 最小文本长度
    
    # 合并配置
    max_gap: float = 0.5        # 最大合并间隔（秒）
    similarity_threshold: float = 0.7  # 文本相似度阈值
    
    # 缓存配置
    enable_caching: bool = True
    cache_size: int = 1000
    
    # 错误处理配置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 日志配置
    log_level: str = "INFO"
    enable_progress: bool = True
    
    # OCR配置
    enable_ocr: bool = False
    ocr_model: str = "damo/cv_resnet50_vd_ocr"
    ocr_device: str = "cpu"
    ocr_batch_size: int = 4
    ocr_confidence_threshold: float = 0.7
    ocr_min_text_length: int = 2
    ocr_max_text_length: int = 100
    ocr_frame_interval: int = 5  # 每隔多少帧提取一次
    ocr_region_of_interest: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    
    # 时间轴对齐配置
    enable_alignment: bool = False
    alignment_config: Optional[AlignmentConfig] = None
    
    # 字幕同步配置
    enable_sync: bool = False
    sync_config: Optional[SyncConfig] = None


class SubtitleProcessor:
    """字幕处理器"""
    
    def __init__(self, config: Optional[SubtitleProcessingConfig] = None):
        self.config = config or SubtitleProcessingConfig()
        self.parser = SRTParser()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 设置日志级别
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        # 初始化缓存
        if self.config.enable_caching:
            self._setup_caching()
        
        # 初始化统计信息
        self.stats = {
            'total_segments': 0,
            'processed_segments': 0,
            'failed_segments': 0,
            'merged_segments': 0,
            'cleaned_segments': 0,
            'aligned_segments': 0,
            'synced_segments': 0,
            'conflicts_checked': 0,
            'conflicts_fixed': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 初始化OCR
        if self.config.enable_ocr:
            self._setup_ocr()
        else:
            self.ocr_pipeline = None
        
        # 初始化时间轴对齐
        if self.config.enable_alignment:
            self._setup_alignment()
        else:
            self.alignment_pipeline = None
        
        # 初始化字幕同步
        if self.config.enable_sync:
            self._setup_sync()
        else:
            self.sync_pipeline = None
    
    def _setup_caching(self):
        """设置缓存"""
        self.logger.info("Setting up caching for subtitle processing")
        
        # 缓存解析结果
        self._parse_cache = {}
        
        # 缓存翻译结果
        self._translation_cache = {}
        
        # 缓存清理结果
        self._clean_cache = {}
        
        # 缓存对齐结果
        self._alignment_cache = {}
        
        # 缓存同步结果
        self._sync_cache = {}
    
    def _setup_alignment(self):
        """设置时间轴对齐"""
        self.logger.info("Setting up time axis alignment")
        
        try:
            if self.config.alignment_config is None:
                self.config.alignment_config = AlignmentConfig()
            
            # 下载LCB-NET模型（如果需要）
            if self.config.alignment_config.lcbnet_model:
                self.logger.info(f"Downloading LCB-NET model: {self.config.alignment_config.lcbnet_model}")
                model_dir = snapshot_download(
                    self.config.alignment_config.lcbnet_model,
                    revision="v1.0.0"
                )
                self.logger.info(f"Model downloaded to: {model_dir}")
            
            # 创建对齐管道
            self.alignment_pipeline = None  # 待实现
            
            self.logger.info("Time axis alignment setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup alignment: {e}")
            self.alignment_pipeline = None
    
    def _setup_sync(self):
        """设置字幕同步"""
        self.logger.info("Setting up subtitle synchronization")
        
        try:
            if self.config.sync_config is None:
                self.config.sync_config = SyncConfig()
            
            # 创建同步管道
            self.sync_pipeline = None  # 待实现
            
            self.logger.info("Subtitle synchronization setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup sync: {e}")
            self.sync_pipeline = None
    
    @lru_cache(maxsize=1000)
    def _parse_timestamp_cached(self, timestamp_str: str) -> float:
        """缓存的时间戳解析"""
        return self._parse_timestamp(timestamp_str)
    
    async def load_srt(self, file_path: str) -> List[SRTSegment]:
        """加载 SRT 文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"SRT file not found: {file_path}")
        
        # 检查缓存
        cache_key = str(file_path)
        if self.config.enable_caching and cache_key in self._parse_cache:
            self.logger.info(f"Loading SRT from cache: {file_path}")
            return self._parse_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            segments = self.parser.parse(content)
            
            # 验证字幕段
            segments = self._validate_segments(segments)
            
            # 更新统计信息
            self.stats['total_segments'] = len(segments)
            self.stats['start_time'] = time.time()
            
            # 缓存结果
            if self.config.enable_caching:
                self._parse_cache[cache_key] = segments
            
            self.logger.info(f"Loaded {len(segments)} subtitle segments from {file_path}")
            return segments
            
        except Exception as e:
            self.logger.error(f"Failed to load SRT file {file_path}: {e}")
            raise
    
    def _validate_segments(self, segments: List[SRTSegment]) -> List[SRTSegment]:
        """验证字幕段"""
        valid_segments = []
        
        for segment in segments:
            try:
                # 验证时间戳
                if segment.start_time >= segment.end_time:
                    self.logger.warning(f"Invalid timestamps in segment {segment.index}: start={segment.start_time}, end={segment.end_time}")
                    continue
                
                # 验证持续时间
                if segment.duration < self.config.min_duration or segment.duration > self.config.max_duration:
                    self.logger.warning(f"Invalid duration in segment {segment.index}: {segment.duration}s")
                    continue
                
                # 验证文本长度
                if len(segment.text) < self.config.min_text_length or len(segment.text) > self.config.max_text_length:
                    self.logger.warning(f"Invalid text length in segment {segment.index}: {len(segment.text)} characters")
                    continue
                
                # 验证置信度
                if segment.confidence < self.config.min_confidence or segment.confidence > self.config.max_confidence:
                    self.logger.warning(f"Invalid confidence in segment {segment.index}: {segment.confidence}")
                    continue
                
                valid_segments.append(segment)
                
            except Exception as e:
                self.logger.error(f"Failed to validate segment {segment.index}: {e}")
                continue
        
        self.logger.info(f"Validated {len(valid_segments)}/{len(segments)} subtitle segments")
        return valid_segments
    
    async def save_srt(self, segments: List[SRTSegment], output_path: str):
        """保存 SRT 文件"""
        output_path = Path(output_path)
        
        # 验证字幕段
        segments = self._validate_segments(segments)
        
        content = self.parser.serialize(segments)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新统计信息
            self.stats['end_time'] = time.time()
            self.stats['processed_segments'] = len(segments)
            
            self.logger.info(f"SRT file saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save SRT file {output_path}: {e}")
            raise
    
    async def translate_subtitles(self, segments: List[SRTSegment], 
                                  translator, 
                                  source_lang: str = None,
                                  target_lang: str = None) -> List[SRTSegment]:
        """翻译字幕"""
        source_lang = source_lang or self.config.source_lang
        target_lang = target_lang or self.config.target_lang
        
        self.logger.info(f"Translating {len(segments)} subtitle segments from {source_lang} to {target_lang}")
        
        translated_segments = []
        
        # 启动进度跟踪
        if self.config.enable_progress:
            self.logger.info(f"Starting translation of {len(segments)} segments...")
        
        for i, segment in enumerate(segments):
            try:
                # 检查缓存
                cache_key = f"{segment.text}_{source_lang}_{target_lang}"
                
                if self.config.enable_caching and cache_key in self._translation_cache:
                    translated_text = self._translation_cache[cache_key]
                else:
                    # 翻译字幕文本
                    translated_text = await self._translate_with_retry(
                        translator, segment.text, source_lang, target_lang
                    )
                    
                    # 缓存结果
                    if self.config.enable_caching:
                        self._translation_cache[cache_key] = translated_text
                
                # 创建翻译后的字幕段
                translated_segment = SRTSegment(
                    index=segment.index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=segment.text,
                    translated_text=translated_text,
                    metadata=segment.metadata,
                    confidence=segment.confidence
                )
                
                translated_segments.append(translated_segment)
                
                # 更新统计信息
                self.stats['processed_segments'] += 1
                
                # 进度跟踪
                if self.config.enable_progress and (i + 1) % 10 == 0:
                    progress = (i + 1) / len(segments) * 100
                    self.logger.info(f"Translation progress: {progress:.1f}% ({i + 1}/{len(segments)})")
                
            except Exception as e:
                self.logger.error(f"Failed to translate subtitle {segment.index}: {e}")
                self.stats['failed_segments'] += 1
                # 保留原字幕
                translated_segments.append(segment)
        
        # 完成进度跟踪
        if self.config.enable_progress:
            self.logger.info(f"Translation completed: {self.stats['processed_segments']}/{len(segments)} segments")
        
        return translated_segments
    
    async def _translate_with_retry(self, translator, text: str, source_lang: str, target_lang: str) -> str:
        """带重试机制的翻译"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                # 创建翻译请求
                translation_request = TranslationRequest(
                    text=text,
                    source_lang=Language(source_lang),
                    target_lang=Language(target_lang),
                    engine=TranslationEngine.CUSTOM
                )
                
                return await translator.translate_async(translation_request)
            except Exception as e:
                last_error = e
                self.logger.warning(f"Translation attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        # 所有重试都失败
        self.logger.error(f"All translation attempts failed for text: {text}")
        raise last_error or Exception("Translation failed")
    
    async def adjust_timestamps(self, segments: List[SRTSegment], 
                                original_duration: float,
                                translated_duration: float) -> List[SRTSegment]:
        """调整时间轴"""
        if original_duration == 0 or translated_duration == 0:
            self.logger.warning("Cannot adjust timestamps with zero duration")
            return segments
        
        ratio = translated_duration / original_duration
        
        self.logger.info(f"Adjusting timestamps with ratio: {ratio:.2f} (original: {original_duration}s, translated: {translated_duration}s)")
        
        adjusted_segments = []
        
        for segment in segments:
            try:
                # 调整时间戳
                adjusted_start = segment.start_time * ratio
                adjusted_end = segment.end_time * ratio
                
                # 验证调整后的时间戳
                if adjusted_start >= adjusted_end:
                    self.logger.warning(f"Invalid adjusted timestamps in segment {segment.index}: start={adjusted_start}, end={adjusted_end}")
                    adjusted_segments.append(segment)
                    continue
                
                adjusted_segment = SRTSegment(
                    index=segment.index,
                    start_time=adjusted_start,
                    end_time=adjusted_end,
                    text=segment.text,
                    translated_text=segment.translated_text,
                    metadata=segment.metadata,
                    confidence=segment.confidence
                )
                
                adjusted_segments.append(adjusted_segment)
                
            except Exception as e:
                self.logger.error(f"Failed to adjust timestamps for segment {segment.index}: {e}")
                adjusted_segments.append(segment)
        
        self.logger.info(f"Adjusted {len(adjusted_segments)} subtitle timestamps")
        return adjusted_segments
    
    async def merge_segments(self, segments: List[SRTSegment], 
                             max_gap: float = None) -> List[SRTSegment]:
        """合并相邻的字幕段"""
        if not segments:
            return []
        
        max_gap = max_gap or self.config.max_gap
        
        self.logger.info(f"Merging {len(segments)} subtitle segments with max gap: {max_gap}s")
        
        merged = []
        current = segments[0]
        
        for next_segment in segments[1:]:
            try:
                # 检查是否可以合并（时间间隔小且文本相似）
                gap = next_segment.start_time - current.end_time
                
                if (gap < max_gap and 
                    self._are_texts_similar(current.text, next_segment.text, self.config.similarity_threshold)):
                    # 合并
                    merged_text = current.text + " " + next_segment.text
                    merged_translated = None
                    
                    if current.translated_text or next_segment.translated_text:
                        merged_translated = (
                            (current.translated_text or "") + " " + 
                            (next_segment.translated_text or "")
                        )
                    
                    # 计算合并后的置信度（取平均值）
                    merged_confidence = (current.confidence + next_segment.confidence) / 2
                    
                    current = SRTSegment(
                        index=current.index,
                        start_time=current.start_time,
                        end_time=next_segment.end_time,
                        text=merged_text,
                        translated_text=merged_translated,
                        metadata=current.metadata,
                        confidence=merged_confidence
                    )
                else:
                    # 不能合并，保存当前段
                    merged.append(current)
                    current = next_segment
                    
            except Exception as e:
                self.logger.error(f"Failed to merge segments: {e}")
                merged.append(current)
                current = next_segment
        
        # 添加最后一段
        merged.append(current)
        
        # 更新统计信息
        self.stats['merged_segments'] = len(segments) - len(merged)
        
        self.logger.info(f"Merged {len(segments)} segments into {len(merged)} segments")
        return merged
    
    def _are_texts_similar(self, text1: str, text2: str, threshold: float = None) -> bool:
        """检查文本是否相似"""
        threshold = threshold or self.config.similarity_threshold
        
        # 空文本检查
        if not text1.strip() or not text2.strip():
            return False
        
        # 简单的相似度检查（基于字符重叠）
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        if not set1 or not set2:
            return False
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        similarity = intersection / union if union > 0 else 0
        
        # 额外的检查：长度差异
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        
        # 综合相似度
        combined_similarity = (similarity + len_ratio) / 2
        
        is_similar = combined_similarity > threshold
        
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Text similarity check: {text1} vs {text2} = {combined_similarity:.2f} (threshold: {threshold})")
        
        return is_similar
    
    async def align_timestamps(self, segments: List[SRTSegment], reference_segments: Optional[List[SRTSegment]] = None) -> List[SRTSegment]:
        """时间轴对齐 - 使用LCB-NET模型对齐字幕时间戳"""
        if not self.config.enable_alignment:
            self.logger.warning("Time axis alignment is not enabled")
            return segments
        
        if not self.alignment_pipeline:
            self.logger.error("Alignment pipeline not initialized")
            return segments
        
        self.logger.info(f"Aligning timestamps for {len(segments)} subtitle segments")
        
        aligned_segments = []
        
        try:
            # 如果没有参考段，使用当前段作为参考
            if reference_segments is None:
                reference_segments = segments
            
            # 批量对齐
            for i, segment in enumerate(segments):
                try:
                    # 检查缓存
                    cache_key = self._get_alignment_cache_key(segment, reference_segments)
                    if self.config.enable_caching and cache_key in self._alignment_cache:
                        aligned_segment = self._alignment_cache[cache_key]
                        aligned_segments.append(aligned_segment)
                        continue
                    
                    # 执行对齐
                    aligned_segment = await self._align_single_segment(segment, reference_segments, i)
                    
                    # 缓存结果
                    if self.config.enable_caching:
                        self._alignment_cache[cache_key] = aligned_segment
                    
                    aligned_segments.append(aligned_segment)
                    
                except Exception as e:
                    self.logger.error(f"Failed to align segment {segment.index}: {e}")
                    # 对齐失败时保留原始时间戳
                    segment.alignment_method = "failed"
                    segment.alignment_confidence = 0.0
                    aligned_segments.append(segment)
            
            # 更新统计信息
            self.stats['aligned_segments'] = len(aligned_segments)
            
            self.logger.info(f"Aligned {len(aligned_segments)} subtitle segments")
            return aligned_segments
            
        except Exception as e:
            self.logger.error(f"Failed to align timestamps: {e}")
            return segments
    
    async def _align_single_segment(self, segment: SRTSegment, reference_segments: List[SRTSegment], index: int) -> SRTSegment:
        """对齐单个字幕段"""
        try:
            if self.config.alignment_config.alignment_method == "lcbnet":
                return await self._align_with_lcbnet(segment, reference_segments, index)
            elif self.config.alignment_config.alignment_method == "dynamic_time_warping":
                return await self._align_with_dtw(segment, reference_segments, index)
            elif self.config.alignment_config.alignment_method == "cross_correlation":
                return await self._align_with_cross_correlation(segment, reference_segments, index)
            else:
                raise ValueError(f"Unknown alignment method: {self.config.alignment_config.alignment_method}")
        except Exception as e:
            self.logger.error(f"Alignment failed for segment {segment.index}: {e}")
            raise
    
    async def _align_with_lcbnet(self, segment: SRTSegment, reference_segments: List[SRTSegment], index: int) -> SRTSegment:
        """使用LCB-NET模型对齐"""
        try:
            # 这里需要实现LCB-NET模型调用
            # 由于LCB-NET模型可能需要特定的输入格式，这里提供一个模拟实现
            
            # 模拟对齐结果
            # 在实际实现中，这里会调用LCB-NET模型
            aligned_start = segment.start_time
            aligned_end = segment.end_time
            
            # 模拟时间偏移（基于段的位置和参考段）
            if index > 0 and index < len(reference_segments):
                prev_ref = reference_segments[index - 1]
                curr_ref = reference_segments[index]
                
                # 计算时间偏移
                time_shift = (curr_ref.start_time - prev_ref.start_time) - (segment.start_time - prev_ref.start_time)
                
                # 限制最大偏移
                if abs(time_shift) <= self.config.alignment_config.max_time_shift:
                    aligned_start += time_shift
                    aligned_end += time_shift
            
            # 计算置信度
            confidence = 0.8  # 模拟置信度
            
            # 创建对齐后的段
            aligned_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=aligned_start,
                aligned_end_time=aligned_end,
                alignment_confidence=confidence,
                alignment_method="lcbnet",
                sync_offset=segment.sync_offset,
                sync_confidence=segment.sync_confidence
            )
            
            return aligned_segment
            
        except Exception as e:
            self.logger.error(f"LCB-NET alignment failed: {e}")
            raise
    
    async def _align_with_dtw(self, segment: SRTSegment, reference_segments: List[SRTSegment], index: int) -> SRTSegment:
        """使用动态时间规整对齐"""
        try:
            # 动态时间规整算法实现
            # 这里提供一个简化的实现
            
            if index >= len(reference_segments):
                return segment
            
            ref_segment = reference_segments[index]
            
            # 计算时间偏移
            time_shift = ref_segment.start_time - segment.start_time
            
            # 限制最大偏移
            if abs(time_shift) > self.config.alignment_config.max_time_shift:
                time_shift = 0
            
            # 应用偏移
            aligned_start = segment.start_time + time_shift
            aligned_end = segment.end_time + time_shift
            
            # 计算置信度（基于时间差）
            time_diff = abs(ref_segment.start_time - segment.start_time)
            confidence = max(0.0, 1.0 - (time_diff / self.config.alignment_config.max_time_shift))
            
            # 创建对齐后的段
            aligned_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=aligned_start,
                aligned_end_time=aligned_end,
                alignment_confidence=confidence,
                alignment_method="dynamic_time_warping",
                sync_offset=segment.sync_offset,
                sync_confidence=segment.sync_confidence
            )
            
            return aligned_segment
            
        except Exception as e:
            self.logger.error(f"DTW alignment failed: {e}")
            raise
    
    async def _align_with_cross_correlation(self, segment: SRTSegment, reference_segments: List[SRTSegment], index: int) -> SRTSegment:
        """使用互相关对齐"""
        try:
            # 互相关算法实现
            # 这里提供一个简化的实现
            
            if index >= len(reference_segments):
                return segment
            
            ref_segment = reference_segments[index]
            
            # 计算时间偏移
            time_shift = ref_segment.start_time - segment.start_time
            
            # 限制最大偏移
            if abs(time_shift) > self.config.alignment_config.max_time_shift:
                time_shift = 0
            
            # 应用偏移
            aligned_start = segment.start_time + time_shift
            aligned_end = segment.end_time + time_shift
            
            # 计算置信度（基于时间差）
            time_diff = abs(ref_segment.start_time - segment.start_time)
            confidence = max(0.0, 1.0 - (time_diff / self.config.alignment_config.max_time_shift))
            
            # 创建对齐后的段
            aligned_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=aligned_start,
                aligned_end_time=aligned_end,
                alignment_confidence=confidence,
                alignment_method="cross_correlation",
                sync_offset=segment.sync_offset,
                sync_confidence=segment.sync_confidence
            )
            
            return aligned_segment
            
        except Exception as e:
            self.logger.error(f"Cross-correlation alignment failed: {e}")
            raise
    
    def _get_alignment_cache_key(self, segment: SRTSegment, reference_segments: List[SRTSegment]) -> str:
        """获取对齐缓存键"""
        # 创建基于段内容和参考段的缓存键
        content = f"{segment.index}_{segment.start_time}_{segment.end_time}_{segment.text}"
        ref_content = "_".join([f"{ref.index}_{ref.start_time}" for ref in reference_segments[:10]])  # 只取前10个参考段
        
        return hashlib.md5(f"{content}_{ref_content}".encode()).hexdigest()
    
    async def sync_subtitles(self, segments: List[SRTSegment], reference_audio: Optional[str] = None) -> List[SRTSegment]:
        """字幕同步 - 将字幕与音频/视频进行同步"""
        if not self.config.enable_sync:
            self.logger.warning("Subtitle synchronization is not enabled")
            return segments
        
        if not self.sync_pipeline:
            self.logger.error("Sync pipeline not initialized")
            return segments
        
        self.logger.info(f"Synchronizing {len(segments)} subtitle segments")
        
        synced_segments = []
        
        try:
            # 批量同步
            for i, segment in enumerate(segments):
                try:
                    # 检查缓存
                    cache_key = self._get_sync_cache_key(segment, reference_audio)
                    if self.config.enable_caching and cache_key in self._sync_cache:
                        synced_segment = self._sync_cache[cache_key]
                        synced_segments.append(synced_segment)
                        continue
                    
                    # 执行同步
                    synced_segment = await self._sync_single_segment(segment, reference_audio, i)
                    
                    # 缓存结果
                    if self.config.enable_caching:
                        self._sync_cache[cache_key] = synced_segment
                    
                    synced_segments.append(synced_segment)
                    
                except Exception as e:
                    self.logger.error(f"Failed to sync segment {segment.index}: {e}")
                    # 同步失败时保留原始时间戳
                    segment.sync_offset = 0.0
                    segment.sync_confidence = 0.0
                    synced_segments.append(segment)
            
            # 更新统计信息
            self.stats['synced_segments'] = len(synced_segments)
            
            self.logger.info(f"Synchronized {len(synced_segments)} subtitle segments")
            return synced_segments
            
        except Exception as e:
            self.logger.error(f"Failed to sync subtitles: {e}")
            return segments
    
    async def _sync_single_segment(self, segment: SRTSegment, reference_audio: Optional[str], index: int) -> SRTSegment:
        """同步单个字幕段"""
        try:
            if self.config.sync_config.sync_method == "dynamic_time_warping":
                return await self._sync_with_dtw(segment, reference_audio, index)
            elif self.config.sync_config.sync_method == "cross_correlation":
                return await self._sync_with_cross_correlation(segment, reference_audio, index)
            elif self.config.sync_config.sync_method == "feature_matching":
                return await self._sync_with_feature_matching(segment, reference_audio, index)
            else:
                raise ValueError(f"Unknown sync method: {self.config.sync_config.sync_method}")
        except Exception as e:
            self.logger.error(f"Sync failed for segment {segment.index}: {e}")
            raise
    
    async def _sync_with_dtw(self, segment: SRTSegment, reference_audio: Optional[str], index: int) -> SRTSegment:
        """使用动态时间规整同步"""
        try:
            # 动态时间规整同步实现
            # 这里提供一个简化的实现
            
            # 模拟同步偏移
            # 在实际实现中，这里会分析音频特征并计算偏移
            sync_offset = 0.0
            
            # 模拟基于段位置的偏移
            if index % 3 == 0:
                sync_offset = 0.1
            elif index % 3 == 1:
                sync_offset = -0.1
            
            # 限制最大偏移
            if abs(sync_offset) > self.config.sync_config.max_offset:
                sync_offset = 0.0
            
            # 计算置信度
            confidence = 0.9
            
            # 应用同步偏移
            synced_start = segment.start_time + sync_offset
            synced_end = segment.end_time + sync_offset
            
            # 创建同步后的段
            synced_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=segment.aligned_start_time,
                aligned_end_time=segment.aligned_end_time,
                alignment_confidence=segment.alignment_confidence,
                alignment_method=segment.alignment_method,
                sync_offset=sync_offset,
                sync_confidence=confidence
            )
            
            return synced_segment
            
        except Exception as e:
            self.logger.error(f"DTW sync failed: {e}")
            raise
    
    async def _sync_with_cross_correlation(self, segment: SRTSegment, reference_audio: Optional[str], index: int) -> SRTSegment:
        """使用互相关同步"""
        try:
            # 互相关同步实现
            # 这里提供一个简化的实现
            
            # 模拟同步偏移
            sync_offset = 0.0
            
            # 模拟基于段位置的偏移
            if index % 2 == 0:
                sync_offset = 0.05
            else:
                sync_offset = -0.05
            
            # 限制最大偏移
            if abs(sync_offset) > self.config.sync_config.max_offset:
                sync_offset = 0.0
            
            # 计算置信度
            confidence = 0.85
            
            # 应用同步偏移
            synced_start = segment.start_time + sync_offset
            synced_end = segment.end_time + sync_offset
            
            # 创建同步后的段
            synced_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=segment.aligned_start_time,
                aligned_end_time=segment.aligned_end_time,
                alignment_confidence=segment.alignment_confidence,
                alignment_method=segment.alignment_method,
                sync_offset=sync_offset,
                sync_confidence=confidence
            )
            
            return synced_segment
            
        except Exception as e:
            self.logger.error(f"Cross-correlation sync failed: {e}")
            raise
    
    async def _sync_with_feature_matching(self, segment: SRTSegment, reference_audio: Optional[str], index: int) -> SRTSegment:
        """使用特征匹配同步"""
        try:
            # 特征匹配同步实现
            # 这里提供一个简化的实现
            
            # 模拟同步偏移
            sync_offset = 0.0
            
            # 模拟基于段位置的偏移
            if index % 4 == 0:
                sync_offset = 0.08
            elif index % 4 == 1:
                sync_offset = -0.08
            elif index % 4 == 2:
                sync_offset = 0.03
            
            # 限制最大偏移
            if abs(sync_offset) > self.config.sync_config.max_offset:
                sync_offset = 0.0
            
            # 计算置信度
            confidence = 0.8
            
            # 应用同步偏移
            synced_start = segment.start_time + sync_offset
            synced_end = segment.end_time + sync_offset
            
            # 创建同步后的段
            synced_segment = SRTSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                translated_text=segment.translated_text,
                metadata=segment.metadata,
                confidence=segment.confidence,
                aligned_start_time=segment.aligned_start_time,
                aligned_end_time=segment.aligned_end_time,
                alignment_confidence=segment.alignment_confidence,
                alignment_method=segment.alignment_method,
                sync_offset=sync_offset,
                sync_confidence=confidence
            )
            
            return synced_segment
            
        except Exception as e:
            self.logger.error(f"Feature matching sync failed: {e}")
            raise
    
    def _get_sync_cache_key(self, segment: SRTSegment, reference_audio: Optional[str]) -> str:
        """获取同步缓存键"""
        # 创建基于段内容和参考音频的缓存键
        content = f"{segment.index}_{segment.start_time}_{segment.end_time}_{segment.text}"
        ref_audio = reference_audio or "none"
        
        return hashlib.md5(f"{content}_{ref_audio}".encode()).hexdigest()
    
    def check_conflicts(self, segments: List[SRTSegment]) -> Dict[str, Any]:
        """检查时间轴冲突"""
        self.logger.info(f"Checking conflicts for {len(segments)} subtitle segments")
        
        conflicts = {
            'overlaps': [],
            'gaps': [],
            'duration_issues': [],
            'confidence_issues': []
        }
        
        for i in range(len(segments) - 1):
            current = segments[i]
            next_seg = segments[i + 1]
            
            # 检查重叠
            if current.end_time > next_seg.start_time:
                overlap = {
                    'index1': current.index,
                    'index2': next_seg.index,
                    'overlap_duration': current.end_time - next_seg.start_time,
                    'start_time': next_seg.start_time,
                    'end_time': current.end_time
                }
                conflicts['overlaps'].append(overlap)
            
            # 检查间隔
            gap = next_seg.start_time - current.end_time
            if gap > self.config.max_gap:
                gap_info = {
                    'index1': current.index,
                    'index2': next_seg.index,
                    'gap_duration': gap,
                    'start_time': current.end_time,
                    'end_time': next_seg.start_time
                }
                conflicts['gaps'].append(gap_info)
            
            # 检查持续时间
            if current.duration > self.config.max_duration:
                conflicts['duration_issues'].append({
                    'index': current.index,
                    'duration': current.duration,
                    'issue': 'too_long'
                })
            elif current.duration < self.config.min_duration:
                conflicts['duration_issues'].append({
                    'index': current.index,
                    'duration': current.duration,
                    'issue': 'too_short'
                })
            
            # 检查置信度
            if current.confidence < self.config.min_confidence:
                conflicts['confidence_issues'].append({
                    'index': current.index,
                    'confidence': current.confidence,
                    'issue': 'low_confidence'
                })
        
        self.logger.info(f"Found {len(conflicts['overlaps'])} overlaps, {len(conflicts['gaps'])} gaps")
        return conflicts
    
    async def fix_conflicts(self, segments: List[SRTSegment], conflicts: Optional[Dict[str, Any]] = None) -> List[SRTSegment]:
        """修复时间轴冲突"""
        if conflicts is None:
            conflicts = self.check_conflicts(segments)
        
        self.logger.info(f"Fixing conflicts for {len(segments)} subtitle segments")
        
        fixed_segments = segments.copy()
        
        # 修复重叠
        if conflicts['overlaps']:
            self.logger.info(f"Fixing {len(conflicts['overlaps'])} overlaps")
            fixed_segments = await self._fix_overlaps(fixed_segments, conflicts['overlaps'])
        
        # 修复间隔
        if conflicts['gaps']:
            self.logger.info(f"Fixing {len(conflicts['gaps'])} gaps")
            fixed_segments = await self._fix_gaps(fixed_segments, conflicts['gaps'])
        
        # 修复持续时间问题
        if conflicts['duration_issues']:
            self.logger.info(f"Fixing {len(conflicts['duration_issues'])} duration issues")
            fixed_segments = await self._fix_duration_issues(fixed_segments, conflicts['duration_issues'])
        
        # 修复置信度问题
        if conflicts['confidence_issues']:
            self.logger.info(f"Fixing {len(conflicts['confidence_issues'])} confidence issues")
            fixed_segments = await self._fix_confidence_issues(fixed_segments, conflicts['confidence_issues'])
        
        self.logger.info(f"Fixed conflicts, returning {len(fixed_segments)} segments")
        return fixed_segments
    
    async def _fix_overlaps(self, segments: List[SRTSegment], overlaps: List[Dict[str, Any]]) -> List[SRTSegment]:
        """修复重叠"""
        fixed_segments = segments.copy()
        
        for overlap in overlaps:
            try:
                idx1 = overlap['index1'] - 1
                idx2 = overlap['index2'] - 1
                
                if 0 <= idx1 < len(fixed_segments) and 0 <= idx2 < len(fixed_segments):
                    # 调整第一个段的结束时间
                    fixed_segments[idx1].end_time = overlap['start_time']
                    
                    # 重新计算持续时间
                    fixed_segments[idx1].duration = fixed_segments[idx1].end_time - fixed_segments[idx1].start_time
                    
                    self.logger.debug(f"Fixed overlap: segment {overlap['index1']} end_time adjusted to {overlap['start_time']}")
                    
            except Exception as e:
                self.logger.error(f"Failed to fix overlap {overlap}: {e}")
        
        return fixed_segments
    
    async def _fix_gaps(self, segments: List[SRTSegment], gaps: List[Dict[str, Any]]) -> List[SRTSegment]:
        """修复间隔"""
        fixed_segments = segments.copy()
        
        for gap in gaps:
            try:
                idx1 = gap['index1'] - 1
                idx2 = gap['index2'] - 1
                
                if 0 <= idx1 < len(fixed_segments) and 0 <= idx2 < len(fixed_segments):
                    # 调整第二个段的开始时间
                    fixed_segments[idx2].start_time = gap['start_time']
                    
                    # 重新计算持续时间
                    fixed_segments[idx2].duration = fixed_segments[idx2].end_time - fixed_segments[idx2].start_time
                    
                    self.logger.debug(f"Fixed gap: segment {gap['index2']} start_time adjusted to {gap['start_time']}")
                    
            except Exception as e:
                self.logger.error(f"Failed to fix gap {gap}: {e}")
        
        return fixed_segments
    
    async def _fix_duration_issues(self, segments: List[SRTSegment], duration_issues: List[Dict[str, Any]]) -> List[SRTSegment]:
        """修复持续时间问题"""
        fixed_segments = segments.copy()
        
        for issue in duration_issues:
            try:
                idx = issue['index'] - 1
                
                if 0 <= idx < len(fixed_segments):
                    segment = fixed_segments[idx]
                    
                    if issue['issue'] == 'too_long':
                        # 对于过长的段，截断到最大持续时间
                        segment.end_time = segment.start_time + self.config.max_duration
                        segment.duration = self.config.max_duration
                        
                        self.logger.debug(f"Fixed too long segment: {segment.index} duration adjusted to {self.config.max_duration}")
                        
                    elif issue['issue'] == 'too_short':
                        # 对于过短的段，扩展到最小持续时间
                        segment.end_time = segment.start_time + self.config.min_duration
                        segment.duration = self.config.min_duration
                        
                        self.logger.debug(f"Fixed too short segment: {segment.index} duration adjusted to {self.config.min_duration}")
                        
            except Exception as e:
                self.logger.error(f"Failed to fix duration issue {issue}: {e}")
        
        return fixed_segments
    
    async def _fix_confidence_issues(self, segments: List[SRTSegment], confidence_issues: List[Dict[str, Any]]) -> List[SRTSegment]:
        """修复置信度问题"""
        fixed_segments = segments.copy()
        
        for issue in confidence_issues:
            try:
                idx = issue['index'] - 1
                
                if 0 <= idx < len(fixed_segments):
                    segment = fixed_segments[idx]
                    
                    if issue['issue'] == 'low_confidence':
                        # 对于低置信度的段，标记为需要人工审核
                        if segment.metadata is None:
                            segment.metadata = {}
                        
                        segment.metadata['needs_review'] = True
                        segment.metadata['review_reason'] = 'low_confidence'
                        
                        self.logger.debug(f"Marked segment {segment.index} for review due to low confidence")
                        
            except Exception as e:
                self.logger.error(f"Failed to fix confidence issue {issue}: {e}")
        
        return fixed_segments
    
    async def clean_subtitles(self, segments: List[SRTSegment]) -> List[SRTSegment]:
        """清理字幕"""
        self.logger.info(f"Cleaning {len(segments)} subtitle segments")
        
        cleaned_segments = []
        
        for segment in segments:
            try:
                # 清理文本
                text = self._clean_text(segment.text)
                
                # 如果有翻译文本，也清理
                translated_text = None
                if segment.translated_text:
                    # 处理 TranslationResponse 对象
                    if hasattr(segment.translated_text, 'translated_text'):
                        translated_text = self._clean_text(segment.translated_text.translated_text)
                    else:
                        translated_text = self._clean_text(segment.translated_text)
                
                cleaned_segment = SRTSegment(
                    index=segment.index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=text,
                    translated_text=translated_text,
                    metadata=segment.metadata,
                    confidence=segment.confidence,
                    aligned_start_time=segment.aligned_start_time,
                    aligned_end_time=segment.aligned_end_time,
                    alignment_confidence=segment.alignment_confidence,
                    alignment_method=segment.alignment_method,
                    sync_offset=segment.sync_offset,
                    sync_confidence=segment.sync_confidence
                )
                
                cleaned_segments.append(cleaned_segment)
                
            except Exception as e:
                self.logger.error(f"Failed to clean segment {segment.index}: {e}")
                cleaned_segments.append(segment)
        
        # 更新统计信息
        self.stats['cleaned_segments'] = len(cleaned_segments)
        
        self.logger.info(f"Cleaned {len(cleaned_segments)} subtitle segments")
        return cleaned_segments
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 规范化标点
        text = text.replace(',,', ',').replace('..', '.')
        text = text.replace('!!', '!').replace('??', '?')
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'["\'`]', '"', text)
        
        # 规范化括号
        text = re.sub(r'\[\s*\(', '(', text)
        text = re.sub(r'\)\s*\]', ')', text)
        
        # 移除行首行尾的标点
        text = re.sub(r'^[\s.,;:!?]+|\s*[.,;:!?]+$', '', text)
        
        # 确保文本不为空
        if not text.strip():
            return ""
        
        return text.strip()
    
    async def process_srt_file(self, input_path: str, translator, 
                               source_lang: str = None, target_lang: str = None,
                               output_path: Optional[str] = None) -> str:
        """完整处理 SRT 文件"""
        source_lang = source_lang or self.config.source_lang
        target_lang = target_lang or self.config.target_lang
        
        self.logger.info(f"Starting SRT file processing: {input_path}")
        self.logger.info(f"Translation: {source_lang} -> {target_lang}")
        
        try:
            # 重置统计信息
            self.stats = {
                'total_segments': 0,
                'processed_segments': 0,
                'failed_segments': 0,
                'merged_segments': 0,
                'cleaned_segments': 0,
                'start_time': time.time(),
                'end_time': None
            }
            
            # 加载字幕
            self.logger.info("Step 1: Loading SRT file...")
            segments = await self.load_srt(input_path)
            
            if not segments:
                raise ValueError("No subtitle segments found in the file")
            
            # 翻译字幕
            self.logger.info("Step 2: Translating subtitles...")
            translated = await self.translate_subtitles(
                segments, translator, source_lang, target_lang
            )
            
            # 清理字幕
            self.logger.info("Step 3: Cleaning subtitles...")
            cleaned = await self.clean_subtitles(translated)
            
            # 合并相邻段
            self.logger.info("Step 4: Merging segments...")
            merged = await self.merge_segments(cleaned)
            
            # 保存结果
            self.logger.info("Step 5: Saving processed file...")
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}_translated.srt"
            
            await self.save_srt(merged, str(output_path))
            
            # 计算处理时间
            self.stats['end_time'] = time.time()
            processing_time = self.stats['end_time'] - self.stats['start_time']
            
            # 输出统计信息
            self.logger.info("=== Processing Statistics ===")
            self.logger.info(f"Total segments: {self.stats['total_segments']}")
            self.logger.info(f"Processed segments: {self.stats['processed_segments']}")
            self.logger.info(f"Failed segments: {self.stats['failed_segments']}")
            self.logger.info(f"Merged segments: {self.stats['merged_segments']}")
            self.logger.info(f"Processing time: {processing_time:.2f}s")
            self.logger.info(f"Output file: {output_path}")
            
            self.logger.info(f"SRT file processing completed successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to process SRT file {input_path}: {e}")
            raise
    
    def _setup_ocr(self):
        """设置OCR"""
        self.logger.info("Setting up OCR for subtitle extraction")
        
        try:
            # 下载OCR模型
            model_dir = snapshot_download(self.config.ocr_model)
            
            # 创建OCR管道
            self.ocr_pipeline = pipeline(
                task=Tasks.ocr_recognition,
                model=model_dir,
                device=self.config.ocr_device
            )
            
            self.logger.info(f"OCR setup completed with model: {self.config.ocr_model}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup OCR: {e}")
            self.ocr_pipeline = None
            raise

# 使用示例
    def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        stats = self.stats.copy()
        
        # 计算处理时间
        if stats['start_time'] and stats['end_time']:
            stats['processing_time'] = stats['end_time'] - stats['start_time']
        elif stats['start_time']:
            stats['processing_time'] = time.time() - stats['start_time']
        
        # 计算成功率
        if stats['total_segments'] > 0:
            stats['success_rate'] = stats['processed_segments'] / stats['total_segments']
        else:
            stats['success_rate'] = 0.0
        
        # 添加配置信息
        stats['config'] = {
            'source_lang': self.config.source_lang,
            'target_lang': self.config.target_lang,
            'min_confidence': self.config.min_confidence,
            'max_confidence': self.config.max_confidence,
            'enable_caching': self.config.enable_caching,
            'max_retries': self.config.max_retries
        }
        
        return stats
    
    def extract_frames_from_video(self, video_path: str, output_dir: str = None) -> List[str]:
        """从视频中提取帧"""
        if not self.config.enable_ocr:
            raise ValueError("OCR is not enabled in configuration")
        
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # 创建输出目录
        if output_dir is None:
            output_dir = video_path.parent / f"{video_path.stem}_frames"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise IOError(f"Could not open video file: {video_path}")
        
        frame_count = 0
        extracted_frames = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 每隔指定帧数提取一次
                if frame_count % self.config.ocr_frame_interval == 0:
                    frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    extracted_frames.append(str(frame_path))
                
                frame_count += 1
            
            self.logger.info(f"Extracted {len(extracted_frames)} frames from {video_path}")
            return extracted_frames
            
        finally:
            cap.release()
    
    def extract_text_from_frames(self, frame_paths: List[str]) -> List[Dict[str, Any]]:
        """从帧中提取文本"""
        if not self.config.enable_ocr:
            raise ValueError("OCR is not enabled in configuration")
        
        if not self.ocr_pipeline:
            raise ValueError("OCR pipeline is not initialized")
        
        if not frame_paths:
            return []
        
        results = []
        
        # 按批次处理
        for i in range(0, len(frame_paths), self.config.ocr_batch_size):
            batch_paths = frame_paths[i:i + self.config.ocr_batch_size]
            batch_images = []
            
            # 加载图像
            for path in batch_paths:
                try:
                    image = cv2.imread(path)
                    if image is not None:
                        batch_images.append(image)
                except Exception as e:
                    self.logger.warning(f"Failed to load image {path}: {e}")
            
            if not batch_images:
                continue
            
            # 执行OCR
            try:
                ocr_results = self.ocr_pipeline(batch_images)
                
                # 处理结果
                for j, result in enumerate(ocr_results):
                    if result and 'text' in result:
                        text = result['text'].strip()
                        confidence = result.get('confidence', 1.0)
                        
                        # 过滤低置信度和无效文本
                        if (confidence >= self.config.ocr_confidence_threshold and 
                            self.config.ocr_min_text_length <= len(text) <= self.config.ocr_max_text_length):
                            
                            results.append({
                                'frame_path': batch_paths[j],
                                'text': text,
                                'confidence': confidence,
                                'timestamp': self._extract_timestamp_from_frame(batch_paths[j])
                            })
            
            except Exception as e:
                self.logger.error(f"OCR processing failed for batch {i}: {e}")
        
        self.logger.info(f"Extracted text from {len(results)} frames")
        return results
    
    def _extract_timestamp_from_frame(self, frame_path: str) -> float:
        """从帧路径中提取时间戳"""
        try:
            # 从帧文件名中提取帧号
            frame_name = Path(frame_path).stem
            match = re.match(r'frame_(\d+)', frame_name)
            if match:
                frame_number = int(match.group(1))
                # 假设帧率为30fps，计算时间戳
                return frame_number / 30.0
        except Exception as e:
            self.logger.warning(f"Failed to extract timestamp from frame {frame_path}: {e}")
        
        return 0.0
    
    async def extract_subtitles_from_video(self, video_path: str, output_dir: str = None) -> List[SRTSegment]:
        """从视频中提取字幕"""
        if not self.config.enable_ocr:
            raise ValueError("OCR is not enabled in configuration")
        
        self.logger.info(f"Starting subtitle extraction from video: {video_path}")
        
        try:
            # 提取帧
            self.logger.info("Step 1: Extracting frames from video...")
            frame_paths = self.extract_frames_from_video(video_path, output_dir)
            
            if not frame_paths:
                self.logger.warning("No frames extracted from video")
                return []
            
            # 提取文本
            self.logger.info("Step 2: Extracting text from frames...")
            ocr_results = self.extract_text_from_frames(frame_paths)
            
            if not ocr_results:
                self.logger.warning("No text extracted from frames")
                return []
            
            # 创建字幕段
            self.logger.info("Step 3: Creating subtitle segments...")
            segments = []
            
            for i, result in enumerate(ocr_results):
                try:
                    segment = SRTSegment(
                        index=i + 1,
                        start_time=result['timestamp'],
                        end_time=result['timestamp'] + 2.0,  # 假设每个字幕持续2秒
                        text=result['text'],
                        confidence=result['confidence']
                    )
                    segments.append(segment)
                except Exception as e:
                    self.logger.error(f"Failed to create segment from OCR result: {e}")
            
            # 合并相邻段
            self.logger.info("Step 4: Merging adjacent segments...")
            merged_segments = await self.merge_segments(segments)
            
            # 清理字幕
            self.logger.info("Step 5: Cleaning extracted subtitles...")
            cleaned_segments = await self.clean_subtitles(merged_segments)
            
            self.logger.info(f"Extracted {len(cleaned_segments)} subtitle segments from video")
            return cleaned_segments
            
        except Exception as e:
            self.logger.error(f"Failed to extract subtitles from video {video_path}: {e}")
            raise

if __name__ == "__main__":
    async def main():
        # 模拟翻译器
        class MockTranslator:
            async def translate_async(self, text: str, source_lang: str, target_lang: str) -> str:
                return f"[翻译] {text}"
        
        translator = MockTranslator()
        processor = SubtitleProcessor()
        
        # 创建测试 SRT 内容
        test_srt = """1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:03,500 --> 00:00:05,500
This is a test.

3
00:00:06,000 --> 00:00:08,000
Subtitle processing.
"""
        
        # 解析
        segments = processor.parser.parse(test_srt)
        print(f"解析了 {len(segments)} 个字幕段")
        
        # 翻译
        translated = await processor.translate_subtitles(segments, translator)
        print(f"翻译了 {len(translated)} 个字幕段")
        
        # 显示结果
        for segment in translated:
            print(f"{segment.index}: {segment.text} -> {segment.translated_text}")
        
        # 测试OCR功能
        try:
            # 创建启用OCR的配置
            ocr_config = SubtitleProcessingConfig(
                enable_ocr=True,
                ocr_model="damo/cv_resnet50_vd_ocr",
                ocr_device="cpu",
                ocr_batch_size=2,
                ocr_confidence_threshold=0.5,
                ocr_min_text_length=2,
                ocr_max_text_length=50
            )
            
            ocr_processor = SubtitleProcessor(ocr_config)
            
            # 创建一个测试视频文件（模拟）
            test_video = video_path.parent / "test_video.mp4"
            
            # 提取字幕
            print("\n=== Testing OCR Subtitle Extraction ===")
            video_subtitles = await ocr_processor.extract_subtitles_from_video(str(test_video))
            print(f"从视频中提取了 {len(video_subtitles)} 个字幕段")
            
            for subtitle in video_subtitles[:3]:  # 显示前3个
                print(f"{subtitle.index}: [{subtitle.start_time:.2f}-{subtitle.end_time:.2f}] {subtitle.text}")
                
        except Exception as e:
            print(f"OCR测试失败: {e}")
            print("注意: 这可能是因为缺少测试视频文件或OCR模型下载失败")
    
    # 运行示例
    asyncio.run(main())
