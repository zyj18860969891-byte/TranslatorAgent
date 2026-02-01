#!/usr/bin/env python3
"""
NarratorAI API Client for video-translation skill
"""

import requests
import os
from typing import Dict, List, Optional

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

if __name__ == "__main__":
    # Example usage
    api_key = os.getenv("NARRATOR_API_KEY")
    if not api_key:
        print("Error: NARRATOR_API_KEY environment variable not set")
        exit(1)
    
    client = NarratorAIClient(api_key)
    
    # Create project
    project = client.create_project("My video-translation Project")
    print(f"Created project: {project}")
