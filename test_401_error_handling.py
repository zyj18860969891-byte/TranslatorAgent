#!/usr/bin/env python3
"""
测试401错误处理
"""

import sys
import os
sys.path.append('.')

def test_401_error_handling():
    """测试401错误处理"""
    try:
        # 设置一个无效的API密钥来触发401错误
        os.environ['DASHSCOPE_API_KEY'] = 'invalid_api_key'
        
        from processing_service.qwen3_integration.config import check_model_availability
        
        print("测试401错误处理...")
        result = check_model_availability()
        
        print(f"结果类型: {type(result)}")
        print(f"结果内容: {result}")
        
        # 验证返回值结构
        if isinstance(result, dict):
            print("✅ 返回值是字典类型")
            if 'available' in result and 'unavailable' in result:
                print("✅ 包含 'available' 和 'unavailable' 键")
                print(f"可用模型: {result['available']}")
                print(f"不可用模型: {result['unavailable']}")
                if 'error' in result:
                    print(f"错误信息: {result['error']}")
                    if 'API认证失败' in result['error']:
                        print("✅ 正确处理了401错误")
                    else:
                        print("❌ 401错误处理不正确")
                else:
                    print("❌ 缺少错误信息")
            else:
                print("❌ 缺少必要的键")
        else:
            print("❌ 返回值不是字典类型")
            
    except Exception as e:
        print(f"❌ 测试401错误处理失败: {e}")

if __name__ == "__main__":
    print("开始测试401错误处理...")
    test_401_error_handling()
    print("\n测试完成")