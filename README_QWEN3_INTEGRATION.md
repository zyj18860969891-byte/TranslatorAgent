# Qwen3集成包使用指南

## 概述

这是一个完整的Qwen3模型集成包，专为OpenManus TranslatorAgent项目设计。该包提供了字幕提取、视频翻译、情感分析和批量处理等功能，支持多种Qwen3模型。

## 功能特性

- 🎬 **字幕提取**: 使用Qwen3-VL-Rerank模型从视频中提取字幕
- 🌍 **视频翻译**: 使用Qwen3-Omni-Flash-Realtime模型进行实时视频翻译
- 😊 **情感分析**: 分析视频内容的情感倾向
- 📦 **批量处理**: 支持批量处理多个视频文件
- 🔧 **配置管理**: 灵活的配置管理系统
- 🛠️ **工具集**: 完整的工具函数库
- 📊 **进度跟踪**: 详细的进度和性能监控

## 文件结构

```
qwen3_integration/
├── __init__.py              # 模块初始化
├── config.py                # 配置管理
├── utils.py                 # 工具函数
├── subtitle_extractor.py    # 字幕提取器
├── video_translator.py      # 视频翻译器
├── emotion_analyzer.py      # 情感分析器
└── batch_processor.py       # 批量处理器

demo_complete_qwen3_integration.py  # 完整演示脚本
start_qwen3_demo.bat               # Windows快速启动脚本
validate_qwen3_config.py          # 配置验证脚本
demo_qwen3_subtitle_extraction.py # 字幕提取演示
```

## 安装要求

### 系统要求
- Python 3.8+
- Windows/Linux/macOS
- 至少4GB内存
- 稳定的网络连接

### Python包依赖
```bash
pip install dashscope opencv-python Pillow requests aiohttp psutil
```

### 环境变量设置
```bash
# 必需的环境变量
export DASHSCOPE_API_KEY="your_api_key_here"

# 可选的环境变量
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com"
export DASHSCOPE_TIMEOUT="30"
export DASHSCOPE_MAX_RETRIES="3"
export DASHSCOPE_RETRY_DELAY="1"
```

## 快速开始

### 方法1: 使用快速启动脚本（推荐）

```bash
# Windows
start_qwen3_demo.bat

# Linux/macOS
chmod +x start_qwen3_demo.sh
./start_qwen3_demo.sh
```

### 方法2: 手动运行

```bash
# 1. 设置环境变量
export DASHSCOPE_API_KEY="your_api_key_here"

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行演示
python demo_complete_qwen3_integration.py
```

### 方法3: 直接使用模块

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "qwen3_integration"))

from qwen3_integration.subtitle_extractor import SubtitleExtractor
from qwen3_integration.video_translator import VideoTranslator
from qwen3_integration.emotion_analyzer import EmotionAnalyzer

# 初始化组件
extractor = SubtitleExtractor()
translator = VideoTranslator()
analyzer = EmotionAnalyzer()

# 使用组件
result = extractor.extract("your_video.mp4")
print(f"提取到 {len(result['subtitles'])} 条字幕")
```

## 详细使用指南

### 1. 字幕提取

```python
from qwen3_integration.subtitle_extractor import SubtitleExtractor

extractor = SubtitleExtractor()

# 基本使用
result = extractor.extract("video.mp4")
if result["success"]:
    subtitles = result["subtitles"]
    for subtitle in subtitles:
        print(f"{subtitle['start']} - {subtitle['end']}: {subtitle['text']}")

# 高级使用
result = extractor.extract(
    "video.mp4",
    frame_interval=30,
    max_frames=200,
    confidence_threshold=0.9,
    output_format="srt"
)
```

### 2. 视频翻译

```python
from qwen3_integration.video_translator import VideoTranslator

translator = VideoTranslator()

# 基本翻译
result = translator.translate("video.mp4", target_language="en")
if result["success"]:
    print(f"翻译结果: {result['translated_text']}")

# 高级翻译
result = translator.translate(
    "video.mp4",
    target_language="en",
    realtime_mode=True,
    emotion_aware=True,
    cultural_adaptation=True
)
```

### 3. 情感分析

```python
from qwen3_integration.emotion_analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer()

# 分析文本情感
result = analyzer.analyze("今天天气真好，我感到很开心！")
if result["success"]:
    emotions = result["emotions"]
    print(f"主要情感: {result['dominant_emotion']}")
    print(f"情感分布: {emotions}")

# 分析字幕情感
result = analyzer.analyze_subtitles(subtitles)
if result["success"]:
    print(f"整体情感趋势: {result['emotion_trend']}")
```

### 4. 批量处理

```python
from qwen3_integration.batch_processor import BatchProcessor

processor = BatchProcessor()

# 批量处理
video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
result = processor.process_video_files(video_files)

if result["success"]:
    print(f"成功处理 {result['processed_count']} 个文件")
    print(f"失败处理 {result['failed_count']} 个文件")
    
    # 查看处理结果
    for item in result["results"]:
        print(f"{item['file']}: {item['status']}")
```

### 5. 配置管理

```python
from qwen3_integration.config import get_config_manager

config_manager = get_config_manager()

# 获取模型配置
model_config = config_manager.get_model_config("qwen3-vl-rerank")
print(f"模型配置: {model_config}")

# 获取功能配置
feature_config = config_manager.get_feature_config("subtitle_extraction")
print(f"功能配置: {feature_config}")

# 更新配置
config_manager.update_model_config("qwen3-vl-rerank", {"enabled": True})
config_manager.save_configs()
```

### 6. 工具函数

```python
from qwen3_integration.utils import (
    get_image_utils, get_text_utils, get_file_utils,
    validate_environment, clean_temp_files
)

# 图像处理
image_utils = get_image_utils()
frames = image_utils.extract_frames("video.mp4", frame_interval=30)

# 文本处理
text_utils = get_text_utils()
cleaned_text = text_utils.clean_text("原始文本...")
chunks = text_utils.split_text(cleaned_text, max_length=100)

# 文件处理
file_utils = get_file_utils()
file_utils.save_json(data, "output.json")

# 环境验证
validation = validate_environment()
print(f"环境验证: {'通过' if validation['valid'] else '失败'}")

# 清理临时文件
clean_temp_files(["temp_*.jpg", "*.tmp"])
```

## 配置文件

### model_config.json

```json
{
  "models": {
    "qwen3-vl-rerank": {
      "name": "Qwen3-VL-Rerank",
      "type": "vision",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "${DASHSCOPE_API_KEY}",
      "max_tokens": 1000,
      "temperature": 0.1,
      "timeout": 30,
      "enabled": true
    },
    "qwen3-omni-flash-realtime": {
      "name": "Qwen3-Omni-Flash-Realtime",
      "type": "realtime",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "${DASHSCOPE_API_KEY}",
      "max_tokens": 2000,
      "temperature": 0.7,
      "timeout": 30,
      "enabled": false
    }
  }
}
```

### feature_config.json

```json
{
  "features": {
    "subtitle_extraction": {
      "primary_model": "qwen3-vl-rerank",
      "fallback_model": "qwen3-omni-flash-realtime",
      "confidence_threshold": 0.95,
      "supported_formats": ["srt", "vtt", "ass", "ssa"],
      "max_text_length": 500
    },
    "video_translation": {
      "primary_model": "qwen3-omni-flash-realtime",
      "embedding_support": "qwen3-embedding",
      "realtime_mode": true,
      "batch_size": 10,
      "max_concurrent_requests": 5
    }
  }
}
```

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: Invalid API key
   解决: 检查DASHSCOPE_API_KEY环境变量是否正确设置
   ```

2. **模型不可用**
   ```
   错误: Model not available
   解决: 检查模型配置，确认模型名称正确
   ```

3. **网络连接问题**
   ```
   错误: Connection timeout
   解决: 检查网络连接，调整DASHSCOPE_TIMEOUT环境变量
   ```

4. **内存不足**
   ```
   错误: Memory allocation failed
   解决: 减少batch_size或增加系统内存
   ```

### 调试模式

```python
import logging
from qwen3_integration.utils import setup_logging

# 启用调试日志
logger = setup_logging("debug", logging.DEBUG)

# 运行调试
python -m qwen3_integration.debug
```

### 性能优化

1. **批量处理优化**
   ```python
   # 调整并发数
   processor = BatchProcessor(max_workers=4)
   
   # 调整批大小
   result = processor.process_video_files(files, batch_size=5)
   ```

2. **缓存优化**
   ```python
   # 启用缓存
   extractor = SubtitleExtractor(use_cache=True)
   translator = VideoTranslator(use_cache=True)
   ```

3. **内存优化**
   ```python
   # 减少帧提取数量
   frames = image_utils.extract_frames(video_path, frame_interval=60, max_frames=100)
   ```

## API参考

### SubtitleExtractor

```python
class SubtitleExtractor:
    def __init__(self, config: Dict[str, Any] = None, use_cache: bool = False)
    def extract(self, video_path: str, **kwargs) -> Dict[str, Any]
    def extract_frames(self, video_path: str, **kwargs) -> List[str]
    def recognize_text(self, frames: List[str], **kwargs) -> List[Dict[str, Any]]
    def post_process(self, results: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]
```

### VideoTranslator

```python
class VideoTranslator:
    def __init__(self, config: Dict[str, Any] = None, use_cache: bool = False)
    def translate(self, video_path: str, target_language: str, **kwargs) -> Dict[str, Any]
    def translate_text(self, text: str, target_language: str, **kwargs) -> Dict[str, Any]
    def translate_with_emotion(self, text: str, emotions: Dict[str, float], **kwargs) -> Dict[str, Any]
```

### EmotionAnalyzer

```python
class EmotionAnalyzer:
    def __init__(self, config: Dict[str, Any] = None, use_cache: bool = False)
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]
    def analyze_subtitles(self, subtitles: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]
    def calculate_emotion_trend(self, emotions: List[Dict[str, Any]]) -> Dict[str, Any]
```

### BatchProcessor

```python
class BatchProcessor:
    def __init__(self, config: Dict[str, Any] = None, max_workers: int = 4)
    def process_video_files(self, video_files: List[str], **kwargs) -> Dict[str, Any]
    def process_single_file(self, video_path: str, **kwargs) -> Dict[str, Any]
    def get_progress(self) -> Dict[str, Any]
    def cancel_all(self) -> None
```

## 版本历史

### v1.0.0 (2024-01-20)
- 初始版本发布
- 支持字幕提取、视频翻译、情感分析
- 完整的配置管理系统
- 批量处理功能
- 完整的工具函数库

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。

## 支持

如果您遇到问题或有建议，请：

1. 查看故障排除部分
2. 检查已知问题
3. 提交Issue
4. 联系开发团队

## 更新日志

### 最新更新
- 完整的Qwen3集成包
- 支持多种模型
- 增强的错误处理
- 性能优化
- 完整的文档

### 计划中的功能
- [ ] 支持更多视频格式
- [ ] 增强的OCR功能
- [ ] 多语言支持
- [ ] 云端部署支持
- [ ] 移动端支持

---

**注意**: 本项目需要有效的DashScope API密钥才能正常工作。请确保您已正确设置相关环境变量。