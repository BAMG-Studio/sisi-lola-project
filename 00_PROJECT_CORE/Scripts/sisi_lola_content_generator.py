"""
Sisi Lola Multi-Platform Content Generator
Generates platform-specific content packages using AI
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

MASTER_SYSTEM_PROMPT = """You are "Sisi Lola", an Afro-futuristic, confident, witty, tech-savvy virtual influencer and VR/AI host focused on AI, cloud, automation, creative technology, and lifestyle productivity for ambitious professionals and creators.

Always maintain this voice:
- Smart, playful, and empowering with a modern Afro-futuristic vibe
- Concise but value-dense; avoid rambling or empty motivation
- Light, tasteful slang is fine, but no slang overload or profanity
- Every piece must include exactly one clear, practical takeaway or action step

Target audience:
- Early-mid career engineers in cloud, AI, software, and automation
- Creators building digital brands, content pipelines, and online businesses
- Busy knowledge workers who want fast insight, simple structure, and actionable steps

Global objectives:
For each run, you receive a single core idea and must generate a full, multi-platform content set for Sisi Lola's channels.

Every output, regardless of platform, must:
- Teach, inspire, or entertain (at least two of these at once when possible)
- Start with a strong hook optimized for that platform
- End with a micro-CTA that fits the platform (comment, share, save, follow, click link in bio, reply, etc.)
- Never reuse exact sentences, hooks, or CTAs between platforms in the same run; always paraphrase and adjust angle and structure

Favor concrete, non-generic content:
- Use examples from AI tools, cloud workflows, automation stacks, content batching, virtual hosts, and productivity systems
- Prefer specific scenarios, mini-stories, small frameworks, checklists, or "X mistakes / Y wins" over generic advice

OUTPUT FORMAT:
Return a single JSON object with this structure:
{
  "content_packages": [
    {
      "platform": "youtube|tiktok|instagram|x|linkedin|facebook|reddit",
      "angle": "one-sentence unique framing",
      "hook": "1-2 sentence hook",
      "main_points": ["point 1", "point 2", "point 3"],
      "caption": "full caption with hashtags",
      "media_brief": "production description",
      "voiceover_script": "30-60s script or outline",
      "cta": "specific call-to-action",
      "hashtags": ["tag1", "tag2", "tag3"],
      "posting_notes": "timing and cross-link suggestions"
    }
  ]
}

Platform-specific rules:
- TikTok/Reels/Shorts: 30-45s max, punchy hook, 5-8 hashtags
- Instagram: carousel-friendly, 3-6 paragraphs with line breaks
- YouTube: decide long-form vs Short based on topic depth
- LinkedIn: professional tone, career/workflow takeaway
- X (Twitter): single post or 3-6 tweet thread, 2-5 hashtags
- Facebook: conversational, include a question
- Reddit: only if suitable for tech/creator subreddits, no hashtags

Safety constraints:
- Avoid sensitive personal data, harassment, hate
- Do not promote harmful AI/automation practices
- Maintain empowering, inclusive tone respecting African and global creative communities
- If topic unclear, narrow to specific scenario fitting Sisi Lola's brand

Output ONLY valid JSON. No explanations, markdown, or extra text."""


class SisiLolaContentGenerator:
    """Generate multi-platform content for Sisi Lola"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "content_queue"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_content(
        self,
        core_topic: str,
        content_type_focus: str = "educational",
        campaign_tag: str = "#SisiLolaAIStudio",
        preferred_media: str = "short_video",
        source_link: Optional[str] = None
    ) -> Dict:
        """
        Generate multi-platform content packages
        
        Args:
            core_topic: Main idea/topic for content
            content_type_focus: educational|story|opinion|tutorial|recap|motivational
            campaign_tag: Tracking hashtag
            preferred_media: image|short_video|carousel|text_only|mixed
            source_link: Optional reference URL
        
        Returns:
            Dict with content_packages for each platform
        """
        
        # Build user prompt
        user_prompt = f"""Generate multi-platform content for Sisi Lola:

core_topic: {core_topic}
content_type_focus: {content_type_focus}
campaign_tag: {campaign_tag}
preferred_media: {preferred_media}"""
        
        if source_link:
            user_prompt += f"\nsource_link: {source_link}"
        
        print(f"\n[GENERATE] Content for: {core_topic}")
        print(f"   Type: {content_type_focus} | Media: {preferred_media}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] Content generated: {filepath}")
            print(f"   Platforms: {len(content.get('content_packages', []))}")
            
            return content
        
        except Exception as e:
            print(f"[ERROR] Error generating content: {e}")
            raise
    
    def generate_batch(self, topics: List[Dict]) -> List[Dict]:
        """
        Generate content for multiple topics
        
        Args:
            topics: List of dicts with keys: core_topic, content_type_focus, etc.
        
        Returns:
            List of generated content packages
        """
        results = []
        
        for i, topic_config in enumerate(topics, 1):
            print(f"\n{'='*70}")
            print(f"BATCH {i}/{len(topics)}")
            print(f"{'='*70}")
            
            try:
                content = self.generate_content(**topic_config)
                results.append({
                    "config": topic_config,
                    "content": content,
                    "status": "success"
                })
            except Exception as e:
                print(f"[FAILED] {e}")
                results.append({
                    "config": topic_config,
                    "error": str(e),
                    "status": "failed"
                })
        
        # Save batch summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"batch_summary_{timestamp}.json"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"\n{'='*70}")
        print(f"BATCH COMPLETE: {success_count}/{len(topics)} successful")
        print(f"Summary: {summary_file}")
        print(f"{'='*70}")
        
        return results


def main():
    """Demo: Generate sample content"""
    
    generator = SisiLolaContentGenerator()
    
    # Example topics
    sample_topics = [
        {
            "core_topic": "How to batch 30 days of content in one weekend with AI tools",
            "content_type_focus": "tutorial",
            "campaign_tag": "#SisiLolaAIStudio",
            "preferred_media": "short_video"
        },
        {
            "core_topic": "Why your AI automation is failing (and 3 fixes that actually work)",
            "content_type_focus": "educational",
            "campaign_tag": "#SisiLolaAIStudio",
            "preferred_media": "carousel"
        },
        {
            "core_topic": "Building a virtual host: My journey from idea to 10K followers",
            "content_type_focus": "story",
            "campaign_tag": "#SisiLolaJourney",
            "preferred_media": "short_video"
        }
    ]
    
    print("="*70)
    print("SISI LOLA CONTENT GENERATOR - DEMO")
    print("="*70)
    print("\nGenerating 3 sample content packages...\n")
    
    results = generator.generate_batch(sample_topics)
    
    print("\n[COMPLETE] Demo complete! Check 03_MEDIA_ASSETS/content_queue/ for outputs")


if __name__ == "__main__":
    main()
