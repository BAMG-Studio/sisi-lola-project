"""
AI-Enhanced Multi-Platform Poster
Leverages all AI services to optimize content for each platform
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from multi_platform_poster import MultiPlatformPoster

load_dotenv(Path(__file__).parent.parent / ".env")

class AIEnhancedPoster:
    def __init__(self):
        self.poster = MultiPlatformPoster()
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def optimize_for_platform(self, content, platform):
        """Use AI to further optimize content for specific platform"""
        
        optimization_prompts = {
            'youtube': "Optimize for YouTube: engaging title, SEO keywords, detailed description",
            'tiktok': "Optimize for TikTok: viral hooks, trending sounds, hashtag strategy",
            'instagram': "Optimize for Instagram: visual storytelling, carousel flow, engagement",
            'twitter': "Optimize for Twitter: concise, thread-worthy, conversation starter",
            'linkedin': "Optimize for LinkedIn: professional, thought leadership, career value",
            'facebook': "Optimize for Facebook: community building, shareable, discussion"
        }
        
        prompt = f"{optimization_prompts.get(platform, 'Optimize this content')}\n\nOriginal: {content['caption'][:200]}"
        
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are Sisi Lola's content optimizer. Enhance content while maintaining her Afro-futuristic, tech-savvy voice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            enhanced = response.choices[0].message.content
            print(f"[AI-OPTIMIZED] {platform.upper()}")
            return enhanced
        except:
            return content['caption']
    
    def post_to_all_platforms(self):
        """Generate fresh content and post to all available platforms"""
        
        # Find latest content
        content_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
        content_files = sorted(content_dir.glob("content_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not content_files:
            print("[ERROR] No content found. Run sisi_lola_content_generator.py first")
            return
        
        with open(content_files[0], 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        packages = content.get('content_packages', [])
        
        # Get video
        video_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "generated"
        videos = list(video_dir.glob("*.mp4"))
        latest_video = max(videos, key=lambda p: p.stat().st_mtime) if videos else None
        
        media_assets = {
            'youtube': str(latest_video) if latest_video else None,
            'tiktok': str(latest_video) if latest_video else None,
            'instagram': str(latest_video) if latest_video else None
        }
        
        print("\n" + "="*70)
        print("AI-ENHANCED MULTI-PLATFORM POSTING")
        print("="*70)
        print(f"Content: {content_files[0].name}")
        print(f"Video: {latest_video.name if latest_video else 'None'}")
        print(f"Platforms: {len(packages)}")
        print(f"AI Services: OpenAI, HeyGen, Kling, ElevenLabs, Cohere, NATLAS")
        print("="*70)
        
        results = []
        
        for pkg in packages:
            platform = pkg['platform']
            
            # AI-optimize content
            optimized_caption = self.optimize_for_platform(pkg, platform)
            pkg['caption'] = optimized_caption
            
            # Post
            print(f"\n[POSTING] {platform.upper()}...")
            result = self.poster.post_content_package(pkg, media_assets)
            results.append(result)
            
            if result['status'] == 'success':
                print(f"   [SUCCESS] {result.get('url', 'Posted')}")
            else:
                print(f"   [STATUS] {result.get('message', 'Pending')[:100]}")
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        print("\n" + "="*70)
        print(f"RESULTS: {success_count}/{len(results)} successful")
        print("="*70)
        
        for r in results:
            status_icon = "[OK]" if r['status'] == 'success' else "[--]"
            print(f"{status_icon} {r['platform'].upper():15} {r['status']}")
            if r['status'] == 'success' and 'url' in r:
                print(f"     {r['url']}")
        
        return results

if __name__ == "__main__":
    print("="*70)
    print("SISI LOLA - AI-ENHANCED MULTI-PLATFORM POSTER")
    print("="*70)
    
    poster = AIEnhancedPoster()
    results = poster.post_to_all_platforms()
    
    print("\n[COMPLETE] Multi-platform posting complete!")
