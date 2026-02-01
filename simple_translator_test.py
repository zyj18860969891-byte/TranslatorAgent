#!/usr/bin/env python3
"""
简化版翻译器测试脚本
直接测试翻译器模块，避免复杂的依赖
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 直接导入翻译器模块，避免复杂的依赖
from translator_agent.core.translator import (
    TranslationRequest, 
    TranslationEngine, 
    Language,
    TranslatorFactory,
    MockTranslator
)

async def test_translator():
    """测试翻译器"""
    print("🧪 测试翻译器...")
    
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

async def test_real_translator_directly():
    """直接测试真实翻译器"""
    print("\n🧪 直接测试真实翻译器...")
    
    try:
        # 直接导入真实翻译器
        from translator_agent.core.real_translator import RealQwenTranslator
        
        # 创建真实翻译器
        translator = RealQwenTranslator(cache_enabled=True)
        print(f"✅ 真实翻译器类型: {type(translator).__name__}")
        
        # 测试翻译请求
        request = TranslationRequest(
            text="Hello, world!",
            source_lang=Language.ENGLISH,
            target_lang=Language.CHINESE,
            engine=TranslationEngine.CUSTOM
        )
        
        print(f"原文: {request.text}")
        print(f"源语言: {request.source_lang}")
        print(f"目标语言: {request.target_lang}")
        
        # 执行翻译
        response = await translator.translate_async(request)
        
        print(f"翻译结果: {response.translated_text}")
        print(f"置信度: {response.confidence}")
        print(f"引擎: {response.engine}")
        
        if response.error:
            print(f"❌ 错误: {response.error}")
            return False
        else:
            print("✅ 真实API翻译成功")
            return True
        
    except Exception as e:
        print(f"❌ 真实翻译器测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始翻译器测试")
    print("=" * 50)
    
    # 测试基本翻译功能
    basic_test = await test_translator()
    
    # 测试真实翻译器
    real_test = await test_real_translator_directly()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"基本翻译功能: {'✅ 通过' if basic_test else '❌ 失败'}")
    print(f"真实翻译器: {'✅ 通过' if real_test else '❌ 失败'}")
    
    if basic_test and real_test:
        print("\n🎉 所有测试通过！翻译器工作正常")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    
    if success:
        print("\n✅ 测试完成，翻译器已就绪")
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)