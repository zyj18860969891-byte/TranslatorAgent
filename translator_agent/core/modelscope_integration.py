"""
ModelScope 集成模块
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ModelScopeClient:
    """ModelScope 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
        self.base_url = "https://api.modelscope.cn/api/v1"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型"""
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                return []
                
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取模型信息"""
        try:
            url = f"{self.base_url}/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"获取模型信息失败: {e}")
            return None
    
    def infer_model(self, model_id: str, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """运行模型推理"""
        try:
            url = f"{self.base_url}/models/{model_id}/infer"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=inputs)
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"模型推理失败: {e}")
            return None