---
name: video-merging
description: This skill should be used when users need to embed translated subtitles into videos using professional video rendering. It supports customizable subtitle styling (font, size, color, position) and maintains video quality during the merge process.
---

# Video Merging

## Overview

Embed SRT subtitle files into videos with professional rendering. Supports extensive subtitle customization including font, size, color, positioning, and alignment.

## When to Use This Skill

Use this skill when:
- Adding translated subtitles to videos
- Customizing subtitle appearance and positioning
- Batch processing multiple videos with subtitles
- Supporting various subtitle styles and themes
- Maintaining video quality during subtitle embedding

## Core Workflow

The video-merging skill handles the following workflow:

1. **Preparation** - Set up project folder and configure parameters
2. **Processing** - Execute the task using NarratorAI API
3. **Monitoring** - Track progress through workflow steps
4. **Delivery** - Retrieve results and processed files

## API Integration

This skill integrates with NarratorAI's backend API at `https://openapi.jieshuo.cn/api/narrator/ai/v1/`

### Required Parameters

- `task_type`: "video-merging" - Type of processing task
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
  "task_type": "video-merging",
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
