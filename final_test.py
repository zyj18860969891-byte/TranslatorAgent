#!/usr/bin/env python3
"""
最终测试脚本
"""

import os
import dashscope
from dashscope import Generation

def test_qwen_models():
    """测试 Qwen 模型"""
    print("🧪 测试 Qwen 模型...")
    
    # 设置环境变量
    os.environ['DASHSCOPE_API_KEY'] = 'sk-88bf1bd605544d208c7338cb1989ab3e'
    
    # 测试不同的模型
    models = ['qwen-turbo', 'qwen-plus', 'qwen-max']
    
    for model in models:
        try:
            print(f"\n🔄 测试模型: {model}")
            
            response = Generation.call(
                model=model,
                messages=[{'role': 'user', 'content': '你好'}],
                parameters={'max_tokens': 10, 'temperature': 0.1}
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功")
                print(f"📝 响应: {response.output.choices[0].message.content}")
                return True
            else:
                print(f"❌ 失败: {response.message}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    return False

def test_qwen3_models():
    """测试 Qwen3 模型"""
    print("\n🧪 测试 Qwen3 模型...")
    
    # 测试 Qwen3 模型
    models = ['qwen3-omni-flash-2025-12-01', 'qwen3-omni-flash-realtime']
    
    for model in models:
        try:
            print(f"\n🔄 测试模型: {model}")
            
            response = Generation.call(
                model=model,
                messages=[{'role': 'user', 'content': '你好'}],
                parameters={'max_tokens': 10, 'temperature': 0.1}
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功")
                print(f"📝 响应: {response.output.choices[0].message.content}")
                return True
            else:
                print(f"❌ 失败: {response.message}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    return False

def main():
    """主函数"""
    print("🚀 DashScope 最终测试")
    print("=" * 40)
    
    # 测试 Qwen 模型
    qwen_success = test_qwen_models()
    
    # 测试 Qwen3 模型
    qwen3_success = test_qwen3_models()
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果:")
    print(f"   - Qwen 模型: {'✅ 通过' if qwen_success else '❌ 失败'}")
    print(f"   - Qwen3 模型: {'✅ 通过' if qwen3_success else '❌ 失败'}")
    
    if qwen_success or qwen3_success:
        print("🎉 至少有一个模型测试成功！")
        return True
    else:
        print("💡 所有模型测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)