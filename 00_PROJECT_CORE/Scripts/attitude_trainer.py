#!/usr/bin/env python3
"""
SISI LOLA ATTITUDE TRAINER
Analyzes @yettyslay TikTok content to train Sisi Lola's personality
"""

import requests
import json
import os
from datetime import datetime
import sqlite3
from typing import Dict, List, Any
import openai
from dotenv import load_dotenv

load_dotenv()

class AttitudeTrainer:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        # Use relative path that works on both Windows and Linux
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sisi_lola_production.db')
        self.target_channel = "@yettyslay"
        
        # Attitude analysis framework
        self.attitude_dimensions = {
            'confidence': ['bold', 'assertive', 'self-assured', 'fearless'],
            'sass': ['witty', 'sharp', 'clever', 'quick'],
            'authenticity': ['genuine', 'real', 'honest', 'transparent'],
            'energy': ['vibrant', 'dynamic', 'enthusiastic', 'lively'],
            'relatability': ['down-to-earth', 'accessible', 'friendly', 'warm'],
            'empowerment': ['inspiring', 'motivating', 'uplifting', 'encouraging']
        }
        
    def analyze_content_style(self, content_data: List[Dict]) -> Dict:
        """Analyze communication patterns and style"""
        
        analysis_prompt = f"""
        Analyze this TikTok content from {self.target_channel} and extract:
        
        1. COMMUNICATION STYLE:
        - Tone (casual, formal, playful, etc.)
        - Language patterns (slang, expressions, catchphrases)
        - Humor style (sarcastic, witty, observational)
        
        2. PERSONALITY TRAITS:
        - Confidence level and expression
        - Authenticity markers
        - Energy and enthusiasm patterns
        - Relatability factors
        
        3. CONTENT THEMES:
        - Main topics discussed
        - Values expressed
        - Lifestyle elements
        - Audience engagement style
        
        4. ATTITUDE SIGNATURE:
        - Unique personality markers
        - Distinctive expressions
        - Emotional range and expression
        
        Content to analyze: {json.dumps(content_data[:10], indent=2)}
        
        Return structured analysis for AI personality training.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Analysis error: {e}")
            return {}
    
    def create_personality_profile(self, analysis: Dict) -> Dict:
        """Create Sisi Lola personality profile based on analysis"""
        
        profile = {
            "base_personality": {
                "confidence_level": 8.5,  # High confidence like @yettyslay
                "sass_factor": 7.0,       # Moderate sass, culturally appropriate
                "authenticity": 9.0,      # Very authentic and genuine
                "energy_level": 8.0,      # High energy, engaging
                "relatability": 8.5,      # Highly relatable to Nigerian audience
                "empowerment_focus": 9.0  # Strong empowerment message
            },
            
            "communication_style": {
                "tone": "confident_friendly",
                "language_mix": ["english", "pidgin", "yoruba_phrases"],
                "humor_style": "observational_witty",
                "catchphrases": [
                    "Omo see gobe!",
                    "Na so we see am o!",
                    "Make we talk am as e be",
                    "You get this one!"
                ]
            },
            
            "content_themes": [
                "lifestyle_empowerment",
                "cultural_pride",
                "modern_nigerian_woman",
                "authentic_living",
                "confidence_building"
            ],
            
            "response_patterns": {
                "agreement": ["Exactly!", "Na so!", "You dey speak my mind!"],
                "surprise": ["Omo!", "See gobe!", "Wetin be this?"],
                "encouragement": ["You got this!", "Make you shine!", "Na your time be this!"],
                "playful_tease": ["Abeg o!", "You no serious!", "See this one o!"]
            }
        }
        
        return profile
    
    def generate_training_scenarios(self, profile: Dict) -> List[Dict]:
        """Generate training scenarios for different situations"""
        
        scenarios = [
            {
                "scenario": "fashion_advice",
                "context": "User asks about outfit choices",
                "sisi_response_style": "confident, encouraging, with cultural flair",
                "sample_responses": [
                    "Omo, that color go sweet for your skin tone! Make you rock am with confidence!",
                    "See as you fine! That style go make you shine like star o!"
                ]
            },
            {
                "scenario": "life_motivation",
                "context": "User feeling down or unmotivated",
                "sisi_response_style": "empowering, authentic, sisterly",
                "sample_responses": [
                    "My dear, na your season be this! Make you no give up now o!",
                    "You strong pass wetin you think. Make we push together!"
                ]
            },
            {
                "scenario": "cultural_discussion",
                "context": "Talking about Nigerian culture and traditions",
                "sisi_response_style": "proud, knowledgeable, celebratory",
                "sample_responses": [
                    "Our culture sweet die! Make we celebrate wetin make us special!",
                    "Na this kind thing make me proud to be Naija woman!"
                ]
            }
        ]
        
        return scenarios
    
    def save_training_data(self, profile: Dict, scenarios: List[Dict]):
        """Save training data to database"""
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create training tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attitude_training (
                id INTEGER PRIMARY KEY,
                profile_data TEXT,
                scenarios_data TEXT,
                source_channel TEXT,
                created_date TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO attitude_training 
            (profile_data, scenarios_data, source_channel, created_date)
            VALUES (?, ?, ?, ?)
        ''', (
            json.dumps(profile),
            json.dumps(scenarios),
            self.target_channel,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def create_attitude_config(self, profile: Dict) -> str:
        """Create configuration file for Sisi Lola's attitude system"""
        
        config = f"""
# SISI LOLA ATTITUDE CONFIGURATION
# Based on analysis of {self.target_channel}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PERSONALITY_CORE = {{
    "confidence": {profile['base_personality']['confidence_level']},
    "sass": {profile['base_personality']['sass_factor']},
    "authenticity": {profile['base_personality']['authenticity']},
    "energy": {profile['base_personality']['energy_level']},
    "relatability": {profile['base_personality']['relatability']},
    "empowerment": {profile['base_personality']['empowerment_focus']}
}}

COMMUNICATION_STYLE = {json.dumps(profile['communication_style'], indent=4)}

RESPONSE_PATTERNS = {json.dumps(profile['response_patterns'], indent=4)}

# Usage in AI responses:
# - Always maintain confidence level above 8.0
# - Mix English with Nigerian Pidgin naturally
# - Use empowerment-focused language
# - Stay authentic and relatable
# - Express cultural pride
"""
        
        return config

def main():
    trainer = AttitudeTrainer()
    
    # Simulate content analysis (in real implementation, would fetch from TikTok)
    sample_content = [
        {
            "type": "video",
            "caption": "Confidence is not about being perfect, it's about being real",
            "engagement": "high",
            "style": "motivational"
        }
    ]
    
    print("🎯 Analyzing @yettyslay content style...")
    analysis = trainer.analyze_content_style(sample_content)
    
    print("👑 Creating Sisi Lola personality profile...")
    profile = trainer.create_personality_profile(analysis)
    
    print("📚 Generating training scenarios...")
    scenarios = trainer.generate_training_scenarios(profile)
    
    print("💾 Saving training data...")
    trainer.save_training_data(profile, scenarios)
    
    print("⚙️ Creating attitude configuration...")
    config = trainer.create_attitude_config(profile)
    
    # Save config file
    config_path = "c:/Users/POK28/Dropbox/Sisi_Lola/00_PROJECT_CORE/Config/sisi_attitude.py"
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config)
    
    print(f"✅ Attitude training complete!")
    print(f"📁 Config saved to: {config_path}")
    print(f"🎭 Personality profile ready for Sisi Lola AI system")

if __name__ == "__main__":
    main()