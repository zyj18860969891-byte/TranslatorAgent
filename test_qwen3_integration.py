#!/usr/bin/env python3
"""
Qwen3-Omni-Flash 集成测试脚本
用于验证字幕提取功能的完整集成
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from translator_agent.core.qwen3_config import config_manager, validate_qwen3_config
from translator_agent.services.qwen3_subtitle_service import Qwen3SubtitleService
from translator_agent.core.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_configuration():
    """测试配置"""
    print("🔧 测试配置...")
    
    # 设置 API 密钥
    api_key = "sk-88bf1bd605544d208c7338cb1989ab3e"
    config_manager.set_api_key(api_key)
    
    # 验证配置
    validation_result = validate_qwen3_config()
    
    if not validation_result["valid"]:
        print("❌ 配置验证失败:")
        for error in validation_result["errors"]:
            print(f"   - {error}")
        return False
    
    if validation_result["warnings"]:
        print("⚠️  配置警告:")
        for warning in validation_result["warnings"]:
            print(f"   - {warning}")
    
    print("✅ 配置验证通过")
    return True

def test_service_initialization():
    """测试服务初始化"""
    print("🚀 测试服务初始化...")
    
    try:
        # 创建配置对象
        config = Config()
        
        # 创建字幕服务
        service = Qwen3SubtitleService(config)
        
        print("✅ 服务初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        return False

def test_api_connection():
    """测试 API 连接"""
    print("🌐 测试 API 连接...")
    
    try:
        from translator_agent.services.enhanced_qwen3_subtitle_extractor import EnhancedQwen3SubtitleExtractor
        
        extractor = EnhancedQwen3SubtitleExtractor(config_manager.get_api_key())
        
        # 创建测试图片
        test_image_path = create_test_image()
        
        if test_image_path:
            # 测试 OCR 识别
            result = extractor._ocr_with_qwen3_parallel(
                [{"frame_path": test_image_path, "timestamp": 0, "frame_index": 0}], 
                Path("temp")
            )
            
            if result and result[0] and result[0].get("text"):
                print("✅ API 连接成功")
                print(f"📝 测试结果: {result[0]['text']}")
                return True
            else:
                print("❌ API 连接失败：无法识别文本")
                return False
        else:
            print("❌ 无法创建测试图片")
            return False
            
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return False

def create_test_image():
    """创建测试图片"""
    try:
        import cv2
        import numpy as np
        
        # 创建一个简单的测试图片
        img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        
        # 添加测试文本
        cv2.putText(img, "测试字幕 Test Subtitle", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # 保存图片
        test_image_path = "temp/test_image.jpg"
        os.makedirs("temp", exist_ok=True)
        cv2.imwrite(test_image_path, img)
        
        return test_image_path
        
    except Exception as e:
        print(f"创建测试图片失败: {e}")
        return None

def test_subtitle_extraction():
    """测试字幕提取功能"""
    print("🎬 测试字幕提取功能...")
    
    # 检查是否有测试视频
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"⚠️  测试视频不存在: {test_video}")
        print("💡 跳过字幕提取测试")
        return True
    
    try:
        from translator_agent.services.qwen3_subtitle_service import Qwen3SubtitleService
        from translator_agent.core.config import Config
        
        # 创建服务
        config = Config()
        service = Qwen3SubtitleService(config)
        
        # 执行字幕提取
        result = service.extract_subtitles(test_video)
        
        if result["success"]:
            print("✅ 字幕提取成功")
            print(f"📊 处理结果:")
            print(f"   - 任务ID: {result['task_id']}")
            print(f"   - 输出文件: {result.get('output_filename', 'N/A')}")
            print(f"   - 处理时间: {result.get('processing_time', 0):.2f}秒")
            return True
        else:
            print(f"❌ 字幕提取失败: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 字幕提取测试失败: {e}")
        return False

def test_task_management():
    """测试任务管理"""
    print("📋 测试任务管理...")
    
    try:
        from translator_agent.services.qwen3_subtitle_service import Qwen3SubtitleService
        from translator_agent.core.config import Config
        
        # 创建服务
        config = Config()
        service = Qwen3SubtitleService(config)
        
        # 获取任务列表
        tasks = service.list_tasks()
        print(f"📝 当前任务数量: {len(tasks)}")
        
        # 测试任务状态查询
        if tasks:
            task_id = tasks[0]["task_id"]
            status = service.get_task_status(task_id)
            if status:
                print(f"✅ 任务状态查询成功: {status['status']}")
            else:
                print("❌ 任务状态查询失败")
                return False
        
        print("✅ 任务管理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 任务管理测试失败: {e}")
        return False

def test_configuration_file():
    """测试配置文件"""
    print("📄 测试配置文件...")
    
    try:
        # 保存配置
        config_manager.save_config()
        
        # 重新加载配置
        new_config_manager = config_manager.__class__("qwen3_config.json")
        new_config = new_config_manager.get_config()
        
        # 验证配置是否一致
        if new_config.api_key == config_manager.get_config().api_key:
            print("✅ 配置文件测试通过")
            return True
        else:
            print("❌ 配置文件测试失败：配置不一致")
            return False
            
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    try:
        import shutil
        
        # 清理临时目录
        if os.path.exists("temp"):
            shutil.rmtree("temp")
        
        # 清理任务目录
        if os.path.exists("tasks"):
            shutil.rmtree("tasks")
        
        # 清理输出目录
        if os.path.exists("output"):
            shutil.rmtree("output")
        
        print("🧹 测试文件清理完成")
        
    except Exception as e:
        print(f"清理测试文件时出错: {e}")

def main():
    """主测试函数"""
    print("🧪 Qwen3-Omni-Flash 集成测试")
    print("=" * 50)
    
    tests = [
        ("配置测试", test_configuration),
        ("服务初始化测试", test_service_initialization),
        ("API 连接测试", test_api_connection),
        ("配置文件测试", test_configuration_file),
        ("任务管理测试", test_task_management),
        ("字幕提取测试", test_subtitle_extraction),
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
    cleanup_test_files()
    
    # 退出状态码
    sys.exit(0 if success else 1)