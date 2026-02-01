#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细API响应分析
用于分析为什么模型列表为空
"""

import os
import sys
import json
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_api_response():
    """详细分析API响应"""
    print("🔍 开始详细API响应分析...")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置DASHSCOPE_API_KEY环境变量")
        return
    
    print(f"✅ API密钥已设置: {api_key[:20]}...")
    
    # 测试不同的API端点
    endpoints = [
        "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
        "https://dashscope.aliyuncs.com/api/v1/models",
        "https://dashscope.aliyuncs.com/v1/models"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint}")
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  响应类型: {type(data)}")
                    print(f"  响应键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                    
                    if isinstance(data, dict) and 'models' in data:
                        models = data['models']
                        print(f"  模型数量: {len(models)}")
                        
                        if models:
                            print("  前3个模型:")
                            for i, model in enumerate(models[:3]):
                                print(f"    {i+1}. {model}")
                        else:
                            print("  ⚠️ 模型列表为空")
                            
                            # 检查响应的其他内容
                            for key, value in data.items():
                                if key != 'models':
                                    print(f"  {key}: {value}")
                    
                except json.JSONDecodeError as e:
                    print(f"  JSON解析失败: {e}")
                    print(f"  响应内容: {response.text[:500]}")
                    
            else:
                print(f"  ❌ 请求失败")
                print(f"  响应内容: {response.text[:500]}")
                
        except requests.RequestException as e:
            print(f"  ❌ 网络请求失败: {str(e)}")
        except Exception as e:
            print(f"  ❌ 其他错误: {str(e)}")

def check_specific_models():
    """检查特定模型是否存在"""
    print("\n" + "=" * 60)
    print("🔍 检查特定模型...")
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置API密钥")
        return
    
    # 检查实际可用的模型
    models_to_check = [
        "qwen-turbo",
        "qwen-plus", 
        "qwen-max",
        "qwen-vl-plus",
        "qwen-audio-turbo",
        "wanx2.1-vace-plus",
        "image-erase-completion",
        "iic/emotion2vec_plus_large"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for model in models_to_check:
        print(f"\n🔍 检查模型: {model}")
        try:
            # 尝试直接调用模型
            test_data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Hello, test connection"}
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 模型可用")
            else:
                print(f"  ❌ 模型不可用 - {response.text[:100]}")
                
        except Exception as e:
            print(f"  ❌ 检查失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始详细API响应分析")
    print("=" * 60)
    
    analyze_api_response()
    check_specific_models()
    
    print("\n" + "=" * 60)
    print("🎉 分析完成")