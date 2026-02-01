# Video Extraction API Reference

## Endpoint

```
POST /api/narrator/ai/v1/videoTasks
```

## Request Parameters

### Required
- `task_type`: "video-extraction"
- `original_language`: String (Chinese/English)
- `target_languages`: Array of language objects with `language` and optional `area`
- `resources`: Object with `file_set_id` and `file_ids`

### Optional
- `auto_run`: Number (0 or 1)
- `style_prompt`: String
- `subtitle_style`: Object with style properties
- `video_erase_mode`: String ("normal" or "advanced") - for erasure tasks only

## Response

```json
{
  "code": 10000,
  "message": "success",
  "data": {
    "id": 123,
    "task_type": "video-extraction",
    "status": 2,
    "created_at": "2026-01-16T10:00:00+08:00",
    "task_flows": []
  }
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 10000 | Success |
| 10001 | System error |
| 10002 | Invalid API key |
| 10003 | Access denied |
| 10004 | API key expired |
| 10005 | Invalid parameters |
| 10006 | Service unavailable |
| 10009 | Insufficient points |

## Rate Limiting

- Rate limit: 100 requests per minute
- Concurrent tasks: Up to 5 simultaneous tasks
