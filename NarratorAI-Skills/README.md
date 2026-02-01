# NarratorAI Skills Collection

A comprehensive collection of 5 modular Claude skills for the NarratorAI project, created using the skill-creator framework. Each skill corresponds to one of NarratorAI's main task types.

## 📋 Skills Directory

### 1. 📺 [video-translation](./video-translation/SKILL.md)
**Video Translation Skill**

Translate videos into multiple languages with automatic subtitle extraction, professional domain-specific neural network translation, optional hard subtitle removal, and seamless video rendering.

**Use Cases:**
- Video content internationalization and localization
- Multi-language versions of shorts, movies, and entertainment content
- Preserving original video quality while adding translated subtitles
- Domain-specific terminology accuracy (technical, legal, medical, etc.)

**Key Features:**
- Automatic subtitle extraction (OCR)
- Hard subtitle seamless removal (optional)
- Professional domain-trained neural network translation
- Cultural terminology localization mapping
- Custom subtitle styling
- Batch processing support

---

### 2. 📄 [srt-translation](./srt-translation/SKILL.md)
**SRT Subtitle Translation Skill**

Translate SRT subtitle files into multiple target languages while preserving timecodes, format, and subtitle structure.

**Use Cases:**
- Individual subtitle file translation (without video processing)
- Batch processing of multiple SRT files
- Maintaining timecode and format accuracy during translation
- Supporting custom terminology and translation styles
- Preparing subtitles for multi-language video versions

**Key Features:**
- Preserves subtitle timecode precision
- Maintains subtitle format integrity
- Professional domain translation
- Custom terminology support
- Batch processing capabilities

---

### 3. 🧹 [video-erasure](./video-erasure/SKILL.md)
**Video Subtitle Erasure Skill**

Remove hard-coded subtitles from videos while maintaining video quality and seamless visual continuity. Uses advanced AI vision recognition and image inpainting techniques.

**Use Cases:**
- Removing original hard-coded subtitles from videos
- Preparing videos for subtitle replacement
- Restoring original video content (subtitle-free)
- Handling different subtitle complexities (normal vs. advanced mode)
- Preserving video quality during subtitle removal process

**Key Features:**
- AI vision recognition for subtitle location
- Intelligent image inpainting/reconstruction
- Normal and advanced erasure modes
- Video quality preservation
- Background reconstruction

---

### 4. 🔍 [video-extraction](./video-extraction/SKILL.md)
**Video Subtitle Extraction Skill**

Extract subtitles from videos using OCR (Optical Character Recognition) technology. Automatically detects and extracts hard-coded subtitles, preserves timing information, and generates SRT format files.

**Use Cases:**
- Extracting hard-coded subtitles from video frames
- Converting video subtitles to SRT format
- Supporting multiple languages and fonts
- Handling various subtitle styles and colors
- Batch processing of multiple video files

**Key Features:**
- High-precision OCR recognition (98%+ accuracy)
- Multi-language and font support
- Automatic subtitle timecode recognition
- SRT format output
- Various subtitle style handling

---

### 5. 🎬 [video-merging](./video-merging/SKILL.md)
**Video Subtitle Merging Skill**

Embed SRT subtitle files into videos with professional rendering. Supports extensive subtitle customization (font, size, color, position) and maintains video quality during the merge process.

**Use Cases:**
- Adding translated subtitles to videos
- Customizing subtitle appearance and positioning
- Batch processing of multiple videos with subtitles
- Supporting various subtitle styles and themes
- Maintaining video quality during subtitle embedding

**Key Features:**
- Professional video rendering engine
- Broadcast-grade quality processing
- Custom subtitle styling (font, size, color, position, alignment, border, shadow)
- High-resolution support (4K, etc.)
- Batch processing capability

---

## 🏗️ Skill Structure

Each skill follows the standard skill-creator structure:

```
skill-name/
├── SKILL.md                    # Main skill documentation with metadata and usage
├── scripts/                    # Executable Python scripts
│   └── narrator_api_client.py  # NarratorAI API client wrapper
├── references/                 # Reference documentation
│   └── api_reference.md        # Detailed API reference
└── assets/                     # Resource files (templates, configs, etc.)
```

## 🔗 API Integration

All skills integrate with NarratorAI's API service:

- **Base URL**: `https://openapi.jieshuo.cn/api/narrator/ai/v1/`
- **Authentication**: API key via `APP-KEY` header
- **Format**: JSON request/response

### Core API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/videoTasks` | Create new task |
| GET | `/videoTasks` | List all tasks |
| GET | `/videoTasks/{id}` | Get task details |
| POST | `/confirm/task/flow/{taskId}` | Confirm workflow step |
| POST | `/fileSets` | Create project folder |
| POST | `/files/upload` | Upload files |

## 🚀 Quick Start

### 1. Copy skill to your project

```bash
cp -r NarratorAI-Skills/video-translation ./skills/
```

### 2. Reference the skill in your Claude prompt

Include the skill's SKILL.md content in your prompt, and Claude will be able to use the skill.

### 3. Use scripts from the skill

```python
from narrator_api_client import NarratorAIClient

client = NarratorAIClient(api_key="your-api-key")
project = client.create_project("My Video Project")
```

## 📦 Packaging and Distribution

Each skill can be validated and packaged using the packaging tool from skill-creator:

```bash
python path/to/skill-creator/scripts/package_skill.py NarratorAI-Skills/video-translation
```

This generates a distributable zip file.

## 🔧 Customization and Extension

Each skill includes customizable aspects:

- **SKILL.md** - Update descriptions, use cases, and workflow instructions
- **scripts/** - Add more API wrappers and utility scripts
- **references/** - Add more detailed documentation
- **assets/** - Add configuration templates and style presets

## 📊 Task Type Mapping

| Skill | Task Type | Primary Function |
|-------|-----------|------------------|
| video-translation | video_translation | Full video translation including extraction, erasure, translation, and merging |
| srt-translation | srt_translation | SRT subtitle translation |
| video-erasure | video_erasure | Hard subtitle removal |
| video-extraction | video_extraction | Subtitle extraction from video |
| video-merging | video_merging | Video merging (subtitle embedding) |

## 🔐 Authentication and Configuration

All skills require the following to function:

1. **API Key** - NarratorAI backend API key
2. **Base URL** - API service address (default: https://openapi.jieshuo.cn)

Configure via environment variables:
```bash
export NARRATOR_API_KEY="your-api-key-here"
```

## 📝 API Response Format

All API responses follow a unified format:

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

## 🆘 FAQ

### Q: How do I create a project folder?
A: Use the `create_project` API call to create a project folder for organizing videos and subtitles.

### Q: Do the skills support batch processing?
A: Yes, all skills support batch processing. When uploading multiple files, ensure they have sequential numbering (e.g., video1.mp4, video2.mp4).

### Q: How long are uploaded files stored?
A: Uploaded resources are stored for 30 days, after which they are automatically deleted.

### Q: What video formats are supported?
A: Currently MP4 format is supported, with vertical orientation recommended.

## 📞 Support and Feedback

- Website: https://ai.jieshuo.cn/
- API Documentation: See references/api_reference.md in each skill

---

**Last Updated**: January 16, 2026
**Framework**: skill-creator by Awesome Claude Skills
**Project**: NarratorAI Skills for Claude
