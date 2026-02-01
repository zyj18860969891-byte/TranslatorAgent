# OpenManus TranslatorAgent 快速开始指南

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 8GB+ RAM
- 稳定的网络连接

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-org/openmanus-translator-agent.git
cd openmanus-translator-agent
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# 创建 .env 文件
echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env
```

#### 4. 初始化配置
```bash
python setup.py
```

## 🎯 基础使用

### 字幕提取

#### 命令行使用
```bash
python -m translator_agent extract_subtitles video.mp4
```

#### Python API
```python
from translator_agent import SubtitleExtractor

# 创建提取器
extractor = SubtitleExtractor()

# 提取字幕
subtitles = extractor.extract("video.mp4")

# 保存结果
extractor.save(subtitles, "output.srt")
```

### 视频翻译

#### 命令行使用
```bash
python -m translator_agent translate video.mp4 --target-language zh
```

#### Python API
```python
from translator_agent import VideoTranslator

# 创建翻译器
translator = VideoTranslator()

# 翻译视频
translations = translator.translate("video.mp4", "zh")

# 保存结果
translator.save(translations, "translation.txt")
```

### 情感分析

#### Python API
```python
from translator_agent import EmotionAnalyzer

# 创建分析器
analyzer = EmotionAnalyzer()

# 分析情感
emotions = analyzer.analyze("video.mp4")

# 输出结果
print(f"主要情感: {emotions['primary_emotion']}")
print(f"置信度: {emotions['confidence']}")
```

## ⚙️ 配置说明

### 模型配置

编辑 `model_config.json` 文件：

```json
{
  "models": {
    "qwen3-omni-flash-realtime": {
      "name": "Qwen3-Omni-Flash-Realtime",
      "type": "realtime",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "${DASHSCOPE_API_KEY}",
      "max_tokens": 2000,
      "temperature": 0.7,
      "timeout": 30,
      "enabled": true
    },
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
    "qwen3-embedding": {
      "name": "Qwen3-Embedding",
      "type": "embedding",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "${DASHSCOPE_API_KEY}",
      "max_tokens": 8192,
      "temperature": 0.0,
      "timeout": 30,
      "enabled": true
    }
  }
}
```

### 功能配置

编辑 `config.json` 文件：

```json
{
  "features": {
    "subtitle_extraction": {
      "primary_model": "qwen3-vl-rerank",
      "fallback_model": "qwen3-omni-flash-realtime",
      "confidence_threshold": 0.95
    },
    "video_translation": {
      "primary_model": "qwen3-omni-flash-realtime",
      "embedding_support": "qwen3-embedding",
      "realtime_mode": true
    },
    "emotion_analysis": {
      "primary_model": "qwen3-omni-flash-realtime",
      "emotion_types": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]
    },
    "localization": {
      "primary_model": "qwen3-omni-flash-realtime",
      "embedding_support": "qwen3-embedding",
      "cultural_adaptation": true
    }
  }
}
```

## 📖 示例代码

### 完整工作流示例

```python
from translator_agent import SubtitleExtractor, VideoTranslator, EmotionAnalyzer
from translator_agent.utils import VideoProcessor, FileManager

def process_video(video_path, target_language="zh"):
    """
    完整的视频处理工作流
    """
    
    # 1. 初始化组件
    extractor = SubtitleExtractor()
    translator = VideoTranslator()
    analyzer = EmotionAnalyzer()
    processor = VideoProcessor()
    
    print(f"开始处理视频: {video_path}")
    
    # 2. 视频预处理
    print("正在预处理视频...")
    processed_video = processor.preprocess(video_path)
    
    # 3. 字幕提取
    print("正在提取字幕...")
    subtitles = extractor.extract(processed_video)
    
    # 4. 情感分析
    print("正在分析情感...")
    emotions = analyzer.analyze(subtitles)
    
    # 5. 视频翻译
    print("正在翻译视频...")
    translations = translator.translate(
        subtitles=subtitles,
        target_language=target_language,
        emotions=emotions
    )
    
    # 6. 保存结果
    print("正在保存结果...")
    
    # 保存字幕
    extractor.save(subtitles, "subtitles.srt")
    
    # 保存翻译
    translator.save(translations, "translations.txt")
    
    # 保存情感分析结果
    analyzer.save(emotions, "emotions.json")
    
    print("处理完成！")
    
    return {
        "subtitles": subtitles,
        "translations": translations,
        "emotions": emotions
    }

# 使用示例
if __name__ == "__main__":
    result = process_video("example.mp4", "zh")
    print(f"处理了 {len(result['subtitles'])} 条字幕")
    print(f"翻译了 {len(result['translations'])} 条文本")
    print(f"检测到主要情感: {result['emotions']['primary_emotion']}")
```

### 批量处理示例

```python
from translator_agent import BatchProcessor
import os

def batch_process_videos(video_dir, output_dir, target_language="zh"):
    """
    批量处理视频文件
    """
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化批量处理器
    batch_processor = BatchProcessor(
        max_workers=4,
        chunk_size=10
    )
    
    # 获取所有视频文件
    video_files = [
        f for f in os.listdir(video_dir)
        if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))
    ]
    
    print(f"找到 {len(video_files)} 个视频文件")
    
    # 批量处理
    results = batch_processor.process(
        video_files=video_files,
        video_dir=video_dir,
        output_dir=output_dir,
        target_language=target_language
    )
    
    # 生成报告
    batch_processor.generate_report(results, "batch_report.json")
    
    return results

# 使用示例
if __name__ == "__main__":
    results = batch_process_videos(
        video_dir="videos/",
        output_dir="output/",
        target_language="zh"
    )
    
    print(f"批量处理完成，共处理 {len(results)} 个视频")
```

## 🔧 故障排除

### 常见问题

#### 1. API 密钥错误
```
Error: Invalid API key
```
**解决方案**:
- 检查 `.env` 文件中的 API 密钥
- 确认 API 密钥是否有效
- 验证网络连接

#### 2. 模型不可用
```
Error: Model not available
```
**解决方案**:
- 检查模型配置文件
- 确认模型是否在可用列表中
- 联系模型提供商

#### 3. 内存不足
```
Error: Out of memory
```
**解决方案**:
- 减小视频文件大小
- 增加系统内存
- 使用分片处理

#### 4. 网络连接问题
```
Error: Connection timeout
```
**解决方案**:
- 检查网络连接
- 增加超时时间
- 使用代理服务器

### 调试模式

启用调试模式：
```bash
export DEBUG=true
python -m translator_agent extract_subtitles video.mp4
```

查看详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 技术支持

### 获取帮助
- **文档**: 查看 [完整文档](https://docs.openmanus.com)
- **示例**: 查看 [示例代码](https://github.com/your-org/openmanus-translator-agent/tree/main/examples)
- **问题报告**: [GitHub Issues](https://github.com/your-org/openmanus-translator-agent/issues)

### 社区支持
- **论坛**: [OpenManus 社区](https://community.openmanus.com)
- **聊天**: [Discord 频道](https://discord.gg/openmanus)
- **邮件**: [support@openmanus.com](mailto:support@openmanus.com)

## 🎯 下一步

### 学习资源
1. [API 文档](https://docs.openmanus.com/api)
2. [最佳实践指南](https://docs.openmanus.com/guides)
3. [视频教程](https://docs.openmanus.com/tutorials)

### 进阶功能
1. [自定义模型配置](https://docs.openmanus.com/advanced/models)
2. [批量处理优化](https://docs.openmanus.com/advanced/batch)
3. [性能调优](https://docs.openmanus.com/advanced/performance)

### 贡献代码
1. [贡献指南](https://docs.openmanus.com/contributing)
2. [代码规范](https://docs.openmanus.com/standards)
3. [测试指南](https://docs.openmanus.com/testing)

---

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 致谢

感谢以下开源项目和贡献者：
- [Qwen3](https://github.com/QwenLM/Qwen)
- [OpenCV](https://opencv.org/)
- [DashScope](https://dashscope.aliyuncs.com/)

---

**开始使用 OpenManus TranslatorAgent，让视频翻译变得简单高效！** 🚀