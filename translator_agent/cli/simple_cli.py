#!/usr/bin/env python3
"""
简化的CLI工具

不依赖click库的纯Python实现
"""

import sys
import argparse
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ..core.translator import Translator
from ..core.modelscope_integration import ModelScopeClient
from ..data.video_processor import VideoProcessor
from ..data.subtitle_processor import SubtitleProcessor
from ..config.settings import ConfigManager


class SimpleCLI:
    """简化的CLI工具"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.translator = None
        self.modelscope_client = None
        self.video_processor = None
        self.subtitle_processor = None
    
    def get_translator(self):
        """获取翻译器实例"""
        if self.translator is None:
            self.translator = Translator()
        return self.translator
    
    def get_modelscope_client(self):
        """获取ModelScope客户端实例"""
        if self.modelscope_client is None:
            self.modelscope_client = ModelScopeClient()
        return self.modelscope_client
    
    def get_video_processor(self):
        """获取视频处理器实例"""
        if self.video_processor is None:
            self.video_processor = VideoProcessor()
        return self.video_processor
    
    def get_subtitle_processor(self):
        """获取字幕处理器实例"""
        if self.subtitle_processor is None:
            self.subtitle_processor = SubtitleProcessor()
        return self.subtitle_processor
    
    async def translate(self, text, source, target, model, temperature, max_tokens):
        """文本翻译"""
        try:
            print(f"正在翻译: {text}")
            print(f"源语言: {source} -> 目标语言: {target}")
            
            from ..core.translator import TranslationRequest, Language, TranslationEngine
            
            translator = self.get_translator()
            request = TranslationRequest(
                text=text,
                source_lang=Language.ENGLISH if source == 'en' else Language.CHINESE,
                target_lang=Language.CHINESE if target == 'zh' else Language.ENGLISH,
                engine=TranslationEngine.CUSTOM
            )
            result = await translator.translate_async(request)
            
            print("\n翻译结果:")
            print(f"原文: {text}")
            print(f"译文: {result.translated_text}")
            print(f"源语言: {result.source_lang.value}")
            print(f"目标语言: {result.target_lang.value}")
            print(f"引擎: {result.engine.value}")
            print(f"置信度: {result.confidence:.2f}")
            if result.metadata:
                print(f"元数据: {result.metadata}")
            
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            raise
    
    async def health(self):
        """健康检查"""
        try:
            print("正在执行健康检查...")
            
            # 检查翻译服务
            try:
                from ..core.translator import TranslationRequest, Language, TranslationEngine
                translator = self.get_translator()
                request = TranslationRequest(
                    text="test",
                    source_lang=Language.ENGLISH,
                    target_lang=Language.CHINESE,
                    engine=TranslationEngine.CUSTOM
                )
                result = await translator.translate_async(request)
                if result.translated_text:
                    print("✓ 翻译服务: 正常")
                else:
                    print(f"✗ 翻译服务: 异常 - 翻译结果为空")
            except Exception as e:
                print(f"✗ 翻译服务: 异常 - {str(e)}")
            
            # 检查 ModelScope 服务
            try:
                modelscope_client = self.get_modelscope_client()
                await modelscope_client.list_models()
                print("✓ ModelScope 服务: 正常")
            except Exception as e:
                print(f"✗ ModelScope 服务: 异常 - {str(e)}")
            
            # 检查视频处理服务
            try:
                video_processor = self.get_video_processor()
                print("✓ 视频处理服务: 正常")
            except Exception as e:
                print(f"✗ 视频处理服务: 异常 - {str(e)}")
            
            # 检查字幕处理服务
            try:
                subtitle_processor = self.get_subtitle_processor()
                print("✓ 字幕处理服务: 正常")
            except Exception as e:
                print(f"✗ 字幕处理服务: 异常 - {str(e)}")
            
            print("\n健康检查完成!")
            
        except Exception as e:
            print(f"健康检查失败: {str(e)}")
            raise
    
    async def config(self):
        """显示配置信息"""
        try:
            config_data = self.config_manager.get_config()
            
            print("当前配置:")
            print("-" * 40)
            
            for key, value in config_data.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key}: {sub_value}")
                else:
                    print(f"{key}: {value}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"获取配置失败: {str(e)}")
            raise
    
    async def list_models(self, model=None):
        """列出可用模型"""
        try:
            print("正在获取可用模型...")
            
            modelscope_client = self.get_modelscope_client()
            models = await modelscope_client.list_models()
            
            if model:
                # 过滤特定模型
                filtered_models = [m for m in models if model.lower() in m.get('name', '').lower()]
                models = filtered_models
            
            if not models:
                print("未找到可用模型")
                return
            
            print(f"\n找到 {len(models)} 个可用模型:")
            print("-" * 80)
            
            for model_info in models:
                name = model_info.get('name', 'Unknown')
                description = model_info.get('description', 'No description')
                languages = model_info.get('supported_languages', [])
                capabilities = model_info.get('capabilities', [])
                
                print(f"名称: {name}")
                print(f"描述: {description}")
                if languages:
                    print(f"支持语言: {', '.join(languages)}")
                if capabilities:
                    print(f"能力: {', '.join(capabilities)}")
                print("-" * 80)
            
        except Exception as e:
            print(f"获取模型列表失败: {str(e)}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Translator Agent CLI 工具')
    parser.add_argument('command', help='要执行的命令')
    parser.add_argument('--text', help='要翻译的文本')
    parser.add_argument('--source', '-s', default='auto', help='源语言')
    parser.add_argument('--target', '-t', help='目标语言')
    parser.add_argument('--model', '-m', help='使用的模型')
    parser.add_argument('--temperature', type=float, default=0.7, help='生成温度')
    parser.add_argument('--max-tokens', type=int, default=1000, help='最大令牌数')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    cli = SimpleCLI()
    
    try:
        if args.command == 'translate':
            if not args.text or not args.target:
                print("错误: translate 命令需要 --text 和 --target 参数")
                return
            
            asyncio.run(cli.translate(
                args.text, args.source, args.target, 
                args.model, args.temperature, args.max_tokens
            ))
        
        elif args.command == 'health':
            asyncio.run(cli.health())
        
        elif args.command == 'config':
            asyncio.run(cli.config())
        
        elif args.command == 'list-models':
            asyncio.run(cli.list_models(args.model))
        
        else:
            print(f"未知命令: {args.command}")
            print("可用命令: translate, health, config, list-models")
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()