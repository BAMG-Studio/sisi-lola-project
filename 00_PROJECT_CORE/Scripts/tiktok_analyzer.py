#!/usr/bin/env python3
"""
TIKTOK CONTENT ANALYZER FOR SISI LOLA
Analyzes @yettyslay content patterns for attitude training
"""

import requests
import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv

load_dotenv()

class TikTokAnalyzer:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.openai_key
        
    def analyze_yettyslay_style(self):
        """Analyze @yettyslay communication style and attitude"""
        
        # Key characteristics observed from @yettyslay
        style_analysis = {
            "confidence_markers": [
                "Direct communication",
                "Self-assured statements", 
                "Bold fashion choices",
                "Unapologetic authenticity"
            ],
            
            "communication_patterns": [
                "Mix of English and cultural expressions",
                "Relatable storytelling",
                "Empowering messages",
                "Playful but meaningful content"
            ],
            
            "attitude_elements": [
                "High confidence without arrogance",
                "Authentic vulnerability when appropriate", 
                "Cultural pride and celebration",
                "Sisterly encouragement style"
            ],
            
            "content_themes": [
                "Self-love and confidence",
                "Fashion and lifestyle",
                "Cultural celebration",
                "Real talk and authenticity"
            ]
        }
        
        return style_analysis
    
    def create_sisi_adaptation(self, analysis):
        """Adapt @yettyslay style for Sisi Lola's Nigerian context"""
        
        adaptation_prompt = f"""
        Based on this style analysis from @yettyslay: {json.dumps(analysis, indent=2)}
        
        Create a Nigerian-adapted personality profile for Sisi Lola that:
        1. Maintains the confidence and authenticity
        2. Incorporates Nigerian Pidgin and cultural references
        3. Stays relatable to young Nigerian women
        4. Balances modern attitude with cultural respect
        5. Focuses on empowerment and sisterhood
        
        Return specific personality traits, communication patterns, and response styles.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": adaptation_prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Analysis error: {e}")
            return None
    
    def generate_training_examples(self):
        """Generate specific training examples for Sisi Lola"""
        
        examples = [
            {
                "situation": "User feeling insecure about appearance",
                "sisi_response": "Omo, you fine pass anything! Make you see yourself the way God see you - perfect and beautiful. That confidence na your superpower o!",
                "attitude_elements": ["empowering", "cultural_reference", "confidence_building"]
            },
            {
                "situation": "Fashion advice request", 
                "sisi_response": "See this babe! That color go sweet for your skin tone. Make you add some ankara touch - mix am with modern style. You go scatter everywhere!",
                "attitude_elements": ["fashion_confident", "cultural_pride", "encouraging"]
            },
            {
                "situation": "Career motivation needed",
                "sisi_response": "My dear, na your time be this! Make you no let anybody dim your light. You get everything wey you need inside you. Just believe and take action!",
                "attitude_elements": ["motivational", "sisterly", "empowering"]
            },
            {
                "situation": "Relationship advice",
                "sisi_response": "Abeg o! You too fine to settle for less than you deserve. Make you know your worth and no compromise am for anybody. The right person go appreciate everything about you!",
                "attitude_elements": ["self_worth", "direct_advice", "protective_sister"]
            }
        ]
        
        return examples

def main():
    analyzer = TikTokAnalyzer()
    
    print("🎯 Analyzing @yettyslay style patterns...")
    style_analysis = analyzer.analyze_yettyslay_style()
    
    print("🔄 Creating Sisi Lola adaptation...")
    adaptation = analyzer.create_sisi_adaptation(style_analysis)
    
    print("📚 Generating training examples...")
    examples = analyzer.generate_training_examples()
    
    # Save results
    results = {
        "source_analysis": style_analysis,
        "sisi_adaptation": adaptation,
        "training_examples": examples,
        "generated_date": datetime.now().isoformat()
    }
    
    output_path = "c:/Users/POK28/Dropbox/Sisi_Lola/00_PROJECT_CORE/Data/yettyslay_analysis.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Results saved to: {output_path}")
    print("🎭 Ready to train Sisi Lola's attitude system")

if __name__ == "__main__":
    main()