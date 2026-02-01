"""
Qwen3集成完整演示脚本
展示所有核心功能和工具的使用方法
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加qwen3_integration模块到路径
sys.path.append(str(Path(__file__).parent / "qwen3_integration"))

try:
    from qwen3_integration.config import get_config_manager, check_model_availability
    from qwen3_integration.utils import (
        setup_logging, validate_environment, clean_temp_files,
        get_image_utils, get_text_utils, get_file_utils
    )
    from qwen3_integration.subtitle_extractor import SubtitleExtractor
    from qwen3_integration.video_translator import VideoTranslator
    from qwen3_integration.emotion_analyzer import EmotionAnalyzer
    from qwen3_integration.batch_processor import BatchProcessor
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

class Qwen3IntegrationDemo:
    """Qwen3集成演示类"""
    
    def __init__(self):
        """初始化演示"""
        self.config_manager = get_config_manager()
        self.logger = setup_logging("Qwen3IntegrationDemo", logging.INFO)
        
        # 初始化组件
        self.subtitle_extractor = SubtitleExtractor()
        self.video_translator = VideoTranslator()
        self.emotion_analyzer = EmotionAnalyzer()
        self.batch_processor = BatchProcessor()
        
        # 工具实例
        self.image_utils = get_image_utils()
        self.text_utils = get_text_utils()
        self.file_utils = get_file_utils()
        
        self.logger.info("Qwen3集成演示初始化完成")
    
    def run_environment_check(self) -> Dict[str, Any]:
        """运行环境检查"""
        self.logger.info("开始环境检查...")
        
        # 验证环境
        env_validation = validate_environment()
        
        # 检查模型可用性
        model_availability = check_model_availability()
        
        # 验证配置
        config_validation = self.config_manager.validate_config()
        
        # 检查API连接
        api_check = self._check_api_connection()
        
        result = {
            "environment": env_validation,
            "model_availability": model_availability,
            "config_validation": config_validation,
            "api_connection": api_check
        }
        
        # 打印结果
        self.logger.info("环境检查结果:")
        self.logger.info(f"  环境验证: {'✅ 通过' if env_validation['valid'] else '❌ 失败'}")
        self.logger.info(f"  模型可用性: {len(model_availability['available'])} 个可用")
        self.logger.info(f"  配置验证: {'✅ 通过' if config_validation['valid'] else '❌ 失败'}")
        self.logger.info(f"  API连接: {'✅ 正常' if api_check['success'] else '❌ 失败'}")
        
        return result
    
    def _check_api_connection(self) -> Dict[str, Any]:
        """检查API连接"""
        try:
            import requests
            
            base_url = self.config_manager.get_env_config("dashscope_base_url") or "https://dashscope.aliyuncs.com"
            api_key = self.config_manager.get_env_config("dashscope_api_key")
            
            if not api_key:
                return {"success": False, "error": "未配置API密钥"}
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/api/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "API连接正常"}
            else:
                return {"success": False, "error": f"API请求失败: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"API连接检查失败: {str(e)}"}
    
    def run_subtitle_extraction_demo(self, video_path: str = None) -> Dict[str, Any]:
        """运行字幕提取演示"""
        self.logger.info("开始字幕提取演示...")
        
        # 如果没有提供视频路径，使用示例视频
        if not video_path:
            video_path = self._get_sample_video_path()
        
        if not video_path:
            return {"success": False, "error": "未找到示例视频"}
        
        try:
            # 提取字幕
            result = self.subtitle_extractor.extract(video_path)
            
            if result["success"]:
                self.logger.info(f"字幕提取成功: {len(result.get('subtitles', []))} 条字幕")
                
                # 保存字幕文件
                subtitle_file = f"extracted_subtitles.srt"
                self.file_utils.save_json(result, subtitle_file.replace('.srt', '.json'))
                
                # 显示部分字幕
                subtitles = result.get('subtitles', [])
                if subtitles:
                    self.logger.info("前5条字幕:")
                    for i, subtitle in enumerate(subtitles[:5]):
                        self.logger.info(f"  {i+1}. {subtitle['text']}")
                
                return {
                    "success": True,
                    "subtitles_count": len(subtitles),
                    "subtitle_file": subtitle_file,
                    "sample_subtitles": subtitles[:3]
                }
            else:
                return {"success": False, "error": result.get("error", "未知错误")}
                
        except Exception as e:
            self.logger.error(f"字幕提取演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_video_translation_demo(self, video_path: str = None) -> Dict[str, Any]:
        """运行视频翻译演示"""
        self.logger.info("开始视频翻译演示...")
        
        # 如果没有提供视频路径，使用示例视频
        if not video_path:
            video_path = self._get_sample_video_path()
        
        if not video_path:
            return {"success": False, "error": "未找到示例视频"}
        
        try:
            # 翻译视频
            result = self.video Translator.translate(video_path, target_language="en")
            
            if result["success"]:
                self.logger.info(f"视频翻译成功: {result.get('translated_text', '')}")
                
                # 保存翻译结果
                translation_file = f"translated_video.json"
                self.file_utils.save_json(result, translation_file)
                
                return {
                    "success": True,
                    "translation_file": translation_file,
                    "translated_text": result.get('translated_text', '')[:200] + "..."
                }
            else:
                return {"success": False, "error": result.get("error", "未知错误")}
                
        except Exception as e:
            self.logger.error(f"视频翻译演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_emotion_analysis_demo(self, text: str = None) -> Dict[str, Any]:
        """运行情感分析演示"""
        self.logger.info("开始情感分析演示...")
        
        # 如果没有提供文本，使用示例文本
        if not text:
            text = "今天天气真好，我感到非常开心和兴奋！"
        
        try:
            # 分析情感
            result = self.emotion_analyzer.analyze(text)
            
            if result["success"]:
                self.logger.info(f"情感分析成功: {result.get('emotions', {})}")
                
                # 保存分析结果
                emotion_file = f"emotion_analysis.json"
                self.file_utils.save_json(result, emotion_file)
                
                return {
                    "success": True,
                    "emotion_file": emotion_file,
                    "emotions": result.get('emotions', {}),
                    "dominant_emotion": result.get('dominant_emotion', 'neutral')
                }
            else:
                return {"success": False, "error": result.get("error", "未知错误")}
                
        except Exception as e:
            self.logger.error(f"情感分析演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_batch_processing_demo(self, video_paths: List[str] = None) -> Dict[str, Any]:
        """运行批量处理演示"""
        self.logger.info("开始批量处理演示...")
        
        # 如果没有提供视频路径，使用示例视频
        if not video_paths:
            video_paths = [self._get_sample_video_path()]
        
        if not video_paths or not video_paths[0]:
            return {"success": False, "error": "未找到示例视频"}
        
        try:
            # 批量处理
            result = self.batch_processor.process_video_files(video_paths)
            
            if result["success"]:
                self.logger.info(f"批量处理完成: {result.get('processed_count', 0)} 个文件")
                
                # 保存处理结果
                batch_file = f"batch_processing_results.json"
                self.file_utils.save_json(result, batch_file)
                
                return {
                    "success": True,
                    "batch_file": batch_file,
                    "processed_count": result.get('processed_count', 0),
                    "failed_count": result.get('failed_count', 0),
                    "results": result.get('results', [])[:3]  # 只显示前3个结果
                }
            else:
                return {"success": False, "error": result.get("error", "未知错误")}
                
        except Exception as e:
            self.logger.error(f"批量处理演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_text_processing_demo(self) -> Dict[str, Any]:
        """运行文本处理演示"""
        self.logger.info("开始文本处理演示...")
        
        try:
            # 示例文本
            sample_text = """
            今天天气真好，阳光明媚，我感到非常开心和兴奋！
            我们一起去公园散步，看到了美丽的花朵和绿树。
            孩子们在草地上奔跑嬉戏，笑声传遍了整个公园。
            这真是一个美好的日子，让人心情愉悦。
            """
            
            # 清理文本
            cleaned_text = self.text_utils.clean_text(sample_text)
            self.logger.info(f"清理后的文本: {cleaned_text[:100]}...")
            
            # 分割文本
            text_chunks = self.text_utils.split_text(cleaned_text, max_length=100)
            self.logger.info(f"文本分割为 {len(text_chunks)} 个片段")
            
            # 检测语言
            language = self.text_utils.detect_language(cleaned_text)
            self.logger.info(f"检测到的语言: {language}")
            
            # 提取情感
            emotions = self.text_utils.extract_emotions(cleaned_text)
            self.logger.info(f"提取的情感: {emotions}")
            
            return {
                "success": True,
                "original_text": sample_text,
                "cleaned_text": cleaned_text,
                "text_chunks": text_chunks,
                "language": language,
                "emotions": emotions
            }
            
        except Exception as e:
            self.logger.error(f"文本处理演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_image_processing_demo(self) -> Dict[str, Any]:
        """运行图像处理演示"""
        self.logger.info("开始图像处理演示...")
        
        try:
            # 获取示例图像路径
            image_path = self._get_sample_image_path()
            
            if not image_path:
                return {"success": False, "error": "未找到示例图像"}
            
            # 调整图像大小
            resized_image = self.image_utils.resize_image(image_path)
            self.logger.info(f"图像调整大小: {image_path} -> {resized_image}")
            
            # 转换为Base64
            base64_image = self.image_utils.image_to_base64(resized_image)
            self.logger.info(f"Base64编码长度: {len(base64_image)}")
            
            # 创建图像消息
            image_message = self.image_utils.create_image_message(resized_image, "请描述这张图像")
            self.logger.info(f"图像消息创建成功: {len(image_message)} 个元素")
            
            return {
                "success": True,
                "original_image": image_path,
                "resized_image": resized_image,
                "base64_length": len(base64_image),
                "message_created": True
            }
            
        except Exception as e:
            self.logger.error(f"图像处理演示失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_sample_video_path(self) -> Optional[str]:
        """获取示例视频路径"""
        # 在实际应用中，这里应该返回真实的视频文件路径
        # 这里返回None，表示没有示例视频
        return None
    
    def _get_sample_image_path(self) -> Optional[str]:
        """获取示例图像路径"""
        # 在实际应用中，这里应该返回真实的图像文件路径
        # 这里返回None，表示没有示例图像
        return None
    
    def run_complete_demo(self) -> Dict[str, Any]:
        """运行完整演示"""
        self.logger.info("开始完整演示...")
        
        demo_results = {}
        
        # 1. 环境检查
        demo_results["environment_check"] = self.run_environment_check()
        
        # 2. 文本处理演示
        demo_results["text_processing"] = self.run_text_processing_demo()
        
        # 3. 图像处理演示
        demo_results["image_processing"] = self.run_image_processing_demo()
        
        # 4. 字幕提取演示
        demo_results["subtitle_extraction"] = self.run_subtitle_extraction_demo()
        
        # 5. 视频翻译演示
        demo_results["video_translation"] = self.run_video_translation_demo()
        
        # 6. 情感分析演示
        demo_results["emotion_analysis"] = self.run_emotion_analysis_demo()
        
        # 7. 批量处理演示
        demo_results["batch_processing"] = self.run_batch_processing_demo()
        
        # 清理临时文件
        clean_temp_files()
        
        # 保存完整演示结果
        demo_file = "complete_demo_results.json"
        self.file_utils.save_json(demo_results, demo_file)
        
        self.logger.info(f"完整演示完成，结果已保存到: {demo_file}")
        
        return demo_results
    
    def print_summary(self, results: Dict[str, Any]):
        """打印演示摘要"""
        print("\n" + "="*60)
        print("Qwen3集成演示摘要")
        print("="*60)
        
        for demo_name, result in results.items():
            if isinstance(result, dict) and "success" in result:
                status = "✅ 成功" if result["success"] else "❌ 失败"
                print(f"{demo_name}: {status}")
                
                if not result["success"]:
                    error = result.get("error", "未知错误")
                    print(f"  错误: {error}")
                else:
                    # 显示一些成功信息
                    if "subtitles_count" in result:
                        print(f"  字幕数量: {result['subtitles_count']}")
                    elif "processed_count" in result:
                        print(f"  处理数量: {result['processed_count']}")
                    elif "emotions" in result:
                        dominant = result.get("dominant_emotion", "unknown")
                        print(f"  主要情感: {dominant}")
        
        print("="*60)

def main():
    """主函数"""
    print("Qwen3集成完整演示")
    print("="*60)
    
    # 创建演示实例
    demo = Qwen3IntegrationDemo()
    
    # 运行完整演示
    results = demo.run_complete_demo()
    
    # 打印摘要
    demo.print_summary(results)
    
    print("\n演示完成！")

if __name__ == "__main__":
    main()