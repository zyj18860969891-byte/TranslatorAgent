#!/usr/bin/env python3
"""
API配置验证测试脚本
验证DASHSCOPE_API_KEY环境变量和API连接
"""

import os
from openai import OpenAI

def test_api_config():
    """测试API配置"""
    print("=== API配置验证测试 ===")
    
    # 检查环境变量
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ DASHSCOPE_API_KEY环境变量未设置")
        return False
    
    print(f"✅ DASHSCOPE_API_KEY已设置: {api_key[:20]}...")
    
    # 初始化API客户端
    try:
        client = OpenAI(
            api_key=api_key,
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
        )
        print("✅ API客户端初始化成功")
    except Exception as e:
        print(f"❌ API客户端初始化失败: {e}")
        return False
    
    # 测试API连接
    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": "请回复'连接成功'"}],
            max_tokens=10
        )
        print("✅ API连接测试成功")
        print(f"📝 API响应: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_api_config()
    if success:
        print("\n🎉 所有测试通过！API配置已就绪")
    else:
        print("\n⚠️  测试失败，请检查配置")