#!/usr/bin/env python3
"""
真实API翻译器测试脚本
验证真实API翻译器的功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from translator_agent.core.translator import (
    TranslationRequest, 
    TranslationEngine, 
    Language,
    TranslatorFactory
)

async def test_real_translator():
    """测试真实API翻译器"""
    print("🧪 测试真实API翻译器...")
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY环境变量未设置")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    try:
        # 获取翻译器
        translator = TranslatorFactory.get_translator(TranslationEngine.CUSTOM)
        print(f"✅ 翻译器类型: {type(translator).__name__}")
        
        # 测试翻译请求
        test_requests = [
            TranslationRequest(
                text="Hello, world!",
                source_lang=Language.ENGLISH,
                target_lang=Language.CHINESE,
                engine=TranslationEngine.CUSTOM
            ),
            TranslationRequest(
                text="你好，世界！",
                source_lang=Language.CHINESE,
                target_lang=Language.ENGLISH,
                engine=TranslationEngine.CUSTOM
            ),
            TranslationRequest(
                text="Bonjour le monde!",
                source_lang="fr",  # 使用字符串
                target_lang=Language.CHINESE,
                engine=TranslationEngine.CUSTOM
            )
        ]
        
        print("\n📝 开始翻译测试...")
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n--- 测试 {i} ---")
            print(f"原文: {request.text}")
            print(f"源语言: {request.source_lang}")
            print(f"目标语言: {request.target_lang}")
            
            try:
                # 执行翻译
                response = await translator.translate_async(request)
                
                print(f"翻译结果: {response.translated_text}")
                print(f"置信度: {response.confidence}")
                print(f"引擎: {response.engine}")
                
                if response.error:
                    print(f"❌ 错误: {response.error}")
                else:
                    print("✅ 翻译成功")
                
            except Exception as e:
                print(f"❌ 翻译失败: {e}")
        
        print("\n🎉 翻译测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_caching():
    """测试缓存功能"""
    print("\n🧪 测试缓存功能...")
    
    try:
        # 获取翻译器
        translator = TranslatorFactory.get_translator(TranslationEngine.CUSTOM)
        
        # 创建相同的翻译请求
        request = TranslationRequest(
            text="Hello, world!",
            source_lang=Language.ENGLISH,
            target_lang=Language.CHINESE,
            engine=TranslationEngine.CUSTOM
        )
        
        print("第一次翻译...")
        response1 = await translator.translate_async(request)
        print(f"结果: {response1.translated_text}")
        
        print("第二次翻译（应该使用缓存）...")
        response2 = await translator.translate_async(request)
        print(f"结果: {response2.translated_text}")
        
        if response1.translated_text == response2.translated_text:
            print("✅ 缓存功能正常")
            return True
        else:
            print("❌ 缓存功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 缓存测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始真实API翻译器测试")
    print("=" * 50)
    
    # 测试基本翻译功能
    basic_test = await test_real_translator()
    
    # 测试缓存功能
    cache_test = await test_caching()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"基本翻译功能: {'✅ 通过' if basic_test else '❌ 失败'}")
    print(f"缓存功能: {'✅ 通过' if cache_test else '❌ 失败'}")
    
    if basic_test and cache_test:
        print("\n🎉 所有测试通过！真实API翻译器工作正常")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    
    if success:
        print("\n✅ 测试完成，真实API翻译器已就绪")
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)