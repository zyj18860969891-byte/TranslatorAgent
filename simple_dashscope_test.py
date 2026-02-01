#!/usr/bin/env python3
"""
简单的 DashScope 测试脚本
"""

import dashscope
from dashscope import Generation

def test_qwen3_model():
    """测试 Qwen3 模型"""
    print("🧪 测试 Qwen3-Omni-Flash 模型...")
    
    # 设置 API 密钥
    api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
    dashscope.api_key = api_key
    
    try:
        # 测试文本生成
        response = Generation.call(
            model='qwen3-omni-flash-realtime',
            messages=[
                {
                    'role': 'user',
                    'content': '你好，请简单介绍一下自己'
                }
            ],
            parameters={
                'max_tokens': 100,
                'temperature': 0.1
            }
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content.strip()
            print("✅ Qwen3 模型测试成功")
            print(f"📝 响应: {content}")
            return True
        else:
            print(f"❌ 测试失败: {response.status_code}")
            print(f"📄 错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试时发生错误: {e}")
        return False

def test_available_models():
    """测试获取可用模型列表"""
    print("\n📋 测试获取可用模型列表...")
    
    try:
        from dashscope import Models
        
        response = Models.list()
        
        if response.status_code == 200:
            models = response.output.models
            qwen_models = [m for m in models if 'qwen' in m.model.lower()]
            
            print("✅ 获取模型列表成功")
            print(f"📊 总模型数: {len(models)}")
            print(f"🔍 Qwen 模型数: {len(qwen_models)}")
            
            print("\n📝 前 10 个模型:")
            for i, model in enumerate(models[:10]):
                print(f"   {i+1}. {model.model} - {model.description}")
            
            print(f"\n🔍 Qwen 模型:")
            for model in qwen_models[:5]:  # 只显示前5个
                print(f"   - {model.model}")
            
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            print(f"📄 错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 获取模型列表时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 DashScope 简单测试")
    print("=" * 40)
    
    # 测试获取模型列表
    models_success = test_available_models()
    
    # 测试 Qwen3 模型
    qwen3_success = test_qwen3_model()
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果:")
    print(f"   - 模型列表: {'✅ 通过' if models_success else '❌ 失败'}")
    print(f"   - Qwen3 模型: {'✅ 通过' if qwen3_success else '❌ 失败'}")
    
    if models_success and qwen3_success:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💡 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)