import os
import sys
import random
from datetime import datetime
from pathlib import Path

# Add Scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from content_template_generator import ContentTemplateGenerator, ContentCategory
from automated_content_scheduler import AutomatedContentScheduler, ScheduledPost, ContentType

def seed_high_quality_content():
    print("🌱 Seeding High-Quality Content Batch for Sisi Lola...")
    
    generator = ContentTemplateGenerator()
    scheduler = AutomatedContentScheduler()
    
    # Define high-quality topics tailored for Sisi Lola
    # Format: (Category, Topic, Description, ContentType for Scheduler)
    seed_topics = [
        # Tech Innovation (Educational/Tech)
        (ContentCategory.TECH_INNOVATION.value, "AI Revolution in Lagos", 
         "Exploring how Artificial Intelligence is transforming the tech ecosystem in Lagos, Nigeria. From startups to daily life.", 
         ContentType.EDUCATIONAL.value),
        
        (ContentCategory.TECH_INNOVATION.value, "Mobile Money Success Stories", 
         "How mobile money platforms like M-Pesa and OPay are driving financial inclusion across the continent.", 
         ContentType.EDUCATIONAL.value),
         
        (ContentCategory.TECH_INNOVATION.value, "African AgriTech Solutions", 
         "Innovative technologies helping African farmers increase yields and combat climate change.", 
         ContentType.EDUCATIONAL.value),

        # African Culture (Culture/Entertainment)
        (ContentCategory.AFRICAN_CULTURE.value, "The Great Jollof Debate", 
         "Settling the score once and for all! Nigerian vs Ghanaian Jollof - with an AI twist! 🍚", 
         ContentType.ENTERTAINMENT.value),
         
        (ContentCategory.AFRICAN_CULTURE.value, "Ankara Fashion Evolution", 
         "From traditional prints to modern runway masterpieces. The story of Ankara fabric.", 
         ContentType.EDUCATIONAL.value),
         
        (ContentCategory.AFRICAN_CULTURE.value, "Afrobeats Taking Over the World", 
         "Why the world can't get enough of African music. A deep dive into the global phenomenon.", 
         ContentType.ENTERTAINMENT.value),

        # Education (Educational)
        (ContentCategory.EDUCATION.value, "AI for Beginners: Explained by Sisi Lola", 
         "Breaking down complex AI concepts into simple, relatable terms. No jargon, just vibes.", 
         ContentType.EDUCATIONAL.value),
         
        (ContentCategory.EDUCATION.value, "Digital Skills for African Youth", 
         "Top 5 digital skills you need to learn in 2025 to secure your future.", 
         ContentType.EDUCATIONAL.value),

        # Entertainment (Entertainment)
        (ContentCategory.ENTERTAINMENT.value, "African Proverbs: AI Edition", 
         "Reimagining classic African proverbs for the digital age. Wisdom meets technology.", 
         ContentType.ENTERTAINMENT.value),
         
        (ContentCategory.ENTERTAINMENT.value, "Sisi Lola Reacts: Viral Trends", 
         "My AI take on the latest viral trends sweeping across social media.", 
         ContentType.ENTERTAINMENT.value),

        # Community (Community)
        (ContentCategory.COMMUNITY_BUILDING.value, "Welcome to Sisi Lola's Circle", 
         "Join our growing community of innovators, creators, and culture lovers. Let's build together!", 
         ContentType.COMMUNITY.value),
         
        (ContentCategory.COMMUNITY_BUILDING.value, "Q&A: Ask Sisi Lola Anything", 
         "Answering your burning questions about AI, Africa, and everything in between.", 
         ContentType.COMMUNITY.value),
         
        (ContentCategory.BEHIND_SCENES.value, "How Sisi Lola Was Made", 
         "A peek behind the curtain at the technology and creativity that brings your favorite AI Auntie to life.", 
         ContentType.PROMOTIONAL.value)
    ]
    
    platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit', 'Twitch']
    
    generated_count = 0
    
    for category, topic, description, scheduler_type in seed_topics:
        print(f"Generating: {topic}...")
        
        # Generate content using the template generator
        content_data = generator.generate(
            category=category,
            topic=topic,
            description=description,
            platforms=platforms
        )
        
        # Use YouTube content as the base for the scheduled post (it usually has the most detail)
        base_content = content_data.get('YouTube')
        
        # Create a ScheduledPost object
        post = ScheduledPost(
            title=base_content['title'],
            caption=base_content['caption'], # This includes hashtags and CTA
            media_type="video",
            content_type=scheduler_type,
            platforms=platforms,
            priority=8, # High priority for seed content
            tags=base_content['hashtags'],
            hashtags=base_content['hashtags'],
            notes=f"Seed content: {category} - {topic}"
        )
        
        # Add to scheduler (this will auto-schedule it)
        scheduler.add_post(post, auto_schedule=True)
        generated_count += 1
        
    print(f"\n✅ Successfully seeded {generated_count} high-quality posts!")
    
    # Export the calendar
    calendar_path = scheduler.export_calendar()
    print(f"📅 Schedule exported to: {calendar_path}")
    
    # Print summary
    scheduler.print_schedule_summary()

if __name__ == "__main__":
    seed_high_quality_content()
