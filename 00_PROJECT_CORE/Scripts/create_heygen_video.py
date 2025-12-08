"""
Create 10-minute Sisi Lola HeyGen Avatar Video
"""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class HeyGenVideoCreator:
    def __init__(self):
        self.api_key = HEYGEN_API_KEY
        self.avatar_id = HEYGEN_AVATAR_ID
        self.openai = OpenAI(api_key=OPENAI_API_KEY)
        self.base_url = "https://api.heygen.com/v2"
        
    def generate_10min_script(self, topic, language="english"):
        """Generate script using AI (max 4800 chars for HeyGen)"""
        
        lang_instruction = "in Yoruba language" if language == "yoruba" else "in English"
        
        prompt = f"""Create a 6-7 minute video script for Sisi Lola, an Afro-futuristic virtual host {lang_instruction}.

Topic: {topic}

Requirements:
- 6-7 minutes (approximately 900-1000 words, MAX 4800 characters)
- Engaging, conversational tone
- Afro-futuristic, tech-savvy personality
- Educational and entertaining
- Include 3 main sections
- Strong opening hook and closing CTA
- Keep it concise and impactful
- Use natural, conversational {language}

Format as a single speaking script. CRITICAL: Keep under 4800 characters total."""

        response = self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a scriptwriter for Sisi Lola, an Afro-futuristic AI virtual host."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    def create_video(self, script, title):
        """Create video using HeyGen API"""
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # HeyGen v2 API payload
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": self.avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": "en-US-JennyNeural"  # Female voice
                },
                "background": {
                    "type": "color",
                    "value": "#1a1a2e"  # Dark Afro-futuristic background
                }
            }],
            "dimension": {
                "width": 1920,
                "height": 1080
            },
            "aspect_ratio": "16:9",
            "test": False,
            "title": title
        }
        
        print(f"[HEYGEN] Creating video: {title}")
        print(f"[HEYGEN] Script length: {len(script)} characters")
        
        # Create video
        response = requests.post(
            f"{self.base_url}/video/generate",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"[ERROR] HeyGen API error: {response.text}")
            return None
        
        result = response.json()
        video_id = result.get("data", {}).get("video_id")
        
        if not video_id:
            print(f"[ERROR] No video_id returned")
            return None
        
        print(f"[HEYGEN] Video ID: {video_id}")
        print(f"[HEYGEN] Status: Processing...")
        
        # Poll for completion
        return self.wait_for_video(video_id)
    
    def wait_for_video(self, video_id):
        """Wait for video to be ready"""
        
        headers = {"X-Api-Key": self.api_key}
        max_wait = 600  # 10 minutes
        elapsed = 0
        
        while elapsed < max_wait:
            response = requests.get(
                f"{self.base_url}/video/{video_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                status = data.get("status")
                
                print(f"[HEYGEN] Status: {status} ({elapsed}s elapsed)")
                
                if status == "completed":
                    video_url = data.get("video_url")
                    print(f"[SUCCESS] Video ready: {video_url}")
                    return video_url
                elif status == "failed":
                    print(f"[ERROR] Video generation failed")
                    return None
            
            time.sleep(10)
            elapsed += 10
        
        print(f"[TIMEOUT] Video not ready after {max_wait}s")
        return None
    
    def download_video(self, video_url, filename):
        """Download video from HeyGen"""
        
        output_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        print(f"[DOWNLOAD] Downloading video...")
        
        response = requests.get(video_url, stream=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[SAVED] {output_path}")
        return str(output_path)

def main():
    print("="*70)
    print("SISI LOLA - 10-MINUTE HEYGEN VIDEO CREATOR")
    print("="*70)
    
    creator = HeyGenVideoCreator()
    
    # Topic options
    topics = [
        "AI and the Future of African Tech Innovation",
        "Building Your Personal Brand as a Creator in 2025",
        "The Rise of Virtual Influencers: My Journey as Sisi Lola",
        "Cloud Computing for Beginners: A Complete Guide",
        "Automation Secrets: How I Create 30 Days of Content in One Weekend"
    ]
    
    print("\nSelect a topic:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    choice = input("\nEnter choice (1-5) or custom topic: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= 5:
        topic = topics[int(choice) - 1]
    else:
        topic = choice if choice else topics[0]
    
    print(f"\n[TOPIC] {topic}")
    
    # Language selection
    lang_choice = input("\nLanguage? (1=English, 2=Yoruba): ").strip()
    language = "yoruba" if lang_choice == "2" else "english"
    
    print(f"[LANGUAGE] {language.upper()}")
    
    # Generate script
    print("\n[AI] Generating script...")
    script = creator.generate_10min_script(topic, language)
    
    print(f"[SCRIPT] Generated {len(script)} characters")
    print(f"[PREVIEW] {script[:200]}...")
    
    # Save script
    script_dir = Path(__file__).parent.parent.parent / "06_RENDER_OUTPUT" / "youtube_videos"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_file = script_dir / f"script_10min_{int(time.time())}.txt"
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(f"TOPIC: {topic}\n\n")
        f.write(script)
    
    print(f"[SAVED] Script: {script_file}")
    
    # Create video
    title = f"Sisi Lola: {topic[:50]}"
    video_url = creator.create_video(script, title)
    
    if video_url:
        # Download
        filename = f"heygen_10min_{int(time.time())}.mp4"
        video_path = creator.download_video(video_url, filename)
        
        print("\n" + "="*70)
        print("VIDEO READY!")
        print("="*70)
        print(f"Path: {video_path}")
        print(f"Script: {script_file}")
        print("\nNext: Post to YouTube with post_to_youtube_now.py")
        
        return video_path
    else:
        print("\n[ERROR] Video creation failed")
        return None

if __name__ == "__main__":
    main()
