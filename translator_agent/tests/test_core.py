"""
核心模块单元测试

测试翻译器和 ModelScope 集成功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from translator_agent.core.agent import TranslatorAgent
from translator_agent.core.modelscope_integration import ModelScopeClient


class TestTranslator:
    """翻译器测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.translator = TranslatorAgent(None, None)
    
    @pytest.mark.asyncio
    async def test_translate_basic(self):
        """测试基本翻译功能"""
        with patch.object(self.translator, '_call_model') as mock_call:
            mock_call.return_value = {
                "translated_text": "你好，世界！",
                "source_language": "en",
                "confidence": 0.95,
                "processing_time": 1.0
            }
            
            result = await self.translator._translate_text_func(
                text="Hello, world!",
                source_lang="en",
                target_lang="zh"
            )
            
            assert result["translated_text"] == "你好，世界！"
            assert result["source_language"] == "en"
            assert result["confidence"] == 0.95
            assert result["processing_time"] == 1.0
            assert result["model_used"] == "mimo-v2-flash"
    
    @pytest.mark.asyncio
    async def test_translate_auto_detect(self):
        """测试自动语言检测"""
        with patch.object(self.translator, '_call_model') as mock_call:
            mock_call.return_value = {
                "translated_text": "Hello, world!",
                "source_language": "zh",
                "confidence": 0.95,
                "processing_time": 1.0
            }
            
            result = await self.translator._translate_text_func(
                text="你好，世界！",
                source_lang="auto",
                target_lang="en"
            )
            
            assert result["translated_text"] == "Hello, world!"
            assert result["source_language"] == "zh"
    
    @pytest.mark.asyncio
    async def test_translate_error_handling(self):
        """测试翻译错误处理"""
        with patch.object(self.translator, '_call_model') as mock_call:
            mock_call.side_effect = Exception("Translation failed")
            
            with pytest.raises(Exception) as exc_info:
                await self.translator._translate_text_func(
                    text="Hello, world!",
                    source_lang="en",
                    target_lang="zh"
                )
            
            assert str(exc_info.value) == "Translation failed"
    
    @pytest.mark.asyncio
    async def test_translate_with_temperature(self):
        """测试温度参数"""
        with patch.object(self.translator, '_call_model') as mock_call:
            mock_call.return_value = {
                "translated_text": "你好，世界！",
                "source_language": "en",
                "confidence": 0.95,
                "processing_time": 1.0
            }
            
            result = await self.translator._translate_text_func(
                text="Hello, world!",
                source_lang="en",
                target_lang="zh"
            )
            
            # 验证参数传递
            mock_call.assert_called_once()
            call_args = mock_call.call_args
            assert call_args[1]['temperature'] == 0.3


class TestModelScopeClient:
    """ModelScope 客户端测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.client = ModelScopeClient()
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """测试获取模型列表"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = Mock()
            mock_get.return_value.json.return_value = [
                {
                    "name": "mimo-v2-flash",
                    "description": "Multimodal model for translation",
                    "supported_languages": ["en", "zh", "ja"],
                    "capabilities": ["translation", "summarization"]
                },
                {
                    "name": "llama-3.2-11b-vision",
                    "description": "Vision model for translation",
                    "supported_languages": ["en", "zh"],
                    "capabilities": ["translation", "vision"]
                }
            ]
            
            models = await self.client.list_models()
            
            assert len(models) == 2
            assert models[0]["name"] == "mimo-v2-flash"
            assert models[1]["name"] == "llama-3.2-11b-vision"
    
    @pytest.mark.asyncio
    async def test_call_model(self):
        """测试调用模型"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.json.return_value = {
                "generated_text": "你好，世界！",
                "confidence": 0.95
            }
            
            result = await self.client.call_model(
                model_name="mimo-v2-flash",
                prompt="Translate: Hello, world!",
                temperature=0.7
            )
            
            assert result["generated_text"] == "你好，世界！"
            assert result["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_call_model_error(self):
        """测试模型调用错误"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("API call failed")
            
            with pytest.raises(Exception) as exc_info:
                await self.client.call_model(
                    model_name="mimo-v2-flash",
                    prompt="Translate: Hello, world!"
                )
            
            assert str(exc_info.value) == "API call failed"
    
    @pytest.mark.asyncio
    async def test_get_model_info(self):
        """测试获取模型信息"""
        with patch.object(self.client, 'list_models') as mock_list:
            mock_list.return_value = [
                {
                    "name": "mimo-v2-flash",
                    "description": "Multimodal model for translation",
                    "supported_languages": ["en", "zh", "ja"],
                    "capabilities": ["translation", "summarization"]
                }
            ]
            
            model_info = await self.client.get_model_info("mimo-v2-flash")
            
            assert model_info["name"] == "mimo-v2-flash"
            assert model_info["description"] == "Multimodal model for translation"
            assert "en" in model_info["supported_languages"]
            assert "zh" in model_info["supported_languages"]
            assert "ja" in model_info["supported_languages"]
            assert "translation" in model_info["capabilities"]
            assert "summarization" in model_info["capabilities"]
    
    @pytest.mark.asyncio
    async def test_get_model_info_not_found(self):
        """测试获取不存在的模型信息"""
        with patch.object(self.client, 'list_models') as mock_list:
            mock_list.return_value = []
            
            model_info = await self.client.get_model_info("nonexistent-model")
            
            assert model_info is None


class TestTranslatorIntegration:
    """翻译器集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_translation_workflow(self):
        """测试完整的翻译工作流"""
        translator = TranslatorAgent(None, None)
        
        with patch.object(translator, '_call_model') as mock_call:
            mock_call.return_value = {
                "translated_text": "你好，世界！",
                "source_language": "en",
                "confidence": 0.95,
                "processing_time": 1.0
            }
            
            # 执行翻译
            result = await translator._translate_text_func(
                text="Hello, world!",
                source_lang="en",
                target_lang="zh"
            )
            
            # 验证结果
            assert result["success"] is True
            assert result["translated_text"] == "你好，世界！"
            assert result["source_language"] == "en"
            assert result["target_language"] == "zh"
            assert result["model_used"] == "mimo-v2-flash"
            assert result["confidence"] == 0.95
            assert result["processing_time"] == 1.0
    
    @pytest.mark.asyncio
    async def test_multiple_translations(self):
        """测试多次翻译"""
        translator = TranslatorAgent(None, None)
        
        with patch.object(translator, '_call_model') as mock_call:
            mock_call.return_value = {
                "translated_text": "你好",
                "source_language": "en",
                "confidence": 0.95,
                "processing_time": 1.0
            }
            
            # 执行多次翻译
            results = []
            for text in ["Hello", "Hi", "Hey"]:
                result = await translator._translate_text_func(
                    text=text,
                    source_lang="en",
                    target_lang="zh"
                )
                results.append(result)
            
            # 验证结果
            assert len(results) == 3
            for result in results:
                assert result["success"] is True
                assert result["translated_text"] in ["你好", "嗨", "嘿"]
                assert result["source_language"] == "en"
                assert result["target_language"] == "zh"


if __name__ == "__main__":
    pytest.main([__file__])