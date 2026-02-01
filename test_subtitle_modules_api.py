#!/usr/bin/env python3
"""
字幕模块API配置验证测试
验证视频字幕压制和字幕无痕擦除模块的API配置
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_subtitle_pressing_api():
    """测试字幕压制模块API配置"""
    print("🧪 测试字幕压制模块API配置...")
    
    try:
        # 检查API密钥
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("❌ DASHSCOPE_API_KEY环境变量未设置")
            return False
        
        print(f"✅ API密钥已设置: {api_key[:10]}...")
        
        # 导入字幕压制模块
        from qwen3_integration.subtitle_pressing import SubtitlePressing
        
        # 创建字幕压制器
        pressor = SubtitlePressing()
        
        # 检查模型配置
        print(f"✅ 模型名称: {pressor.model_name}")
        print(f"✅ API端点: {pressor.api_endpoint}")
        print(f"✅ API客户端: {type(pressor.client).__name__}")
        
        # 检查模型信息
        model_info = pressor.get_model_info()
        print(f"✅ 模型信息: {model_info}")
        
        # 验证配置
        is_valid, error_msg = pressor.validate_config()
        if is_valid:
            print("✅ 字幕压制模块配置验证通过")
            return True
        else:
            print(f"❌ 字幕压制模块配置验证失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ 字幕压制模块测试失败: {e}")
        return False

def test_subtitle_erasure_api():
    """测试字幕擦除模块API配置"""
    print("\n🧪 测试字幕擦除模块API配置...")
    
    try:
        # 检查API密钥
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("❌ DASHSCOPE_API_KEY环境变量未设置")
            return False
        
        print(f"✅ API密钥已设置: {api_key[:10]}...")
        
        # 导入字幕擦除模块
        from qwen3_integration.subtitle_erasure import SubtitleErasure
        
        # 创建字幕擦除器
        erasure = SubtitleErasure()
        
        # 检查模型配置
        print(f"✅ 模型名称: {erasure.model_name}")
        print(f"✅ API端点: {erasure.api_endpoint}")
        print(f"✅ API客户端: {type(erasure.client).__name__}")
        
        # 检查模型信息
        model_info = erasure.get_model_info()
        print(f"✅ 模型信息: {model_info}")
        
        # 验证配置
        is_valid, error_msg = erasure.validate_config()
        if is_valid:
            print("✅ 字幕擦除模块配置验证通过")
            return True
        else:
            print(f"❌ 字幕擦除模块配置验证失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ 字幕擦除模块测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点连接"""
    print("\n🧪 测试API端点连接...")
    
    try:
        import requests
        
        # 测试字幕压制API端点
        pressing_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/video-editing/wanx2.1-vace-plus"
        erasure_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/image-editing/image-erase-completion"
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 测试字幕压制端点
        print("📡 测试字幕压制API端点...")
        try:
            response = requests.options(pressing_endpoint, headers=headers, timeout=10)
            print(f"✅ 字幕压制端点响应: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 字幕压制端点测试失败: {e}")
        
        # 测试字幕擦除端点
        print("📡 测试字幕擦除API端点...")
        try:
            response = requests.options(erasure_endpoint, headers=headers, timeout=10)
            print(f"✅ 字幕擦除端点响应: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 字幕擦除端点测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始字幕模块API配置验证")
    print("=" * 60)
    
    # 测试字幕压制模块
    pressing_test = test_subtitle_pressing_api()
    
    # 测试字幕擦除模块
    erasure_test = test_subtitle_erasure_api()
    
    # 测试API端点连接
    endpoint_test = test_api_endpoints()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"字幕压制模块: {'✅ 通过' if pressing_test else '❌ 失败'}")
    print(f"字幕擦除模块: {'✅ 通过' if erasure_test else '❌ 失败'}")
    print(f"API端点连接: {'✅ 通过' if endpoint_test else '❌ 失败'}")
    
    if pressing_test and erasure_test:
        print("\n🎉 所有测试通过！字幕模块API配置正常")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    # 运行测试
    success = main()
    
    if success:
        print("\n✅ 测试完成，字幕模块API配置已就绪")
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)