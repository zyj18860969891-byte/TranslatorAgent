#!/usr/bin/env python3
import os
import requests

def test_qwen3_connection():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    url = "https://dashscope.aliyuncs.com/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "qwen3-omni-flash-realtime",
        "messages": [{"role": "user", "content": "请简单介绍一下自己"}],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Qwen3-Omni-Flash 连接成功")
            print(f"响应: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f"❌ 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_qwen3_connection()
