"""
Content Template Generator
Platform-optimized content generation with AI assistance
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ContentCategory(Enum):
    """Content categories"""
    TECH_INNOVATION = "tech_innovation"
    AFRICAN_CULTURE = "african_culture"
    COMMUNITY_BUILDING = "community_building"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    BEHIND_SCENES = "behind_scenes"
    COLLABORATION = "collaboration"


@dataclass
class ContentTemplate:
    """Content template structure"""
    category: str
    title_template: str
    caption_templates: List[str]
    hashtag_groups: List[List[str]]
    optimal_platforms: List[str]
    optimal_length_seconds: Dict[str, int]
    call_to_action: List[str]
    hook_styles: List[str]


class PlatformOptimizer:
    """Platform-specific content optimization"""
    
    # Platform character limits
    PLATFORM_LIMITS = {
        'YouTube': {
            'title': 100,
            'description': 5000,
            'tags': 500
        },
        'Instagram': {
            'caption': 2200,
            'hashtags': 30
        },
        'TikTok': {
            'caption': 150,
            'hashtags': 5
        },
        'Facebook': {
            'post': 63206,
            'title': 255
        },
        'Twitch': {
            'title': 140
        },
        'Reddit': {
            'title': 300,
            'post': 40000
        }
    }
    
    # Optimal video lengths (seconds)
    VIDEO_LENGTHS = {
        'YouTube': {'shorts': 60, 'standard': 480, 'long': 1200},
        'Instagram': {'reel': 60, 'video': 90},
        'TikTok': {'short': 15, 'medium': 30, 'long': 60},
        'Facebook': {'short': 30, 'medium': 120, 'long': 300}
    }
    
    @staticmethod
    def optimize_caption(caption: str, platform: str) -> str:
        """Optimize caption for platform"""
        limit = PlatformOptimizer.PLATFORM_LIMITS.get(platform, {}).get('caption', 2000)
        
        if len(caption) <= limit:
            return caption
        
        # Truncate with ellipsis
        return caption[:limit-3] + "..."
    
    @staticmethod
    def optimize_hashtags(hashtags: List[str], platform: str) -> List[str]:
        """Optimize hashtags for platform"""
        if platform == 'TikTok':
            return hashtags[:5]  # TikTok: max 5 hashtags recommended
        elif platform == 'Instagram':
            return hashtags[:30]  # Instagram: max 30 hashtags
        elif platform == 'YouTube':
            return hashtags[:15]  # YouTube: reasonable limit
        else:
            return hashtags
    
    @staticmethod
    def format_hashtags(hashtags: List[str], platform: str) -> str:
        """Format hashtags for platform"""
        optimized = PlatformOptimizer.optimize_hashtags(hashtags, platform)
        
        if platform in ['Instagram', 'TikTok', 'Facebook']:
            return ' '.join(f'#{tag}' for tag in optimized)
        elif platform == 'YouTube':
            return ', '.join(optimized)  # YouTube uses comma-separated tags
        else:
            return ' '.join(f'#{tag}' for tag in optimized)
    
    @staticmethod
    def generate_title(base_title: str, platform: str) -> str:
        """Generate platform-optimized title"""
        limit = PlatformOptimizer.PLATFORM_LIMITS.get(platform, {}).get('title', 100)
        
        if len(base_title) <= limit:
            return base_title
        
        # Truncate intelligently at word boundary
        truncated = base_title[:limit]
        last_space = truncated.rfind(' ')
        if last_space > limit * 0.7:  # Only if we're not losing too much
            return truncated[:last_space] + "..."
        
        return truncated + "..."


class ContentTemplateGenerator:
    """
    Generates platform-optimized content from templates
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.optimizer = PlatformOptimizer()
    
    def _load_templates(self) -> Dict[str, ContentTemplate]:
        """Load content templates"""
        templates = {
            ContentCategory.TECH_INNOVATION.value: ContentTemplate(
                category=ContentCategory.TECH_INNOVATION.value,
                title_template="African Tech Innovation: {topic}",
                caption_templates=[
                    "🌍 Discovering {topic} in Africa's tech ecosystem!\n\n{description}\n\nWhat's your favorite African tech innovation? Drop a comment! 👇",
                    "African innovation spotlight: {topic} 🚀\n\n{description}\n\nFollow for more African tech stories!",
                    "The future of tech is African! 🌍\n\nToday exploring: {topic}\n\n{description}\n\nLet's celebrate innovation together!"
                ],
                hashtag_groups=[
                    ['AfricanTech', 'Innovation', 'TechAfrica', 'StartupAfrica'],
                    ['Lagos', 'Nairobi', 'CapeTown', 'AfricanEntrepreneurs'],
                    ['AI', 'Fintech', 'EdTech', 'AgriTech', 'HealthTech']
                ],
                optimal_platforms=['YouTube', 'LinkedIn', 'TikTok', 'Instagram'],
                optimal_length_seconds={
                    'YouTube': 180,
                    'TikTok': 45,
                    'Instagram': 60
                },
                call_to_action=[
                    "Subscribe for more African tech stories!",
                    "Follow for daily innovation updates!",
                    "Share with someone building in Africa!"
                ],
                hook_styles=[
                    "Did you know Africa is leading in {topic}?",
                    "This African innovation will blow your mind!",
                    "The next big tech wave is happening in Africa!"
                ]
            ),
            
            ContentCategory.AFRICAN_CULTURE.value: ContentTemplate(
                category=ContentCategory.AFRICAN_CULTURE.value,
                title_template="African Culture Spotlight: {topic}",
                caption_templates=[
                    "✨ Celebrating {topic} today!\n\n{description}\n\nWhat's your favorite cultural tradition? 🌍",
                    "African heritage moment: {topic} 🎭\n\n{description}\n\nTag someone who loves culture!",
                    "Our roots, our pride! 🌍\n\nToday: {topic}\n\n{description}"
                ],
                hashtag_groups=[
                    ['AfricanCulture', 'AfricanHeritage', 'AfricanPride'],
                    ['CulturalCelebration', 'AfricanTraditions', 'AfricanArt'],
                    ['AfricanMusic', 'AfricanFashion', 'AfricanCuisine']
                ],
                optimal_platforms=['Instagram', 'TikTok', 'Facebook', 'YouTube'],
                optimal_length_seconds={
                    'YouTube': 240,
                    'TikTok': 30,
                    'Instagram': 45
                },
                call_to_action=[
                    "Celebrate African culture with us!",
                    "Share your cultural story below!",
                    "Follow for daily cultural highlights!"
                ],
                hook_styles=[
                    "The beauty of {topic} will amaze you!",
                    "African culture at its finest!",
                    "You've never seen {topic} like this before!"
                ]
            ),
            
            ContentCategory.EDUCATION.value: ContentTemplate(
                category=ContentCategory.EDUCATION.value,
                title_template="Learn: {topic}",
                caption_templates=[
                    "📚 Today's lesson: {topic}\n\n{description}\n\nWhat did you learn today? Comment below!",
                    "Educational moment! 🎓\n\nTopic: {topic}\n\n{description}\n\nSave this for later!",
                    "Knowledge is power! 💡\n\n{topic}\n\n{description}\n\nShare with someone learning!"
                ],
                hashtag_groups=[
                    ['Education', 'LearnWithMe', 'KnowledgeSharing'],
                    ['AfricanEducation', 'TechEducation', 'SkillBuilding'],
                    ['Tutorial', 'HowTo', 'DidYouKnow']
                ],
                optimal_platforms=['YouTube', 'Instagram', 'TikTok', 'Reddit'],
                optimal_length_seconds={
                    'YouTube': 360,
                    'TikTok': 60,
                    'Instagram': 60
                },
                call_to_action=[
                    "Subscribe for daily lessons!",
                    "Save this for your learning journey!",
                    "Comment what you want to learn next!"
                ],
                hook_styles=[
                    "Here's what nobody tells you about {topic}",
                    "The fastest way to understand {topic}",
                    "Everything you need to know about {topic}"
                ]
            ),
            
            ContentCategory.COMMUNITY_BUILDING.value: ContentTemplate(
                category=ContentCategory.COMMUNITY_BUILDING.value,
                title_template="Community: {topic}",
                caption_templates=[
                    "💬 Community check-in: {topic}\n\n{description}\n\nDrop your thoughts below! 👇",
                    "Building together! 🌍\n\n{topic}\n\n{description}\n\nYour voice matters!",
                    "Community spotlight: {topic}\n\n{description}\n\nLet's grow together!"
                ],
                hashtag_groups=[
                    ['Community', 'CommunityBuilding', 'TogetherWeGrow'],
                    ['AfricanCommunity', 'SupportLocal', 'CommunityFirst'],
                    ['Collaboration', 'NetworkingAfrica', 'CommunityLove']
                ],
                optimal_platforms=['Instagram', 'Facebook', 'Reddit', 'Twitch'],
                optimal_length_seconds={
                    'YouTube': 300,
                    'Instagram': 45,
                    'Facebook': 90
                },
                call_to_action=[
                    "Join our community!",
                    "Share your story with us!",
                    "Tag your community!"
                ],
                hook_styles=[
                    "Our community's biggest win this week!",
                    "You're part of something special!",
                    "Community update you don't want to miss!"
                ]
            ),
            
            ContentCategory.ENTERTAINMENT.value: ContentTemplate(
                category=ContentCategory.ENTERTAINMENT.value,
                title_template="{topic} - Entertainment",
                caption_templates=[
                    "😂 {topic}\n\n{description}\n\nTag someone who needs to see this!",
                    "Entertainment time! 🎬\n\n{topic}\n\n{description}",
                    "You're going to love this! ✨\n\n{topic}\n\n{description}\n\nDouble tap if you agree!"
                ],
                hashtag_groups=[
                    ['Entertainment', 'Fun', 'AfricanEntertainment'],
                    ['Comedy', 'Viral', 'Trending'],
                    ['AfricanComedy', 'Funny', 'Laugh']
                ],
                optimal_platforms=['TikTok', 'Instagram', 'YouTube', 'Facebook'],
                optimal_length_seconds={
                    'TikTok': 15,
                    'Instagram': 30,
                    'YouTube': 120
                },
                call_to_action=[
                    "Follow for daily entertainment!",
                    "Share the fun!",
                    "Tag your friends!"
                ],
                hook_styles=[
                    "Wait for it... 😂",
                    "This is hilarious!",
                    "You won't believe this!"
                ]
            ),
            
            ContentCategory.BEHIND_SCENES.value: ContentTemplate(
                category=ContentCategory.BEHIND_SCENES.value,
                title_template="Behind the Scenes: {topic}",
                caption_templates=[
                    "🎬 Behind the scenes: {topic}\n\n{description}\n\nWhat do you want to see next?",
                    "Here's how it's made! 🔧\n\n{topic}\n\n{description}\n\nComment your questions!",
                    "BTS magic! ✨\n\n{topic}\n\n{description}"
                ],
                hashtag_groups=[
                    ['BehindTheScenes', 'BTS', 'MakingOf'],
                    ['ContentCreation', 'CreatorLife', 'Process'],
                    ['AI', 'Technology', 'Innovation']
                ],
                optimal_platforms=['Instagram', 'YouTube', 'TikTok', 'Twitch'],
                optimal_length_seconds={
                    'YouTube': 420,
                    'Instagram': 60,
                    'TikTok': 45
                },
                call_to_action=[
                    "Want more BTS content?",
                    "Ask me anything in comments!",
                    "Subscribe for behind-the-scenes!"
                ],
                hook_styles=[
                    "Ever wondered how I create content?",
                    "The secret behind {topic}",
                    "Here's what you don't see!"
                ]
            )
        }
        
        return templates
    
    def generate(self, category: str, topic: str, description: str, 
                platforms: List[str] = None) -> Dict[str, Dict]:
        """
        Generate platform-optimized content
        
        Args:
            category: Content category
            topic: Main topic/subject
            description: Detailed description
            platforms: List of target platforms (if None, uses optimal platforms)
        
        Returns:
            Dictionary mapping platform to optimized content
        """
        template = self.templates.get(category)
        if not template:
            raise ValueError(f"Unknown category: {category}")
        
        if platforms is None:
            platforms = template.optimal_platforms
        
        content = {}
        
        for platform in platforms:
            content[platform] = self._generate_for_platform(
                template, topic, description, platform
            )
        
        return content
    
    def _generate_for_platform(self, template: ContentTemplate, 
                              topic: str, description: str,
                              platform: str) -> Dict:
        """Generate content optimized for specific platform"""
        # Select random caption template
        caption_template = random.choice(template.caption_templates)
        
        # Fill in template
        caption = caption_template.format(topic=topic, description=description)
        
        # Optimize for platform
        caption = self.optimizer.optimize_caption(caption, platform)
        
        # Generate title
        title_base = template.title_template.format(topic=topic)
        title = self.optimizer.generate_title(title_base, platform)
        
        # Select hashtags (mix from different groups)
        all_hashtags = []
        for group in template.hashtag_groups:
            all_hashtags.extend(random.sample(group, min(2, len(group))))
        
        hashtags = self.optimizer.optimize_hashtags(all_hashtags, platform)
        hashtag_string = self.optimizer.format_hashtags(hashtags, platform)
        
        # Add CTA
        cta = random.choice(template.call_to_action)
        
        # Add hook (for video scripts)
        hook = random.choice(template.hook_styles).format(topic=topic)
        
        # Combine caption with hashtags (platform-specific)
        if platform in ['Instagram', 'TikTok', 'Facebook']:
            full_caption = f"{caption}\n\n{hashtag_string}\n\n{cta}"
        elif platform == 'YouTube':
            full_caption = f"{caption}\n\n{cta}"
        else:
            full_caption = f"{caption}\n\n{cta}"
        
        return {
            'title': title,
            'caption': full_caption,
            'hashtags': hashtags,
            'hook': hook,
            'cta': cta,
            'optimal_length': template.optimal_length_seconds.get(platform, 60),
            'raw_caption': caption,
            'raw_hashtag_string': hashtag_string
        }
    
    def generate_batch(self, count: int = 10, 
                      category_distribution: Dict[str, float] = None) -> List[Dict]:
        """
        Generate batch of content following category distribution
        
        Args:
            count: Number of content pieces to generate
            category_distribution: Distribution of categories (if None, uses default mix)
        
        Returns:
            List of content dictionaries
        """
        if category_distribution is None:
            # Default mix: 40% education, 30% entertainment, 20% culture, 10% other
            category_distribution = {
                ContentCategory.EDUCATION.value: 0.40,
                ContentCategory.ENTERTAINMENT.value: 0.30,
                ContentCategory.AFRICAN_CULTURE.value: 0.20,
                ContentCategory.TECH_INNOVATION.value: 0.10
            }
        
        # Calculate count per category
        categories = []
        for cat, percentage in category_distribution.items():
            category_count = int(count * percentage)
            categories.extend([cat] * category_count)
        
        # Fill remainder
        while len(categories) < count:
            categories.append(random.choice(list(category_distribution.keys())))
        
        random.shuffle(categories)
        
        # Sample topics
        topics = {
            ContentCategory.TECH_INNOVATION.value: [
                "AI in African Agriculture", "Fintech Revolution", "E-commerce Growth",
                "Mobile Banking Innovation", "EdTech Solutions", "HealthTech Advances"
            ],
            ContentCategory.AFRICAN_CULTURE.value: [
                "Traditional Music", "Fashion Heritage", "Culinary Traditions",
                "Art and Crafts", "Dance Styles", "Storytelling Traditions"
            ],
            ContentCategory.EDUCATION.value: [
                "Python Programming Basics", "Digital Marketing 101", "AI Fundamentals",
                "Entrepreneurship Tips", "Financial Literacy", "Social Media Strategy"
            ],
            ContentCategory.ENTERTAINMENT.value: [
                "Funny Moments Compilation", "African Memes", "Comedy Sketches",
                "Viral Challenges", "Trending Sounds", "Fun Facts"
            ]
        }
        
        batch = []
        
        for category in categories:
            topic = random.choice(topics.get(category, ["General Content"]))
            description = f"Exploring {topic} from an African perspective with insights and stories."
            
            content_data = self.generate(
                category=category,
                topic=topic,
                description=description
            )
            
            batch.append({
                'category': category,
                'topic': topic,
                'description': description,
                'platform_content': content_data,
                'created_at': datetime.now().isoformat()
            })
        
        return batch
    
    def export_batch(self, batch: List[Dict], filepath: str = None):
        """Export batch to JSON file"""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "03_MEDIA_ASSETS" / "content_queue" / f"content_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Batch exported to: {filepath}")
        return filepath
    
    def print_content_preview(self, content_data: Dict):
        """Print content preview for all platforms"""
        print("\n" + "=" * 70)
        print("CONTENT PREVIEW")
        print("=" * 70)
        
        for platform, content in content_data.items():
            print(f"\n{platform.upper()}")
            print("-" * 70)
            print(f"Title: {content['title']}")
            print(f"Hook: {content['hook']}")
            print(f"Caption:\n{content['caption'][:200]}...")
            print(f"Optimal Length: {content['optimal_length']}s")
            print(f"Hashtags: {len(content['hashtags'])} tags")


def main():
    """Example usage"""
    generator = ContentTemplateGenerator()
    
    # Generate single content piece
    print("Generating content for African Tech Innovation...")
    
    content = generator.generate(
        category=ContentCategory.TECH_INNOVATION.value,
        topic="Mobile Money Revolution in Kenya",
        description="How M-Pesa transformed financial inclusion across East Africa, enabling millions to access banking services for the first time.",
        platforms=['YouTube', 'Instagram', 'TikTok', 'Facebook']
    )
    
    generator.print_content_preview(content)
    
    # Generate batch
    print("\n\nGenerating batch of 14 content pieces...")
    batch = generator.generate_batch(count=14)
    
    print(f"\n✅ Generated {len(batch)} content pieces")
    print("\nCategory Distribution:")
    category_counts = {}
    for item in batch:
        cat = item['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in category_counts.items():
        percentage = count / len(batch) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")
    
    # Export batch
    filepath = generator.export_batch(batch)
    print(f"\n📦 Batch saved to: {filepath}")


if __name__ == "__main__":
    main()
