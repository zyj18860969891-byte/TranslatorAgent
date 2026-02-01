#!/usr/bin/env python3
"""
翻译API路由

提供文本翻译相关的REST API接口
"""

import asyncio
import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ...core.translator import TranslatorFactory, TranslationEngine, Language
from ..schemas import (
    TranslationRequest,
    TranslationResponse,
    ErrorResponse,
    ModelInfo
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/translation", tags=["translation"])

# 全局翻译器实例
_translator = None


def get_translator():
    """获取翻译器实例"""
    global _translator
    if _translator is None:
        _translator = TranslatorFactory.get_translator(TranslationEngine.CUSTOM)
    return _translator


@router.get("/health", response_model=dict)
async def health_check():
    """翻译服务健康检查"""
    return {
        "status": "healthy",
        "service": "translation",
        "timestamp": time.time()
    }


@router.get("/models", response_model=list[ModelInfo])
async def list_models():
    """获取可用的翻译模型列表"""
    try:
        models = [
            ModelInfo(
                name="mimo-v2-flash",
                description="小米MIMO V2 Flash翻译模型",
                supported_languages=["en", "zh", "ja", "ko", "fr", "de", "es", "it", "ru", "ar"],
                capabilities=["translation", "context_aware"],
                version="2.0.0"
            ),
            ModelInfo(
                name="mimo-v2-pro",
                description="小米MIMO V2 Pro翻译模型",
                supported_languages=["en", "zh", "ja", "ko", "fr", "de", "es", "it", "ru", "ar", "pt", "nl"],
                capabilities=["translation", "context_aware", "formal_style"],
                version="2.0.0"
            )
        ]
        return models
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {e}")


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """翻译文本"""
    start_time = time.time()
    
    try:
        # 获取翻译器
        translator = get_translator()
        
        # 检测源语言
        source_lang = request.source_language
        if source_lang == "auto":
            # 使用NLP处理器检测语言
            from ...nlp.processor import TextProcessor
            nlp_processor = TextProcessor()
            detected_lang = nlp_processor.detect_language(request.text)
            source_lang = detected_lang.value if detected_lang else "en"
            logger.info(f"Detected source language: {source_lang}")
        
        # 创建翻译请求
        from ...core.translator import TranslationRequest as CoreTranslationRequest, Language
        from ...core.translator import TranslationEngine
        
        core_request = CoreTranslationRequest(
            text=request.text,
            source_lang=Language(source_lang),
            target_lang=Language(request.target_language),
            engine=TranslationEngine.CUSTOM,
            metadata={
                "model_name": request.model_name,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        )
        
        # 执行翻译
        translation_response = await translator.translate_async(core_request)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 构建响应
        response = TranslationResponse(
            success=True,
            translated_text=translation_response.translated_text,
            source_language=source_lang,
            target_language=request.target_language,
            model_used=translation_response.engine.value if hasattr(translation_response.engine, 'value') else str(translation_response.engine),
            processing_time=processing_time,
            confidence=translation_response.confidence,
            metadata=translation_response.metadata
        )
        
        logger.info(f"Translation completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        processing_time = time.time() - start_time
        
        error_response = ErrorResponse(
            success=False,
            error_code="TRANSLATION_FAILED",
            error_message=str(e),
            details={"text": request.text[:100]},
            timestamp=datetime.now()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@router.post("/translate/batch", response_model=list[TranslationResponse])
async def translate_batch(requests: list[TranslationRequest]):
    """批量翻译文本"""
    start_time = time.time()
    results = []
    
    try:
        translator = get_translator()
        
        for req in requests:
            try:
                # 检测源语言
                source_lang = req.source_language
                if source_lang == "auto":
                    from ...nlp.processor import NLPProcessor
                    nlp_processor = NLPProcessor()
                    detected_lang = nlp_processor.detect_language(req.text)
                    source_lang = detected_lang.value if detected_lang else "en"
                
                # 执行翻译
                translation_response = await translator.translate_async(
                    text=req.text,
                    source_lang=source_lang,
                    target_lang=req.target_language,
                    model_name=req.model_name,
                    temperature=req.temperature,
                    max_tokens=req.max_tokens
                )
                
                # 构建响应
                response = TranslationResponse(
                    success=True,
                    translated_text=translation_response.translated_text,
                    source_language=source_lang,
                    target_language=req.target_language,
                    model_used=translation_response.model_used,
                    processing_time=time.time() - start_time,
                    confidence=translation_response.confidence,
                    metadata=translation_response.metadata
                )
                
                results.append(response)
                
            except Exception as e:
                logger.error(f"Batch translation failed for request {req.text[:50]}: {e}")
                error_response = ErrorResponse(
                    success=False,
                    error_code="TRANSLATION_FAILED",
                    error_message=str(e),
                    details={"text": req.text[:100]},
                    timestamp=time.time()
                )
                results.append(error_response)
        
        logger.info(f"Batch translation completed: {len(results)} items in {time.time() - start_time:.2f}s")
        return results
        
    except Exception as e:
        logger.error(f"Batch translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {e}")


@router.get("/languages", response_model=dict)
async def get_supported_languages():
    """获取支持的语言列表"""
    try:
        languages = {
            "en": "English",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "ru": "Russian",
            "ar": "Arabic",
            "pt": "Portuguese",
            "nl": "Dutch"
        }
        return languages
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {e}")


@router.get("/detect", response_model=dict)
async def detect_language(text: str = Query(..., description="要检测语言的文本")):
    """检测文本语言"""
    try:
        from ...nlp.processor import NLPProcessor
        nlp_processor = NLPProcessor()
        
        detected_lang = nlp_processor.detect_language(text)
        
        if detected_lang:
            return {
                "language": detected_lang.value,
                "confidence": 1.0,
                "text": text[:100]
            }
        else:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "text": text[:100]
            }
            
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {e}")
