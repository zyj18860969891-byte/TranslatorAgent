#!/usr/bin/env python3
"""
测试模型可用性检查修复
"""

import sys
import os
sys.path.append('.')

def test_processing_service_config():
    """测试处理服务配置"""
    try:
        from processing_service.qwen3_integration.config import check_model_availability
        
        print("测试处理服务配置...")
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
            else:
                print("❌ 缺少必要的键")
        else:
            print("❌ 返回值不是字典类型")
            
    except Exception as e:
        print(f"❌ 测试处理服务配置失败: {e}")

def test_main_config():
    """测试主配置"""
    try:
        from qwen3_integration.config import check_model_availability as check_model_availability_main
        
        print("\n测试主配置...")
        result = check_model_availability_main()
        
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
            else:
                print("❌ 缺少必要的键")
        else:
            print("❌ 返回值不是字典类型")
            
    except Exception as e:
        print(f"❌ 测试主配置失败: {e}")

if __name__ == "__main__":
    print("开始测试模型可用性检查修复...")
    test_processing_service_config()
    test_main_config()
    print("\n测试完成")