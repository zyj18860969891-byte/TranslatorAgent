"""
SRT Translation Skill Integration
"""

from narratorai_integration.client import NarratorAIClient
from typing import Dict, List
import os

class SRTTranslationIntegration:
    def __init__(self, api_key: str, base_url: str = "https://openapi.jieshuo.cn"):
        self.client = NarratorAIClient(api_key, base_url)
    
    def translate_srt(self, 
                     original_language: str, 
                     target_languages: List[str],
                     srt_file_path: str,
                     auto_run: int = 1,
                     style_prompt: str = None,
                     subtitle_style: Dict = None) -> Dict:
        """
        Translate an SRT subtitle file using NarratorAI's srt-translation skill
        
        Args:
            original_language: Source language (e.g., "Chinese", "English")
            target_languages: List of target languages
            srt_file_path: Path to the SRT file
            auto_run: Automation mode (0=manual steps, 1=full automation)
            style_prompt: Custom translation/processing style requirements
            subtitle_style: Subtitle formatting options
            
        Returns:
            Task creation response
        """
        # Create project
        project = self.client.create_project(f"SRT Translation - {os.path.basename(srt_file_path)}")
        project_id = project.get("id")
        
        if not project_id:
            return {"error": "Failed to create project", "details": project}
        
        # Upload SRT file
        upload_result = self.client.upload_file(project_id, srt_file_path)
        file_id = upload_result.get("file_id")
        
        if not file_id:
            return {"error": "Failed to upload file", "details": upload_result}
        
        # Create task data
        task_data = {
            "task_type": "srt-translation",
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
        """Get the status of an SRT translation task"""
        return self.client.get_task_status(task_id)