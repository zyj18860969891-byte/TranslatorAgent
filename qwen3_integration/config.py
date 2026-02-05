"""
Qwen3集成配置管理模块
负责加载和管理模型配置、功能配置等
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "."):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.model_config = {}
        self.feature_config = {}
        self.env_config = {}
        
        # 加载配置
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置"""
        try:
            # 加载模型配置
            self.model_config = self._load_json_file("model_config.json")
            
            # 加载功能配置
            self.feature_config = self._load_json_file("feature_config.json")
            
            # 加载环境配置
            self._load_env_config()
            
            logger.info("配置加载完成")
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 使用默认配置
            self._load_default_configs()
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """加载JSON配置文件"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"配置文件加载成功: {filename}")
            return config
            
        except Exception as e:
            logger.error(f"配置文件加载失败 {filename}: {e}")
            return {}
    
    def _load_env_config(self):
        """加载环境配置"""
        env_vars = {
            "DASHSCOPE_API_KEY": "dashscope_api_key",
            "DASHSCOPE_BASE_URL": "dashscope_base_url",
            "DASHSCOPE_TIMEOUT": "dashscope_timeout",
            "DASHSCOPE_MAX_RETRIES": "dashscope_max_retries",
            "DASHSCOPE_RETRY_DELAY": "dashscope_retry_delay"
        }
        
        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value:
                self.env_config[config_key] = value
                logger.debug(f"环境变量加载: {config_key} = {value}")
    
    def _load_default_configs(self):
        """加载默认配置"""
        self.model_config = {
            "models": {
                "qwen3-omni-flash-realtime": {
                    "name": "Qwen3-Omni-Flash-Realtime",
                    "type": "realtime",
                    "base_url": "https://dashscope.aliyuncs.com/api/v1",
                    "api_key": "${DASHSCOPE_API_KEY}",
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "timeout": 30,
                    "enabled": False
                },
                "qwen3-vl-rerank": {
                    "name": "Qwen3-VL-Rerank",
                    "type": "vision",
                    "base_url": "https://dashscope.aliyuncs.com/api/v1",
                    "api_key": "${DASHSCOPE_API_KEY}",
                    "max_tokens": 1000,
                    "temperature": 0.1,
                    "timeout": 30,
                    "enabled": True
                },
                "qwen3-embedding": {
                    "name": "Qwen3-Embedding",
                    "type": "embedding",
                    "base_url": "https://dashscope.aliyuncs.com/api/v1",
                    "api_key": "${DASHSCOPE_API_KEY}",
                    "max_tokens": 8192,
                    "temperature": 0.0,
                    "timeout": 30,
                    "enabled": False
                }
            }
        }
        
        self.feature_config = {
            "features": {
                "subtitle_extraction": {
                    "primary_model": "qwen3-vl-rerank",
                    "fallback_model": "qwen3-omni-flash-realtime",
                    "confidence_threshold": 0.95,
                    "supported_formats": ["srt", "vtt", "ass", "ssa"],
                    "max_text_length": 500
                },
                "video_translation": {
                    "primary_model": "qwen3-omni-flash-realtime",
                    "embedding_support": "qwen3-embedding",
                    "realtime_mode": True,
                    "batch_size": 10,
                    "max_concurrent_requests": 5
                },
                "emotion_analysis": {
                    "primary_model": "qwen3-omni-flash-realtime",
                    "emotion_types": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"],
                    "confidence_threshold": 0.8
                },
                "localization": {
                    "primary_model": "qwen3-omni-flash-realtime",
                    "embedding_support": "qwen3-embedding",
                    "cultural_adaptation": True,
                    "target_cultures": ["chinese", "japanese", "korean", "western"]
                }
            }
        }
        
        logger.info("使用默认配置")
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        获取指定模型的配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型配置字典
        """
        return self.model_config.get("models", {}).get(model_name, {})
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """
        获取指定功能的配置
        
        Args:
            feature_name: 功能名称
            
        Returns:
            功能配置字典
        """
        return self.feature_config.get("features", {}).get(feature_name, {})
    
    def get_env_config(self, key: str) -> Optional[str]:
        """
        获取环境配置
        
        Args:
            key: 配置键
            
        Returns:
            配置值
        """
        return self.env_config.get(key)
    
    def get_all_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型配置
        
        Returns:
            所有模型配置字典
        """
        return self.model_config.get("models", {})
    
    def get_all_feature_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有功能配置
        
        Returns:
            所有功能配置字典
        """
        return self.feature_config.get("features", {})
    
    def get_enabled_models(self) -> List[str]:
        """
        获取启用的模型列表
        
        Returns:
            启用的模型名称列表
        """
        models = []
        for model_name, model_config in self.get_all_model_configs().items():
            if model_config.get("enabled", False):
                models.append(model_name)
        return models
    
    def get_enabled_features(self) -> List[str]:
        """
        获取启用的功能列表
        
        Returns:
            启用的功能名称列表
        """
        features = []
        for feature_name, feature_config in self.get_all_feature_configs().items():
            if feature_config.get("enabled", True):
                features.append(feature_name)
        return features
    
    def update_model_config(self, model_name: str, config: Dict[str, Any]):
        """
        更新模型配置
        
        Args:
            model_name: 模型名称
            config: 新配置
        """
        if "models" not in self.model_config:
            self.model_config["models"] = {}
        
        self.model_config["models"][model_name] = config
        logger.info(f"模型配置已更新: {model_name}")
    
    def update_feature_config(self, feature_name: str, config: Dict[str, Any]):
        """
        更新功能配置
        
        Args:
            feature_name: 功能名称
            config: 新配置
        """
        if "features" not in self.feature_config:
            self.feature_config["features"] = {}
        
        self.feature_config["features"][feature_name] = config
        logger.info(f"功能配置已更新: {feature_name}")
    
    def save_configs(self):
        """保存所有配置"""
        try:
            # 保存模型配置
            self._save_json_file("model_config.json", self.model_config)
            
            # 保存功能配置
            self._save_json_file("feature_config.json", self.feature_config)
            
            logger.info("配置保存完成")
            
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
    
    def _save_json_file(self, filename: str, config: Dict[str, Any]):
        """保存JSON配置文件"""
        config_path = self.config_dir / filename
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置文件保存成功: {filename}")
            
        except Exception as e:
            logger.error(f"配置文件保存失败 {filename}: {e}")
            raise
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置
        
        Returns:
            验证结果字典
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # 验证模型配置
            models = self.get_all_model_configs()
            if not models:
                validation_result["errors"].append("没有配置任何模型")
                validation_result["valid"] = False
            
            for model_name, model_config in models.items():
                # 检查必需字段
                required_fields = ["name", "type", "base_url", "api_key"]
                for field in required_fields:
                    if field not in model_config:
                        validation_result["errors"].append(f"模型 {model_name} 缺少必需字段: {field}")
                        validation_result["valid"] = False
                
                # 检查API Key
                api_key = model_config.get("api_key", "")
                if api_key and not api_key.startswith("${"):
                    # 检查API Key是否有效
                    if not self._validate_api_key(api_key):
                        validation_result["warnings"].append(f"模型 {model_name} 的API Key可能无效")
            
            # 验证功能配置
            features = self.get_all_feature_configs()
            if not features:
                validation_result["errors"].append("没有配置任何功能")
                validation_result["valid"] = False
            
            for feature_name, feature_config in features.items():
                # 检查必需字段
                required_fields = ["primary_model"]
                for field in required_fields:
                    if field not in feature_config:
                        validation_result["errors"].append(f"功能 {feature_name} 缺少必需字段: {field}")
                        validation_result["valid"] = False
                
                # 检查主模型是否存在
                primary_model = feature_config.get("primary_model")
                if primary_model and primary_model not in models:
                    validation_result["errors"].append(f"功能 {feature_name} 的主模型 {primary_model} 不存在")
                    validation_result["valid"] = False
            
            # 验证环境配置
            if not self.env_config:
                validation_result["warnings"].append("没有配置环境变量")
            
            # 检查DashScope API Key
            api_key = self.env_config.get("dashscope_api_key")
            if not api_key:
                validation_result["warnings"].append("未配置DASHSCOPE_API_KEY")
            else:
                if not self._validate_api_key(api_key):
                    validation_result["warnings"].append("DASHSCOPE_API_KEY可能无效")
            
        except Exception as e:
            validation_result["errors"].append(f"配置验证失败: {e}")
            validation_result["valid"] = False
        
        return validation_result
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        验证API Key
        
        Args:
            api_key: API Key
            
        Returns:
            是否有效
        """
        # 这里可以实现更复杂的API Key验证逻辑
        # 例如：尝试调用API验证
        
        # 简单验证：检查长度和格式
        if len(api_key) < 10:
            return False
        
        # 检查是否包含特殊字符
        import re
        if not re.match(r'^[a-zA-Z0-9\-_]+$', api_key):
            return False
        
        return True
    
    def get_merged_config(self) -> Dict[str, Any]:
        """
        获取合并后的配置
        
        Returns:
            合并后的配置字典
        """
        merged_config = {
            "models": self.model_config.get("models", {}),
            "features": self.feature_config.get("features", {}),
            "environment": self.env_config
        }
        
        return merged_config
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self._load_default_configs()
        logger.info("配置已重置为默认值")

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def load_config(config_dir: str = ".") -> Dict[str, Any]:
    """
    加载配置
    
    Args:
        config_dir: 配置文件目录
        
    Returns:
        配置字典
    """
    config_manager = ConfigManager(config_dir)
    return config_manager.get_merged_config()

def check_model_availability() -> Dict[str, Any]:
    """
    检查模型可用性
    
    Returns:
        模型可用性字典
    """
    try:
        import requests
        
        config_manager = get_config_manager()
        base_url = config_manager.get_env_config("dashscope_base_url") or "https://dashscope.aliyuncs.com"
        api_key = config_manager.get_env_config("dashscope_api_key")
        
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
        
        try:
            response = requests.get(f"{base_url}/compatible-mode/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = []
                unavailable_models = []
                
                target_models = [
                    "qwen3-omni-flash-realtime",
                    "qwen3-vl-rerank",
                    "qwen3-embedding"
                ]
                
                # 检查API响应格式
                if 'data' in models_data and isinstance(models_data['data'], list):
                    # OpenAI兼容模式格式 - 使用 'id' 字段
                    models_list = models_data['data']
                    for model_id in target_models:
                        model_found = False
                        for model in models_list:
                            if model_id in model.get('id', ''):
                                model_found = True
                                available_models.append(model_id)
                                break
                        
                        if not model_found:
                            unavailable_models.append(model_id)
                            
                elif 'models' in models_data and isinstance(models_data['models'], list):
                    # 原始格式 - 使用 'model' 字段
                    models_list = models_data['models']
                    for model_id in target_models:
                        model_found = False
                        for model in models_list:
                            if model_id in model.get('model', ''):
                                model_found = True
                                available_models.append(model_id)
                                break
                        
                        if not model_found:
                            unavailable_models.append(model_id)
                else:
                    # 未知格式，假设所有模型都不可用
                    unavailable_models = target_models.copy()
                
                return {
                    "available": available_models,
                    "unavailable": unavailable_models,
                    "total_models": len(available_models) + len(unavailable_models)
                }
            else:
                # 处理其他HTTP状态码
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', str(error_data))
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                if response.status_code == 401:
                    logger.error(f"API认证失败: {error_msg}")
                    return {
                        "available": [],
                        "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                        "error": f"API认证失败: {error_msg}"
                    }
                elif response.status_code == 403:
                    logger.error(f"API访问被拒绝: {error_msg}")
                    return {
                        "available": [],
                        "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                        "error": f"API访问被拒绝: {error_msg}"
                    }
                elif response.status_code == 429:
                    logger.error(f"API请求频率限制: {error_msg}")
                    return {
                        "available": [],
                        "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                        "error": f"API请求频率限制: {error_msg}"
                    }
                else:
                    logger.error(f"API请求失败: HTTP {response.status_code} - {error_msg}")
                    return {
                        "available": [],
                        "unavailable": ["qwen3-omni-flash-realtime", "qwen3-vl-rerank", "qwen3-embedding"],
                        "error": f"API请求失败: HTTP {response.status_code} - {error_msg}"
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

def run_system_tests():
    """运行系统测试"""
    try:
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("开始运行系统测试...")
        
        test_results = []
        
        # 测试1: 配置验证
        config_manager = get_config_manager()
        config_validation = config_manager.validate_config()
        test_results.append(("配置验证", config_validation["valid"], 
                           f"错误: {len(config_validation['errors'])}, 警告: {len(config_validation['warnings'])}"))
        
        # 测试2: 模型可用性检查
        model_availability = check_model_availability()
        test_results.append(("模型可用性", len(model_availability["available"]) > 0,
                           f"可用: {len(model_availability['available'])}, 不可用: {len(model_availability['unavailable'])}"))
        
        # 测试3: 环境变量检查
        env_vars = ["DASHSCOPE_API_KEY", "DASHSCOPE_BASE_URL"]
        env_check = all(os.getenv(var) for var in env_vars)
        test_results.append(("环境变量", env_check, 
                           f"配置的变量: {sum(1 for var in env_vars if os.getenv(var))}/{len(env_vars)}"))
        
        # 测试4: 基础组件初始化
        try:
            from .subtitle_extractor import SubtitleExtractor
            from .video_translator import VideoTranslator
            from .emotion_analyzer import EmotionAnalyzer
            
            extractor = SubtitleExtractor()
            translator = VideoTranslator()
            analyzer = EmotionAnalyzer()
            
            components_ok = True
            error_msg = ""
        except Exception as e:
            components_ok = False
            error_msg = str(e)
        
        test_results.append(("基础组件", components_ok, error_msg))
        
        # 打印测试结果
        logger.info("系统测试结果:")
        for test_name, success, message in test_results:
            status = "✅ 通过" if success else "❌ 失败"
            logger.info(f"  {test_name}: {status} - {message}")
        
        # 计算总体结果
        passed_tests = sum(1 for _, success, _ in test_results if success)
        total_tests = len(test_results)
        
        logger.info(f"总体结果: {passed_tests}/{total_tests} 测试通过")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"系统测试失败: {e}")
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "test_results": [],
            "error": str(e)
        }