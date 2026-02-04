"""
Qwen3视频翻译器
基于Qwen3-Omni-Flash模型的智能视频翻译工具
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

from .subtitle_extractor import SubtitleExtractor
from .emotion_analyzer import EmotionAnalyzer

logger = logging.getLogger(__name__)

class VideoTranslator:
    """视频翻译器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化视频翻译器
        
        Args:
            config: 配置字典，包含模型参数和设置
        """
        self.config = config or self._load_default_config()
        self.model_name = self.config.get("primary_model", "qwen3-omni-flash")
        self.embedding_model = self.config.get("embedding_model", "qwen3-text")
        self.realtime_mode = self.config.get("realtime_mode", True)
        self.batch_size = self.config.get("batch_size", 10)
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 5)
        self.enable_cache = self.config.get("enable_cache", True)
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        self.include_emotions = self.config.get("include_emotions", True)
        self.cultural_adaptation = self.config.get("cultural_adaptation", True)
        
        # 初始化组件
        self.subtitle_extractor = SubtitleExtractor(self.config)
        self.emotion_analyzer = EmotionAnalyzer(self.config)
        
        # 初始化DashScope客户端
        self._init_dashscope_client()
        
        # 初始化缓存
        self._init_cache()
        
        logger.info(f"视频翻译器初始化完成，使用模型: {self.model_name}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "primary_model": "qwen3-omni-flash",
            "embedding_model": "qwen3-text",
            "realtime_mode": True,
            "batch_size": 10,
            "max_concurrent_requests": 5,
            "enable_cache": True,
            "cache_ttl": 3600,
            "include_emotions": True,
            "cultural_adaptation": True,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.8,
            "top_k": 50,
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0
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
    
    def _get_cache_key(self, text: str, target_language: str, **kwargs) -> str:
        """生成缓存键"""
        import hashlib
        cache_data = f"{text}:{target_language}:{json.dumps(kwargs, sort_keys=True)}"
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
    
    async def translate(self, 
                       video_path: str, 
                       target_language: str = "zh",
                       source_language: Optional[str] = None,
                       include_emotions: Optional[bool] = None,
                       cultural_adaptation: Optional[bool] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        翻译视频内容
        
        Args:
            video_path: 视频文件路径
            target_language: 目标语言代码
            source_language: 源语言代码（自动检测如果为None）
            include_emotions: 是否包含情感分析
            cultural_adaptation: 是否进行文化适配
            **kwargs: 额外参数
            
        Returns:
            翻译结果字典
        """
        logger.info(f"开始翻译视频: {video_path} -> {target_language}")
        
        try:
            # 设置参数
            include_emotions = include_emotions if include_emotions is not None else self.include_emotions
            cultural_adaptation = cultural_adaptation if cultural_adaptation is not None else self.cultural_adaptation
            
            # 提取字幕
            subtitles = await self._extract_subtitles_async(video_path)
            
            if not subtitles:
                return {
                    "success": False,
                    "error": "未能提取到字幕",
                    "video_path": video_path,
                    "target_language": target_language,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 分析情感
            emotions = None
            if include_emotions:
                emotions = await self._analyze_emotions_async(subtitles)
            
            # 翻译字幕
            translations = await self._translate_subtitles_async(
                subtitles, 
                target_language, 
                source_language,
                emotions,
                cultural_adaptation,
                **kwargs
            )
            
            # 生成结果
            result = {
                "success": True,
                "video_path": video_path,
                "target_language": target_language,
                "source_language": source_language,
                "subtitle_count": len(subtitles),
                "emotions": emotions,
                "translations": translations,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"视频翻译完成，共翻译 {len(translations)} 条字幕")
            return result
            
        except Exception as e:
            logger.error(f"视频翻译失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "target_language": target_language,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def _extract_subtitles_async(self, video_path: str) -> List[Dict[str, Any]]:
        """异步提取字幕"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.subtitle_extractor.extract, video_path)
    
    async def _analyze_emotions_async(self, subtitles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """异步分析情感"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.emotion_analyzer.analyze_subtitles, subtitles)
    
    async def _translate_subtitles_async(self,
                                       subtitles: List[Dict[str, Any]],
                                       target_language: str,
                                       source_language: Optional[str],
                                       emotions: Optional[Dict[str, Any]],
                                       cultural_adaptation: bool,
                                       **kwargs) -> List[Dict[str, Any]]:
        """异步翻译字幕"""
        if self.realtime_mode:
            return await self._translate_realtime_async(
                subtitles, target_language, source_language, emotions, cultural_adaptation, **kwargs
            )
        else:
            return await self._translate_batch_async(
                subtitles, target_language, source_language, emotions, cultural_adaptation, **kwargs
            )
    
    async def _translate_realtime_async(self,
                                      subtitles: List[Dict[str, Any]],
                                      target_language: str,
                                      source_language: Optional[str],
                                      emotions: Optional[Dict[str, Any]],
                                      cultural_adaptation: bool,
                                      **kwargs) -> List[Dict[str, Any]]:
        """使用实时模式翻译字幕"""
        logger.info("使用实时模式翻译字幕...")
        
        translations = []
        
        for subtitle in subtitles:
            try:
                # 构建翻译请求
                translation_request = self._build_translation_request(
                    subtitle["text"], 
                    target_language, 
                    source_language,
                    emotions,
                    cultural_adaptation,
                    **kwargs
                )
                
                # 执行翻译
                translation_result = await self._translate_with_qwen_realtime(translation_request)
                
                if translation_result:
                    translations.append({
                        "original_text": subtitle["text"],
                        "translated_text": translation_result["text"],
                        "start_time": subtitle["start_time"],
                        "end_time": subtitle["end_time"],
                        "confidence": translation_result.get("confidence", 0.0),
                        "emotion_context": emotions.get("primary_emotion", "neutral") if emotions else None,
                        "cultural_adaptation": cultural_adaptation
                    })
                else:
                    translations.append({
                        "original_text": subtitle["text"],
                        "translated_text": subtitle["text"],  # 翻译失败，使用原文
                        "start_time": subtitle["start_time"],
                        "end_time": subtitle["end_time"],
                        "confidence": 0.0,
                        "emotion_context": emotions.get("primary_emotion", "neutral") if emotions else None,
                        "cultural_adaptation": cultural_adaptation
                    })
                
                # 添加延迟避免API限制
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"字幕翻译失败: {e}")
                translations.append({
                    "original_text": subtitle["text"],
                    "translated_text": subtitle["text"],  # 翻译失败，使用原文
                    "start_time": subtitle["start_time"],
                    "end_time": subtitle["end_time"],
                    "confidence": 0.0,
                    "emotion_context": emotions.get("primary_emotion", "neutral") if emotions else None,
                    "cultural_adaptation": cultural_adaptation
                })
        
        return translations
    
    async def _translate_batch_async(self,
                                    subtitles: List[Dict[str, Any]],
                                    target_language: str,
                                    source_language: Optional[str],
                                    emotions: Optional[Dict[str, Any]],
                                    cultural_adaptation: bool,
                                    **kwargs) -> List[Dict[str, Any]]:
        """使用批处理模式翻译字幕"""
        logger.info("使用批处理模式翻译字幕...")
        
        translations = []
        
        # 将字幕分组
        batches = self._group_subtitles_into_batches(subtitles, self.batch_size)
        
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            async def translate_batch(batch):
                async with semaphore:
                    try:
                        # 构建批处理翻译请求
                        batch_request = self._build_batch_translation_request(
                            batch, target_language, source_language, emotions, cultural_adaptation, **kwargs
                        )
                        
                        # 执行批处理翻译
                        batch_result = await self._translate_batch_with_qwen(batch_request, session)
                        
                        return batch_result
                    except Exception as e:
                        logger.error(f"批处理翻译失败: {e}")
                        return [{"text": sub["text"], "confidence": 0.0} for sub in batch]
            
            # 并发执行批处理翻译
            batch_tasks = [translate_batch(batch) for batch in batches]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # 合并结果
            for batch_result in batch_results:
                translations.extend(batch_result)
        
        return translations
    
    def _build_translation_request(self,
                                 text: str,
                                 target_language: str,
                                 source_language: Optional[str],
                                 emotions: Optional[Dict[str, Any]],
                                 cultural_adaptation: bool,
                                 **kwargs) -> Dict[str, Any]:
        """构建翻译请求"""
        # 语言映射
        language_map = {
            "zh": "中文",
            "en": "英语",
            "ja": "日语",
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
            "ru": "俄语",
            "ar": "阿拉伯语",
            "hi": "印地语"
        }
        
        target_lang_name = language_map.get(target_language, target_language)
        source_lang_name = language_map.get(source_language, source_language) if source_language else "自动检测"
        
        # 构建提示词
        prompt = f"请将以下文本翻译成{target_lang_name}。"
        
        if source_language:
            prompt += f"源语言是{source_lang_name}。"
        
        if emotions and emotions.get("primary_emotion"):
            prompt += f"文本的情感色彩是{emotions['primary_emotion']}，请在翻译时保持这种情感。"
        
        if cultural_adaptation:
            prompt += "请进行文化适配，使翻译结果符合目标语言的文化习惯。"
        
        prompt += f"\n\n原文：{text}\n\n译文："
        
        return {
            "prompt": prompt,
            "text": text,
            "target_language": target_language,
            "source_language": source_language,
            "emotions": emotions,
            "cultural_adaptation": cultural_adaptation,
            **kwargs
        }
    
    def _build_batch_translation_request(self,
                                       batch: List[Dict[str, Any]],
                                       target_language: str,
                                       source_language: Optional[str],
                                       emotions: Optional[Dict[str, Any]],
                                       cultural_adaptation: bool,
                                       **kwargs) -> Dict[str, Any]:
        """构建批处理翻译请求"""
        # 语言映射
        language_map = {
            "zh": "中文",
            "en": "英语",
            "ja": "日语",
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
            "ru": "俄语",
            "ar": "阿拉伯语",
            "hi": "印地语"
        }
        
        target_lang_name = language_map.get(target_language, target_language)
        source_lang_name = language_map.get(source_language, source_language) if source_language else "自动检测"
        
        # 构建提示词
        prompt = f"请将以下文本批量翻译成{target_lang_name}。"
        
        if source_language:
            prompt += f"源语言是{source_lang_name}。"
        
        if emotions and emotions.get("primary_emotion"):
            prompt += f"文本的情感色彩是{emotions['primary_emotion']}，请在翻译时保持这种情感。"
        
        if cultural_adaptation:
            prompt += "请进行文化适配，使翻译结果符合目标语言的文化习惯。"
        
        prompt += "\n\n请按以下格式返回翻译结果：\n"
        prompt += "1. 原文1\n译文1\n\n"
        prompt += "2. 原文2\n译文2\n\n"
        prompt += "...\n\n"
        
        # 添加原文
        for i, subtitle in enumerate(batch):
            prompt += f"{i+1}. {subtitle['text']}\n"
        
        prompt += "\n译文："
        
        return {
            "prompt": prompt,
            "batch": batch,
            "target_language": target_language,
            "source_language": source_language,
            "emotions": emotions,
            "cultural_adaptation": cultural_adaptation,
            **kwargs
        }
    
    async def _translate_with_qwen_realtime(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Qwen3实时模型进行翻译"""
        if not self.dashscope_client:
            logger.warning("DashScope客户端未初始化，无法使用Qwen3模型")
            return None
        
        try:
            # 检查缓存
            cache_key = self._get_cache_key(
                request["text"], 
                request["target_language"], 
                emotions=request["emotions"],
                cultural_adaptation=request["cultural_adaptation"]
            )
            
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug(f"使用缓存翻译结果: {cache_key}")
                return cached_result
            
            # 构建请求
            qwen_request = {
                "model": self.model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": request["prompt"]
                                }
                            ]
                        }
                    ]
                },
                "parameters": {
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 2000),
                    "top_p": self.config.get("top_p", 0.8),
                    "top_k": self.config.get("top_k", 50)
                }
            }
            
            # 发送请求
            response = await self._make_async_request(qwen_request)
            
            if response and response.get("output", {}).get("text"):
                # 解析翻译结果
                translated_text = self._parse_translation_response(response["output"]["text"])
                
                result = {
                    "text": translated_text,
                    "confidence": 0.9,  # Qwen3通常有很高的置信度
                    "model": self.model_name,
                    "request": request
                }
                
                # 缓存结果
                self._set_cache(cache_key, result)
                
                return result
            else:
                logger.error(f"Qwen3翻译请求失败: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Qwen3翻译失败: {e}")
            return None
    
    async def _translate_batch_with_qwen(self, request: Dict[str, Any], session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """使用Qwen3模型进行批处理翻译"""
        if not self.dashscope_client:
            logger.warning("DashScope客户端未初始化，无法使用Qwen3模型")
            return [{"text": sub["text"], "confidence": 0.0} for sub in request["batch"]]
        
        try:
            # 构建请求
            qwen_request = {
                "model": self.model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": request["prompt"]
                                }
                            ]
                        }
                    ]
                },
                "parameters": {
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 2000),
                    "top_p": self.config.get("top_p", 0.8),
                    "top_k": self.config.get("top_k", 50)
                }
            }
            
            # 发送请求
            response = await self._make_async_request(qwen_request)
            
            if response and response.get("output", {}).get("text"):
                # 解析批处理翻译结果
                translations = self._parse_batch_translation_response(response["output"]["text"], request["batch"])
                
                return translations
            else:
                logger.error(f"Qwen3批处理翻译请求失败: {response}")
                return [{"text": sub["text"], "confidence": 0.0} for sub in request["batch"]]
                
        except Exception as e:
            logger.error(f"Qwen3批处理翻译失败: {e}")
            return [{"text": sub["text"], "confidence": 0.0} for sub in request["batch"]]
    
    async def _make_async_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """异步发送API请求"""
        try:
            import base64
            
            # 这里应该实现真正的异步HTTP请求
            # 由于dashscope库的限制，我们暂时使用同步请求
            response = self.dashscope_client.get(
                url=f"{self.config.get('base_url', 'https://dashscope.aliyuncs.com')}/api/v1/services/aigc/text-generation/generation",
                json=request,
                timeout=self.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API请求失败: {e}")
            return None
    
    def _parse_translation_response(self, response_text: str) -> str:
        """解析翻译响应"""
        # 提取翻译文本
        lines = response_text.strip().split('\n')
        translation_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('原文', '译文', '1.', '2.', '3.', '4.', '5.')):
                translation_lines.append(line)
        
        return ' '.join(translation_lines) if translation_lines else response_text.strip()
    
    def _parse_batch_translation_response(self, response_text: str, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析批处理翻译响应"""
        translations = []
        
        # 尝试按格式解析
        lines = response_text.strip().split('\n')
        current_translation = ""
        
        for line in lines:
            line = line.strip()
            
            if line and ':' in line:
                # 格式: "数字. 原文" 或 "译文"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    if key.isdigit():
                        # 这是原文，跳过
                        continue
                    else:
                        # 这是译文
                        current_translation = value
                else:
                    current_translation = line
            else:
                current_translation = line
            
            if current_translation:
                translations.append({
                    "text": current_translation,
                    "confidence": 0.9
                })
                current_translation = ""
        
        # 如果解析失败，返回原文
        if not translations:
            translations = [{"text": sub["text"], "confidence": 0.0} for sub in batch]
        
        # 确保翻译数量匹配
        while len(translations) < len(batch):
            translations.append({"text": batch[len(translations)]["text"], "confidence": 0.0})
        
        return translations[:len(batch)]
    
    def _group_subtitles_into_batches(self, subtitles: List[Dict[str, Any]], batch_size: int) -> List[List[Dict[str, Any]]]:
        """将字幕分组为批处理"""
        batches = []
        
        for i in range(0, len(subtitles), batch_size):
            batch = subtitles[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def translate_to_file(self,
                         video_path: str,
                         output_path: str,
                         target_language: str = "zh",
                         format: str = "srt",
                         **kwargs) -> bool:
        """
        翻译视频并保存到文件
        
        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            target_language: 目标语言代码
            format: 输出格式 (srt, vtt, json)
            **kwargs: 额外参数
            
        Returns:
            是否成功保存
        """
        try:
            # 翻译视频
            result = asyncio.run(self.translate(video_path, target_language, **kwargs))
            
            if not result["success"]:
                logger.error(f"视频翻译失败: {result['error']}")
                return False
            
            # 根据格式保存
            if format.lower() == "srt":
                return self._save_translations_srt(result["translations"], output_path)
            elif format.lower() == "vtt":
                return self._save_translations_vtt(result["translations"], output_path)
            elif format.lower() == "json":
                return self._save_translations_json(result, output_path)
            else:
                raise ValueError(f"不支持的输出格式: {format}")
                
        except Exception as e:
            logger.error(f"视频翻译并保存失败: {e}")
            return False
    
    def _save_translations_srt(self, translations: List[Dict[str, Any]], output_path: str) -> bool:
        """保存翻译结果为SRT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, translation in enumerate(translations, 1):
                    start_time = self._format_time(translation["start_time"])
                    end_time = self._format_time(translation["end_time"])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{translation['translated_text']}\n\n")
            
            logger.info(f"翻译SRT文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存翻译SRT文件失败: {e}")
            return False
    
    def _save_translations_vtt(self, translations: List[Dict[str, Any]], output_path: str) -> bool:
        """保存翻译结果为VTT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                for translation in translations:
                    start_time = self._format_time_vtt(translation["start_time"])
                    end_time = self._format_time_vtt(translation["end_time"])
                    
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{translation['translated_text']}\n\n")
            
            logger.info(f"翻译VTT文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存翻译VTT文件失败: {e}")
            return False
    
    def _save_translations_json(self, result: Dict[str, Any], output_path: str) -> bool:
        """保存翻译结果为JSON格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"翻译JSON文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存翻译JSON文件失败: {e}")
            return False
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """格式化时间为VTT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"