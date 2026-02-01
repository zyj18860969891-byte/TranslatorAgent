#!/usr/bin/env python3
"""
Translator Agent - 核心翻译器模块

基于 NotebookLM 文档驱动开发
文档: OpenManus_架构详解.md, OpenManus Translator Agent Architecture and Deployment Plan

功能:
- 翻译器基类
- 多语言支持
- 翻译引擎接口
- 翻译缓存
- 错误处理
"""

import abc
import asyncio
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Language(Enum):
    """支持的语言枚举"""
    ENGLISH = "en"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    RUSSIAN = "ru"
    PORTUGUESE = "pt"


class TranslationEngine(Enum):
    """翻译引擎枚举"""
    GOOGLE = "google"
    DEEPL = "deepl"
    OPENAI = "openai"
    MODELSCOPE = "modelscope"
    CUSTOM = "custom"


@dataclass
class TranslationRequest:
    """翻译请求数据类"""
    text: str
    source_lang: Language | str  # 支持Language枚举或字符串（如"auto"）
    target_lang: Language | str   # 支持Language枚举或字符串
    engine: TranslationEngine = TranslationEngine.GOOGLE
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TranslationResponse:
    """翻译响应数据类"""
    translated_text: str
    source_lang: Language
    target_lang: Language
    engine: TranslationEngine
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TranslationCache:
    """翻译缓存管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".translator_agent" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "translation_cache.json"
        self.cache: Dict[str, TranslationResponse] = {}
        self._load_cache()
    
    def _load_cache(self):
        """从文件加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        # 将字符串转换回枚举类型
                        if isinstance(value['source_lang'], str):
                            value['source_lang'] = Language(value['source_lang'])
                        if isinstance(value['target_lang'], str):
                            value['target_lang'] = Language(value['target_lang'])
                        if isinstance(value['engine'], str):
                            value['engine'] = TranslationEngine(value['engine'])
                        # 重新创建 TranslationResponse 对象
                        self.cache[key] = TranslationResponse(**value)
                logger.info(f"Loaded {len(self.cache)} entries from cache")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            # 将 TranslationResponse 转换为字典
            cache_dict = {}
            for key, response in self.cache.items():
                response_dict = asdict(response)
                # 转换枚举类型为字符串（如果它们是枚举）
                if hasattr(response_dict['source_lang'], 'value'):
                    response_dict['source_lang'] = response_dict['source_lang'].value
                if hasattr(response_dict['target_lang'], 'value'):
                    response_dict['target_lang'] = response_dict['target_lang'].value
                if hasattr(response_dict['engine'], 'value'):
                    response_dict['engine'] = response_dict['engine'].value
                cache_dict[key] = response_dict
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.cache)} entries to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _generate_key(self, request: TranslationRequest) -> str:
        """生成缓存键"""
        # 处理source_lang和target_lang（可能是Language枚举或字符串）
        source_lang_value = request.source_lang.value if hasattr(request.source_lang, 'value') else str(request.source_lang)
        target_lang_value = request.target_lang.value if hasattr(request.target_lang, 'value') else str(request.target_lang)
        engine_value = request.engine.value if hasattr(request.engine, 'value') else str(request.engine)
        
        key_data = f"{request.text}:{source_lang_value}:{target_lang_value}:{engine_value}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(self, request: TranslationRequest) -> Optional[TranslationResponse]:
        """获取缓存的翻译"""
        key = self._generate_key(request)
        return self.cache.get(key)
    
    def set(self, request: TranslationRequest, response: TranslationResponse):
        """设置缓存"""
        key = self._generate_key(request)
        self.cache[key] = response
        self._save_cache()
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self._save_cache()


class BaseTranslator(abc.ABC):
    """翻译器基类"""
    
    def __init__(self, engine: TranslationEngine, cache_enabled: bool = True):
        self.engine = engine
        self.cache_enabled = cache_enabled
        self.cache = TranslationCache() if cache_enabled else None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abc.abstractmethod
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """异步翻译方法（子类必须实现）"""
        pass
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """同步翻译方法"""
        # 检查缓存
        if self.cache_enabled and self.cache:
            cached = self.cache.get(request)
            if cached:
                self.logger.info("Cache hit")
                return cached
        
        # 执行翻译
        try:
            # 使用 asyncio 运行异步方法
            try:
                loop = asyncio.get_running_loop()
                # 如果已经在事件循环中，创建任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.translate_async(request))
                    response = future.result()
            except RuntimeError:
                # 如果没有事件循环，直接运行
                response = asyncio.run(self.translate_async(request))
            
            # 保存到缓存
            if self.cache_enabled and self.cache and not response.error:
                self.cache.set(request, response)
            
            return response
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            self.logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=request.engine,
                error=error_msg
            )
    
    def translate_batch(self, requests: List[TranslationRequest]) -> List[TranslationResponse]:
        """批量翻译"""
        responses = []
        for request in requests:
            response = self.translate(request)
            responses.append(response)
        return responses
    
    async def translate_batch_async(self, requests: List[TranslationRequest]) -> List[TranslationResponse]:
        """异步批量翻译"""
        tasks = [self.translate_async(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)


class MockTranslator(BaseTranslator):
    """模拟翻译器（用于测试）"""
    
    def __init__(self, cache_enabled: bool = True):
        super().__init__(TranslationEngine.CUSTOM, cache_enabled)
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """模拟翻译"""
        # 模拟延迟
        await asyncio.sleep(0.1)
        
        # 简单的模拟翻译
        if request.target_lang == Language.CHINESE:
            translated_text = f"[翻译] {request.text}"
        else:
            translated_text = f"[translated] {request.text}"
        
        return TranslationResponse(
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            engine=self.engine,
            confidence=0.95,
            metadata={
                "mock": True,
                "original_length": len(request.text),
                "translated_length": len(translated_text)
            }
        )


class TranslatorFactory:
    """翻译器工厂"""
    
    _translators: Dict[TranslationEngine, BaseTranslator] = {}
    
    @classmethod
    def get_translator(cls, engine: TranslationEngine, cache_enabled: bool = True) -> BaseTranslator:
        """获取翻译器实例"""
        if engine not in cls._translators:
            if engine == TranslationEngine.CUSTOM:
                # 优先使用真实API翻译器
                try:
                    from .real_translator import RealQwenTranslator
                    cls._translators[engine] = RealQwenTranslator(cache_enabled)
                    logger.info("使用真实API翻译器 (RealQwenTranslator)")
                except ImportError:
                    try:
                        from .real_translator import RealMimoTranslator
                        cls._translators[engine] = RealMimoTranslator(cache_enabled)
                        logger.info("使用真实API翻译器 (RealMimoTranslator)")
                    except ImportError:
                        cls._translators[engine] = MockTranslator(cache_enabled)
                        logger.warning("使用模拟翻译器，请安装真实API翻译器")
            else:
                # TODO: 实现其他翻译引擎
                raise NotImplementedError(f"Translator for {engine} not implemented yet")
        
        return cls._translators[engine]
    
    @classmethod
    def register_translator(cls, engine: TranslationEngine, translator: BaseTranslator):
        """注册自定义翻译器"""
        cls._translators[engine] = translator


class Translator(BaseTranslator):
    """默认翻译器实现"""
    
    def __init__(self, cache_enabled: bool = True):
        super().__init__(TranslationEngine.CUSTOM, cache_enabled)
    
    def _get_cache_key(self, request: TranslationRequest) -> str:
        """生成缓存键"""
        import hashlib
        # 处理source_lang和target_lang（可能是Language枚举或字符串）
        source_lang_value = request.source_lang.value if hasattr(request.source_lang, 'value') else str(request.source_lang)
        target_lang_value = request.target_lang.value if hasattr(request.target_lang, 'value') else str(request.target_lang)
        engine_value = request.engine.value if hasattr(request.engine, 'value') else str(request.engine)
        
        key_data = f"{request.text}:{source_lang_value}:{target_lang_value}:{engine_value}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """执行翻译"""
        # 检查缓存
        if self.cache_enabled and self.cache:
            cached = self.cache.get(request)
            if cached:
                logger.info(f"Translation cache hit")
                return cached
        
        # 执行翻译
        try:
            # 这里可以集成实际的翻译服务
            translated_text = await self._translate_text(request)
            
            response = TranslationResponse(
                translated_text=translated_text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=self.engine,
                confidence=0.95,
                metadata={
                    "translation_time": asyncio.get_event_loop().time(),
                    "original_length": len(request.text),
                    "translated_length": len(translated_text)
                }
            )
            
            # 缓存结果
            if self.cache_enabled and self.cache:
                self.cache.set(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return TranslationResponse(
                translated_text="",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=self.engine,
                confidence=0.0,
                error=str(e)
            )
    
    async def _translate_text(self, request: TranslationRequest) -> str:
        """实际翻译逻辑"""
        # 处理target_lang（可能是Language枚举或字符串）
        target_lang_value = request.target_lang.value if hasattr(request.target_lang, 'value') else str(request.target_lang)
        
        # 简单的翻译实现
        if request.target_lang == Language.CHINESE or target_lang_value == "zh":
            return f"[翻译] {request.text}"
        elif request.target_lang == Language.ENGLISH or target_lang_value == "en":
            return f"[translated] {request.text}"
        else:
            return f"[{target_lang_value}] {request.text}"


# 使用示例
if __name__ == "__main__":
    # 创建翻译请求
    request = TranslationRequest(
        text="Hello, world!",
        source_lang=Language.ENGLISH,
        target_lang=Language.CHINESE,
        engine=TranslationEngine.CUSTOM
    )
    
    # 获取翻译器
    translator = TranslatorFactory.get_translator(TranslationEngine.CUSTOM)
    
    # 执行翻译
    response = translator.translate(request)
    
    print(f"原文: {request.text}")
    print(f"翻译: {response.translated_text}")
    print(f"引擎: {response.engine}")
    print(f"置信度: {response.confidence}")
    print(f"错误: {response.error}")
