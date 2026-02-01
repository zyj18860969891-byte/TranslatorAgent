#!/usr/bin/env python3
"""
Qwen3-Omni-Flash 字幕提取脚本
"""

import os
import cv2
import json
import requests
from pathlib import Path
from typing import List, Dict, Any

class Qwen3SubtitleExtractor:
    """Qwen3-Omni-Flash 字幕提取器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/chat/completions"
        
    def extract_subtitles_from_video(self, video_path: str, output_path: str) -> bool:
        """从视频中提取字幕"""
        try:
            print(f"🎬 开始处理视频: {video_path}")
            
            # 1. 提取视频帧
            frames = self._extract_frames(video_path)
            print(f"📸 提取了 {len(frames)} 帧")
            
            # 2. 检测字幕帧
            subtitle_frames = self._detect_subtitle_frames(frames)
            print(f"🔍 检测到 {len(subtitle_frames)} 字幕帧")
            
            # 3. 使用 Qwen3 进行 OCR 识别
            subtitles = self._ocr_with_qwen3(subtitle_frames)
            
            # 4. 生成 SRT 文件
            self._generate_srt(subtitles, output_path)
            
            print(f"✅ 字幕提取完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 字幕提取失败: {e}")
            return False
    
    def _extract_frames(self, video_path: str, fps: int = 1) -> List[str]:
        """提取视频帧"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps_video = cap.get(cv2.CAP_PROP_FPS)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 按指定 fps 采样
            if frame_count % int(fps_video / fps) == 0:
                frame_path = f"temp/frame_{frame_count}.jpg"
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
            
            frame_count += 1
            
        cap.release()
        return frames
    
    def _detect_subtitle_frames(self, frames: List[str]) -> List[str]:
        """检测包含字幕的帧"""
        subtitle_frames = []
        
        for frame_path in frames:
            # 简单的字幕检测逻辑
            # 实际应用中可以使用更复杂的算法
            subtitle_frames.append(frame_path)
        
        return subtitle_frames
    
    def _ocr_with_qwen3(self, frames: List[str]) -> List[Dict[str, Any]]:
        """使用 Qwen3 进行 OCR 识别"""
        subtitles = []
        
        for i, frame_path in enumerate(frames):
            try:
                with open(frame_path, 'rb') as f:
                    image_data = f.read()
                
                # 构建请求
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
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
                    "max_tokens": 500
                }
                
                response = requests.post(self.base_url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    if content.strip():
                        subtitles.append({
                            "index": i,
                            "time": i * 1.0,  # 假设每帧间隔1秒
                            "text": content.strip()
                        })
                
                # 避免请求过于频繁
                import time
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ 处理帧 {frame_path} 失败: {e}")
                continue
        
        return subtitles
    
    def _generate_srt(self, subtitles: List[Dict[str, Any]], output_path: str):
        """生成 SRT 文件"""
        srt_content = ""
        
        for i, sub in enumerate(subtitles):
            start_time = sub["time"]
            end_time = start_time + 3.0  # 假设每条字幕显示3秒
            
            srt_content += f"{i + 1}
"
            srt_content += f"{self._format_time(start_time)} --> {self._format_time(end_time)}
"
            srt_content += f"{sub['text']}

"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def main():
    """主函数"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    extractor = Qwen3SubtitleExtractor(api_key)
    
    # 示例用法
    video_path = "example_video.mp4"
    output_path = "output_subtitles.srt"
    
    if os.path.exists(video_path):
        success = extractor.extract_subtitles_from_video(video_path, output_path)
        if success:
            print("🎉 字幕提取成功！")
        else:
            print("❌ 字幕提取失败")
    else:
        print(f"❌ 视频文件不存在: {video_path}")

if __name__ == "__main__":
    main()
