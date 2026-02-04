#!/usr/bin/env python3
"""
测试模型匹配逻辑
"""

import requests
import json

# API配置
api_key = 'sk-88bf1bd605544d208c7338cb1989ab3e'
base_url = 'https://dashscope.aliyuncs.com/api/v1'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# 目标模型配置
target_models = [
    "qwen3-omni-flash",
    "qwen3-vision", 
    "qwen3-text"
]

def check_model_availability():
    """检查模型可用性"""
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            available_models = []
            unavailable_models = []
            
            if 'data' in models_data and isinstance(models_data['data'], list):
                models_list = models_data['data']
                print(f"找到 {len(models_list)} 个模型")
                
                for model_id in target_models:
                    model_found = False
                    for model in models_list:
                        available_model_id = model.get('id', '')
                        
                        # 精确匹配
                        if model_id == available_model_id:
                            model_found = True
                            available_models.append(model_id)
                            print(f"✅ 精确匹配: {model_id} -> {available_model_id}")
                            break
                        # 模糊匹配（忽略版本后缀）
                        elif available_model_id.startswith(model_id.split('-')[0] + '-' + model_id.split('-')[1]):
                            model_found = True
                            available_models.append(model_id)
                            print(f"✅ 模糊匹配: {model_id} -> {available_model_id}")
                            break
                    
                    if not model_found:
                        unavailable_models.append(model_id)
                        print(f"❌ 未找到: {model_id}")
            
            print(f"\n结果: {len(available_models)} 个可用, {len(unavailable_models)} 个不可用")
            print(f"可用模型: {available_models}")
            print(f"不可用模型: {unavailable_models}")
            
            return {
                "available": available_models,
                "unavailable": unavailable_models
            }
        else:
            print(f"API请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"异常: {e}")
        return None

if __name__ == "__main__":
    print("测试模型匹配逻辑...")
    result = check_model_availability()