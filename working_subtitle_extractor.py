#!/usr/bin/env python3
"""
工作字幕提取器
基于 DashScope API 和 Qwen 模型
"""

import os
import sys
import json
import time
import logging
import base64
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkingSubtitleExtractor:
    """工作字幕提取器"""
    
    def __init__(self, api_key: str = "sk-88bf1bd605544d208c7338cb1989ab3e"):
        """初始化字幕提取器"""
        self.api_key = api_key
        self.model = "qwen-plus"  # 使用已经验证可用的模型
        self.setup_environment()
        
    def setup_environment(self):
        """设置环境变量"""
        os.environ['DASHSCOPE_API_KEY'] = self.api_key
        
    def extract_frames_from_video(self, video_path: str, output_dir: str, 
                                 frame_interval: int = 30) -> List[str]:
        """从视频中提取帧"""
        logger.info(f"🎬 从视频中提取帧: {video_path}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ 无法打开视频文件: {video_path}")
            return []
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        logger.info(f"📊 视频信息:")
        logger.info(f"   - 总帧数: {total_frames}")
        logger.info(f"   - 帧率: {fps:.2f} FPS")
        logger.info(f"   - 时长: {duration:.2f} 秒")
        
        # 提取帧
        frame_paths = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 按间隔提取帧
            if frame_count % frame_interval == 0:
                frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                
            frame_count += 1
            
            # 进度显示
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"🔄 处理进度: {progress:.1f}%")
        
        cap.release()
        logger.info(f"✅ 提取了 {len(frame_paths)} 帧到: {output_dir}")
        return frame_paths
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """从图片中提取文本"""
        logger.info(f"📸 从图片中提取文本: {image_path}")
        
        try:
            import dashscope
            from dashscope import Generation
            
            # 读取图片并转换为 base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 调用 DashScope API
            response = Generation.call(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': [
                            {
                                'image': f'data:image/jpeg;base64,{image_base64}'
                            },
                            {
                                'text': '请仔细识别图片中的字幕文本。如果有多行字幕，请按时间顺序排列。只返回字幕文本，不要其他解释。如果图片中没有字幕文本，请返回"无字幕"。'
                            }
                        ]
                    }
                ],
                parameters={
                    'max_tokens': 200,
                    'temperature': 0.1
                }
            )
            
            if response.status_code == 200:
                if hasattr(response, 'output') and response.output:
                    if hasattr(response.output, 'text') and response.output.text:
                        text = response.output.text.strip()
                        logger.info(f"📝 识别结果: {text}")
                        return text
                    else:
                        logger.error(f"❌ 响应结构异常: text 为空")
                        return None
                else:
                    logger.error(f"❌ 响应结构异常: output 为空")
                    return None
            else:
                logger.error(f"❌ API 调用失败: {response.message}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 提取文本时发生错误: {e}")
            return None
    
    def process_frames_with_subtitles(self, frame_paths: List[str], 
                                   output_file: str) -> Dict[str, Any]:
        """处理包含字幕的帧"""
        logger.info(f"🔄 处理 {len(frame_paths)} 帧...")
        
        results = []
        processed_count = 0
        subtitle_count = 0
        
        for i, frame_path in enumerate(frame_paths):
            logger.info(f"🔄 处理第 {i+1}/{len(frame_paths)} 帧...")
            
            # 提取文本
            text = self.extract_text_from_image(frame_path)
            
            if text and text != "无字幕":
                # 计算时间戳（假设每帧间隔 1 秒）
                timestamp = i * 1.0  # 简化处理
                
                results.append({
                    'timestamp': timestamp,
                    'text': text,
                    'frame_path': frame_path
                })
                
                subtitle_count += 1
                logger.info(f"✅ 发现字幕: {text}")
            
            processed_count += 1
            
            # 进度显示
            if processed_count % 10 == 0:
                progress = (processed_count / len(frame_paths)) * 100
                logger.info(f"🔄 处理进度: {progress:.1f}%")
        
        # 生成 SRT 文件
        self.generate_srt_file(results, output_file)
        
        return {
            'success': True,
            'processed_frames': processed_count,
            'subtitle_frames': subtitle_count,
            'output_file': output_file,
            'results': results
        }
    
    def generate_srt_file(self, results: List[Dict], output_file: str):
        """生成 SRT 文件"""
        logger.info(f"📝 生成 SRT 文件: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, result in enumerate(results):
                start_time = result['timestamp']
                end_time = start_time + 3.0  # 假设字幕显示 3 秒
                text = result['text']
                
                # 格式化时间
                start_time_str = self.format_time(start_time)
                end_time_str = self.format_time(end_time)
                
                # 写入 SRT 格式
                f.write(f"{i+1}\n")
                f.write(f"{start_time_str} --> {end_time_str}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"✅ SRT 文件已生成: {output_file}")
    
    def format_time(self, seconds: float) -> str:
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def extract_subtitles_from_video(self, video_path: str, 
                                   output_file: str) -> Dict[str, Any]:
        """从视频中提取字幕"""
        logger.info(f"🎬 开始从视频中提取字幕: {video_path}")
        
        start_time = time.time()
        
        # 提取帧
        frames_dir = os.path.join(os.path.dirname(output_file), "frames")
        frame_paths = self.extract_frames_from_video(video_path, frames_dir)
        
        if not frame_paths:
            return {
                'success': False,
                'error': '无法从视频中提取帧'
            }
        
        # 处理帧
        result = self.process_frames_with_subtitles(frame_paths, output_file)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        result['processing_time'] = processing_time
        
        logger.info(f"✅ 字幕提取完成:")
        logger.info(f"   - 处理时间: {processing_time:.2f} 秒")
        logger.info(f"   - 处理帧数: {result['processed_frames']}")
        logger.info(f"   - 字幕帧数: {result['subtitle_frames']}")
        logger.info(f"   - 输出文件: {output_file}")
        
        return result

def main():
    """主函数"""
    print("🚀 工作字幕提取器")
    print("=" * 40)
    
    # 创建提取器
    extractor = WorkingSubtitleExtractor()
    
    # 测试视频文件
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"⚠️  测试视频不存在: {test_video}")
        print("💡 跳过测试")
        return
    
    # 执行字幕提取
    result = extractor.extract_subtitles_from_video(test_video, "test_output.srt")
    
    if result["success"]:
        print("🎉 字幕提取成功！")
        print(f"📊 处理结果:")
        print(f"   - 处理时间: {result.get('processing_time', 0):.2f} 秒")
        print(f"   - 处理帧数: {result.get('processed_frames', 0)}")
        print(f"   - 字幕帧数: {result.get('subtitle_frames', 0)}")
        print(f"   - 输出文件: {result.get('output_file', 'N/A')}")
    else:
        print(f"❌ 字幕提取失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()