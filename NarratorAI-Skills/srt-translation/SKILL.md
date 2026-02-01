---
name: srt-translation
description: This skill should be used when users need to translate SRT subtitle files into multiple target languages while maintaining timing, format, and translating only text content. It supports professional domain-specific translation with custom terminology and style requirements.
---

# Srt Translation

## Overview

Translate subtitle files (SRT format) into multiple languages while preserving timing information and subtitle structure. Uses domain-specific translation models for professional terminology.

## When to Use This Skill

Use this skill when:
- Translating subtitle files without requiring video processing
- Batch processing multiple SRT files
- Maintaining subtitle timing and format during translation
- Supporting custom terminology and translation styles
- Preparing subtitles for multiple language versions

## Core Workflow

The srt-translation skill handles the following workflow:

1. **Preparation** - Set up project folder and configure parameters
2. **Processing** - Execute the task using NarratorAI API
3. **Monitoring** - Track progress through workflow steps
4. **Delivery** - Retrieve results and processed files

## API Integration

This skill integrates with NarratorAI's backend API at `https://openapi.jieshuo.cn/api/narrator/ai/v1/`

### Required Parameters

- `task_type`: "srt-translation" - Type of processing task
- `original_language`: Source language (Chinese/English)
- `target_languages`: Array of target languages with optional regional variants
- `resources`: File references (project folder ID and file IDs)

### Optional Parameters

- `auto_run`: Automation mode (0=manual steps, 1=full automation)
- `style_prompt`: Custom translation/processing style requirements
- `subtitle_style`: Subtitle formatting options (font, color, position, etc.)
- `video_erase_mode`: For erasure tasks - "normal" or "advanced"

## Task Status Tracking

All tasks return status information:

```json
{
  "id": 123,
  "task_type": "srt-translation",
  "status": 2,
  "created_at": "2026-01-16T10:00:00+08:00",
  "started_at": "2026-01-16T10:05:00+08:00",
  "completed_at": null,
  "task_flows": [
    {
      "flow_type": "step_name",
      "status": 2,
      "started_at": "2026-01-16T10:05:00+08:00",
      "finished_at": null,
      "error_message": null
    }
  ]
}
```

Status codes:
- 0: Pending
- 1: Paused (awaiting user confirmation)
- 2: In Progress
- 3: Success
- 4: Error
- 5: Failed

## Workflow Steps (task_flows)

Each task executes through multiple internal workflow steps that can be monitored independently.

## Resources

### scripts/
Python utility scripts for API integration and batch processing:
- `narrator_api_client.py` - Client wrapper for NarratorAI API
- `task_monitor.py` - Monitor and track task progress
- `batch_processor.py` - Process multiple files with shared configuration

### references/
Detailed documentation:
- `api_reference.md` - Complete API endpoint specifications
- `parameter_guide.md` - Detailed parameter documentation
- `troubleshooting.md` - Common issues and solutions
- `examples.md` - Real-world usage examples

### assets/
Template and configuration files:
- `config_templates/` - Pre-configured parameter templates
- `style_presets/` - Subtitle style and translation style presets
