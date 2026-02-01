"""
API 路由定义 (兼容旧版本)

定义所有 API 端点和处理函数
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 导入配置管理器和ModelScope客户端
from translator_agent.cli.commands import get_config_manager, get_modelscope_client
from translator_agent.core.translator import Translator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from .schemas import (
    TranslationRequest,
    TranslationResponse,
    VideoTranslationRequest,
    VideoTranslationResponse,
    SubtitleTranslationRequest,
    SubtitleTranslationResponse,
    HealthResponse,
    ModelInfo,
    ErrorResponse
)
from ..core.agent import TranslatorAgent
from ..core.modelscope_integration import ModelScopeClient
from ..data.video_processor import VideoProcessor
from ..data.subtitle_processor import SubtitleProcessor
from ..config.settings import ConfigManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="")

# 全局依赖
config_manager = ConfigManager()
modelscope_client = ModelScopeClient()
translator_agent = TranslatorAgent(modelscope_client, modelscope_client)
video_processor = VideoProcessor()
subtitle_processor = SubtitleProcessor()

def get_translator():
    """获取翻译器实例"""
    return Translator(modelscope_client)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    try:
        # 检查各服务状态
        services_status = {}
        
        # 检查翻译服务
        try:
            await translator_agent._translate_text_func("test", "en", "zh")
            services_status["translator"] = "healthy"
        except Exception as e:
            services_status["translator"] = f"unhealthy: {str(e)}"
        
        # 检查 ModelScope 服务
        try:
            await modelscope_client.list_models()
            services_status["modelscope"] = "healthy"
        except Exception as e:
            services_status["modelscope"] = f"unhealthy: {str(e)}"
        
        # 检查视频处理服务
        try:
            services_status["video_processor"] = "healthy"
        except Exception as e:
            services_status["video_processor"] = f"unhealthy: {str(e)}"
        
        # 检查字幕处理服务
        try:
            services_status["subtitle_processor"] = "healthy"
        except Exception as e:
            services_status["subtitle_processor"] = f"unhealthy: {str(e)}"
        
        # 确定整体状态
        overall_status = "healthy" if all(
            status == "healthy" for status in services_status.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            timestamp=datetime.now(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """获取可用模型列表"""
    try:
        models = await modelscope_client.list_models()
        
        model_infos = []
        for model in models:
            model_infos.append(ModelInfo(
                name=model.get("name", ""),
                description=model.get("description", ""),
                supported_languages=model.get("supported_languages", []),
                capabilities=model.get("capabilities", []),
                version=model.get("version", "1.0.0")
            ))
        
        return model_infos
        
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """文本翻译端点"""
    try:
        start_time = time.time()
        
        # 执行翻译
        result = await translator_agent._translate_text_func(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        # 确保返回的是字典格式
        if isinstance(result, str):
            # 如果返回的是字符串，转换为字典格式
            result_dict = {
                "translated_text": result,
                "source_language": request.source_language,
                "target_language": request.target_language,
                "model_used": "mimo-v2-flash",
                "confidence": 0.95,
                "metadata": {}
            }
        else:
            result_dict = result
            
        processing_time = time.time() - start_time
        
        return TranslationResponse(
            success=True,
            translated_text=result_dict.get("translated_text", ""),
            source_language=result_dict.get("source_language", ""),
            target_language=request.target_language,
            model_used=result_dict.get("model_used", ""),
            processing_time=processing_time,
            confidence=result_dict.get("confidence", 0.0),
            metadata=result_dict.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/translate", response_model=VideoTranslationResponse)
async def translate_video(request: VideoTranslationRequest):
    """视频翻译端点"""
    try:
        start_time = time.time()
        
        # 验证文件存在
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video file not found: {request.video_path}")
        
        # 创建视频处理器
        config_manager = get_config_manager()
        video_processor = VideoProcessor(config_manager.get_video_config())
        
        # 创建 ModelScope 客户端
        modelscope_client = get_modelscope_client()
        
        # 处理视频
        result = await video_processor.process_video(
            video_path=str(video_path),
            model_client=modelscope_client,
            enable_subtitle_extraction=request.enable_subtitle_extraction,
            enable_subtitle_erasure=request.enable_subtitle_erasure
        )
        
        processing_time = time.time() - start_time
        
        return VideoTranslationResponse(
            success=True,
            video_path=result.get("output_video_path", ""),
            extracted_subtitles=result.get("extracted_subtitles", []),
            translated_subtitles=result.get("translated_subtitles", []),
            processing_time=processing_time,
            statistics=result.get("statistics", {}),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Video translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/extract-subtitles", response_model=VideoTranslationResponse)
async def extract_subtitles(request: VideoTranslationRequest):
    """提取视频字幕端点"""
    try:
        start_time = time.time()
        
        # 验证文件存在
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video file not found: {request.video_path}")
        
        # 创建视频处理器
        config_manager = get_config_manager()
        video_processor = VideoProcessor(config_manager.get_video_config())
        
        # 创建 ModelScope 客户端
        modelscope_client = get_modelscope_client()
        
        # 只提取字幕
        result = await video_processor.process_video(
            video_path=str(video_path),
            model_client=modelscope_client,
            enable_subtitle_extraction=True,
            enable_subtitle_erasure=False
        )
        
        processing_time = time.time() - start_time
        
        return VideoTranslationResponse(
            success=True,
            video_path="",
            extracted_subtitles=result.get("extracted_subtitles", []),
            translated_subtitles=[],
            processing_time=processing_time,
            statistics=result.get("statistics", {}),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Subtitle extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/erase-subtitles", response_model=VideoTranslationResponse)
async def erase_subtitles(request: VideoTranslationRequest):
    """擦除视频字幕端点"""
    try:
        start_time = time.time()
        
        # 验证文件存在
        video_path = Path(request.video_path)
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video file not found: {request.video_path}")
        
        # 创建视频处理器
        config_manager = get_config_manager()
        video_processor = VideoProcessor(config_manager.get_video_config())
        
        # 创建 ModelScope 客户端
        modelscope_client = get_modelscope_client()
        
        # 只擦除字幕
        result = await video_processor.process_video(
            video_path=str(video_path),
            model_client=modelscope_client,
            enable_subtitle_extraction=False,
            enable_subtitle_erasure=True
        )
        
        processing_time = time.time() - start_time
        
        return VideoTranslationResponse(
            success=True,
            video_path=result.get("output_video_path", ""),
            extracted_subtitles=[],
            translated_subtitles=[],
            processing_time=processing_time,
            statistics=result.get("statistics", {}),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Subtitle erasure failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subtitle/translate", response_model=SubtitleTranslationResponse)
async def translate_subtitles(request: SubtitleTranslationRequest):
    """字幕翻译端点"""
    try:
        start_time = time.time()
        
        # 验证文件存在
        subtitle_path = Path(request.subtitle_path)
        if not subtitle_path.exists():
            raise HTTPException(status_code=404, detail=f"Subtitle file not found: {request.subtitle_path}")
        
        # 创建字幕处理器
        config_manager = get_config_manager()
        subtitle_processor = SubtitleProcessor(config_manager.get_subtitle_config())
        
        # 创建翻译器
        translator = get_translator()
        
        # 处理字幕
        result = await subtitle_processor.process_srt_file(
            input_path=str(subtitle_path),
            translator=translator,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        processing_time = time.time() - start_time
        
        # 获取统计信息
        stats = subtitle_processor.get_statistics()
        
        return SubtitleTranslationResponse(
            success=True,
            original_subtitle_path=str(subtitle_path),
            translated_subtitle_path=result,
            subtitle_count=stats.get('total_segments', 0),
            processing_time=processing_time,
            errors=[],
            metadata=stats
        )
        
    except Exception as e:
        logger.error(f"Subtitle translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/translate", response_model=VideoTranslationResponse)
async def translate_video(request: VideoTranslationRequest):
    """视频翻译端点"""
    try:
        start_time = time.time()
        
        # 提取帧
        extracted_frames = []
        if request.extract_frames:
            frames = await video_processor.extract_frames(
                video_path=request.video_path
            )
            extracted_frames = frames
        
        # 处理字幕
        translated_subtitles = None
        if request.process_subtitles:
            # 使用正确的函数名 process_srt_file
            subtitle_result = await subtitle_processor.process_srt_file(
                input_path=request.subtitle_path or f"{request.video_path}.srt",
                translator=translator_agent,  # 使用翻译器
                source_lang="en",  # 源语言
                target_lang=request.target_language,
                output_path=request.output_path
            )
            translated_subtitles = subtitle_result
        
        processing_time = time.time() - start_time
        
        return VideoTranslationResponse(
            success=True,
            video_path=request.video_path,
            extracted_frames=extracted_frames,
            translated_subtitles=translated_subtitles,
            processing_time=processing_time,
            frame_count=len(extracted_frames),
            subtitle_count=1 if translated_subtitles else 0,
            errors=[],
            metadata={}
        )
        
    except Exception as e:
        logger.error(f"Video translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subtitle/translate", response_model=SubtitleTranslationResponse)
async def translate_subtitles(request: SubtitleTranslationRequest):
    """字幕翻译端点"""
    try:
        start_time = time.time()
        
        # 翻译字幕
        result = await subtitle_processor.translate_subtitles(
            subtitle_path=request.subtitle_path,
            target_language=request.target_language,
            output_path=request.output_path,
            model_name=request.model_name,
            temperature=request.temperature,
            merge_segments=request.merge_segments
        )
        
        processing_time = time.time() - start_time
        
        return SubtitleTranslationResponse(
            success=True,
            original_subtitle_path=request.subtitle_path,
            translated_subtitle_path=result.get("output_path", ""),
            subtitle_count=result.get("subtitle_count", 0),
            processing_time=processing_time,
            errors=result.get("errors", []),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Subtitle translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """获取支持的语言列表"""
    try:
        # 这里可以从配置或模型中获取支持的语言
        supported_languages = [
            "zh", "en", "ja", "ko", "fr", "de", "es", "it", "ru", "ar",
            "hi", "th", "vi", "pt", "nl", "sv", "da", "no", "fi", "pl"
        ]
        
        return {
            "success": True,
            "languages": supported_languages,
            "source_languages": ["auto"] + supported_languages,
            "target_languages": supported_languages
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_translation_stats():
    """获取翻译统计信息"""
    try:
        # 这里可以从数据库或缓存中获取统计信息
        stats = {
            "total_translations": 0,
            "total_videos_processed": 0,
            "total_subtitles_processed": 0,
            "average_processing_time": 0.0,
            "success_rate": 100.0,
            "popular_languages": ["en", "zh", "ja", "ko"]
        }
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 错误处理 - 移到 middleware.py 中处理