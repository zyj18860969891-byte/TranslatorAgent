#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的模型可用性检查
正确解析API响应格式
"""

import os
import sys
import json
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_model_availability_fixed():
    """
    修复后的模型可用性检查函数
    正确解析不同格式的API响应
    """
    print("🔍 使用修复后的逻辑检查模型可用性...")
    print("=" * 60)
    
    try:
        import requests
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return {
                "available": [],
                "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                "error": "未配置DASHSCOPE_API_KEY"
            }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 使用正确的端点
        base_url = "https://dashscope.aliyuncs.com"
        endpoint = f"{base_url}/compatible-mode/v1/models"
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = []
                unavailable_models = []
                
                # 检查API响应格式
                if 'data' in models_data and isinstance(models_data['data'], list):
                    # OpenAI兼容模式格式
                    models_list = models_data['data']
                    print(f"📊 找到 {len(models_list)} 个模型 (OpenAI兼容格式)")
                    
                    target_models = [
                        "qwen3-omni-flash-realtime",
                        "qwen3-vl-rerank",
                        "qwen3-embedding"
                    ]
                    
                    for target_model in target_models:
                        model_found = False
                        for model in models_list:
                            model_id = model.get('id', '')
                            if target_model in model_id:
                                model_found = True
                                available_models.append(target_model)
                                print(f"  ✅ {target_model} - 可用")
                                break
                        
                        if not model_found:
                            unavailable_models.append(target_model)
                            print(f"  ❌ {target_model} - 不可用")
                            
                elif 'models' in models_data and isinstance(models_data['models'], list):
                    # 原始格式
                    models_list = models_data['models']
                    print(f"📊 找到 {len(models_list)} 个模型 (原始格式)")
                    
                    target_models = [
                        "qwen3-omni-flash-realtime",
                        "qwen3-vl-rerank",
                        "qwen3-embedding"
                    ]
                    
                    for target_model in target_models:
                        model_found = False
                        for model in models_list:
                            model_id = model.get('model', '')
                            if target_model in model_id:
                                model_found = True
                                available_models.append(target_model)
                                print(f"  ✅ {target_model} - 可用")
                                break
                        
                        if not model_found:
                            unavailable_models.append(target_model)
                            print(f"  ❌ {target_model} - 不可用")
                else:
                    print(f"⚠️ 未知响应格式: {models_data.keys()}")
                    # 显示实际可用的模型
                    print("🔍 实际可用的模型:")
                    test_models = ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-vl-plus"]
                    for test_model in test_models:
                        try:
                            test_response = requests.post(
                                f"{base_url}/compatible-mode/v1/chat/completions",
                                headers=headers,
                                json={
                                    "model": test_model,
                                    "messages": [{"role": "user", "content": "test"}],
                                    "max_tokens": 5
                                },
                                timeout=5
                            )
                            if test_response.status_code == 200:
                                available_models.append(test_model)
                                print(f"  ✅ {test_model} - 可用")
                            else:
                                unavailable_models.append(test_model)
                                print(f"  ❌ {test_model} - 不可用")
                        except:
                            unavailable_models.append(test_model)
                            print(f"  ❌ {test_model} - 检查失败")
                
                return {
                    "available": available_models,
                    "unavailable": unavailable_models,
                    "total_models": len(available_models) + len(unavailable_models)
                }
            else:
                return {
                    "available": [],
                    "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                    "error": f"API请求失败: {response.status_code}"
                }
                
        except requests.RequestException as e:
            return {
                "available": [],
                "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                "error": f"网络请求失败: {str(e)}"
            }
        
    except Exception as e:
        return {
            "available": [],
            "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
            "error": f"检查模型可用性失败: {str(e)}"
        }

def check_actual_available_models():
    """检查实际可用的模型"""
    print("\n" + "=" * 60)
    print("🔍 检查实际可用的模型...")
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置API密钥")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试实际使用的模型
    models_to_test = [
        ("qwen-turbo", "通用翻译模型"),
        ("qwen-plus", "增强翻译模型"),
        ("qwen-max", "高性能翻译模型"),
        ("qwen-vl-plus", "视觉语言模型"),
        ("iic/emotion2vec_plus_large", "情感分析模型"),
        ("wanx2.1-vace-plus", "视频编辑模型"),
        ("image-erase-completion", "图像编辑模型")
    ]
    
    available_models = []
    
    for model_name, description in models_to_test:
        print(f"\n🔍 测试模型: {model_name} ({description})")
        try:
            # 根据模型类型选择不同的测试方法
            if "chat" in model_name.lower() or model_name in ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-vl-plus"]:
                # 聊天模型测试
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    },
                    timeout=10
                )
            elif "emotion" in model_name.lower():
                # 情感分析模型测试
                response = requests.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/inference/text-to-vector",
                    headers=headers,
                    json={
                        "model": model_name,
                        "input": {"text": "测试情感分析"}
                    },
                    timeout=10
                )
            elif "video" in model_name.lower() or "image" in model_name.lower():
                # 视频/图像编辑模型测试
                response = requests.post(
                    f"https://dashscope.aliyuncs.com/api/v1/services/{'video-editing' if 'video' in model_name.lower() else 'image-editing'}/{model_name}",
                    headers=headers,
                    json={
                        "model": model_name,
                        "input": {"prompt": "test"}
                    },
                    timeout=10
                )
            else:
                # 其他模型测试
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                available_models.append(model_name)
                print(f"  ✅ 模型可用")
            else:
                print(f"  ❌ 模型不可用 - {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
    
    print(f"\n📊 实际可用模型总结:")
    print(f"  可用模型数量: {len(available_models)}")
    print(f"  可用模型列表: {available_models}")

if __name__ == "__main__":
    print("🚀 开始修复后的模型可用性检查")
    print("=" * 60)
    
    # 测试修复后的逻辑
    result = check_model_availability_fixed()
    print(f"\n📊 修复后的检查结果:")
    print(f"  可用模型: {result.get('available', [])}")
    print(f"  不可用模型: {result.get('unavailable', [])}")
    print(f"  总模型数: {result.get('total_models', 0)}")
    print(f"  错误信息: {result.get('error', '无')}")
    
    check_actual_available_models()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成")