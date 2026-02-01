#!/usr/bin/env python3
"""
Qwen3模型字幕提取演示脚本
演示如何使用Qwen3-VL-Rerank模型进行视频字幕提取
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from qwen3_integration.subtitle_extractor import SubtitleExtractor
    from qwen3_integration.video_processor import VideoProcessor
    from qwen3_integration.config import load_config
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有必需的依赖包")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qwen3_subtitle_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Qwen3SubtitleDemo:
    """Qwen3字幕提取演示类"""
    
    def __init__(self):
        """初始化演示类"""
        self.config = load_config()
        self.subtitle_extractor = SubtitleExtractor(self.config)
        self.video_processor = VideoProcessor(self.config)
        
    def create_demo_video(self, output_path: str = "demo_video.mp4") -> bool:
        """创建演示视频文件"""
        try:
            import cv2
            import numpy as np
            
            logger.info("创建演示视频...")
            
            # 视频参数
            width, height = 640, 480
            fps = 30
            duration = 10  # 10秒视频
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 生成视频帧
            for frame_num in range(fps * duration):
                # 创建背景
                frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
                
                # 添加时间戳
                timestamp = frame_num / fps
                time_text = f"Time: {timestamp:.2f}s"
                cv2.putText(frame, time_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # 添加模拟字幕
                if frame_num % 60 == 0:  # 每2秒显示一次字幕
                    subtitle_texts = [
                        "Hello, this is a demo video",
                        "Welcome to Qwen3 subtitle extraction",
                        "This is a test subtitle",
                        "AI-powered subtitle extraction",
                        "Thank you for watching"
                    ]
                    subtitle_index = (frame_num // 60) % len(subtitle_texts)
                    subtitle_text = subtitle_texts[subtitle_index]
                    
                    # 添加字幕到视频底部
                    cv2.putText(frame, subtitle_text, (10, height - 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                
                # 写入帧
                out.write(frame)
            
            # 释放资源
            out.release()
            
            logger.info(f"演示视频已创建: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建演示视频失败: {e}")
            return False
    
    def extract_subtitles_basic(self, video_path: str) -> Dict[str, Any]:
        """基础字幕提取演示"""
        logger.info(f"开始基础字幕提取: {video_path}")
        
        try:
            start_time = time.time()
            
            # 提取字幕
            subtitles = self.subtitle_extractor.extract(video_path)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "success": True,
                "video_path": video_path,
                "subtitle_count": len(subtitles),
                "processing_time": processing_time,
                "subtitles": subtitles,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"字幕提取完成: {len(subtitles)} 条字幕, 耗时 {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"字幕提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def extract_subtitles_with_config(self, video_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """使用自定义配置的字幕提取演示"""
        logger.info(f"开始自定义配置字幕提取: {video_path}")
        
        try:
            start_time = time.time()
            
            # 使用自定义配置创建提取器
            custom_extractor = SubtitleExtractor(config)
            subtitles = custom_extractor.extract(video_path)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "success": True,
                "video_path": video_path,
                "config": config,
                "subtitle_count": len(subtitles),
                "processing_time": processing_time,
                "subtitles": subtitles,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"自定义配置字幕提取完成: {len(subtitles)} 条字幕, 耗时 {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"自定义配置字幕提取失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path,
                "config": config,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def extract_subtitles_batch(self, video_paths: List[str]) -> List[Dict[str, Any]]:
        """批量字幕提取演示"""
        logger.info(f"开始批量字幕提取: {len(video_paths)} 个视频")
        
        results = []
        
        for i, video_path in enumerate(video_paths):
            logger.info(f"处理视频 {i+1}/{len(video_paths)}: {video_path}")
            
            try:
                result = self.extract_subtitles_basic(video_path)
                results.append(result)
                
                # 添加延迟避免API限制
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"处理视频 {video_path} 时出错: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "video_path": video_path,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return results
    
    def save_subtitles_to_file(self, subtitles: List[Dict[str, Any]], output_path: str, format: str = "srt") -> bool:
        """保存字幕到文件"""
        try:
            if format.lower() == "srt":
                return self._save_srt_format(subtitles, output_path)
            elif format.lower() == "json":
                return self._save_json_format(subtitles, output_path)
            elif format.lower() == "vtt":
                return self._save_vtt_format(subtitles, output_path)
            else:
                logger.error(f"不支持的格式: {format}")
                return False
                
        except Exception as e:
            logger.error(f"保存字幕文件失败: {e}")
            return False
    
    def _save_srt_format(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为SRT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, subtitle in enumerate(subtitles, 1):
                    start_time = self._format_time(subtitle['start'])
                    end_time = self._format_time(subtitle['end'])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['text']}\n\n")
            
            logger.info(f"SRT字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存SRT文件失败: {e}")
            return False
    
    def _save_json_format(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为JSON格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(subtitles, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False
    
    def _save_vtt_format(self, subtitles: List[Dict[str, Any]], output_path: str) -> bool:
        """保存为VTT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                for subtitle in subtitles:
                    start_time = self._format_time_vtt(subtitle['start'])
                    end_time = self._format_time_vtt(subtitle['end'])
                    
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['text']}\n\n")
            
            logger.info(f"VTT字幕文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存VTT文件失败: {e}")
            return False
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """格式化时间为VTT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def analyze_extraction_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析字幕提取结果"""
        logger.info("分析字幕提取结果...")
        
        analysis = {
            "total_videos": len(results),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_subtitles": 0,
            "average_processing_time": 0,
            "average_subtitles_per_video": 0,
            "error_analysis": {}
        }
        
        processing_times = []
        subtitle_counts = []
        
        for result in results:
            if result["success"]:
                analysis["successful_extractions"] += 1
                analysis["total_subtitles"] += result["subtitle_count"]
                processing_times.append(result["processing_time"])
                subtitle_counts.append(result["subtitle_count"])
            else:
                analysis["failed_extractions"] += 1
                error_type = type(result.get("error", str(result.get("error", "unknown")))).__name__
                analysis["error_analysis"][error_type] = analysis["error_analysis"].get(error_type, 0) + 1
        
        # 计算平均值
        if processing_times:
            analysis["average_processing_time"] = sum(processing_times) / len(processing_times)
        
        if subtitle_counts:
            analysis["average_subtitles_per_video"] = sum(subtitle_counts) / len(subtitle_counts)
        
        logger.info(f"分析完成: {analysis['successful_extractions']}/{analysis['total_videos']} 成功")
        return analysis
    
    def run_demo(self, demo_type: str = "basic") -> Dict[str, Any]:
        """运行演示"""
        logger.info(f"开始Qwen3字幕提取演示: {demo_type}")
        
        demo_result = {
            "demo_type": demo_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": {}
        }
        
        try:
            # 创建演示视频
            demo_video_path = "demo_video.mp4"
            if not os.path.exists(demo_video_path):
                if not self.create_demo_video(demo_video_path):
                    logger.error("无法创建演示视频")
                    return demo_result
            
            if demo_type == "basic":
                # 基础演示
                result = self.extract_subtitles_basic(demo_video_path)
                demo_result["results"]["basic"] = result
                
                # 保存结果
                if result["success"]:
                    self.save_subtitles_to_file(result["subtitles"], "demo_subtitles.srt", "srt")
                    self.save_subtitles_to_file(result["subtitles"], "demo_subtitles.json", "json")
            
            elif demo_type == "advanced":
                # 高级演示
                # 使用不同配置
                configs = [
                    {"confidence_threshold": 0.9},
                    {"confidence_threshold": 0.95},
                    {"confidence_threshold": 0.98}
                ]
                
                advanced_results = {}
                for i, config in enumerate(configs):
                    result = self.extract_subtitles_with_config(demo_video_path, config)
                    advanced_results[f"config_{i+1}"] = result
                
                demo_result["results"]["advanced"] = advanced_results
                
                # 保存最佳结果
                best_result = max(advanced_results.values(), key=lambda x: x["subtitle_count"] if x["success"] else 0)
                if best_result["success"]:
                    self.save_subtitles_to_file(best_result["subtitles"], "best_subtitles.srt", "srt")
            
            elif demo_type == "batch":
                # 批量演示
                video_paths = [demo_video_path]
                
                # 创建额外的演示视频
                for i in range(2, 4):
                    extra_video = f"demo_video_{i}.mp4"
                    if not os.path.exists(extra_video):
                        self.create_demo_video(extra_video)
                    video_paths.append(extra_video)
                
                batch_results = self.extract_subtitles_batch(video_paths)
                demo_result["results"]["batch"] = batch_results
                
                # 分析结果
                analysis = self.analyze_extraction_results(batch_results)
                demo_result["results"]["analysis"] = analysis
                
                # 保存所有结果
                for i, result in enumerate(batch_results):
                    if result["success"]:
                        self.save_subtitles_to_file(result["subtitles"], f"batch_subtitles_{i+1}.srt", "srt")
            
            else:
                logger.error(f"未知的演示类型: {demo_type}")
            
            logger.info("演示完成")
            return demo_result
            
        except Exception as e:
            logger.error(f"演示运行失败: {e}")
            demo_result["error"] = str(e)
            return demo_result
    
    def print_demo_summary(self, demo_result: Dict[str, Any]):
        """打印演示摘要"""
        print("\n" + "=" * 60)
        print("Qwen3字幕提取演示摘要")
        print("=" * 60)
        print(f"演示类型: {demo_result['demo_type']}")
        print(f"演示时间: {demo_result['timestamp']}")
        print()
        
        results = demo_result.get("results", {})
        
        if "basic" in results:
            basic_result = results["basic"]
            print("基础演示结果:")
            print(f"  状态: {'✅ 成功' if basic_result['success'] else '❌ 失败'}")
            if basic_result["success"]:
                print(f"  字幕数量: {basic_result['subtitle_count']}")
                print(f"  处理时间: {basic_result['processing_time']:.2f}秒")
                print(f"  字幕预览:")
                for i, subtitle in enumerate(basic_result['subtitles'][:3]):
                    print(f"    {i+1}. {subtitle['text'][:50]}...")
            print()
        
        if "advanced" in results:
            print("高级演示结果:")
            for config_name, result in results["advanced"].items():
                print(f"  {config_name}: {'✅ 成功' if result['success'] else '❌ 失败'}")
                if result["success"]:
                    print(f"    字幕数量: {result['subtitle_count']}")
                    print(f"    处理时间: {result['processing_time']:.2f}秒")
            print()
        
        if "batch" in results:
            batch_results = results["batch"]
            analysis = results.get("analysis", {})
            
            print("批量演示结果:")
            print(f"  总视频数: {analysis.get('total_videos', 0)}")
            print(f"  成功提取: {analysis.get('successful_extractions', 0)}")
            print(f"  失败提取: {analysis.get('failed_extractions', 0)}")
            print(f"  总字幕数: {analysis.get('total_subtitles', 0)}")
            print(f"  平均处理时间: {analysis.get('average_processing_time', 0):.2f}秒")
            print(f"  平均每视频字幕数: {analysis.get('average_subtitles_per_video', 0):.1f}")
            print()
        
        if "error" in demo_result:
            print(f"错误: {demo_result['error']}")
        
        print("=" * 60)

def main():
    """主函数"""
    print("Qwen3字幕提取演示工具")
    print("=" * 50)
    
    # 创建演示实例
    demo = Qwen3SubtitleDemo()
    
    # 选择演示类型
    print("请选择演示类型:")
    print("1. 基础演示")
    print("2. 高级演示")
    print("3. 批量演示")
    print("4. 退出")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    if choice == "1":
        demo_type = "basic"
    elif choice == "2":
        demo_type = "advanced"
    elif choice == "3":
        demo_type = "batch"
    elif choice == "4":
        print("退出演示")
        return
    else:
        print("无效选择，使用默认基础演示")
        demo_type = "basic"
    
    # 运行演示
    demo_result = demo.run_demo(demo_type)
    
    # 打印摘要
    demo.print_demo_summary(demo_result)
    
    print("\n演示完成！")
    print("日志文件: qwen3_subtitle_extraction.log")
    print("字幕文件: demo_subtitles.srt, demo_subtitles.json")

if __name__ == "__main__":
    main()