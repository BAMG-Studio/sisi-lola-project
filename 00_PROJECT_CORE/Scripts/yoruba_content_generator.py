"""
Yoruba Content Generator - Uses NATLAS/Cohere for authentic Yoruba scripts
Enforces 60% Yoruba, 30% Pidgin, 10% English ratio
"""
import os
import cohere
from pathlib import Path
from dotenv import load_dotenv
from langdetect import detect_langs

load_dotenv(Path(__file__).parent.parent / ".env")

YORUBA_SYSTEM_PROMPT = """You are Sisi Lola, an Afro-futuristic Nigerian virtual host from Lagos.

CRITICAL LANGUAGE REQUIREMENTS:
- Speak ONLY in Yoruba/Yorunglish mix
- 60% pure Yoruba words and grammar
- 30% Nigerian Pidgin English
- 10% Standard English (technical terms only)
- Use Yoruba proverbs and idioms
- Natural Lagos auntie vibe
- Code-switch naturally like real Nigerians

NEVER respond in pure English. If you cannot express something in Yoruba/Pidgin, you have failed.

Example opening: "Ẹ káàbọ̀! I dey very happy say you come here today! Make I tell you about..."

Your personality: Warm, tech-savvy, culturally proud, educational, entertaining."""

class YorubaContentGenerator:
    def __init__(self):
        self.cohere = cohere.Client(os.getenv("COHERE_API_KEY"))
        self.model = os.getenv("COHERE_MODEL", "command-r-plus-08-2024")
        
    def validate_yoruba_content(self, text):
        """Validate Yoruba/Pidgin ratio"""
        # Count Yoruba markers
        yoruba_markers = ['ẹ', 'ọ', 'ṣ', 'káàbọ̀', 'dey', 'wetin', 'make', 'say']
        yoruba_count = sum(text.lower().count(marker) for marker in yoruba_markers)
        
        # Rough validation
        words = len(text.split())
        yoruba_ratio = (yoruba_count / words) * 100 if words > 0 else 0
        
        return yoruba_ratio > 15  # At least 15% Yoruba markers
    
    def generate_yoruba_script(self, topic, duration_minutes=7):
        """Generate Yoruba/Yorunglish script"""
        
        words_needed = duration_minutes * 150  # ~150 words per minute
        
        prompt = f"""Topic: {topic}

Create a {duration_minutes}-minute video script for Sisi Lola in Yoruba/Yorunglish.

Requirements:
- {words_needed} words total
- 60% Yoruba, 30% Nigerian Pidgin, 10% English
- Include Yoruba greetings, proverbs, cultural references
- Natural code-switching (like real Lagos people)
- Engaging, educational, entertaining
- Strong opening hook in Yoruba
- Clear sections with transitions
- Closing call-to-action in Yorunglish

Format: Single speaking script (no stage directions)."""

        response = self.cohere.chat(
            model=self.model,
            message=prompt,
            preamble=YORUBA_SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=2000
        )
        
        script = response.text
        
        # Validate
        if not self.validate_yoruba_content(script):
            print("[WARN] Script failed Yoruba validation, regenerating...")
            # Try again with stronger prompt
            return self.generate_yoruba_script(topic, duration_minutes)
        
        print(f"[OK] Yoruba script generated: {len(script)} chars, {len(script.split())} words")
        return script

def main():
    print("="*70)
    print("YORUBA CONTENT GENERATOR - Authentic Sisi Lola Scripts")
    print("="*70)
    
    generator = YorubaContentGenerator()
    
    topics = [
        "AI and the Future of African Tech Innovation",
        "How to Build Your Personal Brand as a Nigerian Creator",
        "The Power of African Languages in Technology",
        "Cloud Computing Explained for Nigerian Businesses",
        "My Journey as Sisi Lola: Virtual Host Revolution"
    ]
    
    print("\nSelect topic:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    choice = input("\nChoice (1-5) or custom: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= 5:
        topic = topics[int(choice) - 1]
    else:
        topic = choice if choice else topics[0]
    
    print(f"\n[TOPIC] {topic}")
    print("[GENERATING] Yoruba/Yorunglish script...")
    
    script = generator.generate_yoruba_script(topic, duration_minutes=7)
    
    # Save
    output_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "yoruba_scripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    import time
    filename = f"yoruba_script_{int(time.time())}.txt"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"TOPIC: {topic}\n\n")
        f.write(f"LANGUAGE: Yoruba/Yorunglish (60/30/10)\n\n")
        f.write(script)
    
    print(f"\n[SAVED] {filepath}")
    print(f"\n[PREVIEW]")
    print(script[:300] + "...")
    
    print("\n[NEXT] Generate Yoruba audio with yoruba_tts_generator.py")

if __name__ == "__main__":
    main()
