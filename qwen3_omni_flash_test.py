#!/usr/bin/env python3
"""
Qwen3-Omni-Flash 测试脚本
"""

import os
import dashscope
from dashscope import Generation

def test_qwen3_omni_flash():
    """测试 Qwen3-Omni-Flash 模型"""
    print("🧪 测试 Qwen3-Omni-Flash 模型...")
    
    # 设置 API 密钥
    api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
    dashscope.api_key = api_key
    
    try:
        # 使用正确的模型名称
        model_name = "qwen3-omni-flash-2025-12-01"
        
        print(f"📝 使用模型: {model_name}")
        
        # 测试文本生成
        response = Generation.call(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': '你好，请简单介绍一下自己'
                }
            ],
            parameters={
                'max_tokens': 100,
                'temperature': 0.1
            }
        )
        
        print(f"📊 API 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content.strip()
            print("✅ Qwen3-Omni-Flash 测试成功")
            print(f"📝 响应: {content}")
            return True
        else:
            print(f"❌ 测试失败: {response.status_code}")
            print(f"📄 错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试时发生错误: {e}")
        return False

def test_qwen3_omni_flash_realtime():
    """测试 Qwen3-Omni-Flash-Realtime 模型"""
    print("\n🧪 测试 Qwen3-Omni-Flash-Realtime 模型...")
    
    # 设置 API 密钥
    api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
    dashscope.api_key = api_key
    
    try:
        # 使用实时版本模型名称
        model_name = "qwen3-omni-flash-realtime"
        
        print(f"📝 使用模型: {model_name}")
        
        # 测试文本生成
        response = Generation.call(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': '你好，请简单介绍一下自己'
                }
            ],
            parameters={
                'max_tokens': 100,
                'temperature': 0.1
            }
        )
        
        print(f"📊 API 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content.strip()
            print("✅ Qwen3-Omni-Flash-Realtime 测试成功")
            print(f"📝 响应: {content}")
            return True
        else:
            print(f"❌ 测试失败: {response.status_code}")
            print(f"📄 错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试时发生错误: {e}")
        return False

def test_multimodal():
    """测试多模态功能"""
    print("\n🎬 测试多模态功能...")
    
    try:
        import base64
        import cv2
        import numpy as np
        
        # 设置 API 密钥
        api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
        dashscope.api_key = api_key
        
        # 创建测试图片
        img = np.ones((200, 600, 3), dtype=np.uint8) * 255
        
        # 添加测试文本
        cv2.putText(img, "测试字幕 Test Subtitle", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        # 保存图片
        test_image_path = "temp/test_image.jpg"
        os.makedirs("temp", exist_ok=True)
        cv2.imwrite(test_image_path, img)
        
        # 读取图片并转换为 base64
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 使用正确的模型名称
        model_name = "qwen3-omni-flash-2025-12-01"
        
        print(f"📝 使用模型: {model_name}")
        
        # 调用 DashScope API 进行多模态处理
        response = Generation.call(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'image': f'data:image/jpeg;base64,{image_base64}'
                        },
                        {
                            'text': '请识别图片中的字幕文本，如果有多行字幕，请按时间顺序排列。只返回字幕文本，不要其他解释。'
                        }
                    ]
                }
            ],
            parameters={
                'max_tokens': 200,
                'temperature': 0.1
            }
        )
        
        print(f"📊 API 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content.strip()
            print("✅ 多模态测试成功")
            print(f"📝 识别结果: {content}")
            return True
        else:
            print(f"❌ 多模态测试失败: {response.status_code}")
            print(f"📄 错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 多模态测试时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Qwen3-Omni-Flash 测试")
    print("=" * 40)
    
    # 测试 Qwen3-Omni-Flash
    omni_flash_success = test_qwen3_omni_flash()
    
    # 测试 Qwen3-Omni-Flash-Realtime
    realtime_success = test_qwen3_omni_flash_realtime()
    
    # 测试多模态功能
    multimodal_success = test_multimodal()
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果:")
    print(f"   - Qwen3-Omni-Flash: {'✅ 通过' if omni_flash_success else '❌ 失败'}")
    print(f"   - Qwen3-Omni-Flash-Realtime: {'✅ 通过' if realtime_success else '❌ 失败'}")
    print(f"   - 多模态功能: {'✅ 通过' if multimodal_success else '❌ 失败'}")
    
    if omni_flash_success and realtime_success and multimodal_success:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💡 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    
    # 清理测试文件
    try:
        if os.path.exists("temp"):
            import shutil
            shutil.rmtree("temp")
    except:
        pass
    
    exit(0 if success else 1)