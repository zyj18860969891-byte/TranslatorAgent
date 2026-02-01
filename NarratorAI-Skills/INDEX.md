# 🎯 NarratorAI Skills - 快速导航

> 使用skill-creator框架为NarratorAI项目构建的5个模块化Claude Skills

## 📁 文件位置

```
D:\MultiMode\Translator\NarratorAI-Skills\
```

## 📚 文档导航

### 📖 项目文档
- [📄 README.md](./README.md) - 英文项目介绍
- [📄 README_CN.md](./README_CN.md) - 中文项目介绍
- [📄 PROJECT_SUMMARY_CN.md](./PROJECT_SUMMARY_CN.md) - 项目完成总结报告
- [📄 INDEX.md](./INDEX.md) - 本文档

### 🎬 5个核心Skills

#### 1. 📺 视频翻译 (video-translation)
```
video-translation/
├── SKILL.md ← 开始阅读
├── scripts/narrator_api_client.py ← 查看代码
└── references/api_reference.md ← API文档
```
**作用**: 将视频翻译成多种语言
**任务类型**: `video_translation`
[详细信息](./video-translation/SKILL.md)

#### 2. 📄 字幕翻译 (srt-translation)
```
srt-translation/
├── SKILL.md ← 开始阅读
├── scripts/narrator_api_client.py ← 查看代码
└── references/api_reference.md ← API文档
```
**作用**: 翻译SRT字幕文件
**任务类型**: `srt_translation`
[详细信息](./srt-translation/SKILL.md)

#### 3. 🧹 字幕擦除 (video-erasure)
```
video-erasure/
├── SKILL.md ← 开始阅读
├── scripts/narrator_api_client.py ← 查看代码
└── references/api_reference.md ← API文档
```
**作用**: 从视频中移除硬字幕
**任务类型**: `video_erasure`
[详细信息](./video-erasure/SKILL.md)

#### 4. 🔍 字幕提取 (video-extraction)
```
video-extraction/
├── SKILL.md ← 开始阅读
├── scripts/narrator_api_client.py ← 查看代码
└── references/api_reference.md ← API文档
```
**作用**: 从视频中提取硬字幕（OCR）
**任务类型**: `video_extraction`
[详细信息](./video-extraction/SKILL.md)

#### 5. 🎬 视频压制 (video-merging)
```
video-merging/
├── SKILL.md ← 开始阅读
├── scripts/narrator_api_client.py ← 查看代码
└── references/api_reference.md ← API文档
```
**作用**: 将字幕嵌入视频
**任务类型**: `video_merging`
[详细信息](./video-merging/SKILL.md)

---

## 🚀 快速开始

### 方法1: 在Claude中直接使用

1. 打开你想使用的skill文件夹
2. 复制该skill的 `SKILL.md` 内容
3. 粘贴到Claude提示中
4. Claude现在可以使用这个skill

### 方法2: 在Python中使用

```python
# 导入API客户端
import sys
sys.path.append('NarratorAI-Skills/video-translation/scripts')
from narrator_api_client import NarratorAIClient

# 创建客户端
client = NarratorAIClient(api_key="your-api-key")

# 创建项目
project = client.create_project("My Project")
print(f"项目ID: {project['data']['id']}")

# 上传文件
result = client.upload_file(project['data']['id'], 'video.mp4')

# 创建翻译任务
task_data = {
    'task_type': 'video_translation',
    'original_language': '中文',
    'target_languages': [{'language': '英语', 'area': '美国'}],
    'resources': {
        'file_set_id': project['data']['id'],
        'file_ids': [result['data']['files'][0]['file_id']]
    }
}
task = client.create_task(task_data)
print(f"任务ID: {task['data']['id']}")

# 查询状态
status = client.get_task_status(task['data']['id'])
print(f"状态: {status['data']['status']}")
```

---

## 📊 Skills 对比表

| 功能 | video-translation | srt-translation | video-erasure | video-extraction | video-merging |
|------|------------------|-----------------|----------------|-----------------|---------------|
| 输入类型 | 视频 | SRT文件 | 视频 | 视频 | 视频+SRT |
| 输出类型 | 视频 | SRT文件 | 视频 | SRT文件 | 视频 |
| 包含提取 | ✓ | ✗ | ✗ | ✓ | ✗ |
| 包含翻译 | ✓ | ✓ | ✗ | ✗ | ✗ |
| 包含擦除 | ✓ | ✗ | ✓ | ✗ | ✗ |
| 包含压制 | ✓ | ✗ | ✗ | ✗ | ✓ |
| 处理速度 | 快 | 最快 | 中等 | 中等 | 中等 |
| 复杂度 | 高 | 低 | 中 | 中 | 低 |

---

## 🔗 API 速查表

### 基础URL
```
https://openapi.jieshuo.cn/api/narrator/ai/v1/
```

### 认证
```
Header: APP-KEY: {your-api-key}
```

### 主要端点

| 方法 | 端点 | 说明 | Skill |
|------|------|------|-------|
| POST | /videoTasks | 创建任务 | 全部 |
| GET | /videoTasks/{id} | 获取任务 | 全部 |
| POST | /confirm/task/flow/{taskId} | 确认步骤 | 全部 |
| POST | /fileSets | 创建项目 | 全部 |
| POST | /files/upload | 上传文件 | 全部 |

---

## 💾 文件结构总览

```
NarratorAI-Skills/
├── README.md                          # 英文介绍
├── README_CN.md                       # 中文介绍
├── PROJECT_SUMMARY_CN.md              # 项目总结
├── INDEX.md                           # 本文档
│
├── video-translation/
│   ├── SKILL.md
│   ├── scripts/narrator_api_client.py
│   ├── references/api_reference.md
│   └── assets/
│
├── srt-translation/
│   ├── SKILL.md
│   ├── scripts/narrator_api_client.py
│   ├── references/api_reference.md
│   └── assets/
│
├── video-erasure/
│   ├── SKILL.md
│   ├── scripts/narrator_api_client.py
│   ├── references/api_reference.md
│   └── assets/
│
├── video-extraction/
│   ├── SKILL.md
│   ├── scripts/narrator_api_client.py
│   ├── references/api_reference.md
│   └── assets/
│
└── video-merging/
    ├── SKILL.md
    ├── scripts/narrator_api_client.py
    ├── references/api_reference.md
    └── assets/

总计: 25个文件
```

---

## 🎓 学习路径

### 初学者
1. 阅读 [README_CN.md](./README_CN.md) - 了解项目概述
2. 选一个简单的skill（如 `srt-translation`）
3. 阅读其SKILL.md文件
4. 尝试在Claude中使用

### 进阶用户
1. 阅读 [PROJECT_SUMMARY_CN.md](./PROJECT_SUMMARY_CN.md) - 了解实现细节
2. 研究 `scripts/narrator_api_client.py` - 了解API调用
3. 阅读 `references/api_reference.md` - 深入理解API
4. 尝试集成到自己的项目

### 开发者
1. 了解skill-creator框架结构
2. 扩展API客户端功能
3. 添加错误处理和重试逻辑
4. 创建自定义工具函数
5. 贡献改进到项目

---

## ⚙️ 配置和使用

### 环境变量
```bash
export NARRATOR_API_KEY="your-api-key-here"
```

### Python依赖
```bash
pip install requests
```

### 验证安装
```bash
python -c "from narrator_api_client import NarratorAIClient; print('✓ Installation OK')"
```

---

## 🆘 常见问题

### Q: 如何获取API密钥？
A: 访问 https://ai.jieshuo.cn/ 注册并获取API密钥

### Q: 文件支持的格式有哪些？
A: 视频(MP4)、字幕(SRT)

### Q: 文件会保存多长时间？
A: 30天

### Q: 如何实现自动化处理？
A: 使用 `auto_run: 1` 参数进行全自动处理

### Q: 是否支持批量处理？
A: 是，按序号命名多个文件即可

### Q: 如何跟踪任务进度？
A: 使用 `get_task_status()` 方法查询

---

## 📞 获取帮助

- 📖 官网文档: https://ai.jieshuo.cn/
- 💬 GitHub Issues: [NarratorAI](https://github.com/Narrator-AI/NarratorAI)
- 📝 skill-creator文档: 参考 skills中的references/

---

## 🎯 相关文件位置

| 项目 | 位置 |
|------|------|
| **NarratorAI Skills** | `D:\MultiMode\Translator\NarratorAI-Skills\` |
| **NarratorAI项目** | `D:\MultiMode\Translator\NarratorAI-main\` |
| **skill-creator工具** | `D:\MultiMode\awesome-claude-skills-temp\awesome-claude-skills-master\skill-creator\` |
| **创建脚本** | `D:\MultiMode\Translator\create_narrator_skills.py` |

---

## ✨ 项目特点

✅ **完全模块化** - 每个功能独立为一个skill
✅ **标准化结构** - 遵循skill-creator框架
✅ **生产就绪** - 包含完整文档和代码
✅ **Claude友好** - 可直接在Claude提示中使用
✅ **易于扩展** - 简单添加新功能
✅ **双语文档** - 中英文都支持

---

## 📅 项目信息

- **创建日期**: 2026年1月16日
- **框架**: skill-creator (awesome-claude-skills)
- **Status**: 🟢 生产就绪
- **版本**: 1.0.0
- **总文件数**: 25+
- **覆盖功能**: 5个核心NarratorAI任务类型

---

**快速链接**:
- [开始使用](#-快速开始)
- [Skills列表](#-5个核心skills)
- [API参考](#-api-速查表)
- [常见问题](#-常见问题)

**上次更新**: 2026年1月16日
