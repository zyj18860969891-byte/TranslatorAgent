"""
视频处理模块
"""

import os
import cv2
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class VideoFrame:
    """视频帧数据"""
    frame_path: str
    timestamp: float
    frame_index: int
    width: int
    height: int

@dataclass
class VideoInfo:
    """视频信息"""
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float
    format: str

class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_video_info(self, video_path: str) -> Optional[VideoInfo]:
        """获取视频信息"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return VideoInfo(
                width=width,
                height=height,
                fps=fps,
                frame_count=frame_count,
                duration=duration,
                format="mp4"  # 简化处理
            )
            
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None
    
    def extract_frames(self, video_path: str, output_dir: str, 
                     fps: int = 1, start_time: float = 0, 
                     duration: float = None) -> List[VideoFrame]:
        """提取视频帧"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 计算采样间隔
            sample_interval = max(1, int(video_fps / fps))
            
            frames = []
            frame_count = 0
            
            # 设置开始时间
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
            
            # 计算结束时间
            end_time = duration if duration else (total_frames / video_fps)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_count / video_fps
                
                if current_time > end_time:
                    break
                
                if frame_count % sample_interval == 0:
                    frame_path = output_path / f"frame_{frame_count}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    
                    frames.append(VideoFrame(
                        frame_path=str(frame_path),
                        timestamp=current_time,
                        frame_index=frame_count,
                        width=frame.shape[1],
                        height=frame.shape[0]
                    ))
                
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            print(f"提取视频帧失败: {e}")
            return []
    
    def detect_motion(self, frames: List[VideoFrame], threshold: float = 0.1) -> List[int]:
        """检测运动帧"""
        try:
            motion_frames = []
            
            if len(frames) < 2:
                return motion_frames
            
            for i in range(1, len(frames)):
                try:
                    # 读取前一帧和当前帧
                    prev_frame = cv2.imread(frames[i-1].frame_path)
                    curr_frame = cv2.imread(frames[i].frame_path)
                    
                    if prev_frame is None or curr_frame is None:
                        continue
                    
                    # 转换为灰度图
                    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
                    
                    # 计算帧差
                    diff = cv2.absdiff(prev_gray, curr_gray)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    
                    # 计算运动比例
                    motion_ratio = cv2.countNonZero(thresh) / (thresh.shape[0] * thresh.shape[1])
                    
                    if motion_ratio > threshold:
                        motion_frames.append(frames[i].frame_index)
                        
                except Exception as e:
                    print(f"处理帧 {frames[i].frame_index} 时出错: {e}")
                    continue
            
            return motion_frames
            
        except Exception as e:
            print(f"检测运动失败: {e}")
            return []
    
    def detect_text_regions(self, frame_path: str) -> List[Dict[str, Any]]:
        """检测文本区域"""
        try:
            frame = cv2.imread(frame_path)
            if frame is None:
                return []
            
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 使用 OCR 检测文本（简化版）
            # 实际应用中可以使用 Tesseract OCR 或其他 OCR 库
            text_regions = []
            
            # 使用边缘检测找到可能的文本区域
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 过滤小区域
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算区域特征
                    region = {
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "area": area,
                        "confidence": min(1.0, area / (frame.shape[0] * frame.shape[1]))
                    }
                    text_regions.append(region)
            
            return text_regions
            
        except Exception as e:
            print(f"检测文本区域失败: {e}")
            return []
    
    def cleanup_frames(self, frames: List[VideoFrame]):
        """清理帧文件"""
        try:
            for frame in frames:
                if os.path.exists(frame.frame_path):
                    os.remove(frame.frame_path)
        except Exception as e:
            print(f"清理帧文件失败: {e}")
    
    def save_video_info(self, video_path: str, output_path: str):
        """保存视频信息"""
        try:
            video_info = self.get_video_info(video_path)
            if video_info:
                info_dict = {
                    "width": video_info.width,
                    "height": video_info.height,
                    "fps": video_info.fps,
                    "frame_count": video_info.frame_count,
                    "duration": video_info.duration,
                    "format": video_info.format
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(info_dict, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            print(f"保存视频信息失败: {e}")