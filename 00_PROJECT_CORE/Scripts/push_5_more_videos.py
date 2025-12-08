"""Generate and Push 5 More Authentic Videos NOW"""
import sys
sys.path.insert(0, '.')
from complete_production_pipeline import generate_yoruba_script_7min, validate_yoruba_ratio, create_video_with_voice, upload_to_youtube
from pathlib import Path

topics = [
    "African fintech revolution transforming mobile banking",
    "Nigerian Nollywood meets AI filmmaking technology",
    "African renewable energy startups solving power crisis",
    "Lagos startup ecosystem attracting global investors",
    "African e-commerce platforms competing with Amazon"
]

print("=" * 70)
print("PUSHING 5 MORE AUTHENTIC SISI LOLA VIDEOS")
print("=" * 70)

total_cost = 0
videos = []

for i, topic in enumerate(topics, 4):
    print(f"\n[VIDEO {i}/8] {topic}")
    print("-" * 70)
    
    script, cost = generate_yoruba_script_7min(topic)
    total_cost += cost
    print(f"[1/4] ✓ Script generated (${cost:.4f})")
    
    validation = validate_yoruba_ratio(script)
    print(f"[2/4] ✓ Yoruba: {validation['yoruba']}%")
    
    script_file = f"../../07_RAW_WORKSPACE/authentic_script_{i:03d}.txt"
    Path(script_file).parent.mkdir(parents=True, exist_ok=True)
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(f"TOPIC: {topic}\n\n{script}")
    
    video_file = f"../../06_RENDER_OUTPUT/authentic_video_{i:03d}.mp4"
    Path(video_file).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        video_path, duration = create_video_with_voice(script_file, video_file)
        print(f"[3/4] ✓ Video created ({duration:.1f} min)")
        
        title = f"{topic[:60]}... - Sisi Lola (Yoruba/English)"
        url = upload_to_youtube(video_file, title, script)
        videos.append(url)
        print(f"[4/4] ✓ Published: {url}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print(f"✓ {len(videos)} MORE VIDEOS PUBLISHED")
print("=" * 70)
print(f"Cost: ${total_cost:.4f}\n")
for i, url in enumerate(videos, 1):
    print(f"{i}. {url}")
