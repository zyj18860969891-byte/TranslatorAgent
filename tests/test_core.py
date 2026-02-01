#!/usr/bin/env python3
"""核心模块测试"""

import pytest
import asyncio
from translator_agent.core.agent import TranslatorAgent
from translator_agent.core.modelscope_integration import ModelScopeClient
from translator_agent.core.translator import (
    Translator, TranslationRequest, Language, TranslationEngine
)


class TestTranslatorAgent:
    """翻译智能体测试类"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """测试智能体初始化"""
        client = ModelScopeClient()
        agent = TranslatorAgent(client, client)
        assert agent is not None
        # 检查 BDI 状态是否正确初始化
        assert agent.bdi is not None
        assert agent.bdi.beliefs is not None
        assert agent.bdi.desires is not None
    
    @pytest.mark.asyncio
    async def test_translate_text_func(self):
        """测试翻译功能"""
        client = ModelScopeClient()
        agent = TranslatorAgent(client, client)
        
        result = await agent._translate_text_func(
            text="Hello, world!",
            source_lang="en",
            target_lang="zh"
        )
        
        assert result is not None
        # 注意：实际返回的是翻译后的文本字符串，不是包含translated_text的字典
        assert isinstance(result, str)


class TestModelScopeClient:
    """ModelScope 客户端测试类"""
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """测试模型列表获取"""
        client = ModelScopeClient()
        models = await client.list_models()
        assert len(models) > 0
        assert any("mimo-v2-flash" in model["name"] for model in models)
    
    @pytest.mark.asyncio
    async def test_get_model_info(self):
        """测试模型信息获取"""
        client = ModelScopeClient()
        model_info = await client.get_model_info("xiaomi/mimo-v2-flash")
        assert model_info["name"] == "xiaomi/mimo-v2-flash"


class TestTranslator:
    """翻译器测试类"""
    
    def test_translator_initialization(self):
        """测试翻译器初始化"""
        translator = Translator()
        assert translator is not None
        assert translator.engine == TranslationEngine.CUSTOM
    
    def test_translation_request(self):
        """测试翻译请求"""
        request = TranslationRequest(
            text="Hello, world!",
            source_lang=Language.ENGLISH,
            target_lang=Language.CHINESE,
            engine=TranslationEngine.CUSTOM
        )
        assert request.text == "Hello, world!"
        assert request.source_lang == Language.ENGLISH
        assert request.target_lang == Language.CHINESE
    
    @pytest.mark.asyncio
    async def test_translate_async(self):
        """测试异步翻译"""
        translator = Translator()
        request = TranslationRequest(
            text="Hello, world!",
            source_lang=Language.ENGLISH,
            target_lang=Language.CHINESE,
            engine=TranslationEngine.CUSTOM
        )
        
        response = await translator.translate_async(request)
        assert response is not None
        assert response.translated_text is not None
        assert response.source_lang == "en"  # 实际返回的是字符串
        assert response.target_lang == "zh"  # 实际返回的是字符串