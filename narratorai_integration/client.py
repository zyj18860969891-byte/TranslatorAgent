"""
NarratorAI API Client for integrating with skills
"""

import requests
import os
from typing import Dict, List, Optional
from pathlib import Path

class NarratorAIClient:
    def __init__(self, api_key: str, base_url: str = "https://openapi.jieshuo.cn"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "APP-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    def create_project(self, name: str) -> Dict:
        """Create a new project folder"""
        url = f"{self.base_url}/api/narrator/ai/v1/fileSets"
        data = {"name": name}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def upload_file(self, project_id: int, file_path: str) -> Dict:
        """Upload a file to a project"""
        url = f"{self.base_url}/api/narrator/ai/v1/files/upload"
        with open(file_path, 'rb') as f:
            files = {'files[]': f}
            data = {'file_set_id': project_id}
            headers = {"APP-KEY": self.api_key}
            response = requests.post(url, files=files, data=data, headers=headers)
        return response.json()
    
    def create_task(self, task_data: Dict) -> Dict:
        """Create a video-translation task"""
        url = f"{self.base_url}/api/narrator/ai/v1/videoTasks"
        response = requests.post(url, json=task_data, headers=self.headers)
        return response.json()
    
    def get_task_status(self, task_id: int) -> Dict:
        """Get task status"""
        url = f"{self.base_url}/api/narrator/ai/v1/videoTasks/{task_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def confirm_task_flow(self, task_id: int, flow_id: int) -> Dict:
        """Confirm a task flow step"""
        url = f"{self.base_url}/api/narrator/ai/v1/confirm/task/flow/{task_id}"
        data = {"flow_id": flow_id}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_skill_info(self, skill_name: str) -> Dict:
        """Get information about a specific skill"""
        # This would typically call an API endpoint to get skill details
        # For now, we'll return a mock response based on our skill structure
        skill_path = Path(f"D:/MultiMode/TranslatorAgent/NarratorAI-Skills/{skill_name}")
        
        if not skill_path.exists():
            return {"error": f"Skill {skill_name} not found"}
        
        return {
            "name": skill_name,
            "path": str(skill_path),
            "scripts": [f.name for f in skill_path.joinpath("scripts").iterdir() if f.is_file()],
            "references": [f.name for f in skill_path.joinpath("references").iterdir() if f.is_file()],
            "assets": [f.name for f in skill_path.joinpath("assets").iterdir() if f.is_file()]
        }