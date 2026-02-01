#!/usr/bin/env python3
"""
API 密钥测试脚本
"""

import os
import dashscope

def test_api_key():
    """测试 API 密钥"""
    print("🔑 测试 API 密钥...")
    
    # 检查环境变量
    env_key = os.environ.get('DASHSCOPE_API_KEY')
    if env_key:
        print(f"✅ 环境变量中的 API 密钥: {env_key[:10]}...")
        dashscope.api_key = env_key
    else:
        print("❌ 环境变量中没有找到 API 密钥")
        return False
    
    try:
        # 测试简单的 API 调用
        from dashscope import Generation
        
        response = Generation.call(
            model='qwen3-omni-flash-realtime',
            messages=[
                {
                    'role': 'user',
                    'content': '你好'
                }
            ],
            parameters={
                'max_tokens': 10,
                'temperature': 0.1
            }
        )
        
        print(f"📊 API 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 密钥有效")
            return True
        else:
            print(f"❌ API 密钥无效: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试时发生错误: {e}")
        return False

def test_models_list():
    """测试获取模型列表"""
    print("\n📋 测试获取模型列表...")
    
    try:
        from dashscope import Models
        
        response = Models.list()
        
        print(f"📊 API 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 获取模型列表成功")
            print(f"📄 响应内容: {response}")
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 获取模型列表时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🔑 API 密钥测试")
    print("=" * 30)
    
    # 测试 API 密钥
    key_success = test_api_key()
    
    # 测试模型列表
    models_success = test_models_list()
    
    print("\n" + "=" * 30)
    print(f"📊 测试结果:")
    print(f"   - API 密钥: {'✅ 有效' if key_success else '❌ 无效'}")
    print(f"   - 模型列表: {'✅ 成功' if models_success else '❌ 失败'}")
    
    if key_success and models_success:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💡 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)