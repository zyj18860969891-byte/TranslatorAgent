#!/usr/bin/env python3
"""
最终测试：验证TypeError修复
"""

import sys
import os
sys.path.append('.')

def test_init_module():
    """测试__init__.py模块初始化"""
    try:
        # 设置一个无效的API密钥来触发401错误
        os.environ['DASHSCOPE_API_KEY'] = 'invalid_api_key'
        
        from processing_service.qwen3_integration import initialize
        
        print("测试__init__.py模块初始化...")
        result = initialize()
        
        if result:
            print("✅ 模块初始化成功")
        else:
            print("❌ 模块初始化失败")
            
    except Exception as e:
        print(f"❌ 测试__init__.py模块初始化失败: {e}")
        import traceback
        traceback.print_exc()

def test_with_valid_api():
    """测试使用有效的API密钥"""
    try:
        # 设置一个有效的API密钥（如果有）
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            print("⚠️  没有设置有效的API密钥，跳过有效API测试")
            return
            
        from processing_service.qwen3_integration import initialize
        
        print("测试使用有效的API密钥...")
        result = initialize()
        
        if result:
            print("✅ 模块初始化成功")
        else:
            print("❌ 模块初始化失败")
            
    except Exception as e:
        print(f"❌ 测试使用有效的API密钥失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始最终测试：验证TypeError修复...")
    test_init_module()
    test_with_valid_api()
    print("\n测试完成")