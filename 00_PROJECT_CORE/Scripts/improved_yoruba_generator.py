"""Improved Yoruba Script Generator - 60/30/10 Ratio Enforced"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

YORUBA_EXAMPLES = """
YORUBA PHRASES (Use frequently):
- Ẹ káàbọ̀ o! (Welcome!)
- Báwo ni? (How are you?)
- Ọjọ́ òní (Today)
- Ẹ ṣeun (Thank you)
- Kò burú (Not bad)
- Mo dúpẹ́ (I'm grateful)
- Ẹ jọ̀wọ́ (Please)
- Ó dára púpọ̀ (Very good)
- A ò mọ̀ (We don't know)
- Ṣé o gbọ́? (Do you hear?)

NIGERIAN PIDGIN (Mix naturally):
- dey (is/are)
- wey (that/which)
- make we (let's)
- go fit (will be able to)
- don happen (has happened)
- wahala (problem)
- wetin (what)
- no be small thing (it's significant)
- e dey kampe (it's fine)
"""

def generate_authentic_yoruba_script(topic, duration_min=5):
    """Generate script with enforced 60% Yoruba, 30% Pidgin, 10% English"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f"""You are Sisi Lola, Nigerian AI influencer in 2-piece ankara attire.

CRITICAL: Generate script with MAJORITY YORUBA language.

LANGUAGE DISTRIBUTION (STRICT):
- 60% YORUBA: Use phrases from list below extensively
- 30% NIGERIAN PIDGIN: Natural code-switching
- 10% ENGLISH: Only technical terms

{YORUBA_EXAMPLES}

STRUCTURE:
1. Opening: Full Yoruba greeting (Ẹ káàbọ̀ o! Báwo ni ẹ ṣe wà?)
2. Introduction: Mix Yoruba + Pidgin (Ọjọ́ òní, we go talk about...)
3. Main content: Heavy Yoruba with Pidgin transitions
4. Closing: Yoruba thank you (Ẹ ṣeun púpọ̀!)

EXAMPLE SENTENCE STRUCTURE:
"Ẹ káàbọ̀ o! Ọjọ́ òní, a fẹ́ sọ̀rọ̀ nípa technology wey dey change Africa. Ó dára púpọ̀ say our people don dey use AI for fashion design. Ṣé ẹ gbọ́?"

Topic: {topic}
Duration: {duration_min} minutes (~{duration_min * 150} words)
Style: Warm, culturally proud, engaging"""
        }],
        max_tokens=2000,
        temperature=0.9
    )
    
    return response.choices[0].message.content, response.usage.total_tokens * 0.0000025

if __name__ == "__main__":
    topics = [
        "African tech startups revolutionizing agriculture",
        "Nigerian music industry meets AI production",
        "African fashion designers using 3D printing",
        "Lagos tech scene and innovation hubs",
        "African women in technology leadership"
    ]
    
    print("=" * 70)
    print("IMPROVED YORUBA SCRIPT GENERATOR - 60/30/10 RATIO")
    print("=" * 70)
    
    for i, topic in enumerate(topics[:3], 1):
        print(f"\n[{i}/3] Generating: {topic}")
        script, cost = generate_authentic_yoruba_script(topic)
        
        # Save script
        filename = f"../../07_RAW_WORKSPACE/yoruba_script_{i:03d}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"TOPIC: {topic}\n\n{script}")
        
        print(f"✓ Saved: {filename} (${cost:.4f})")
        print(f"Preview: {script[:200]}...\n")
    
    print("=" * 70)
    print("✓ 3 IMPROVED SCRIPTS GENERATED")
    print("Next: Review scripts, select best, upload to YouTube")
