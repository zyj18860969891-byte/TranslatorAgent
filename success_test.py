#!/usr/bin/env python3
"""
成功测试脚本
"""

import os
import dashscope
from dashscope import Generation

def test_qwen_models():
    """测试 Qwen 模型"""
    print("🧪 测试 Qwen 模型...")
    
    # 设置环境变量
    os.environ['DASHSCOPE_API_KEY'] = 'sk-88bf1bd605544d208c7338cb1989ab3e'
    
    # 测试不同的模型
    models = ['qwen-turbo', 'qwen-plus', 'qwen-max']
    
    for model in models:
        try:
            print(f"\n🔄 测试模型: {model}")
            
            response = Generation.call(
                model=model,
                messages=[{'role': 'user', 'content': '你好'}],
                parameters={'max_tokens': 10, 'temperature': 0.1}
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功")
                # 检查响应结构
                if hasattr(response, 'output') and response.output:
                    if hasattr(response.output, 'text') and response.output.text:
                        content = response.output.text
                        print(f"📝 响应: {content}")
                        return True
                    else:
                        print(f"❌ 响应结构异常: text 为空")
                        print(f"📄 完整响应: {response}")
                else:
                    print(f"❌ 响应结构异常: output 为空")
                    print(f"📄 完整响应: {response}")
            else:
                print(f"❌ 失败: {response.message}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    return False

def test_qwen3_models():
    """测试 Qwen3 模型"""
    print("\n🧪 测试 Qwen3 模型...")
    
    # 测试 Qwen3 模型
    models = ['qwen3-omni-flash-2025-12-01', 'qwen3-omni-flash-realtime']
    
    for model in models:
        try:
            print(f"\n🔄 测试模型: {model}")
            
            response = Generation.call(
                model=model,
                messages=[{'role': 'user', 'content': '你好'}],
                parameters={'max_tokens': 10, 'temperature': 0.1}
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功")
                # 检查响应结构
                if hasattr(response, 'output') and response.output:
                    if hasattr(response.output, 'text') and response.output.text:
                        content = response.output.text
                        print(f"📝 响应: {content}")
                        return True
                    else:
                        print(f"❌ 响应结构异常: text 为空")
                        print(f"📄 完整响应: {response}")
                else:
                    print(f"❌ 响应结构异常: output 为空")
                    print(f"📄 完整响应: {response}")
            else:
                print(f"❌ 失败: {response.message}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    return False

def test_multimodal():
    """测试多模态功能"""
    print("\n🎬 测试多模态功能...")
    
    try:
        import base64
        import cv2
        import numpy as np
        
        # 设置环境变量
        os.environ['DASHSCOPE_API_KEY'] = 'sk-88bf1bd605544d208c7338cb1989ab3e'
        
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
        
        # 使用 Qwen 模型进行多模态测试
        model = 'qwen-plus'
        
        print(f"📝 使用模型: {model}")
        
        # 调用 DashScope API 进行多模态处理
        response = Generation.call(
            model=model,
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
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 多模态测试成功")
            if hasattr(response, 'output') and response.output:
                if hasattr(response.output, 'text') and response.output.text:
                    content = response.output.text
                    print(f"📝 识别结果: {content}")
                    return True
                else:
                    print(f"❌ 响应结构异常: text 为空")
                    print(f"📄 完整响应: {response}")
            else:
                print(f"❌ 响应结构异常: output 为空")
                print(f"📄 完整响应: {response}")
        else:
            print(f"❌ 多模态测试失败: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 多模态测试时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 DashScope 成功测试")
    print("=" * 40)
    
    # 测试 Qwen 模型
    qwen_success = test_qwen_models()
    
    # 测试 Qwen3 模型
    qwen3_success = test_qwen3_models()
    
    # 测试多模态功能
    multimodal_success = test_multimodal()
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果:")
    print(f"   - Qwen 模型: {'✅ 通过' if qwen_success else '❌ 失败'}")
    print(f"   - Qwen3 模型: {'✅ 通过' if qwen3_success else '❌ 失败'}")
    print(f"   - 多模态功能: {'✅ 通过' if multimodal_success else '❌ 失败'}")
    
    if qwen_success or qwen3_success or multimodal_success:
        print("🎉 至少有一个功能测试成功！")
        return True
    else:
        print("💡 所有功能测试失败")
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