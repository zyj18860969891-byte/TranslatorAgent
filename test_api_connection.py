"""
测试百炼API连接性
测试两种API密钥格式哪种能连通
"""

import os
import sys
from openai import OpenAI

def test_api_connection(api_key: str, test_name: str) -> bool:
    """测试API连接"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"API密钥: {api_key[:20]}...")
    print(f"{'='*60}")
    
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 测试简单调用
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=50
        )
        
        print(f"✅ 连接成功！")
        print(f"响应: {response.choices[0].message.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def main():
    print("🧪 百炼API连接性测试")
    print("="*60)
    
    # 测试1: 百炼API密钥
    api_key_1 = "sk-88bf1bd605544d208c7338cb1989ab3e"
    result_1 = test_api_connection(api_key_1, "百炼API密钥")
    
    # 测试2: 阿里云AccessKey
    api_key_2 = "LTAI5t6TBo9HDHq7eHoqd2dN"
    result_2 = test_api_connection(api_key_2, "阿里云AccessKey")
    
    # 测试3: AccessKey:Secret格式
    api_key_3 = "LTAI5t6TBo9HDHq7eHoqd2dN:r2AYxKTIgYaToNFVRESy03t0VLylj3"
    result_3 = test_api_connection(api_key_3, "AccessKey:Secret格式")
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")
    print(f"百炼API密钥: {'✅ 通过' if result_1 else '❌ 失败'}")
    print(f"阿里云AccessKey: {'✅ 通过' if result_2 else '❌ 失败'}")
    print(f"AccessKey:Secret: {'✅ 通过' if result_3 else '❌ 失败'}")
    
    if result_1:
        print(f"\n🎉 推荐使用百炼API密钥: {api_key_1}")
        print(f"配置方式: $env:DASHSCOPE_API_KEY = \"{api_key_1}\"")
    elif result_2:
        print(f"\n⚠️  百炼API密钥失败，但AccessKey可以使用")
        print(f"配置方式: $env:DASHSCOPE_API_KEY = \"{api_key_2}\"")
    else:
        print(f"\n❌ 所有测试都失败，请检查:")
        print(f"1. 网络连接")
        print(f"2. API密钥是否正确")
        print(f"3. 是否开通了百炼服务")

if __name__ == "__main__":
    main()
