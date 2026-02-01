#!/usr/bin/env python3
"""
简单的 Qwen3-Omni-Flash 测试脚本
"""

import os
import sys
import json
import requests
from pathlib import Path

# 设置 API 密钥
API_KEY = "sk-88bf1bd605544d208c7338cb1989ab3e"
BASE_URL = "https://dashscope.aliyuncs.com/api/v1/chat/completions"

def test_qwen3_connection():
    """测试 Qwen3 连接"""
    print("🌐 测试 Qwen3-Omni-Flash 连接...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "qwen3-omni-flash-realtime",
        "messages": [
            {
                "role": "user",
                "content": "请简单介绍一下自己"
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print("✅ Qwen3 连接成功")
            print(f"📝 响应: {content}")
            return True
        else:
            print(f"❌ 连接失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试连接时发生错误: {e}")
        return False

def test_qwen3_ocr():
    """测试 Qwen3 OCR 功能"""
    print("\n📸 测试 Qwen3 OCR 功能...")
    
    # 创建测试图片
    try:
        import cv2
        import numpy as np
        
        # 创建测试图片
        img = np.ones((200, 600, 3), dtype=np.uint8) * 255
        
        # 添加测试文本
        cv2.putText(img, "测试字幕 Test Subtitle", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        # 保存图片
        test_image_path = "temp/test_image.jpg"
        os.makedirs("temp", exist_ok=True)
        cv2.imwrite(test_image_path, img)
        
        # 读取图片数据
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": "qwen3-omni-flash-realtime",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data.hex()}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "请识别图片中的字幕文本，如果有多行字幕，请按时间顺序排列。只返回字幕文本，不要其他解释。"
                        }
                    ]
                }
            ],
            "max_tokens": 200
        }
        
        try:
            response = requests.post(BASE_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print("✅ Qwen3 OCR 测试成功")
                print(f"📝 识别结果: {content}")
                return True
            else:
                print(f"❌ OCR 测试失败: {response.status_code}")
                print(f"📄 错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ OCR 测试时发生错误: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}")
        return False

def test_configuration():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    try:
        from translator_agent.core.qwen3_config import config_manager
        
        # 设置 API 密钥
        config_manager.set_api_key(API_KEY)
        
        # 验证配置
        validation_result = config_manager.validate_config()
        
        if validation_result["valid"]:
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败:")
            for error in validation_result["errors"]:
                print(f"   - {error}")
            return False
            
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Qwen3-Omni-Flash 集成测试")
    print("=" * 50)
    
    tests = [
        ("配置测试", test_configuration),
        ("连接测试", test_qwen3_connection),
        ("OCR 测试", test_qwen3_ocr),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                failed += 1
                print(f"❌ {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果:")
    print(f"   - 通过: {passed}")
    print(f"   - 失败: {failed}")
    print(f"   - 总计: {passed + failed}")
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return True
    else:
        print("💡 部分测试失败，请检查错误信息")
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
    
    # 退出状态码
    sys.exit(0 if success else 1)