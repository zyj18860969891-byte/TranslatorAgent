"""
API 模块单元测试

测试 API 接口的功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from translator_agent.api.routes import router
from translator_agent.api.schemas import TranslationRequest, TranslationResponse
from translator_agent.core.agent import TranslatorAgent
from translator_agent.core.modelscope_integration import ModelScopeClient
from translator_agent.data.video_processor import VideoProcessor
from translator_agent.data.subtitle_processor import SubtitleProcessor


class TestAPI:
    """API 测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        
        # 模拟依赖
        self.mock_translator_agent = Mock(spec=TranslatorAgent)
        self.mock_modelscope_client = Mock(spec=ModelScopeClient)
        self.mock_video_processor = Mock(spec=VideoProcessor)
        self.mock_subtitle_processor = Mock(spec=SubtitleProcessor)
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查端点"""
        # 模拟翻译服务正常
        self.mock_translator_agent._translate_text_func = AsyncMock(return_value="test")
        
        # 模拟 ModelScope 服务正常
        self.mock_modelscope_client.list_models = AsyncMock(return_value=[
            {"name": "test_model", "description": "Test model"}
        ])
        
        with patch('translator_agent.api.routes.translator_agent', self.mock_translator_agent), \
             patch('translator_agent.api.routes.modelscope_client', self.mock_modelscope_client), \
             patch('translator_agent.api.routes.video_processor', self.mock_video_processor), \
             patch('translator_agent.api.routes.subtitle_processor', self.mock_subtitle_processor):
            
            response = self.client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "1.0.0"
            assert "translator" in data["services"]
            assert "modelscope" in data["services"]
            assert "video_processor" in data["services"]
            assert "subtitle_processor" in data["services"]
    
    @pytest.mark.asyncio
    async def test_get_models(self):
        """测试获取模型列表端点"""
        mock_models = [
            {
                "name": "mimo-v2-flash",
                "description": "Multimodal model for translation",
                "supported_languages": ["en", "zh", "ja"],
                "capabilities": ["translation", "summarization"],
                "version": "1.0.0"
            },
            {
                "name": "llama-3.2-11b-vision",
                "description": "Vision model for translation",
                "supported_languages": ["en", "zh"],
                "capabilities": ["translation", "vision"],
                "version": "1.0.0"
            }
        ]
        
        self.mock_modelscope_client.list_models = AsyncMock(return_value=mock_models)
        
        with patch('translator_agent.api.routes.modelscope_client', self.mock_modelscope_client):
            response = self.client.get("/models")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "mimo-v2-flash"
            assert data[1]["name"] == "llama-3.2-11b-vision"
    
    @pytest.mark.asyncio
    async def test_translate_text(self):
        """测试文本翻译端点"""
        # 模拟翻译结果
        mock_result = {
            "translated_text": "你好，世界！",
            "source_language": "en",
            "model_used": "mimo-v2-flash",
            "confidence": 0.95,
            "processing_time": 1.0,
            "metadata": {}
        }
        
        self.mock_translator_agent._translate_text_func = AsyncMock(return_value=mock_result["translated_text"])
        
        # 创建测试请求
        request_data = {
            "text": "Hello, world!",
            "source_language": "en",
            "target_language": "zh",
            "model_name": "mimo-v2-flash",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        with patch('translator_agent.api.routes.translator_agent', self.mock_translator_agent):
            response = self.client.post("/translate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["translated_text"] == "你好，世界！"
            assert data["source_language"] == "en"
            assert data["target_language"] == "zh"
            assert data["model_used"] == "mimo-v2-flash"
            assert data["confidence"] == 0.95
            assert data["processing_time"] == 1.0
    
    @pytest.mark.asyncio
    async def test_translate_text_validation_error(self):
        """测试文本翻译验证错误"""
        # 缺少必需字段
        request_data = {
            "text": "Hello, world!",
            "source_language": "en"
            # 缺少 target_language
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 422
        
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
    
    @pytest.mark.asyncio
    async def test_translate_text_error(self):
        """测试文本翻译错误处理"""
        # 模拟翻译失败
        self.mock_translator_agent._translate_text_func = AsyncMock(side_effect=Exception("Translation failed"))
        
        request_data = {
            "text": "Hello, world!",
            "source_language": "en",
            "target_language": "zh"
        }
        
        with patch('translator_agent.api.routes.translator_agent', self.mock_translator_agent):
            response = self.client.post("/translate", json=request_data)
            assert response.status_code == 500
            
            data = response.json()
            assert data["success"] is False
            assert data["error_code"] == "HTTP_ERROR"
    
    @pytest.mark.asyncio
    async def test_get_supported_languages(self):
        """测试获取支持的语言列表"""
        response = self.client.get("/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "languages" in data
        assert "source_languages" in data
        assert "target_languages" in data
        assert "zh" in data["languages"]
        assert "en" in data["languages"]
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """测试获取统计信息"""
        response = self.client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        assert "timestamp" in data
        assert "total_translations" in data["stats"]
        assert "total_videos_processed" in data["stats"]
        assert "total_subtitles_processed" in data["stats"]
    
    def test_api_schemas(self):
        """测试 API 数据模型"""
        # 测试翻译请求模型
        request = TranslationRequest(
            text="Hello, world!",
            source_language="en",
            target_language="zh",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert request.text == "Hello, world!"
        assert request.source_language == "en"
        assert request.target_language == "zh"
        assert request.temperature == 0.7
        assert request.max_tokens == 1000
        
        # 测试翻译响应模型
        response = TranslationResponse(
            success=True,
            translated_text="你好，世界！",
            source_language="en",
            target_language="zh",
            model_used="mimo-v2-flash",
            processing_time=1.0,
            confidence=0.95,
            metadata={}
        )
        
        assert response.success is True
        assert response.translated_text == "你好，世界！"
        assert response.source_language == "en"
        assert response.target_language == "zh"
        assert response.model_used == "mimo-v2-flash"
        assert response.processing_time == 1.0
        assert response.confidence == 0.95
        assert response.metadata == {}


class TestAPIIntegration:
    """API 集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_translation_workflow(self):
        """测试完整的翻译工作流"""
        # 模拟完整的翻译流程
        mock_result = {
            "translated_text": "你好，世界！",
            "source_language": "en",
            "model_used": "mimo-v2-flash",
            "confidence": 0.95,
            "processing_time": 1.0,
            "metadata": {}
        }
        
        with patch('translator_agent.api.routes.translator_agent') as mock_translator:
            mock_translator._translate_text_func = AsyncMock(return_value=mock_result["translated_text"])
            
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # 执行翻译
            response = client.post("/translate", json={
                "text": "Hello, world!",
                "source_language": "en",
                "target_language": "zh"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["translated_text"] == "你好，世界！"


if __name__ == "__main__":
    pytest.main([__file__])