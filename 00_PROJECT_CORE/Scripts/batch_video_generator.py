#!/usr/bin/env python3
"""
Batch Video Generator for Sisi Lola
Generate multiple videos from topic list
"""
import os
import json
from pathlib import Path
from datetime import datetime
from generate_first_video import generate_script, generate_heygen_video, upload_to_youtube

# Load environment
env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

OUTPUT_DIR = Path(__file__).parent.parent.parent / '06_RENDER_OUTPUT' / 'youtube_videos'

# Content topics for first 10 videos
VIDEO_TOPICS = [
    {
        'title': 'Meet Sisi Lola - Your AI Guide to African Culture 🌍',
        'prompt': 'Create a 60-second introduction for Sisi Lola, AI-powered African cultural ambassador. Warm, authentic, include African greetings.',
        'tags': ['Sisi Lola', 'African Culture', 'AI Influencer', 'Introduction']
    },
    {
        'title': 'What is African Innovation? 🚀',
        'prompt': 'Explain African innovation in 60 seconds. Examples: M-Pesa, African tech hubs, renewable energy solutions. Inspiring tone.',
        'tags': ['African Innovation', 'Technology', 'M-Pesa', 'Fintech']
    },
    {
        'title': 'Swahili Basics: 5 Essential Phrases 🗣️',
        'prompt': 'Teach 5 essential Swahili phrases in 60 seconds: Jambo, Asante, Karibu, Habari, Kwaheri. Pronunciation tips.',
        'tags': ['Swahili', 'African Languages', 'Language Learning', 'Tutorial']
    },
    {
        'title': 'Afrobeat Explained: The Sound of Africa 🎵',
        'prompt': 'Explain Afrobeat music in 60 seconds. Origins, key artists (Fela Kuti), modern evolution. Energetic tone.',
        'tags': ['Afrobeat', 'African Music', 'Fela Kuti', 'Music Education']
    },
    {
        'title': 'African Fashion: The Story of Ankara 👗',
        'prompt': 'Tell the story of Ankara fabric in 60 seconds. Origins, cultural significance, modern fashion. Celebratory tone.',
        'tags': ['African Fashion', 'Ankara', 'Traditional Clothing', 'Culture']
    },
    {
        'title': 'Did You Know? 5 Amazing African Facts 🌍',
        'prompt': 'Share 5 surprising facts about Africa in 60 seconds. Geography, wildlife, innovation, culture. Fun, engaging tone.',
        'tags': ['African Facts', 'Education', 'Geography', 'Culture']
    },
    {
        'title': 'African Cuisine: Jollof Rice Origins 🍚',
        'prompt': 'Tell the story of Jollof rice in 60 seconds. Origins, regional variations, cultural importance. Mouth-watering tone.',
        'tags': ['African Cuisine', 'Jollof Rice', 'Food', 'West Africa']
    },
    {
        'title': 'Meet African Tech Innovators 💡',
        'prompt': 'Spotlight 3 African tech innovators in 60 seconds. Their innovations, impact. Inspiring, forward-looking tone.',
        'tags': ['African Tech', 'Innovators', 'Entrepreneurs', 'Technology']
    },
    {
        'title': 'Ubuntu Philosophy: I Am Because We Are 🤝',
        'prompt': 'Explain Ubuntu philosophy in 60 seconds. Meaning, cultural significance, modern relevance. Warm, communal tone.',
        'tags': ['Ubuntu', 'African Philosophy', 'Community', 'Culture']
    },
    {
        'title': 'Your Questions About Africa Answered! ❓',
        'prompt': 'Answer 3 common questions about Africa in 60 seconds. Myths vs reality. Informative, friendly tone.',
        'tags': ['Q&A', 'African Culture', 'Education', 'Community']
    }
]

def generate_custom_script(topic):
    """Generate script for specific topic"""
    print(f"📝 Generating script: {topic['title']}")
    
    import requests
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}",
            'Content-Type': 'application/json'
        },
        json={
            'model': 'gpt-4',
            'messages': [{'role': 'user', 'content': topic['prompt']}],
            'temperature': 0.8
        }
    )
    
    script = response.json()['choices'][0]['message']['content']
    
    # Save script
    safe_title = "".join(c for c in topic['title'] if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
    script_path = OUTPUT_DIR / f'script_{safe_title}_{datetime.now().strftime("%Y%m%d")}.txt'
    script_path.write_text(script)
    
    return script

def generate_batch(start_index=0, count=3, auto_upload=False):
    """Generate batch of videos"""
    print("=" * 60)
    print(f"BATCH VIDEO GENERATION: {count} videos starting from #{start_index + 1}")
    print("=" * 60)
    
    results = []
    
    for i in range(start_index, min(start_index + count, len(VIDEO_TOPICS))):
        topic = VIDEO_TOPICS[i]
        print(f"\n{'=' * 60}")
        print(f"VIDEO {i + 1}/{len(VIDEO_TOPICS)}: {topic['title']}")
        print(f"{'=' * 60}")
        
        try:
            # Generate script
            script = generate_custom_script(topic)
            
            # Generate video
            video_path = generate_heygen_video(script)
            
            if not video_path:
                print(f"❌ Video {i + 1} failed")
                results.append({'index': i + 1, 'status': 'failed', 'title': topic['title']})
                continue
            
            # Upload if auto mode
            video_id = None
            if auto_upload:
                print(f"📤 Auto-uploading video {i + 1}...")
                
                description = f"""{script[:200]}...

Subscribe for more African culture, innovation, and community content!

#SisiLola #AfricanCulture #{' #'.join(topic['tags'][:3])}"""
                
                from youtube_content_uploader import upload_video
                video_id = upload_video(
                    video_path=str(video_path),
                    title=topic['title'],
                    description=description,
                    tags=topic['tags'],
                    category_id="22",
                    privacy="public"
                )
                
                print(f"✅ Video {i + 1} uploaded: https://youtu.be/{video_id}")
            
            results.append({
                'index': i + 1,
                'status': 'success',
                'title': topic['title'],
                'video_path': str(video_path),
                'video_id': video_id,
                'url': f"https://youtu.be/{video_id}" if video_id else None
            })
            
        except Exception as e:
            print(f"❌ Error on video {i + 1}: {e}")
            results.append({'index': i + 1, 'status': 'error', 'title': topic['title'], 'error': str(e)})
    
    # Save batch report
    report_path = OUTPUT_DIR / f'batch_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_path.write_text(json.dumps(results, indent=2))
    
    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print("=" * 60)
    print(f"Report: {report_path}")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"Success: {success_count}/{len(results)}")
    
    return results

if __name__ == '__main__':
    import sys
    
    # Usage: python batch_video_generator.py [start_index] [count] [auto_upload]
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    auto = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    print(f"Generating {count} videos starting from #{start + 1}")
    print(f"Auto-upload: {auto}")
    
    if not auto:
        confirm = input("\nContinue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            sys.exit(0)
    
    generate_batch(start, count, auto)
