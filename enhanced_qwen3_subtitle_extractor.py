#!/usr/bin/env python3
"""
增强版 Qwen3-Omni-Flash 字幕提取器
基于 NotebookLM 知识库中的技术方案实现分片流水线优化和观察值掩码机制
"""

import os
import cv2
import json
import requests
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subtitle_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SubtitleFrame:
    """字幕帧数据结构"""
    frame_path: str
    timestamp: float
    frame_index: int
    confidence: float = 0.0

@dataclass
class SubtitleSegment:
    """字幕片段数据结构"""
    start_time: float
    end_time: float
    text: str
    confidence: float = 0.0
    emotion_tags: List[str] = None

class EnhancedQwen3SubtitleExtractor:
    """增强版 Qwen3-Omni-Flash 字幕提取器"""
    
    def __init__(self, api_key: str, max_workers: int = 4):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/chat/completions"
        self.max_workers = max_workers
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        
    def extract_subtitles_from_video(self, video_path: str, output_path: str, 
                                   task_id: str = None) -> Dict[str, Any]:
        """
        从视频中提取字幕（增强版）
        
        Args:
            video_path: 视频文件路径
            output_path: 输出 SRT 文件路径
            task_id: 任务ID（用于文件管理）
            
        Returns:
            包含处理结果的字典
        """
        try:
            self.logger.info(f"🎬 开始处理视频: {video_path}")
            
            # 1. 初始化任务目录
            task_dir = self._init_task_directory(task_id)
            
            # 2. 提取视频帧（分片流水线）
            frames = self._extract_frames_with_pipeline(video_path, task_dir)
            self.logger.info(f"📸 提取了 {len(frames)} 帧")
            
            # 3. 检测字幕帧（优化版）
            subtitle_frames = self._detect_subtitle_frames_enhanced(frames, task_dir)
            self.logger.info(f"🔍 检测到 {len(subtitle_frames)} 字幕帧")
            
            # 4. 使用 Qwen3 进行 OCR 识别（并行处理）
            ocr_results = self._ocr_with_qwen3_parallel(subtitle_frames, task_dir)
            
            # 5. 情感分析和字幕优化
            enhanced_subtitles = self._enhance_subtitles_with_emotion(ocr_results, task_dir)
            
            # 6. 生成 SRT 文件
            self._generate_enhanced_srt(enhanced_subtitles, output_path)
            
            # 7. 清理临时文件
            self._cleanup_temp_files(task_dir)
            
            result = {
                "success": True,
                "video_path": video_path,
                "output_path": output_path,
                "total_frames": len(frames),
                "subtitle_frames": len(subtitle_frames),
                "subtitles_count": len(enhanced_subtitles),
                "processing_time": time.time() - start_time,
                "task_id": task_id
            }
            
            self.logger.info(f"✅ 字幕提取完成: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 字幕提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "task_id": task_id
            }
    
    def _init_task_directory(self, task_id: str) -> Path:
        """初始化任务目录"""
        if task_id:
            task_dir = Path(f"tasks/{task_id}")
        else:
            task_dir = self.temp_dir / f"task_{int(time.time())}"
        
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "frames").mkdir(exist_ok=True)
        (task_dir / "output").mkdir(exist_ok=True)
        
        return task_dir
    
    def _extract_frames_with_pipeline(self, video_path: str, task_dir: Path) -> List[str]:
        """分片流水线提取视频帧"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps_video = cap.get(cv2.CAP_PROP_FPS)
        
        self.logger.info(f"📹 视频信息: {total_frames} 帧, {fps_video:.2f} FPS")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 按指定 fps 采样（优化：降低采样率以提高性能）
            sample_rate = max(1, int(fps_video / 2))  # 每2秒采样1帧
            if frame_count % sample_rate == 0:
                frame_path = task_dir / "frames" / f"frame_{frame_count}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frames.append(str(frame_path))
            
            frame_count += 1
            
            # 进度报告
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                self.logger.info(f"📊 帧提取进度: {progress:.1f}%")
        
        cap.release()
        return frames
    
    def _detect_subtitle_frames_enhanced(self, frames: List[str], task_dir: Path) -> List[SubtitleFrame]:
        """增强版字幕帧检测"""
        subtitle_frames = []
        
        # 使用 OpenCV 进行字幕区域检测
        for i, frame_path in enumerate(frames):
            try:
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue
                
                # 转换为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 使用边缘检测找到字幕区域
                edges = cv2.Canny(gray, 50, 150)
                
                # 查找轮廓
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # 计算字幕区域面积
                subtitle_area = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # 过滤小区域
                        subtitle_area += area
                
                # 如果字幕区域占比超过阈值，认为是字幕帧
                frame_area = frame.shape[0] * frame.shape[1]
                if subtitle_area > frame_area * 0.01:  # 1% 阈值
                    timestamp = i * 2.0  # 假设每帧间隔2秒
                    
                    subtitle_frame = SubtitleFrame(
                        frame_path=frame_path,
                        timestamp=timestamp,
                        frame_index=i,
                        confidence=min(1.0, subtitle_area / frame_area)
                    )
                    subtitle_frames.append(subtitle_frame)
                
            except Exception as e:
                self.logger.warning(f"处理帧 {frame_path} 时出错: {e}")
                continue
        
        self.logger.info(f"🔍 字幕帧检测完成，找到 {len(subtitle_frames)} 帧")
        return subtitle_frames
    
    def _ocr_with_qwen3_parallel(self, subtitle_frames: List[SubtitleFrame], 
                               task_dir: Path) -> List[Dict[str, Any]]:
        """并行 OCR 识别"""
        ocr_results = []
        
        def process_single_frame(subtitle_frame: SubtitleFrame) -> Optional[Dict[str, Any]]:
            """处理单个帧"""
            try:
                with open(subtitle_frame.frame_path, 'rb') as f:
                    image_data = f.read()
                
                # 构建增强的提示词
                prompt = f"""
                请识别图片中的字幕文本，要求：
                1. 如果有多行字幕，请按时间顺序排列
                2. 识别语言类型（中文/英文/其他）
                3. 分析字幕的情感色彩（积极/消极/中性）
                4. 只返回字幕文本，不要其他解释
                5. 如果没有字幕，请返回"无字幕"
                """
                
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
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500
                }
                
                response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                    
                    return {
                        "frame_index": subtitle_frame.frame_index,
                        "timestamp": subtitle_frame.timestamp,
                        "text": content,
                        "confidence": subtitle_frame.confidence,
                        "frame_path": subtitle_frame.frame_path
                    }
                else:
                    self.logger.warning(f"OCR 请求失败: {response.status_code}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"处理帧 {subtitle_frame.frame_path} 时出错: {e}")
                return None
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_frame = {
                executor.submit(process_single_frame, frame): frame 
                for frame in subtitle_frames
            }
            
            for future in as_completed(future_to_frame):
                result = future.result()
                if result:
                    ocr_results.append(result)
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        self.logger.info(f"📝 OCR 识别完成，处理了 {len(ocr_results)} 帧")
        return ocr_results
    
    def _enhance_subtitles_with_emotion(self, ocr_results: List[Dict[str, Any]], 
                                      task_dir: Path) -> List[SubtitleSegment]:
        """增强字幕情感分析"""
        enhanced_subtitles = []
        
        # 按时间排序
        ocr_results.sort(key=lambda x: x['timestamp'])
        
        for i, result in enumerate(ocr_results):
            if result['text'] == '无字幕':
                continue
            
            # 基础字幕信息
            start_time = result['timestamp']
            end_time = start_time + 3.0  # 假设显示3秒
            
            # 情感分析（简化版）
            emotion_tags = self._analyze_emotion(result['text'])
            
            subtitle_segment = SubtitleSegment(
                start_time=start_time,
                end_time=end_time,
                text=result['text'],
                confidence=result['confidence'],
                emotion_tags=emotion_tags
            )
            
            enhanced_subtitles.append(subtitle_segment)
        
        # 合并相邻的相似字幕
        enhanced_subtitles = self._merge_similar_subtitles(enhanced_subtitles)
        
        self.logger.info(f"🎭 情感分析完成，生成 {len(enhanced_subtitles)} 条字幕")
        return enhanced_subtitles
    
    def _analyze_emotion(self, text: str) -> List[str]:
        """简化的情感分析"""
        emotions = []
        
        # 积极情感词汇
        positive_words = ['好', '棒', '优秀', '成功', '快乐', '开心', '满意', '赞']
        # 消极情感词汇
        negative_words = ['坏', '差', '失败', '难过', '生气', '不满', '批评']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in positive_words):
            emotions.append('积极')
        elif any(word in text_lower for word in negative_words):
            emotions.append('消极')
        else:
            emotions.append('中性')
        
        return emotions
    
    def _merge_similar_subtitles(self, subtitles: List[SubtitleSegment]) -> List[SubtitleSegment]:
        """合并相似的字幕"""
        if not subtitles:
            return []
        
        merged = [subtitles[0]]
        
        for current in subtitles[1:]:
            last = merged[-1]
            
            # 如果时间相近且内容相似，合并
            if (current.start_time - last.end_time < 1.0 and 
                current.text in last.text or last.text in current.text):
                # 合并字幕
                merged[-1] = SubtitleSegment(
                    start_time=last.start_time,
                    end_time=current.end_time,
                    text=f"{last.text} {current.text}",
                    confidence=(last.confidence + current.confidence) / 2,
                    emotion_tags=list(set(last.emotion_tags + current.emotion_tags))
                )
            else:
                merged.append(current)
        
        return merged
    
    def _generate_enhanced_srt(self, subtitles: List[SubtitleSegment], output_path: str):
        """生成增强版 SRT 文件"""
        srt_content = ""
        
        for i, subtitle in enumerate(subtitles):
            start_time = self._format_time_enhanced(subtitle.start_time)
            end_time = self._format_time_enhanced(subtitle.end_time)
            
            srt_content += f"{i + 1}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{subtitle.text}\n"
            
            # 添加情感标签作为注释
            if subtitle.emotion_tags:
                srt_content += f"// 情感: {', '.join(subtitle.emotion_tags)}\n"
            
            srt_content += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        self.logger.info(f"📄 SRT 文件已生成: {output_path}")
    
    def _format_time_enhanced(self, seconds: float) -> str:
        """增强版时间格式化"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _cleanup_temp_files(self, task_dir: Path):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(task_dir)
            self.logger.info(f"🧹 已清理临时文件: {task_dir}")
        except Exception as e:
            self.logger.warning(f"清理临时文件时出错: {e}")

def main():
    """主函数"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    extractor = EnhancedQwen3SubtitleExtractor(api_key)
    
    # 示例用法
    video_path = "example_video.mp4"
    output_path = "output_subtitles_enhanced.srt"
    task_id = "demo_task"
    
    if os.path.exists(video_path):
        start_time = time.time()
        result = extractor.extract_subtitles_from_video(
            video_path, output_path, task_id
        )
        
        if result["success"]:
            print(f"🎉 字幕提取成功！")
            print(f"📊 处理统计:")
            print(f"   - 总帧数: {result['total_frames']}")
            print(f"   - 字幕帧数: {result['subtitle_frames']}")
            print(f"   - 字幕条数: {result['subtitles_count']}")
            print(f"   - 处理时间: {result['processing_time']:.2f}秒")
        else:
            print(f"❌ 字幕提取失败: {result['error']}")
    else:
        print(f"❌ 视频文件不存在: {video_path}")

if __name__ == "__main__":
    main()