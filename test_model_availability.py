#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型可用性检查测试
用于准确定位"3个不可用"的具体原因
"""

import os
import sys
import json
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_model_availability():
    """测试模型可用性检查逻辑"""
    print("🔍 开始模型可用性检查测试...")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置DASHSCOPE_API_KEY环境变量")
        return
    
    print(f"✅ API密钥已设置: {api_key[:20]}...")
    
    # 设置API端点
    base_url = "https://dashscope.aliyuncs.com"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 检查基础连接
    print("\n📡 测试基础API连接...")
    try:
        response = requests.get(f"{base_url}/compatible-mode/v1/models", headers=headers, timeout=10)
        print(f"📊 API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            models_data = response.json()
            print(f"📋 返回的模型总数: {len(models_data.get('models', []))}")
            
            # 显示前10个模型
            models = models_data.get('models', [])
            print("\n🔍 前10个可用模型:")
            for i, model in enumerate(models[:10]):
                model_id = model.get('model', '')
                model_name = model.get('name', '')
                print(f"  {i+1}. {model_id} - {model_name}")
            
            # 检查目标模型
            target_models = [
                "qwen3-omni-flash-realtime",
                "qwen3-vl-rerank", 
                "qwen3-embedding"
            ]
            
            print(f"\n🎯 检查目标模型:")
            available_models = []
            unavailable_models = []
            
            for target_model in target_models:
                model_found = False
                for model in models:
                    if target_model in model.get('model', ''):
                        model_found = True
                        available_models.append(target_model)
                        print(f"  ✅ {target_model} - 可用")
                        break
                
                if not model_found:
                    unavailable_models.append(target_model)
                    print(f"  ❌ {target_model} - 不可用")
            
            print(f"\n📊 模型可用性总结:")
            print(f"  可用模型: {len(available_models)} 个")
            print(f"  不可用模型: {len(unavailable_models)} 个")
            print(f"  不可用模型列表: {unavailable_models}")
            
            # 检查是否有类似模型
            print(f"\n🔍 搜索类似模型:")
            similar_models = []
            for model in models:
                model_id = model.get('model', '')
                if any(keyword in model_id.lower() for keyword in ['qwen', 'omni', 'flash', 'embedding']):
                    similar_models.append(model_id)
            
            print(f"  找到 {len(similar_models)} 个相关模型:")
            for model in similar_models[:10]:
                print(f"    - {model}")
                
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {str(e)}")
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")

def check_qwen3_integration_logic():
    """检查qwen3_integration模块的逻辑"""
    print("\n" + "=" * 60)
    print("🔍 检查qwen3_integration模块逻辑...")
    
    try:
        # 尝试导入qwen3_integration模块
        sys.path.append('.')
        from qwen3_integration.config import check_model_availability
        
        print("✅ 成功导入check_model_availability函数")
        
        # 调用函数
        result = check_model_availability()
        print(f"\n📊 qwen3_integration检查结果:")
        print(f"  可用模型: {result.get('available', [])}")
        print(f"  不可用模型: {result.get('unavailable', [])}")
        print(f"  总模型数: {result.get('total_models', 0)}")
        print(f"  错误信息: {result.get('error', '无')}")
        
    except Exception as e:
        print(f"❌ 导入或调用失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始模型可用性检查测试")
    print("=" * 60)
    
    test_model_availability()
    check_qwen3_integration_logic()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成")