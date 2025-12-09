"""
SISI LOLA CONTENT GENERATION ENGINE
====================================
Generates content of various durations and formats:

SHORT FORM (< 3 minutes):
- Reels (15-60 sec)
- Snippets/Clips
- Ads/Promos
- Captions

LONG FORM (> 3 minutes):
- Full Episodes (15-45 min)
- Podcast Sessions (30-90 min)
- Live Shows (60-120 min)
- Documentary/Educational

The engine creates structured content plans that can be
rendered through video generation APIs (HeyGen, etc.)
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Literal
from enum import Enum


class ContentFormat(Enum):
    """Output format types"""
    SCRIPT = "script"           # Text script only
    STORYBOARD = "storyboard"   # Script + visual descriptions
    FULL_PRODUCTION = "full"    # Ready for video generation
    AUDIO_ONLY = "audio"        # Podcast/audio content


@dataclass
class ScriptSegment:
    """A segment of a script (scene, section, etc.)"""
    segment_id: str
    segment_type: str  # intro, main, transition, outro, ad_break, etc.
    duration_seconds: float
    
    # Content
    dialogue: str  # What Sisi Lola says
    tone: str  # energetic, thoughtful, humorous, etc.
    
    # Visual/Audio cues
    visual_description: Optional[str] = None
    camera_direction: Optional[str] = None  # close-up, wide, etc.
    background_music: Optional[str] = None
    sound_effects: List[str] = field(default_factory=list)
    
    # B-roll/cutaway suggestions
    broll_suggestions: List[str] = field(default_factory=list)
    
    # On-screen elements
    text_overlays: List[str] = field(default_factory=list)
    graphics: List[str] = field(default_factory=list)


@dataclass
class ContentPlan:
    """Complete content production plan"""
    # Identification
    plan_id: str
    title: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Classification
    content_type: str  # reel, episode, podcast, etc.
    duration_category: str  # micro, short, medium, long, extended
    target_duration_seconds: int = 60
    
    # Target platform
    platform: Optional[str] = None
    aspect_ratio: str = "9:16"  # Default vertical
    
    # Content
    hook: str = ""  # First 3 seconds - grab attention
    premise: str = ""  # What this content is about
    segments: List[ScriptSegment] = field(default_factory=list)
    call_to_action: str = ""
    
    # Metadata
    hashtags: List[str] = field(default_factory=list)
    description: str = ""
    thumbnail_prompt: str = ""
    
    # Source material (if derived from input content)
    source_content_id: Optional[str] = None
    
    def total_duration(self) -> float:
        """Calculate total duration from segments"""
        return sum(s.duration_seconds for s in self.segments)
    
    def to_script_text(self) -> str:
        """Export as plain text script"""
        lines = [
            f"# {self.title}",
            f"Duration: {self.total_duration():.0f} seconds",
            f"Platform: {self.platform or 'General'}",
            "",
            f"## HOOK ({self.hook[:50]}...)" if len(self.hook) > 50 else f"## HOOK",
            self.hook,
            "",
            "## SEGMENTS",
        ]
        
        for i, seg in enumerate(self.segments, 1):
            lines.append(f"\n### {i}. {seg.segment_type.upper()} ({seg.duration_seconds:.0f}s)")
            lines.append(f"*{seg.tone}*")
            lines.append(seg.dialogue)
            if seg.visual_description:
                lines.append(f"\n[VISUAL: {seg.visual_description}]")
            if seg.text_overlays:
                lines.append(f"[TEXT: {', '.join(seg.text_overlays)}]")
        
        lines.extend([
            "",
            "## CALL TO ACTION",
            self.call_to_action,
            "",
            f"## HASHTAGS",
            " ".join(f"#{tag}" for tag in self.hashtags),
        ])
        
        return "\n".join(lines)
    
    def to_heygen_script(self) -> str:
        """Export as HeyGen-compatible script (just the dialogue)"""
        parts = [self.hook]
        for seg in self.segments:
            parts.append(seg.dialogue)
        parts.append(self.call_to_action)
        return "\n\n".join(parts)
    
    def to_dict(self) -> Dict:
        """Export as dictionary"""
        data = asdict(self)
        # Convert segments properly
        data['segments'] = [asdict(s) for s in self.segments]
        return data


class ContentGenerator:
    """
    Main content generation engine.
    
    Usage:
        generator = ContentGenerator()
        
        # Generate a reel about Lagos tech
        plan = generator.generate_reel(
            topic="Lagos tech startups",
            duration_seconds=60,
            platform="instagram"
        )
        
        # Generate a full podcast episode
        plan = generator.generate_podcast(
            topic="The rise of Afrobeats globally",
            duration_minutes=45
        )
    """
    
    # Sisi Lola's voice patterns
    OPENINGS = {
        'casual': [
            "Omo! Make I gist you something...",
            "Ehh! You need to hear this o!",
            "Bros, Sis, gather round!",
            "Wetin dey happen? Let me tell you...",
        ],
        'professional': [
            "Good day everyone, it's your girl Sisi Lola...",
            "Welcome back to another discussion...",
            "Today we're exploring something fascinating...",
        ],
        'dramatic': [
            "The tea is HOT today!",
            "You won't believe what I found out...",
            "This one go shock you o!",
        ],
        'educational': [
            "Let me break this down for you...",
            "Here's what you need to know...",
            "Fun fact that will blow your mind...",
        ],
    }
    
    TRANSITIONS = [
        "Now, make we look at...",
        "But wait, there's more o!",
        "The koko is this...",
        "And here's the interesting part...",
        "Moving on to the next gist...",
    ]
    
    CLOSINGS = {
        'casual': [
            "That's the gist for today! Drop your comment, make we yarn!",
            "Na so e be! Like and follow for more gist!",
            "Until next time, stay blessed!",
        ],
        'call_to_action': [
            "Follow for more Nigerian excellence! 🇳🇬",
            "Subscribe so you no go miss the next episode!",
            "Share this with someone who needs to hear it!",
        ],
        'podcast': [
            "Thank you for tuning in to another episode! Remember to subscribe and leave a review!",
            "We'll continue this conversation next week. Stay connected!",
        ],
    }
    
    def __init__(self, output_dir: Optional[Path] = None, llm_client=None):
        """
        Initialize the generator.
        
        Args:
            output_dir: Directory to save generated content plans
            llm_client: Optional LLM for enhanced content generation
        """
        self.output_dir = output_dir or Path(__file__).parent.parent / "03_MEDIA_ASSETS" / "content_plans"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm_client = llm_client
    
    def generate_reel(self, 
                      topic: str,
                      duration_seconds: int = 60,
                      platform: str = "instagram",
                      style: str = "casual",
                      source_context: Optional[str] = None) -> ContentPlan:
        """
        Generate a short-form reel (15-60 seconds).
        
        Args:
            topic: What the reel is about
            duration_seconds: Target duration (15-60)
            platform: Target platform (instagram, tiktok, etc.)
            style: Content style (casual, professional, dramatic, etc.)
            source_context: Context from processed content (for reaction/discussion reels)
        """
        plan_id = str(uuid.uuid4())[:8]
        
        # Calculate segment timings
        hook_duration = 3
        outro_duration = 5
        main_duration = duration_seconds - hook_duration - outro_duration
        
        # Create hook (first 3 seconds - CRITICAL for engagement)
        hook = self._create_hook(topic, style)
        
        # Main content segments
        segments = []
        
        if source_context:
            # This is a reaction/discussion reel
            segments.extend(self._create_reaction_segments(
                topic, source_context, main_duration, style
            ))
        else:
            # Original content reel
            segments.extend(self._create_original_segments(
                topic, main_duration, style
            ))
        
        # Create CTA
        cta = self._create_cta(platform, style)
        
        # Create outro segment
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_outro",
            segment_type="outro",
            duration_seconds=outro_duration,
            dialogue=cta,
            tone="enthusiastic",
            text_overlays=["FOLLOW FOR MORE"],
        ))
        
        # Generate hashtags
        hashtags = self._generate_hashtags(topic, platform)
        
        plan = ContentPlan(
            plan_id=plan_id,
            title=f"Reel: {topic[:50]}",
            content_type="reel",
            duration_category="short" if duration_seconds > 30 else "micro",
            target_duration_seconds=duration_seconds,
            platform=platform,
            aspect_ratio="9:16",
            hook=hook,
            premise=topic,
            segments=segments,
            call_to_action=cta,
            hashtags=hashtags,
            description=self._create_description(topic, hashtags),
            thumbnail_prompt=f"Sisi Lola, Nigerian woman, expressive face, discussing {topic}, vibrant Ankara outfit",
        )
        
        # Save plan
        self._save_plan(plan)
        
        return plan
    
    def generate_episode(self,
                         topic: str,
                         duration_minutes: int = 20,
                         platform: str = "youtube",
                         style: str = "educational") -> ContentPlan:
        """
        Generate a medium-form episode (5-45 minutes).
        
        Args:
            topic: Episode topic
            duration_minutes: Target duration in minutes
            platform: Target platform
            style: Content style
        """
        plan_id = str(uuid.uuid4())[:8]
        duration_seconds = duration_minutes * 60
        
        # Episode structure
        intro_duration = 30
        outro_duration = 60
        main_duration = duration_seconds - intro_duration - outro_duration
        
        # Number of main segments based on duration
        num_segments = max(3, duration_minutes // 5)
        segment_duration = main_duration / num_segments
        
        hook = self._create_hook(topic, style)
        
        segments = []
        
        # Intro segment
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_intro",
            segment_type="intro",
            duration_seconds=intro_duration,
            dialogue=f"{hook}\n\nToday we're diving deep into {topic}. I promise, by the end of this episode, you'll understand everything you need to know!",
            tone="welcoming",
            visual_description="Sisi Lola in studio setting, warm lighting",
            text_overlays=[topic.upper()],
        ))
        
        # Main segments with topics
        main_topics = self._generate_subtopics(topic, num_segments)
        
        for i, subtopic in enumerate(main_topics):
            segments.append(ScriptSegment(
                segment_id=f"{plan_id}_main_{i+1}",
                segment_type="main_point",
                duration_seconds=segment_duration,
                dialogue=f"[Content about: {subtopic}]\n\nMake I break this down proper proper...",
                tone="informative" if i % 2 == 0 else "enthusiastic",
                visual_description=f"B-roll or graphics related to {subtopic}",
                text_overlays=[f"Point {i+1}: {subtopic[:30]}"],
                broll_suggestions=[f"Stock footage of {subtopic}", f"Graphics explaining {subtopic}"],
            ))
            
            # Add transition between segments (except last)
            if i < len(main_topics) - 1:
                segments.append(ScriptSegment(
                    segment_id=f"{plan_id}_trans_{i+1}",
                    segment_type="transition",
                    duration_seconds=5,
                    dialogue=self.TRANSITIONS[i % len(self.TRANSITIONS)],
                    tone="bridging",
                ))
        
        # Outro
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_outro",
            segment_type="outro",
            duration_seconds=outro_duration,
            dialogue=f"And that's the full gist about {topic}!\n\n{self.CLOSINGS['call_to_action'][0]}\n\nUntil next time, na your girl Sisi Lola. Stay blessed!",
            tone="warm",
            text_overlays=["SUBSCRIBE", "LIKE", "COMMENT"],
        ))
        
        cta = self.CLOSINGS['call_to_action'][0]
        hashtags = self._generate_hashtags(topic, platform)
        
        plan = ContentPlan(
            plan_id=plan_id,
            title=f"{topic}",
            content_type="episode",
            duration_category="medium" if duration_minutes <= 15 else "long",
            target_duration_seconds=duration_seconds,
            platform=platform,
            aspect_ratio="16:9",
            hook=hook,
            premise=topic,
            segments=segments,
            call_to_action=cta,
            hashtags=hashtags,
            description=self._create_long_description(topic, main_topics, hashtags),
            thumbnail_prompt=f"Sisi Lola, Nigerian woman, thumbnail face, bold text '{topic[:20]}...', vibrant colors",
        )
        
        self._save_plan(plan)
        return plan
    
    def generate_podcast(self,
                         topic: str,
                         duration_minutes: int = 45,
                         has_guest: bool = False,
                         guest_name: Optional[str] = None) -> ContentPlan:
        """
        Generate a podcast episode (30-120 minutes).
        
        Args:
            topic: Podcast topic
            duration_minutes: Target duration
            has_guest: Whether there's a guest
            guest_name: Guest's name if applicable
        """
        plan_id = str(uuid.uuid4())[:8]
        duration_seconds = duration_minutes * 60
        
        # Podcast structure
        intro_duration = 60  # Longer intro for podcasts
        outro_duration = 90
        main_duration = duration_seconds - intro_duration - outro_duration
        
        # More segments for longer format
        num_segments = duration_minutes // 10
        segment_duration = main_duration / num_segments
        
        hook = self._create_hook(topic, "professional")
        
        segments = []
        
        # Podcast intro with music cue
        intro_text = f"Welcome to Sisi Lola's Corner! I'm your host, and today we're having a real conversation about {topic}."
        if has_guest and guest_name:
            intro_text += f" And I'm so excited to have {guest_name} joining us today!"
        
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_intro",
            segment_type="podcast_intro",
            duration_seconds=intro_duration,
            dialogue=intro_text,
            tone="welcoming",
            background_music="podcast intro jingle",
            visual_description="Podcast studio, microphones visible" if not has_guest else f"Split screen with {guest_name}",
        ))
        
        # Main discussion segments
        discussion_points = self._generate_subtopics(topic, num_segments)
        
        for i, point in enumerate(discussion_points):
            if has_guest:
                dialogue = f"[Discussion about: {point}]\n\n{guest_name}, what's your take on this?"
            else:
                dialogue = f"[Deep dive into: {point}]\n\nLet me share my thoughts on this..."
            
            segments.append(ScriptSegment(
                segment_id=f"{plan_id}_discussion_{i+1}",
                segment_type="discussion",
                duration_seconds=segment_duration,
                dialogue=dialogue,
                tone="conversational",
            ))
        
        # Podcast outro
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_outro",
            segment_type="podcast_outro",
            duration_seconds=outro_duration,
            dialogue=self.CLOSINGS['podcast'][0],
            tone="warm",
            background_music="podcast outro jingle",
        ))
        
        plan = ContentPlan(
            plan_id=plan_id,
            title=f"Sisi Lola's Corner: {topic}",
            content_type="podcast",
            duration_category="long" if duration_minutes <= 45 else "extended",
            target_duration_seconds=duration_seconds,
            platform="spotify",
            aspect_ratio="1:1",  # Square for podcast cover
            hook=hook,
            premise=topic,
            segments=segments,
            call_to_action=self.CLOSINGS['podcast'][0],
            hashtags=self._generate_hashtags(topic, "podcast"),
            description=self._create_podcast_description(topic, discussion_points, guest_name),
        )
        
        self._save_plan(plan)
        return plan
    
    def generate_live_session(self,
                              topic: str,
                              duration_minutes: int = 60,
                              session_type: str = "discussion") -> ContentPlan:
        """
        Generate a live session plan (45-120 minutes).
        
        Args:
            topic: Session topic
            duration_minutes: Target duration
            session_type: Type of live (discussion, q&a, interview, etc.)
        """
        plan_id = str(uuid.uuid4())[:8]
        duration_seconds = duration_minutes * 60
        
        # Live structure is more flexible
        segments = []
        
        # Opening
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_open",
            segment_type="live_opening",
            duration_seconds=120,
            dialogue=f"We are LIVE! Welcome welcome! Today we're going to talk about {topic}. Drop your comments, let me see where you're watching from!",
            tone="energetic",
            text_overlays=["🔴 LIVE", "DROP YOUR LOCATION"],
        ))
        
        # Main segments (flexible for live format)
        main_points = self._generate_subtopics(topic, duration_minutes // 15)
        segment_duration = (duration_seconds - 300) / len(main_points)  # Minus intro/outro
        
        for i, point in enumerate(main_points):
            segments.append(ScriptSegment(
                segment_id=f"{plan_id}_segment_{i+1}",
                segment_type="live_segment",
                duration_seconds=segment_duration,
                dialogue=f"[Live discussion: {point}]\n\nI'm seeing your comments... Yes! Great point!",
                tone="interactive",
            ))
            
            # Q&A breaks
            if i < len(main_points) - 1:
                segments.append(ScriptSegment(
                    segment_id=f"{plan_id}_qa_{i+1}",
                    segment_type="qa_break",
                    duration_seconds=60,
                    dialogue="Let me answer some of your questions... [READ COMMENTS]",
                    tone="engaging",
                ))
        
        # Closing
        segments.append(ScriptSegment(
            segment_id=f"{plan_id}_close",
            segment_type="live_closing",
            duration_seconds=120,
            dialogue="Thank you all for joining today's live! Remember to follow, and I'll see you next time!",
            tone="grateful",
        ))
        
        plan = ContentPlan(
            plan_id=plan_id,
            title=f"LIVE: {topic}",
            content_type="live_session",
            duration_category="extended",
            target_duration_seconds=duration_seconds,
            platform="instagram",  # Default to IG live
            aspect_ratio="9:16",
            hook="🔴 LIVE NOW",
            premise=topic,
            segments=segments,
            call_to_action="Follow for the next live session!",
            hashtags=self._generate_hashtags(topic, "live"),
        )
        
        self._save_plan(plan)
        return plan
    
    # Helper methods
    
    def _create_hook(self, topic: str, style: str) -> str:
        """Create an attention-grabbing hook"""
        import random
        openings = self.OPENINGS.get(style, self.OPENINGS['casual'])
        opening = random.choice(openings)
        return f"{opening} {topic}!"
    
    def _create_reaction_segments(self, topic: str, context: str, 
                                   duration: float, style: str) -> List[ScriptSegment]:
        """Create segments for reaction/discussion content"""
        segments = []
        
        # Context summary segment
        segments.append(ScriptSegment(
            segment_id="reaction_context",
            segment_type="context",
            duration_seconds=duration * 0.3,
            dialogue=f"So I just watched/read this about {topic}... Let me tell you wetin I see...",
            tone="curious",
        ))
        
        # Reaction segment
        segments.append(ScriptSegment(
            segment_id="reaction_main",
            segment_type="reaction",
            duration_seconds=duration * 0.5,
            dialogue=f"[React to key points from: {context[:200]}]",
            tone="expressive",
        ))
        
        # Opinion/take segment
        segments.append(ScriptSegment(
            segment_id="reaction_take",
            segment_type="hot_take",
            duration_seconds=duration * 0.2,
            dialogue="Here's my take on this matter...",
            tone="thoughtful",
        ))
        
        return segments
    
    def _create_original_segments(self, topic: str, duration: float, 
                                   style: str) -> List[ScriptSegment]:
        """Create segments for original content"""
        segments = []
        
        # Main point
        segments.append(ScriptSegment(
            segment_id="main_point",
            segment_type="main",
            duration_seconds=duration * 0.6,
            dialogue=f"[Main content about {topic}]",
            tone="informative",
        ))
        
        # Supporting point
        segments.append(ScriptSegment(
            segment_id="support_point",
            segment_type="supporting",
            duration_seconds=duration * 0.4,
            dialogue="And here's why this matters...",
            tone="passionate",
        ))
        
        return segments
    
    def _create_cta(self, platform: str, style: str) -> str:
        """Create platform-appropriate call to action"""
        ctas = {
            'instagram': "Follow for more Nigerian content! Double tap if this resonated!",
            'tiktok': "Follow and share! Let's blow this up!",
            'youtube': "Subscribe and hit the bell! More content coming!",
            'twitter': "Retweet and follow for the gist!",
        }
        return ctas.get(platform, self.CLOSINGS['call_to_action'][0])
    
    def _generate_hashtags(self, topic: str, platform: str) -> List[str]:
        """Generate relevant hashtags"""
        base_tags = ['SisiLola', 'Nigerian', 'Naija', 'African']
        
        # Extract words from topic
        topic_words = [w.strip().title() for w in topic.split() if len(w) > 3][:3]
        
        platform_tags = {
            'instagram': ['ReelsAfrica', 'NaijaContent', 'AfricanCreator'],
            'tiktok': ['NaijaTikTok', 'AfricanTikTok', 'FYP'],
            'youtube': ['NaijaYouTube', 'AfricanYouTuber'],
            'podcast': ['AfricanPodcast', 'NaijaPodcast'],
            'live': ['LiveWithSisi', 'NaijaLive'],
        }
        
        all_tags = base_tags + topic_words + platform_tags.get(platform, [])
        return list(dict.fromkeys(all_tags))[:15]  # Unique, max 15
    
    def _generate_subtopics(self, topic: str, count: int) -> List[str]:
        """Generate subtopics for longer content"""
        # This would ideally use LLM, but for now generate placeholders
        return [f"Aspect {i+1} of {topic}" for i in range(count)]
    
    def _create_description(self, topic: str, hashtags: List[str]) -> str:
        """Create short description for reels"""
        tags_str = " ".join(f"#{tag}" for tag in hashtags[:10])
        return f"{topic}\n\n{tags_str}"
    
    def _create_long_description(self, topic: str, points: List[str], hashtags: List[str]) -> str:
        """Create detailed description for episodes"""
        points_str = "\n".join(f"• {p}" for p in points)
        tags_str = " ".join(f"#{tag}" for tag in hashtags)
        
        return f"""In this episode, Sisi Lola discusses {topic}!

WHAT WE COVER:
{points_str}

Don't forget to LIKE, SUBSCRIBE, and COMMENT!

{tags_str}
"""
    
    def _create_podcast_description(self, topic: str, points: List[str], 
                                     guest: Optional[str]) -> str:
        """Create podcast episode description"""
        guest_line = f"\n\nFeaturing special guest: {guest}" if guest else ""
        points_str = "\n".join(f"  - {p}" for p in points)
        
        return f"""Sisi Lola's Corner - Episode: {topic}{guest_line}

In this episode, we explore:
{points_str}

Subscribe on Spotify, Apple Podcasts, and wherever you listen!
"""
    
    def _save_plan(self, plan: ContentPlan):
        """Save content plan to file"""
        filename = f"{plan.plan_id}_{plan.content_type}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Content plan saved: {filepath.name}")


# Quick generation functions
def create_reel(topic: str, **kwargs) -> ContentPlan:
    """Quick function to create a reel"""
    generator = ContentGenerator()
    return generator.generate_reel(topic, **kwargs)


def create_episode(topic: str, **kwargs) -> ContentPlan:
    """Quick function to create an episode"""
    generator = ContentGenerator()
    return generator.generate_episode(topic, **kwargs)


def create_podcast(topic: str, **kwargs) -> ContentPlan:
    """Quick function to create a podcast"""
    generator = ContentGenerator()
    return generator.generate_podcast(topic, **kwargs)


if __name__ == "__main__":
    print("=" * 60)
    print("SISI LOLA CONTENT GENERATOR")
    print("=" * 60)
    
    generator = ContentGenerator()
    
    # Demo: Generate a reel
    print("\n--- Generating Reel ---")
    reel = generator.generate_reel(
        topic="Lagos tech startups changing Africa",
        duration_seconds=60,
        platform="instagram"
    )
    print(f"Created: {reel.title}")
    print(f"Duration: {reel.total_duration():.0f}s")
    print(f"Segments: {len(reel.segments)}")
    
    # Demo: Generate an episode
    print("\n--- Generating Episode ---")
    episode = generator.generate_episode(
        topic="The Rise of Afrobeats",
        duration_minutes=15,
        platform="youtube"
    )
    print(f"Created: {episode.title}")
    print(f"Duration: {episode.total_duration()/60:.0f} minutes")
    
    # Print sample script
    print("\n--- Sample Script (Reel) ---")
    print(reel.to_script_text()[:500])
