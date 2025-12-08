"""Test GPT-4o Yoruba Content Generation Quality"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import re

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv("../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_language_ratio(text):
    """Estimate Yoruba/Pidgin/English ratio"""
    yoruba_markers = len(re.findall(r'\b(ẹ|ọ|ṣ|káàbọ̀|báwo|ṣé|dára|wá|ti|ni|kò|jẹ)\b', text, re.IGNORECASE))
    pidgin_markers = len(re.findall(r'\b(dey|wey|make|go|fit|don|una|wetin|abi|sha)\b', text, re.IGNORECASE))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    total = yoruba_markers + pidgin_markers + english_words
    if total == 0: return (0, 0, 0)
    
    return (
        round(yoruba_markers/total*100, 1),
        round(pidgin_markers/total*100, 1),
        round(english_words/total*100, 1)
    )

# Test prompt with examples
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "system",
        "content": """You are Sisi Lola, Nigerian AI host in 2-piece ankara attire.
        Generate 2-minute script about African tech innovation.
        
        STRICT LANGUAGE RATIO:
        - 60% Yoruba: Use ẹ káàbọ̀, báwo ni, ṣé dára, ọjọ́ òní, ẹ ṣeun, kò burú
        - 30% Nigerian Pidgin: Use dey, wey, make we, go fit, don happen, wahala, wetin
        - 10% English: Only for tech terms like AI, innovation, technology
        
        Example opening: "Ẹ káàbọ̀ o! Báwo ni everybody dey? Today we go yarn about how technology dey change Africa. Ọjọ́ òní, make we discuss innovation wey dey burst brain!"
        
        Use natural code-switching between languages."""
    }],
    temperature=0.9
)

script = response.choices[0].message.content
yoruba_pct, pidgin_pct, english_pct = count_language_ratio(script)

print("=" * 60)
print("GPT-4o YORUBA QUALITY TEST")
print("=" * 60)
print(f"\nLANGUAGE RATIO:")
print(f"   Yoruba:  {yoruba_pct}% (Target: 60%)")
print(f"   Pidgin:  {pidgin_pct}% (Target: 30%)")
print(f"   English: {english_pct}% (Target: 10%)")
print(f"\nPASS" if 50 <= yoruba_pct <= 70 else f"\nFAIL")
print(f"\nGENERATED SCRIPT:\n{script[:500]}...")
print(f"\nCost: ${response.usage.total_tokens * 0.0000025:.4f}")
