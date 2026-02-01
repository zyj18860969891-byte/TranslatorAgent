#!/usr/bin/env python3
"""
简单的 API 测试脚本
"""

import dashscope
from dashscope import Generation

def test_api():
    """测试 API"""
    print("🧪 测试 DashScope API...")
    
    # 设置 API 密钥
    api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
    dashscope.api_key = api_key
    
    try:
        # 测试简单的 API 调用
        response = Generation.call(
            model='qwen3-omni-flash-2025-12-01',
            messages=[{'role': 'user', 'content': '你好'}],
            parameters={'max_tokens': 10, 'temperature': 0.1}
        )
        
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 成功")
            print(f"响应: {response.output.choices[0].message.content}")
            return True
        else:
            print(f"❌ 失败: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    test_api()