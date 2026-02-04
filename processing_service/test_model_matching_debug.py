#!/usr/bin/env python3
"""
测试模型匹配逻辑
"""

import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
            
            # 提取模型列表
            models_list = []
            if 'output' in models_data and 'models' in models_data['output']:
                models_list = models_data['output']['models']
                logger.info(f"检测到DashScope API格式，找到 {len(models_list)} 个模型")
            elif 'data' in models_data and isinstance(models_data['data'], list):
                models_list = models_data['data']
                logger.info(f"检测到OpenAI兼容格式，找到 {len(models_list)} 个模型")
            elif 'models' in models_data and isinstance(models_data['models'], list):
                models_list = models_data['models']
                logger.info(f"检测到原始格式，找到 {len(models_list)} 个模型")
            else:
                logger.warning(f"未知的API响应格式: {list(models_data.keys())}")
                return None
            
            # 打印前几个模型用于调试
            logger.info("前5个模型:")
            for i, model in enumerate(models_list[:5]):
                model_id = model.get('model', model.get('id', ''))
                logger.info(f"  {i}: {model_id}")
            
            # 检查每个目标模型
            for model_id in target_models:
                model_found = False
                
                # 首先尝试精确匹配
                for model in models_list:
                    available_model_id = model.get('model', model.get('id', ''))
                    if model_id == available_model_id:
                        model_found = True
                        available_models.append(model_id)
                        logger.info(f"模型精确匹配成功: {model_id}")
                        break
                
                # 如果没有精确匹配，尝试模糊匹配
                if not model_found:
                    for model in models_list:
                        available_model_id = model.get('model', model.get('id', ''))
                        
                        # 针对特定模型的智能匹配
                        if model_id == "qwen3-omni-flash":
                            # 匹配任何qwen3-omni-flash变体
                            if "qwen3-omni-flash" in available_model_id:
                                model_found = True
                                available_models.append(model_id)
                                logger.info(f"模型模糊匹配成功: {model_id} -> {available_model_id}")
                                break
                        elif model_id == "qwen3-text":
                            # 匹配任何纯文本qwen3模型
                            if ("qwen3" in available_model_id and 
                                "vl" not in available_model_id and 
                                "live" not in available_model_id and
                                "omni" not in available_model_id):
                                model_found = True
                                available_models.append(model_id)
                                logger.info(f"文本模型匹配成功: {model_id} -> {available_model_id}")
                                break
                            # 如果没有找到纯文本模型，使用omni-flash作为后备
                            elif "qwen3-omni-flash" in available_model_id:
                                model_found = True
                                available_models.append(model_id)
                                logger.info(f"文本模型后备匹配: {model_id} -> {available_model_id}")
                                break
                        else:
                            # 通用模糊匹配
                            base_name = model_id.rsplit('-', 1)[0] if '-' in model_id else model_id
                            if base_name in available_model_id:
                                model_found = True
                                available_models.append(model_id)
                                logger.info(f"模型模糊匹配成功: {model_id} -> {available_model_id}")
                                break
                
                if not model_found:
                    unavailable_models.append(model_id)
                    logger.warning(f"模型未找到: {model_id}")
            
            logger.info(f"结果: {len(available_models)} 个可用, {len(unavailable_models)} 个不可用")
            logger.info(f"可用模型: {available_models}")
            logger.info(f"不可用模型: {unavailable_models}")
            
            return {
                "available": available_models,
                "unavailable": unavailable_models
            }
        else:
            logger.error(f"API请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"异常: {e}")
        return None

if __name__ == "__main__":
    print("测试模型匹配逻辑...")
    result = check_model_availability()