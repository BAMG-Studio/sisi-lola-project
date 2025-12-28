import modal
import os
import sys

def test_sisi_scenarios():
    print("🚀 TESTING SISI LOLA MEDIA SCENARIOS (Empire Mode)")
    
    scenarios = [
        ("radio_host", "Start the morning show and give me the latest highlights"),
        ("culture_tutor", "Explain the meaning of 'E choke' and give me a Yoruba proverb about hard work"),
        ("hustle_clinic", "Sisi, I want to japa to UK but I no get enough money. What should I do?")
    ]
    
    try:
        f = modal.Function.from_name("sisi-lola-inference", "chat_api")
        
        for scenario, query in scenarios:
            print(f"\n🎬 SCENARIO: {scenario.upper()}")
            print(f"❓ PROMPT: {query}")
            
            response = f.remote({
                "message": query,
                "scenario": scenario
            })
            print(f"\n✨ SISI'S {scenario.upper()} REPLY:\n{response}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_sisi_scenarios()
