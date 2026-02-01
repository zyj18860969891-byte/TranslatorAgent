#!/usr/bin/env python3
"""
Translator Agent 主程序入口

基于 NotebookLM 文档驱动开发
功能: 协调所有模块，提供统一的翻译和视频处理接口
"""

import asyncio
import logging
import argparse
from pathlib import Path
from typing import Optional

# 导入配置管理
from config.settings import ConfigManager, AppConfig

# 导入核心模块
from core.translator import TranslatorFactory, TranslationEngine, Language
from core.modelscope_integration import ModelScopeClient, MultiModelCoordinator
from core.agent import TranslatorAgent, VideoTranslatorAgent, SupervisorAgent
from data.video_processor import VideoProcessor, VideoProcessingConfig


# 配置日志（使用配置管理器）
config = ConfigManager.get_config()
config.setup_logging()
logger = logging.getLogger(__name__)


class TranslatorAgentApp:
    """Translator Agent 应用程序"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config or ConfigManager.get_config()
        
        # 验证配置
        errors = self.config.validate()
        if errors:
            self.logger.warning(f"Configuration warnings: {errors}")
        
        # 初始化客户端
        self.model_client = ModelScopeClient(self.config.modelscope)
        self.video_processor = VideoProcessor(self.config.video_processing)
        self.coordinator = MultiModelCoordinator(self.model_client)
        
        # 初始化智能体
        self.translator_agent = TranslatorAgent(
            translator_client=None,  # 暂时为 None，使用 model_client
            model_client=self.model_client
        )
        
        self.video_agent = VideoTranslatorAgent(
            video_processor=self.video_processor,
            model_client=self.model_client,
            translator_agent=self.translator_agent
        )
        
        self.supervisor = SupervisorAgent(
            translator_agent=self.translator_agent,
            video_agent=self.video_agent
        )
        
        self.logger.info(f"Translator Agent initialized (env: {self.config.environment.value})")
    
    async def translate_text(self, text: str, source_lang: str = "en", 
                            target_lang: str = "zh") -> str:
        """翻译文本"""
        self.logger.info(f"Translating text: {text[:50]}...")
        
        try:
            result = await self.translator_agent.run({
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "enable_emotion_analysis": False
            })
            
            if "act_result" in result and "translated_text" in result["act_result"]:
                return result["act_result"]["translated_text"]
            else:
                # 回退到直接调用
                return await self.model_client.translate(text, source_lang, target_lang)
                
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise
    
    async def process_video(self, video_path: str, source_lang: str = "en", 
                           target_lang: str = "zh") -> dict:
        """处理视频"""
        self.logger.info(f"Processing video: {video_path}")
        
        try:
            result = await self.video_agent.run({
                "video_path": video_path,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "enable_subtitle_extraction": True,
                "enable_subtitle_erasure": False,
                "enable_emotion_analysis": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            raise
    
    async def run_supervisor_task(self, task_type: str, **kwargs) -> dict:
        """运行主管智能体任务"""
        self.logger.info(f"Running supervisor task: {task_type}")
        
        context = {"task_type": task_type, **kwargs}
        
        try:
            result = await self.supervisor.run(context)
            return result
        except Exception as e:
            self.logger.error(f"Supervisor task failed: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Translator Agent - 基于 NotebookLM 的翻译智能体")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 翻译命令
    translate_parser = subparsers.add_parser("translate", help="翻译文本")
    translate_parser.add_argument("--text", required=True, help="要翻译的文本")
    translate_parser.add_argument("--source-lang", default="en", help="源语言")
    translate_parser.add_argument("--target-lang", default="zh", help="目标语言")
    
    # 视频处理命令
    video_parser = subparsers.add_parser("process-video", help="处理视频")
    video_parser.add_argument("--video-path", required=True, help="视频文件路径")
    video_parser.add_argument("--source-lang", default="en", help="源语言")
    video_parser.add_argument("--target-lang", default="zh", help="目标语言")
    
    # 测试命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    app = TranslatorAgentApp()
    
    async def run_command():
        if args.command == "translate":
            try:
                result = await app.translate_text(
                    text=args.text,
                    source_lang=args.source_lang,
                    target_lang=args.target_lang
                )
                print(f"翻译结果: {result}")
            except Exception as e:
                print(f"翻译失败: {e}")
        
        elif args.command == "process-video":
            try:
                result = await app.process_video(
                    video_path=args.video_path,
                    source_lang=args.source_lang,
                    target_lang=args.target_lang
                )
                print(f"视频处理结果: {result}")
            except Exception as e:
                print(f"视频处理失败: {e}")
        
        elif args.command == "test":
            print("=== 测试 Translator Agent ===")
            
            # 测试文本翻译
            print("\n1. 测试文本翻译:")
            try:
                result = await app.translate_text("Hello, world!", "en", "zh")
                print(f"   结果: {result}")
            except Exception as e:
                print(f"   失败: {e}")
            
            # 测试智能体
            print("\n2. 测试智能体:")
            try:
                result = await app.run_supervisor_task(
                    "text_translation",
                    text="This is a test.",
                    source_lang="en",
                    target_lang="zh"
                )
                print(f"   结果: {result}")
            except Exception as e:
                print(f"   失败: {e}")
            
            print("\n测试完成!")
    
    asyncio.run(run_command())


if __name__ == "__main__":
    main()
