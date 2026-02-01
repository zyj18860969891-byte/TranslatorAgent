# NarratorAI Skills Collection

这是使用skill-creator框架为NarratorAI项目构造的5个独立skill包。每个skill对应NarratorAI的一个主要任务类型。

## 📋 Skills 目录

### 1. 📺 [video-translation](./video-translation/SKILL.md)
**视频翻译 - Video Translation**

将视频翻译成多种语言，包括自动字幕提取、专业级神经网络翻译、可选的硬字幕移除和视频渲染。

**应用场景：**
- 视频内容国际化和本地化
- 短剧、电影内容多语言版本
- 保留原始视频质量同时添加翻译字幕
- 需要专业术语精准度的领域（技术、法律、医学等）

**关键功能：**
- 自动字幕提取（OCR）
- 硬字幕无痕擦除（可选）
- 专业领域神经网络翻译
- 文化术语本地化映射
- 自定义字幕样式
- 批量处理支持

---

### 2. 📄 [srt-translation](./srt-translation/SKILL.md)
**字幕翻译 - SRT Translation**

翻译SRT字幕文件到多个目标语言，同时保持时间码、格式和字幕结构。

**应用场景：**
- 单独的字幕文件翻译（不需要视频处理）
- 多个SRT文件的批量处理
- 在字幕翻译期间保持时间码和格式
- 支持自定义术语和翻译风格
- 为多语言视频版本准备字幕

**关键功能：**
- 保持字幕时间码精确性
- 字幕格式保留
- 专业领域翻译
- 自定义术语支持
- 批量处理

---

### 3. 🧹 [video-erasure](./video-erasure/SKILL.md)
**字幕擦除 - Video Subtitle Erasure**

从视频中移除硬编码的字幕，同时保持视频质量和无缝视觉连续性。使用高级AI视觉识别和图像修复技术。

**应用场景：**
- 从视频中移除原始硬字幕
- 为字幕替换准备视频
- 恢复原始视频内容（无字幕覆盖）
- 处理不同复杂度的字幕（普通模式 vs 高级模式）
- 视频质量保留在字幕移除过程中

**关键功能：**
- AI视觉识别定位字幕
- 智能图像修复/Inpainting
- 普通和高级擦除模式
- 视频质量保留
- 背景重建

---

### 4. 🔍 [video-extraction](./video-extraction/SKILL.md)
**字幕提取 - Video Subtitle Extraction**

使用OCR（光学字符识别）技术从视频中提取字幕。自动检测并提取硬编码字幕，保留时间信息并生成SRT格式文件。

**应用场景：**
- 从视频中提取硬编码字幕
- 将视频字幕转换为SRT格式
- 支持多种语言和字体
- 处理各种字幕样式和颜色
- 多个视频文件的批量处理

**关键功能：**
- 高精度OCR识别（98%+准确率）
- 多语言和字体支持
- 字幕时间码自动识别
- SRT格式输出
- 各种字幕样式处理

---

### 5. 🎬 [video-merging](./video-merging/SKILL.md)
**视频压制 - Video Subtitle Merging**

将SRT字幕文件嵌入视频中进行专业渲染。支持广泛的字幕定制（字体、大小、颜色、位置）并在合并过程中保持视频质量。

**应用场景：**
- 将翻译字幕添加到视频中
- 自定义字幕外观和位置
- 多个视频和字幕的批量处理
- 支持各种字幕样式和主题
- 字幕嵌入过程中保持视频质量

**关键功能：**
- 专业视频渲染引擎
- 广播级质量处理
- 自定义字幕样式（字体、大小、颜色、位置、对齐、边框、阴影）
- 高分辨率支持（4K等）
- 批量处理能力

---

## 🏗️ Skill 结构

每个skill遵循标准的skill-creator结构：

```
skill-name/
├── SKILL.md                    # 主要skill文档，包含元数据和使用说明
├── scripts/                    # 可执行的Python脚本
│   └── narrator_api_client.py  # NarratorAI API客户端封装
├── references/                 # 参考文档
│   └── api_reference.md        # 详细的API参考
└── assets/                     # 资源文件（模板、配置等）
```

## 🔗 API 集成

所有skills都集成了NarratorAI的API服务：

- **基础URL**: `https://openapi.jieshuo.cn/api/narrator/ai/v1/`
- **认证**: 使用 `APP-KEY` 头进行API密钥认证
- **格式**: JSON请求/响应

### 核心API端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/videoTasks` | 创建新任务 |
| GET | `/videoTasks` | 获取任务列表 |
| GET | `/videoTasks/{id}` | 获取任务详情 |
| POST | `/confirm/task/flow/{taskId}` | 确认任务流程步骤 |
| POST | `/fileSets` | 创建项目文件夹 |
| POST | `/files/upload` | 上传文件 |

## 🚀 快速开始

### 1. 复制skill到你的项目

```bash
cp -r NarratorAI-Skills/video-translation ./skills/
```

### 2. 在你的Claude提示中引用skill

在你的提示中包含skill的SKILL.md内容，Claude将能够使用该skill。

### 3. 使用skill中的脚本

```python
from narrator_api_client import NarratorAIClient

client = NarratorAIClient(api_key="your-api-key")
project = client.create_project("My Video Project")
```

## 📦 打包和分发

每个skill可以使用skill-creator中的打包工具进行验证和打包：

```bash
python path/to/skill-creator/scripts/package_skill.py NarratorAI-Skills/video-translation
```

这将生成一个可分发的zip文件。

## 🔧 自定义和扩展

每个skill都包含以下可定制的方面：

- **SKILL.md** - 更新描述、使用场景和工作流程说明
- **scripts/** - 添加更多API包装器和工具脚本
- **references/** - 添加更详细的文档
- **assets/** - 添加配置模板和样式预设

## 📊 Tasks类型对应关系

| Skill | Task Type | 主要功能 |
|-------|-----------|---------|
| video-translation | video_translation | 视频翻译，含字幕提取、擦除、翻译和压制 |
| srt-translation | srt_translation | SRT字幕翻译 |
| video-erasure | video_erasure | 硬字幕擦除 |
| video-extraction | video_extraction | 字幕提取 |
| video-merging | video_merging | 视频压制（字幕嵌入） |

## 🔐 认证和配置

所有skills需要以下信息才能工作：

1. **API密钥** - NarratorAI后端API密钥
2. **基础URL** - API服务地址（默认：https://openapi.jieshuo.cn）

通过环境变量配置：
```bash
export NARRATOR_API_KEY="your-api-key-here"
```

## 📝 API返回格式

所有API响应遵循统一格式：

```json
{
  "code": 10000,
  "message": "success",
  "data": {
    "id": 123,
    "task_type": "video-translation",
    "status": 2,
    "created_at": "2026-01-16T10:00:00+08:00"
  },
  "trace": {
    "request_id": "uuid",
    "timestamp": 1673913600,
    "take_time": 100
  }
}
```

## 🆘 常见问题

### Q: 如何创建项目文件夹？
A: 使用`create_project` API调用创建项目文件夹来组织视频和字幕文件。

### Q: 是否支持批量处理？
A: 是的，所有skills都支持批量处理。上传多个文件时，确保它们具有序列号命名（如 video1.mp4, video2.mp4）。

### Q: 文件会存储多长时间？
A: 上传的资源在30天内保存，之后会自动删除。

### Q: 支持哪些视频格式？
A: 目前支持MP4格式，建议为竖屏视频。

## 📞 支持和反馈

- 官网：https://ai.jieshuo.cn/
- API文档：参考各skill中的references/api_reference.md

---

**最后更新**: 2026年1月16日
**框架**: skill-creator by Awesome Claude Skills
**项目**: NarratorAI Skills for Claude
