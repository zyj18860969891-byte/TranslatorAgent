#!/usr/bin/env python3
"""
基于 DashScope SDK 的 Qwen3-Omni-Flash 字幕提取器
使用官方 SDK 实现更可靠的多模态处理
"""

import os
import cv2
import json
import base64
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import dashscope
from dashscope import TextGeneration, ImageUnderstanding

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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

class DashScopeQwen3SubtitleExtractor:
    """基于 DashScope SDK 的 Qwen3-Omni-Flash 字幕提取器"""
    
    def __init__(self, api_key: str = None):
        """初始化字幕提取器"""
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")
        
        dashscope.api_key = self.api_key
        
        # 配置参数
        self.max_workers = 4
        self.request_timeout = 30
        self.retry_attempts = 3
        self.retry_delay = 1.0
        
        # 临时目录
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("DashScope Qwen3 字幕提取器初始化完成")
    
    def extract_subtitles_from_video(self, video_path: str, output_path: str, 
                                   task_id: str = None) -> Dict[str, Any]:
        """
        从视频中提取字幕
        
        Args:
            video_path: 视频文件路径
            output_path: 输出 SRT 文件路径
            task_id: 任务ID
            
        Returns:
            处理结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎬 开始处理视频: {video_path}")
            
            # 1. 提取视频帧
            frames = self._extract_frames(video_path)
            logger.info(f"📸 提取了 {len(frames)} 帧")
            
            # 2. 检测字幕帧
            subtitle_frames = self._detect_subtitle_frames(frames)
            logger.info(f"🔍 检测到 {len(subtitle_frames)} 字幕帧")
            
            # 3. 使用 DashScope 进行 OCR 识别
            ocr_results = self._ocr_with_dashscope(subtitle_frames)
            
            # 4. 情感分析和字幕优化
            enhanced_subtitles = self._enhance_subtitles_with_emotion(ocr_results)
            
            # 5. 生成 SRT 文件
            self._generate_enhanced_srt(enhanced_subtitles, output_path)
            
            # 6. 清理临时文件
            self._cleanup_temp_files()
            
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
            
            logger.info(f"✅ 字幕提取完成: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 字幕提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "task_id": task_id
            }
    
    def _extract_frames(self, video_path: str, fps: int = 1) -> List[str]:
        """提取视频帧"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps_video = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"📹 视频信息: {total_frames} 帧, {fps_video:.2f} FPS")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 按指定 fps 采样
            sample_rate = max(1, int(fps_video / fps))
            if frame_count % sample_rate == 0:
                frame_path = self.temp_dir / f"frame_{frame_count}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frames.append(str(frame_path))
            
            frame_count += 1
            
            # 进度报告
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"📊 帧提取进度: {progress:.1f}%")
        
        cap.release()
        return frames
    
    def _detect_subtitle_frames(self, frames: List[str]) -> List[SubtitleFrame]:
        """检测包含字幕的帧"""
        subtitle_frames = []
        
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
                logger.warning(f"处理帧 {frame_path} 时出错: {e}")
                continue
        
        logger.info(f"🔍 字幕帧检测完成，找到 {len(subtitle_frames)} 帧")
        return subtitle_frames
    
    def _ocr_with_dashscope(self, subtitle_frames: List[SubtitleFrame]) -> List[Dict[str, Any]]:
        """使用 DashScope 进行 OCR 识别"""
        ocr_results = []
        
        for i, subtitle_frame in enumerate(subtitle_frames):
            try:
                # 读取图片并转换为 base64
                with open(subtitle_frame.frame_path, 'rb') as f:
                    image_data = f.read()
                
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # 构建提示词
                prompt = f"""
                请识别图片中的字幕文本，要求：
                1. 如果有多行字幕，请按时间顺序排列
                2. 识别语言类型（中文/英文/其他）
                3. 分析字幕的情感色彩（积极/消极/中性）
                4. 只返回字幕文本，不要其他解释
                5. 如果没有字幕，请返回"无字幕"
                """
                
                # 调用 DashScope 文本生成 API
                response = TextGeneration.call(
                    model='qwen3-omni-flash-realtime',
                    messages=[
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'image': f'data:image/jpeg;base64,{image_base64}'
                                },
                                {
                                    'text': prompt
                                }
                            ]
                        }
                    ],
                    parameters={
                        'max_tokens': 500,
                        'temperature': 0.1
                    }
                )
                
                if response.status_code == 200:
                    content = response.output.choices[0].message.content.strip()
                    
                    ocr_result = {
                        "frame_index": subtitle_frame.frame_index,
                        "timestamp": subtitle_frame.timestamp,
                        "text": content,
                        "confidence": subtitle_frame.confidence,
                        "frame_path": subtitle_frame.frame_path
                    }
                    ocr_results.append(ocr_result)
                else:
                    logger.warning(f"OCR 请求失败: {response.status_code}")
                
                # 避免请求过于频繁
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"处理帧 {subtitle_frame.frame_path} 时出错: {e}")
                continue
        
        logger.info(f"📝 OCR 识别完成，处理了 {len(ocr_results)} 帧")
        return ocr_results
    
    def _enhance_subtitles_with_emotion(self, ocr_results: List[Dict[str, Any]]) -> List[SubtitleSegment]:
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
        
        logger.info(f"🎭 情感分析完成，生成 {len(enhanced_subtitles)} 条字幕")
        return enhanced_subtitles
    
    def _analyze_emotion(self, text: str) -> List[str]:
        """简化的情感分析"""
        emotions = []
        
        # 积极情感词汇
        positive_words = ['好', '棒', '优秀', '成功', '快乐', '开心', '满意', '赞', '爱', '希望']
        # 消极情感词汇
        negative_words = ['坏', '差', '失败', '难过', '生气', '不满', '批评', '讨厌', '痛苦', '绝望']
        
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
                (current.text in last.text or last.text in current.text)):
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
        
        logger.info(f"📄 SRT 文件已生成: {output_path}")
    
    def _format_time_enhanced(self, seconds: float) -> str:
        """增强版时间格式化"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 已清理临时文件: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"清理临时文件时出错: {e}")

def main():
    """主函数"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    extractor = DashScopeQwen3SubtitleExtractor(api_key)
    
    # 示例用法
    video_path = "example_video.mp4"
    output_path = "output_subtitles_dashscope.srt"
    task_id = "demo_task"
    
    if os.path.exists(video_path):
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