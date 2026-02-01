"""
Test script for NarratorAI Skills Integration
"""

import os
from narratorai_integration.client import NarratorAIClient
from narratorai_integration.video_translation_integration import VideoTranslationIntegration
from narratorai_integration.srt_translation_integration import SRTTranslationIntegration

def test_client():
    """Test the NarratorAI client functionality"""
    print("Testing NarratorAI Client...")
    
    # Get API key from environment variable
    api_key = os.getenv("NARRATOR_API_KEY")
    if not api_key:
        print("Warning: NARRATOR_API_KEY environment variable not set")
        print("Using mock test data instead")
        api_key = "mock-api-key"
    
    client = NarratorAIClient(api_key)
    
    # Test skill info retrieval
    skills = ["video-translation", "srt-translation", "video-erasure", "video-extraction", "video-merging"]
    
    for skill in skills:
        try:
            info = client.get_skill_info(skill)
            print(f"✓ Skill {skill} info retrieved successfully")
            print(f"  Scripts: {info.get('scripts', [])}")
            print(f"  References: {info.get('references', [])}")
            print(f"  Assets: {info.get('assets', [])}")
        except Exception as e:
            print(f"✗ Error retrieving info for skill {skill}: {e}")
    
    print("Client test completed.\n")

def test_video_translation_integration():
    """Test video translation integration"""
    print("Testing Video Translation Integration...")
    
    # Get API key from environment variable
    api_key = os.getenv("NARRATOR_API_KEY")
    if not api_key:
        print("Warning: NARRATOR_API_KEY environment variable not set")
        print("Using mock test data instead")
        api_key = "mock-api-key"
    
    integration = VideoTranslationIntegration(api_key)
    
    # Test skill info retrieval
    try:
        info = integration.client.get_skill_info("video-translation")
        print("✓ Video translation skill info retrieved successfully")
        print(f"  Scripts: {info.get('scripts', [])}")
    except Exception as e:
        print(f"✗ Error retrieving video translation skill info: {e}")
    
    print("Video translation integration test completed.\n")

def test_srt_translation_integration():
    """Test SRT translation integration"""
    print("Testing SRT Translation Integration...")
    
    # Get API key from environment variable
    api_key = os.getenv("NARRATOR_API_KEY")
    if not api_key:
        print("Warning: NARRATOR_API_KEY environment variable not set")
        print("Using mock test data instead")
        api_key = "mock-api-key"
    
    integration = SRTTranslationIntegration(api_key)
    
    # Test skill info retrieval
    try:
        info = integration.client.get_skill_info("srt-translation")
        print("✓ SRT translation skill info retrieved successfully")
        print(f"  Scripts: {info.get('scripts', [])}")
    except Exception as e:
        print(f"✗ Error retrieving SRT translation skill info: {e}")
    
    print("SRT translation integration test completed.\n")

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("NarratorAI Skills Integration Tests")
    print("=" * 60)
    
    test_client()
    test_video_translation_integration()
    test_srt_translation_integration()
    
    print("=" * 60)
    print("Integration tests completed.")

if __name__ == "__main__":
    main()