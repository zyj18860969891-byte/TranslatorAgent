#!/usr/bin/env python3
"""API 模块测试"""

import pytest
from fastapi.testclient import TestClient
from translator_agent.api.main import app
from translator_agent.api.schemas import TranslationRequest

client = TestClient(app)


class TestAPI:
    """API 测试类"""
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Translator Agent API" in response.json()["message"]
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_translation_request_schema(self):
        """测试翻译请求模式"""
        request = TranslationRequest(
            text="Hello, world!",
            source_language="en",
            target_language="zh"
        )
        assert request.text == "Hello, world!"
        assert request.source_language == "en"
        assert request.target_language == "zh"
    
    def test_translate_endpoint(self):
        """测试翻译端点"""
        response = client.post(
            "/api/v1/translate",
            json={
                "text": "Hello, world!",
                "source_language": "en",
                "target_language": "zh"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "translated_text" in result
        assert "source_language" in result
        assert "target_language" in result