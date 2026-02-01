#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的模型可用性检查
"""

import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fixed_model_availability():
    """测试修复后的模型可用性检查"""
    print("🔍 测试修复后的模型可用性检查...")
    print("=" * 60)
    
    try:
        # 添加qwen3_integration模块路径
        sys.path.append('.')
        
        from qwen3_integration.config import check_model_availability
        
        print("✅ 成功导入check_model_availability函数")
        
        # 调用修复后的函数
        result = check_model_availability()
        
        print(f"\n📊 修复后的检查结果:")
        print(f"  可用模型: {result.get('available', [])}")
        print(f"  不可用模型: {result.get('unavailable', [])}")
        print(f"  总模型数: {result.get('total_models', 0)}")
        print(f"  错误信息: {result.get('error', '无')}")
        
        # 分析结果
        available_count = len(result.get('available', []))
        unavailable_count = len(result.get('unavailable', []))
        
        print(f"\n📈 结果分析:")
        print(f"  可用模型数量: {available_count}")
        print(f"  不可用模型数量: {unavailable_count}")
        
        if available_count > 0:
            print(f"  ✅ 至少有一个模型可用，系统应该正常工作")
        else:
            print(f"  ⚠️ 没有可用模型，可能影响系统功能")
            
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return None

def check_qwen3_integration_status():
    """检查qwen3_integration模块状态"""
    print("\n" + "=" * 60)
    print("🔍 检查qwen3_integration模块状态...")
    
    try:
        # 测试导入
        from qwen3_integration import check_model_availability
        print("✅ qwen3_integration模块导入成功")
        
        # 测试函数调用
        result = check_model_availability()
        print(f"✅ check_model_availability函数调用成功")
        
        # 显示详细信息
        print(f"\n📋 详细信息:")
        print(f"  可用模型: {result.get('available', [])}")
        print(f"  不可用模型: {result.get('unavailable', [])}")
        
        # 分析"3个不可用"的具体含义
        unavailable = result.get('unavailable', [])
        if len(unavailable) == 3:
            print(f"\n🎯 '3个不可用'的具体含义:")
            print(f"  这表示系统检查了3个目标模型:")
            for i, model in enumerate(unavailable, 1):
                print(f"    {i}. {model}")
            print(f"  所有这些模型在当前配置下都不可用")
        else:
            print(f"\n📊 实际不可用模型数量: {len(unavailable)}")
            print(f"  不可用模型列表: {unavailable}")
        
        return result
        
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 开始验证修复后的模型可用性检查")
    print("=" * 60)
    
    # 测试修复后的函数
    result1 = test_fixed_model_availability()
    
    # 检查模块状态
    result2 = check_qwen3_integration_status()
    
    print("\n" + "=" * 60)
    print("🎉 验证完成")
    
    if result1 and result2:
        print("✅ 修复成功！模型可用性检查现在应该能正确显示结果")
    else:
        print("❌ 修复仍有问题，需要进一步调试")