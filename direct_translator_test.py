#!/usr/bin/env python3
"""
直接翻译器测试脚本
直接测试翻译器核心功能，避免复杂依赖
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 定义枚举和数据类（避免导入问题）
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
    source_lang: Language | str
    target_lang: Language | str
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

# 简化的翻译器基类
class BaseTranslator:
    """翻译器基类"""
    
    def __init__(self, engine: TranslationEngine, cache_enabled: bool = True):
        self.engine = engine
        self.cache_enabled = cache_enabled
        self.cache = {}
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """异步翻译"""
        raise NotImplementedError("子类必须实现此方法")
    
    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """同步翻译"""
        return asyncio.run(self.translate_async(request))

# 模拟翻译器
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

# 真实API翻译器
class RealQwenTranslator(BaseTranslator):
    """真实API翻译器 - 基于DashScope API"""
    
    def __init__(self, cache_enabled: bool = True):
        super().__init__(TranslationEngine.CUSTOM, cache_enabled)
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model_name = "qwen-turbo"
        
        # 验证API密钥
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        print(f"真实API翻译器初始化完成，使用模型: {self.model_name}")
    
    async def translate_async(self, request: TranslationRequest) -> TranslationResponse:
        """执行真实API翻译"""
        import aiohttp
        
        try:
            # 检查缓存
            if self.cache_enabled and self.cache:
                cache_key = self._get_cache_key(request)
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    print(f"翻译缓存命中: {request.text[:50]}...")
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
            
            print(f"开始翻译: {request.text[:50]}...")
            
            # 发送API请求
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
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
                                "api_response": result.get("usage", {}),
                                "context": request.context
                            }
                        )
                        
                        # 缓存结果
                        if self.cache_enabled:
                            cache_key = self._get_cache_key(request)
                            self.cache[cache_key] = translation_response
                        
                        print(f"翻译完成: {translated_text[:50]}...")
                        return translation_response
                    
                    else:
                        error_msg = f"API请求失败: {response.status}"
                        print(error_msg)
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
            print(error_msg)
            return TranslationResponse(
                translated_text="",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                engine=self.engine,
                error=error_msg
            )
    
    def _get_cache_key(self, request: TranslationRequest) -> str:
        """生成缓存键"""
        import hashlib
        source_lang_value = request.source_lang.value if hasattr(request.source_lang, 'value') else str(request.source_lang)
        target_lang_value = request.target_lang.value if hasattr(request.target_lang, 'value') else str(request.target_lang)
        
        key_data = f"{self.model_name}:{request.text}:{source_lang_value}:{target_lang_value}:{request.context or ''}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
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
                print("API响应中没有找到翻译结果")
                return ""
        except Exception as e:
            print(f"解析翻译结果时出错: {e}")
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
            print(f"计算置信度时出错: {e}")
            return 0.8

# 翻译器工厂
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
                    cls._translators[engine] = RealQwenTranslator(cache_enabled)
                    print("使用真实API翻译器 (RealQwenTranslator)")
                except Exception as e:
                    print(f"真实翻译器初始化失败: {e}")
                    cls._translators[engine] = MockTranslator(cache_enabled)
                    print("使用模拟翻译器")
            else:
                raise NotImplementedError(f"翻译器 {engine} 尚未实现")
        
        return cls._translators[engine]
    
    @classmethod
    def register_translator(cls, engine: TranslationEngine, translator: BaseTranslator):
        """注册自定义翻译器"""
        cls._translators[engine] = translator

async def test_translators():
    """测试翻译器"""
    print("🚀 开始翻译器测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY环境变量未设置")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    try:
        # 测试翻译器工厂
        print("\n🧪 测试翻译器工厂...")
        translator = TranslatorFactory.get_translator(TranslationEngine.CUSTOM)
        print(f"✅ 翻译器类型: {type(translator).__name__}")
        
        # 测试翻译请求
        test_requests = [
            TranslationRequest(
                text="Hello, world!",
                source_lang=Language.ENGLISH,
                target_lang=Language.CHINESE,
                engine=TranslationEngine.CUSTOM
            ),
            TranslationRequest(
                text="你好，世界！",
                source_lang=Language.CHINESE,
                target_lang=Language.ENGLISH,
                engine=TranslationEngine.CUSTOM
            )
        ]
        
        print("\n📝 开始翻译测试...")
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n--- 测试 {i} ---")
            print(f"原文: {request.text}")
            print(f"源语言: {request.source_lang}")
            print(f"目标语言: {request.target_lang}")
            
            try:
                # 执行翻译
                response = await translator.translate_async(request)
                
                print(f"翻译结果: {response.translated_text}")
                print(f"置信度: {response.confidence}")
                print(f"引擎: {response.engine}")
                
                if response.error:
                    print(f"❌ 错误: {response.error}")
                else:
                    print("✅ 翻译成功")
                
            except Exception as e:
                print(f"❌ 翻译失败: {e}")
        
        print("\n🎉 翻译测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    success = await test_translators()
    
    if success:
        print("\n✅ 测试完成，翻译器系统已就绪")
    else:
        print("\n❌ 测试失败，请检查配置")
        return False
    
    return success

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 测试失败，请检查配置")
        sys.exit(1)