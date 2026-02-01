#!/usr/bin/env python3
"""
真实API翻译器实现
基于DashScope API的真实翻译服务
"""

import os
import json
import logging
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from .translator import (
    BaseTranslator, 
    TranslationRequest, 
    TranslationResponse, 
    TranslationEngine,
    Language,
    TranslationCache
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealMimoTranslator(BaseTranslator):
    """真实API翻译器 - 基于DashScope API"""
    
    def __init__(self, cache_enabled: bool = True):
        super().__init__(TranslationEngine.CUSTOM, cache_enabled)
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.model_name = "qwen-turbo"
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # 验证API密钥
        if not self.api_key:
            logger.error("DASHSCOPE_API_KEY环境变量未设置")
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        logger.info(f"真实API翻译器初始化完成，使用模型: {self.model_name}")
    
    def _get_cache_key(self, request: TranslationRequest) -> str:
        """生成缓存键"""
        import hashlib
        source_lang_value = request.source_lang.value if hasattr(request.source_lang, 'value') else str(request.source_lang)
        target_lang_value = request.target_lang.value if hasattr(request.target_lang, 'value') else str(request.target_lang)
        
        key_data = f"{self.model_name}:{request.text}:{source_lang_value}:{target_lang_value}:{request.context or ''}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """执行真实API翻译"""
        start_time = time.time()
        
        try:
            # 检查缓存
            if self.cache_enabled and self.cache:
                cache_key = self._get_cache_key(request)
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    logger.info(f"翻译缓存命中: {request.text[:50]}...")
                    return cached_response
            
            # 构建翻译请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建提示词
            source_lang_name = self._get_language_name(request.source_lang)
            target_lang_name = self._get_language_name(request.target_lang)
            
            prompt = self._build_translation_prompt(
                request.text, 
                source_lang_name, 
                target_lang_name,
                request.context
            )
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "parameters": {
                    "max_tokens": 2000,
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 50
                }
            }
            
            logger.info(f"开始翻译: {request.text[:50]}...")
            
            # 发送API请求
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 解析响应
                        translated_text = self._extract_translation_result(result)
                        
                        # 创建响应对象
                        translation_response = TranslationResponse(
                            translated_text=translated_text,
                            source_lang=request.source_lang,
                            target_lang=request.target_lang,
                            engine=self.engine,
                            confidence=self._calculate_confidence(result),
                            metadata={
                                "model": self.model_name,
                                "processing_time": time.time() - start_time,
                                "api_response": result.get("usage", {}),
                                "context": request.context
                            }
                        )
                        
                        # 缓存结果
                        if self.cache_enabled:
                            cache_key = self._get_cache_key(request)
                            self.cache[cache_key] = translation_response
                        
                        logger.info(f"翻译完成: {translated_text[:50]}...")
                        return translation_response
                    
                    else:
                        error_msg = f"API请求失败: {response.status}"
                        logger.error(error_msg)
                        return TranslationResponse(
                            translated_text="",
                            source_lang=request.source_lang,
                            target_lang=request.target_lang,
                            engine=self.engine,
                            error=error_msg,
                            metadata={
                                "api_error": await response.text(),
                                "status_code": response.status
                            }
                        )
        
        except Exception as e:
            error_msg = f"翻译过程中发生错误: {str(e)}"
            logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=self.engine,
                error=error_msg
            )
    
    def _get_language_name(self, lang: Language | str) -> str:
        """获取语言名称"""
        if isinstance(lang, Language):
            return lang.name.lower()
        elif lang == "auto":
            return "auto"
        else:
            return lang.lower()
    
    def _build_translation_prompt(self, text: str, source_lang: str, target_lang: str, context: str = None) -> str:
        """构建翻译提示词"""
        prompt = f"""请将以下文本从{source_lang}翻译为{target_lang}。

文本：{text}

"""
        
        if context:
            prompt += f"上下文：{context}\n\n"
        
        prompt += """翻译要求：
1. 保持原文的语义和情感
2. 确保翻译自然流畅
3. 如果是专业术语，请保持准确性
4. 如果有文化差异，请适当调整

翻译结果："""
        
        return prompt
    
    def _extract_translation_result(self, result: Dict[str, Any]) -> str:
        """从API响应中提取翻译结果"""
        try:
            choices = result.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                return content.strip()
            else:
                logger.warning("API响应中没有找到翻译结果")
                return ""
        except Exception as e:
            logger.error(f"解析翻译结果时出错: {e}")
            return ""
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """计算翻译置信度"""
        try:
            usage = result.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)
            
            # 基于token使用情况计算置信度
            if completion_tokens > 0 and prompt_tokens > 0:
                # 简单的置信度计算
                confidence = min(1.0, completion_tokens / (prompt_tokens + completion_tokens))
                return round(confidence, 2)
            else:
                return 0.8  # 默认置信度
        except Exception as e:
            logger.warning(f"计算置信度时出错: {e}")
            return 0.8


class RealQwenTranslator(BaseTranslator):
    """真实API翻译器 - 基于Qwen模型"""
    
    def __init__(self, cache_enabled: bool = True):
        super().__init__(TranslationEngine.CUSTOM, cache_enabled)
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model_name = "qwen-turbo"
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # 验证API密钥
        if not self.api_key:
            logger.error("DASHSCOPE_API_KEY环境变量未设置")
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        logger.info(f"真实API翻译器初始化完成，使用模型: {self.model_name}")
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """执行真实API翻译"""
        start_time = time.time()
        
        try:
            # 检查缓存
            if self.cache_enabled and self.cache:
                cache_key = self._get_cache_key(request)
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    logger.info(f"翻译缓存命中: {request.text[:50]}...")
                    return cached_response
            
            # 构建翻译请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建提示词
            source_lang_name = self._get_language_name(request.source_lang)
            target_lang_name = self._get_language_name(request.target_lang)
            
            prompt = self._build_translation_prompt(
                request.text, 
                source_lang_name, 
                target_lang_name,
                request.context
            )
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "parameters": {
                    "max_tokens": 2000,
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 50
                }
            }
            
            logger.info(f"开始翻译: {request.text[:50]}...")
            
            # 发送API请求
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 解析响应
                        translated_text = self._extract_translation_result(result)
                        
                        # 创建响应对象
                        translation_response = TranslationResponse(
                            translated_text=translated_text,
                            source_lang=request.source_lang,
                            target_lang=request.target_lang,
                            engine=self.engine,
                            confidence=self._calculate_confidence(result),
                            metadata={
                                "model": self.model_name,
                                "processing_time": time.time() - start_time,
                                "api_response": result.get("usage", {}),
                                "context": request.context
                            }
                        )
                        
                        # 缓存结果
                        if self.cache_enabled:
                            cache_key = self._get_cache_key(request)
                            self.cache[cache_key] = translation_response
                        
                        logger.info(f"翻译完成: {translated_text[:50]}...")
                        return translation_response
                    
                    else:
                        error_msg = f"API请求失败: {response.status}"
                        logger.error(error_msg)
                        return TranslationResponse(
                            translated_text="",
                            source_lang=request.source_lang,
                            target_lang=request.target_lang,
                            engine=self.engine,
                            error=error_msg,
                            metadata={
                                "api_error": await response.text(),
                                "status_code": response.status
                            }
                        )
        
        except Exception as e:
            error_msg = f"翻译过程中发生错误: {str(e)}"
            logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=self.engine,
                error=error_msg
            )
    
    def _get_language_name(self, lang: Language | str) -> str:
        """获取语言名称"""
        if isinstance(lang, Language):
            return lang.name.lower()
        elif lang == "auto":
            return "auto"
        else:
            return lang.lower()
    
    def _build_translation_prompt(self, text: str, source_lang: str, target_lang: str, context: str = None) -> str:
        """构建翻译提示词"""
        prompt = f"""请将以下文本从{source_lang}翻译为{target_lang}。

文本：{text}

"""
        
        if context:
            prompt += f"上下文：{context}\n\n"
        
        prompt += """翻译要求：
1. 保持原文的语义和情感
2. 确保翻译自然流畅
3. 如果是专业术语，请保持准确性
4. 如果有文化差异，请适当调整

翻译结果："""
        
        return prompt
    
    def _extract_translation_result(self, result: Dict[str, Any]) -> str:
        """从API响应中提取翻译结果"""
        try:
            choices = result.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                return content.strip()
            else:
                logger.warning("API响应中没有找到翻译结果")
                return ""
        except Exception as e:
            logger.error(f"解析翻译结果时出错: {e}")
            return ""
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """计算翻译置信度"""
        try:
            usage = result.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)
            
            # 基于token使用情况计算置信度
            if completion_tokens > 0 and prompt_tokens > 0:
                # 简单的置信度计算
                confidence = min(1.0, completion_tokens / (prompt_tokens + completion_tokens))
                return round(confidence, 2)
            else:
                return 0.8  # 默认置信度
        except Exception as e:
            logger.warning(f"计算置信度时出错: {e}")
            return 0.8