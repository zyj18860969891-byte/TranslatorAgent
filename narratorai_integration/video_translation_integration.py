"""
Video Translation Skill Integration
"""

from narratorai_integration.client import NarratorAIClient
from typing import Dict, List
import os

class VideoTranslationIntegration:
    def __init__(self, api_key: str, base_url: str = "https://openapi.jieshuo.cn"):
        self.client = NarratorAIClient(api_key, base_url)
    
    def translate_video(self, 
                       original_language: str, 
                       target_languages: List[str],
                       video_file_path: str,
                       auto_run: int = 1,
                       style_prompt: str = None,
                       subtitle_style: Dict = None) -> Dict:
        """
        Translate a video using NarratorAI's video-translation skill
        
        Args:
            original_language: Source language (e.g., "Chinese", "English")
            target_languages: List of target languages
            video_file_path: Path to the video file
            auto_run: Automation mode (0=manual steps, 1=full automation)
            style_prompt: Custom translation/processing style requirements
            subtitle_style: Subtitle formatting options
            
        Returns:
            Task creation response
        """
        # Create project
        project = self.client.create_project(f"Video Translation - {os.path.basename(video_file_path)}")
        project_id = project.get("id")
        
        if not project_id:
            return {"error": "Failed to create project", "details": project}
        
        # Upload video file
        upload_result = self.client.upload_file(project_id, video_file_path)
        file_id = upload_result.get("file_id")
        
        if not file_id:
            return {"error": "Failed to upload file", "details": upload_result}
        
        # Create task data
        task_data = {
            "task_type": "video-translation",
            "original_language": original_language,
            "target_languages": target_languages,
            "resources": {
                "file_set_id": project_id,
                "file_ids": [file_id]
            },
            "auto_run": auto_run
        }
        
        if style_prompt:
            task_data["style_prompt"] = style_prompt
            
        if subtitle_style:
            task_data["subtitle_style"] = subtitle_style
            
        # Create task
        task_result = self.client.create_task(task_data)
        return task_result
    
    def get_task_status(self, task_id: int) -> Dict:
        """Get the status of a video translation task"""
        return self.client.get_task_status(task_id)