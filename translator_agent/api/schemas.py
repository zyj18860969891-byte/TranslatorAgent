"""
API 数据模型定义

定义所有 API 请求和响应的数据结构
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoProcessingRequest(BaseModel):
    """视频处理请求模型"""
    video_path: str = Field(..., description="视频文件路径")
    output_path: Optional[str] = Field(None, description="输出路径")
    
    # 处理选项
    enable_frame_extraction: bool = Field(True, description="是否提取视频帧")
    enable_subtitle_extraction: bool = Field(False, description="是否提取字幕")
    enable_subtitle_erasure: bool = Field(False, description="是否擦除字幕")
    enable_visual_analysis: bool = Field(False, description="是否进行视觉分析")
    
    # 配置参数
    frame_rate: float = Field(2.0, description="帧率（FPS）")
    max_frames: int = Field(100, description="最大帧数")
    batch_size: int = Field(10, description="批处理大小")
    
    # 字幕配置
    subtitle_language: str = Field("zh", description="字幕语言")
    subtitle_confidence_threshold: float = Field(0.7, description="字幕置信度阈值")
    
    # 模型配置
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度")


class VideoProcessingResponse(BaseModel):
    """视频处理响应模型"""
    success: bool = Field(..., description="是否成功")
    task_id: Optional[str] = Field(None, description="任务ID")
    video_path: Optional[str] = Field(None, description="处理后的视频路径")
    extracted_frames: List[str] = Field(default_factory=list, description="提取的帧文件")
    subtitle_path: Optional[str] = Field(None, description="字幕文件路径")
    analysis_path: Optional[str] = Field(None, description="分析报告路径")
    processing_time: float = Field(..., description="处理时间（秒）")
    frame_count: int = Field(0, description="处理的帧数")
    subtitle_count: int = Field(0, description="处理的字幕数")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class SubtitleProcessingRequest(BaseModel):
    """字幕处理请求模型"""
    subtitle_path: str = Field(..., description="字幕文件路径")
    output_path: Optional[str] = Field(None, description="输出路径")
    
    # 处理选项
    enable_translation: bool = Field(True, description="是否翻译字幕")
    enable_alignment: bool = Field(False, description="是否对齐时间轴")
    enable_sync: bool = Field(False, description="是否同步字幕")
    enable_conflict_check: bool = Field(True, description="是否检查冲突")
    enable_conflict_fix: bool = Field(False, description="是否修复冲突")
    
    # 翻译配置
    source_language: str = Field("auto", description="源语言")
    target_language: str = Field("zh", description="目标语言")
    
    # 对齐配置
    alignment_method: str = Field("dynamic_time_warping", description="对齐方法")
    reference_segments: Optional[List[Dict[str, Any]]] = Field(None, description="参考字幕段")
    
    # 同步配置
    sync_method: str = Field("dynamic_time_warping", description="同步方法")
    reference_audio: Optional[str] = Field(None, description="参考音频路径")
    
    # 模型配置
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度")


class SubtitleProcessingResponse(BaseModel):
    """字幕处理响应模型"""
    success: bool = Field(..., description="是否成功")
    task_id: Optional[str] = Field(None, description="任务ID")
    original_subtitle_path: str = Field(..., description="原始字幕文件路径")
    processed_subtitle_path: Optional[str] = Field(None, description="处理后的字幕文件路径")
    subtitle_count: int = Field(..., description="字幕段数量")
    processing_time: float = Field(..., description="处理时间（秒）")
    aligned_count: int = Field(0, description="对齐的字幕段数")
    synced_count: int = Field(0, description="同步的字幕段数")
    conflicts_found: int = Field(0, description="发现的冲突数")
    conflicts_fixed: int = Field(0, description="修复的冲突数")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class TaskInfo(BaseModel):
    """任务信息模型"""
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field(..., description="任务类型")
    status: TaskStatus = Field(..., description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    progress: float = Field(0.0, description="进度（0-1）")
    files: List[str] = Field(default_factory=list, description="任务文件")
    memory: Dict[str, Any] = Field(default_factory=dict, description="任务内存")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    success: bool = Field(..., description="是否成功")
    task: Optional[TaskInfo] = Field(None, description="任务信息")


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    success: bool = Field(..., description="是否成功")
    tasks: List[TaskInfo] = Field(..., description="任务列表")
    total: int = Field(..., description="总任务数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")


class TranslationRequest(BaseModel):
    """翻译请求模型"""
    text: str = Field(..., description="要翻译的文本")
    source_language: str = Field("auto", description="源语言，默认为自动检测")
    target_language: str = Field(..., description="目标语言")
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度，控制翻译的创造性")
    max_tokens: int = Field(1000, description="最大令牌数")


class TranslationResponse(BaseModel):
    """翻译响应模型"""
    success: bool = Field(..., description="是否成功")
    translated_text: str = Field(..., description="翻译后的文本")
    source_language: str = Field(..., description="检测到的源语言")
    target_language: str = Field(..., description="目标语言")
    model_used: str = Field(..., description="使用的模型")
    processing_time: float = Field(..., description="处理时间（秒）")
    confidence: float = Field(..., description="翻译置信度")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class TranslationRequest(BaseModel):
    """翻译请求模型"""
    text: str = Field(..., description="要翻译的文本")
    source_language: str = Field("auto", description="源语言，默认为自动检测")
    target_language: str = Field(..., description="目标语言")
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度，控制翻译的创造性")
    max_tokens: int = Field(1000, description="最大令牌数")


class TranslationResponse(BaseModel):
    """翻译响应模型"""
    success: bool = Field(..., description="是否成功")
    translated_text: str = Field(..., description="翻译后的文本")
    source_language: str = Field(..., description="检测到的源语言")
    target_language: str = Field(..., description="目标语言")
    model_used: str = Field(..., description="使用的模型")
    processing_time: float = Field(..., description="处理时间（秒）")
    confidence: float = Field(..., description="翻译置信度")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class VideoTranslationRequest(BaseModel):
    """视频翻译请求模型（兼容旧版本）"""
    video_path: str = Field(..., description="视频文件路径")
    target_language: str = Field(..., description="目标语言")
    output_path: Optional[str] = Field(None, description="输出路径")
    extract_frames: bool = Field(True, description="是否提取帧")
    process_subtitles: bool = Field(True, description="是否处理字幕")
    enable_subtitle_extraction: bool = Field(True, description="是否提取字幕")
    enable_subtitle_erasure: bool = Field(False, description="是否擦除字幕")
    enable_subtitle_translation: bool = Field(True, description="是否翻译字幕")
    subtitle_path: Optional[str] = Field(None, description="字幕文件路径")
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度")


class VideoTranslationResponse(BaseModel):
    """视频翻译响应模型（兼容旧版本）"""
    success: bool = Field(..., description="是否成功")
    video_path: str = Field(..., description="处理后的视频路径")
    extracted_frames: List[str] = Field(default_factory=list, description="提取的帧文件")
    translated_subtitles: Optional[str] = Field(None, description="翻译后的字幕文件路径")
    processing_time: float = Field(..., description="处理时间（秒）")
    frame_count: int = Field(..., description="处理的帧数")
    subtitle_count: int = Field(0, description="处理的字幕数")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class SubtitleTranslationRequest(BaseModel):
    """字幕翻译请求模型（兼容旧版本）"""
    subtitle_path: str = Field(..., description="字幕文件路径")
    source_language: str = Field("auto", description="源语言，默认为自动检测")
    target_language: str = Field(..., description="目标语言")
    output_path: Optional[str] = Field(None, description="输出路径")
    model_name: Optional[str] = Field(None, description="使用的模型名称")
    temperature: float = Field(0.7, description="生成温度")
    merge_segments: bool = Field(True, description="是否合并字幕段")


class SubtitleTranslationResponse(BaseModel):
    """字幕翻译响应模型（兼容旧版本）"""
    success: bool = Field(..., description="是否成功")
    original_subtitle_path: str = Field(..., description="原始字幕文件路径")
    translated_subtitle_path: str = Field(..., description="翻译后的字幕文件路径")
    subtitle_count: int = Field(..., description="字幕段数量")
    processing_time: float = Field(..., description="处理时间（秒）")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    timestamp: datetime = Field(..., description="检查时间")
    services: Dict[str, str] = Field(default_factory=dict, description="子服务状态")


class ModelInfo(BaseModel):
    """模型信息模型"""
    name: str = Field(..., description="模型名称")
    description: str = Field(..., description="模型描述")
    supported_languages: List[str] = Field(..., description="支持的语言列表")
    capabilities: List[str] = Field(..., description="模型能力")
    version: str = Field(..., description="模型版本")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="是否成功")
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(..., description="错误时间")