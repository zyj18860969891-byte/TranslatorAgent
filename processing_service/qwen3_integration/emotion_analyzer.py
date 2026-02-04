"""
Qwen3情感分析器
基于Qwen3-Omni-Flash模型的智能情感分析工具
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import asyncio
import aiohttp

try:
    import dashscope
    from dashscope import Generation
except ImportError:
    dashscope = None

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """情感分析器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化情感分析器
        
        Args:
            config: 配置字典，包含模型参数和设置
        """
        self.config = config or self._load_default_config()
        self.model_name = self.config.get("primary_model", "qwen3-omni-flash")
        self.emotion_types = self.config.get("emotion_types", [
            "joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"
        ])
        self.confidence_threshold = self.config.get("confidence_threshold", 0.8)
        self.enable_cache = self.config.get("enable_cache", True)
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        
        # 初始化DashScope客户端
        self._init_dashscope_client()
        
        # 初始化缓存
        self._init_cache()
        
        logger.info(f"情感分析器初始化完成，使用模型: {self.model_name}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "primary_model": "qwen-turbo",
            "fallback_model": "qwen-plus",
            "emotion_types": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"],
            "confidence_threshold": 0.8,
            "enable_cache": True,
            "cache_ttl": 3600,
            "temperature": 0.3,
            "max_tokens": 500,
            "top_p": 0.8,
            "top_k": 50,
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0,
            "instruction": "请分析以下文本的情感倾向，并给出详细分析："
        }
    
    def _init_dashscope_client(self):
        """初始化DashScope客户端"""
        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("未配置DASHSCOPE_API_KEY，无法使用DashScope服务")
                self.dashscope_client = None
                return
            
            dashscope.api_key = api_key
            self.dashscope_client = dashscope
            logger.info("DashScope客户端初始化成功")
            
        except Exception as e:
            logger.error(f"DashScope客户端初始化失败: {e}")
            self.dashscope_client = None
    
    def _init_cache(self):
        """初始化缓存系统"""
        self.cache = {}
        self.cache_timestamps = {}
        logger.info("缓存系统初始化完成")
    
    def _get_cache_key(self, text: str, **kwargs) -> str:
        """生成缓存键"""
        import hashlib
        cache_data = f"{text}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.enable_cache:
            return None
        
        if cache_key in self.cache:
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.cache_ttl:
                return self.cache[cache_key]
            else:
                # 缓存过期，删除
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        if self.enable_cache:
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = time.time()
    
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 要分析的文本
            **kwargs: 额外参数
            
        Returns:
            情感分析结果字典
        """
        logger.info(f"开始分析文本情感: {text[:50]}...")
        
        try:
            # 检查缓存
            cache_key = self._get_cache_key(text, **kwargs)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug(f"使用缓存情感分析结果: {cache_key}")
                return cached_result
            
            # 构建情感分析请求
            request = self._build_emotion_analysis_request(text, **kwargs)
            
            # 执行情感分析
            result = self._analyze_with_qwen(request)
            
            if result:
                # 后处理结果
                processed_result = self._post_process_emotion_result(result, text)
                
                # 缓存结果
                self._set_cache(cache_key, processed_result)
                
                logger.info(f"情感分析完成: {processed_result['primary_emotion']}")
                return processed_result
            else:
                logger.error("情感分析失败")
                return {
                    "success": False,
                    "error": "情感分析失败",
                    "text": text,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def analyze_subtitles(self, subtitles: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        分析字幕列表的情感
        
        Args:
            subtitles: 字幕列表
            **kwargs: 额外参数
            
        Returns:
            字幕情感分析结果字典
        """
        logger.info(f"开始分析 {len(subtitles)} 条字幕的情感...")
        
        try:
            # 分析每条字幕的情感
            emotion_results = []
            emotion_counts = {emotion: 0 for emotion in self.emotion_types}
            total_confidence = 0
            
            for subtitle in subtitles:
                try:
                    # 分析单条字幕情感
                    result = self.analyze(subtitle["text"], **kwargs)
                    
                    if result["success"]:
                        emotion_results.append({
                            "text": subtitle["text"],
                            "start_time": subtitle["start_time"],
                            "end_time": subtitle["end_time"],
                            "primary_emotion": result["primary_emotion"],
                            "emotion_distribution": result["distribution"],
                            "confidence": result["confidence"]
                        })
                        
                        # 统计情感分布
                        emotion_counts[result["primary_emotion"]] += 1
                        total_confidence += result["confidence"]
                    
                except Exception as e:
                    logger.warning(f"字幕情感分析失败: {e}")
                    continue
            
            # 计算总体情感分布
            total_subtitles = len(emotion_results)
            if total_subtitles > 0:
                average_confidence = total_confidence / total_subtitles
                
                # 计算情感分布百分比
                emotion_distribution = {
                    emotion: (count / total_subtitles) * 100 
                    for emotion, count in emotion_counts.items()
                }
                
                # 确定主要情感
                primary_emotion = max(emotion_counts, key=emotion_counts.get)
                
                # 计算情感变化趋势
                emotion_trend = self._calculate_emotion_trend(emotion_results)
                
                result = {
                    "success": True,
                    "total_subtitles": total_subtitles,
                    "primary_emotion": primary_emotion,
                    "emotion_distribution": emotion_distribution,
                    "average_confidence": average_confidence,
                    "emotion_trend": emotion_trend,
                    "detailed_results": emotion_results,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                result = {
                    "success": False,
                    "error": "未能分析任何字幕的情感",
                    "total_subtitles": 0,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            logger.info(f"字幕情感分析完成: {total_subtitles} 条字幕, 主要情感: {primary_emotion}")
            return result
            
        except Exception as e:
            logger.error(f"字幕情感分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_subtitles": len(subtitles),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _build_emotion_analysis_request(self, text: str, **kwargs) -> Dict[str, Any]:
        """构建情感分析请求"""
        # 获取指令模板
        instruction = self.config.get("instruction", "请分析以下文本的情感倾向，并给出详细分析：")
        
        # 构建提示词
        emotion_types_str = "、".join(self.emotion_types)
        
        prompt = f"""{instruction}

可选的情感类型：{emotion_types_str}

请按以下JSON格式返回分析结果：
{{
    "primary_emotion": "主要情感",
    "distribution": {{
        "joy": 0.0,
        "sadness": 0.0,
        "anger": 0.0,
        "fear": 0.0,
        "surprise": 0.0,
        "disgust": 0.0,
        "neutral": 0.0
    }},
    "confidence": 0.0,
    "explanation": "分析解释"
}}

文本：{text}

分析结果："""
        
        return {
            "prompt": prompt,
            "text": text,
            "emotion_types": self.emotion_types,
            **kwargs
        }
    
    def _analyze_with_qwen(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Qwen模型进行情感分析"""
        if not self.dashscope_client:
            logger.warning("DashScope客户端未初始化，无法使用Qwen模型")
            return None
        
        try:
            # 构建请求 - 使用兼容模式
            qwen_request = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": request["prompt"]
                    }
                ],
                "max_tokens": self.config.get("max_tokens", 500),
                "temperature": self.config.get("temperature", 0.3),
                "top_p": self.config.get("top_p", 0.8)
            }
            
            # 发送请求
            response = self.dashscope_client.get(
                url=f"{self.config.get('base_url', 'https://dashscope.aliyuncs.com')}/compatible-mode/v1/chat/completions",
                json=qwen_request,
                timeout=self.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("choices", [{}])[0].get("message", {}).get("content"):
                    return {
                        "raw_response": result["choices"][0]["message"]["content"],
                        "model": self.model_name,
                        "request": request
                    }
                else:
                    logger.error(f"Qwen3情感分析返回空结果: {result}")
                    return None
            else:
                logger.error(f"Qwen3情感分析请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Qwen3情感分析失败: {e}")
            return None
    
    def _post_process_emotion_result(self, raw_result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """后处理情感分析结果"""
        try:
            # 解析JSON响应
            response_text = raw_result["raw_response"]
            
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    emotion_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    # JSON解析失败，使用默认值
                    emotion_data = self._create_default_emotion_data()
            else:
                # 没有找到JSON，使用默认值
                emotion_data = self._create_default_emotion_data()
            
            # 验证和标准化数据
            emotion_data = self._validate_emotion_data(emotion_data, text)
            
            return emotion_data
            
        except Exception as e:
            logger.error(f"情感分析结果后处理失败: {e}")
            return self._create_default_emotion_data(text)
    
    def _create_default_emotion_data(self, text: str = "") -> Dict[str, Any]:
        """创建默认情感数据"""
        return {
            "success": True,
            "primary_emotion": "neutral",
            "distribution": {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "disgust": 0.0,
                "neutral": 100.0
            },
            "confidence": 0.5,
            "explanation": "使用默认情感分析结果",
            "text": text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _validate_emotion_data(self, data: Dict[str, Any], text: str) -> Dict[str, Any]:
        """验证和标准化情感数据"""
        # 确保必需字段存在
        if "primary_emotion" not in data:
            data["primary_emotion"] = "neutral"
        
        if "distribution" not in data:
            data["distribution"] = {emotion: 0.0 for emotion in self.emotion_types}
            data["distribution"]["neutral"] = 100.0
        
        if "confidence" not in data:
            data["confidence"] = 0.5
        
        if "explanation" not in data:
            data["explanation"] = "情感分析结果"
        
        # 验证情感类型
        if data["primary_emotion"] not in self.emotion_types:
            data["primary_emotion"] = "neutral"
        
        # 验证分布数据
        distribution = data["distribution"]
        total_percentage = sum(distribution.values())
        
        if total_percentage == 0:
            # 如果没有分布数据，设置为中性
            distribution = {emotion: 0.0 for emotion in self.emotion_types}
            distribution["neutral"] = 100.0
            data["distribution"] = distribution
        else:
            # 归一化分布数据
            normalized_distribution = {
                emotion: (percentage / total_percentage) * 100
                for emotion, percentage in distribution.items()
            }
            data["distribution"] = normalized_distribution
        
        # 验证置信度
        if not isinstance(data["confidence"], (int, float)) or data["confidence"] < 0 or data["confidence"] > 1:
            data["confidence"] = 0.5
        
        # 添加其他字段
        data["success"] = True
        data["text"] = text
        data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return data
    
    def _calculate_emotion_trend(self, emotion_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算情感变化趋势"""
        if len(emotion_results) < 2:
            return {
                "trend": "insufficient_data",
                "volatility": 0.0,
                "transitions": []
            }
        
        # 计算情感变化
        transitions = []
        emotion_values = {emotion: [] for emotion in self.emotion_types}
        
        for result in emotion_results:
            primary_emotion = result["primary_emotion"]
            emotion_values[primary_emotion].append(result["start_time"])
        
        # 计算情感转换
        for i in range(len(emotion_results) - 1):
            current_emotion = emotion_results[i]["primary_emotion"]
            next_emotion = emotion_results[i + 1]["primary_emotion"]
            
            if current_emotion != next_emotion:
                transitions.append({
                    "from_emotion": current_emotion,
                    "to_emotion": next_emotion,
                    "timestamp": emotion_results[i + 1]["start_time"],
                    "time_gap": emotion_results[i + 1]["start_time"] - emotion_results[i]["start_time"]
                })
        
        # 计算波动性
        volatility = len(transitions) / len(emotion_results)
        
        # 确定趋势
        if volatility < 0.1:
            trend = "stable"
        elif volatility < 0.3:
            trend = "gradual"
        else:
            trend = "frequent"
        
        return {
            "trend": trend,
            "volatility": volatility,
            "transitions": transitions,
            "total_transitions": len(transitions)
        }
    
    def get_emotion_statistics(self, emotion_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取情感统计信息
        
        Args:
            emotion_results: 情感分析结果列表
            
        Returns:
            统计信息字典
        """
        if not emotion_results:
            return {
                "total_analyses": 0,
                "primary_emotion": "neutral",
                "most_common_emotion": "neutral",
                "average_confidence": 0.0,
                "emotion_distribution": {}
            }
        
        # 统计情感分布
        emotion_counts = {emotion: 0 for emotion in self.emotion_types}
        total_confidence = 0
        
        for result in emotion_results:
            emotion = result["primary_emotion"]
            emotion_counts[emotion] += 1
            total_confidence += result["confidence"]
        
        # 计算统计信息
        total_analyses = len(emotion_results)
        primary_emotion = max(emotion_counts, key=emotion_counts.get)
        most_common_emotion = primary_emotion  # 与主要情感相同
        average_confidence = total_confidence / total_analyses
        
        # 计算情感分布百分比
        emotion_distribution = {
            emotion: (count / total_analyses) * 100 
            for emotion, count in emotion_counts.items()
        }
        
        return {
            "total_analyses": total_analyses,
            "primary_emotion": primary_emotion,
            "most_common_emotion": most_common_emotion,
            "average_confidence": average_confidence,
            "emotion_distribution": emotion_distribution
        }
    
    def classify_emotion_intensity(self, text: str) -> Dict[str, Any]:
        """
        分类情感强度
        
        Args:
            text: 要分析的文本
            
        Returns:
            情感强度分类结果
        """
        # 首先进行情感分析
        emotion_result = self.analyze(text)
        
        if not emotion_result["success"]:
            return {
                "success": False,
                "error": "情感分析失败",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # 基于置信度和情感分布计算强度
        confidence = emotion_result["confidence"]
        distribution = emotion_result["distribution"]
        primary_emotion = emotion_result["primary_emotion"]
        
        # 计算强度分数
        intensity_score = confidence * (distribution[primary_emotion] / 100)
        
        # 分类强度
        if intensity_score >= 0.8:
            intensity_level = "high"
        elif intensity_score >= 0.5:
            intensity_level = "medium"
        else:
            intensity_level = "low"
        
        return {
            "success": True,
            "primary_emotion": primary_emotion,
            "intensity_level": intensity_level,
            "intensity_score": intensity_score,
            "confidence": confidence,
            "distribution": distribution,
            "text": text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }