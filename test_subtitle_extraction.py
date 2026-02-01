#!/usr/bin/env python3
"""
测试字幕提取功能
"""

import os
import cv2
import numpy as np
from working_subtitle_extractor import WorkingSubtitleExtractor

def create_test_image():
    """创建测试图片"""
    print("🖼️ 创建测试图片...")
    
    # 创建测试图片
    img = np.ones((400, 800, 3), dtype=np.uint8) * 255
    
    # 添加字幕文本
    subtitle_texts = [
        "这是第一行字幕 This is the first subtitle",
        "这是第二行字幕 This is the second subtitle",
        "这是第三行字幕 This is the third subtitle"
    ]
    
    y_position = 50
    for text in subtitle_texts:
        cv2.putText(img, text, (20, y_position), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y_position += 80
    
    # 保存图片
    test_image_path = "test_subtitle_image.jpg"
    cv2.imwrite(test_image_path, img)
    
    print(f"✅ 测试图片已创建: {test_image_path}")
    return test_image_path

def test_subtitle_extraction():
    """测试字幕提取功能"""
    print("🧪 测试字幕提取功能...")
    
    # 创建测试图片
    test_image_path = create_test_image()
    
    # 创建提取器
    extractor = WorkingSubtitleExtractor()
    
    # 提取文本
    text = extractor.extract_text_from_image(test_image_path)
    
    if text:
        print("✅ 字幕提取成功！")
        print(f"📝 提取结果: {text}")
        
        # 保存结果
        with open("extracted_subtitles.txt", "w", encoding="utf-8") as f:
            f.write(text)
        
        print("✅ 结果已保存到: extracted_subtitles.txt")
        return True
    else:
        print("❌ 字幕提取失败")
        return False

def main():
    """主函数"""
    print("🚀 测试字幕提取功能")
    print("=" * 40)
    
    success = test_subtitle_extraction()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 测试成功！")
    else:
        print("💡 测试失败")
    
    # 清理测试文件
    try:
        if os.path.exists("test_subtitle_image.jpg"):
            os.remove("test_subtitle_image.jpg")
    except:
        pass

if __name__ == "__main__":
    main()