#!/usr/bin/env python3
"""
SISI LOLA ATTITUDE TRAINING RUNNER
Executes the complete attitude training pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from attitude_trainer import AttitudeTrainer
from tiktok_analyzer import TikTokAnalyzer
import json
from datetime import datetime

def main():
    print("SISI LOLA ATTITUDE TRAINING SYSTEM")
    print("=" * 50)
    
    # Step 1: Analyze @yettyslay content
    print("\nStep 1: Analyzing @yettyslay TikTok style...")
    analyzer = TikTokAnalyzer()
    style_analysis = analyzer.analyze_yettyslay_style()
    training_examples = analyzer.generate_training_examples()
    
    # Step 2: Create Sisi Lola personality profile
    print("\nStep 2: Creating Sisi Lola personality profile...")
    trainer = AttitudeTrainer()
    profile = trainer.create_personality_profile(style_analysis)
    scenarios = trainer.generate_training_scenarios(profile)
    
    # Step 3: Generate attitude configuration
    print("\nStep 3: Generating attitude configuration...")
    config = trainer.create_attitude_config(profile)
    
    # Step 4: Save all training data
    print("\nStep 4: Saving training data...")
    
    # Create Data directory if it doesn't exist (use relative path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'Data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save comprehensive training package
    training_package = {
        "source_channel": "@yettyslay",
        "analysis_date": datetime.now().isoformat(),
        "style_analysis": style_analysis,
        "personality_profile": profile,
        "training_scenarios": scenarios,
        "training_examples": training_examples,
        "implementation_notes": {
            "confidence_level": "High (8.5/10) - Bold but not arrogant",
            "cultural_integration": "Strong Nigerian identity with modern attitude",
            "language_style": "English-Pidgin mix, natural and relatable",
            "empowerment_focus": "Sister-to-sister encouragement and support",
            "authenticity_priority": "Real talk, genuine responses, no fake energy"
        }
    }
    
    # Save training package
    package_path = f"{data_dir}/sisi_lola_attitude_training.json"
    with open(package_path, 'w', encoding='utf-8') as f:
        json.dump(training_package, f, indent=2, ensure_ascii=False)
    
    # Save to database
    trainer.save_training_data(profile, scenarios)
    
    print(f"\nTRAINING COMPLETE!")
    print(f"Training package: {package_path}")
    config_path = os.path.join(script_dir, '..', 'Config', 'sisi_attitude.py')
    print(f"Attitude config: {config_path}")
    print(f"Database updated with training data")
    
    print("\nNEXT STEPS:")
    print("1. Review the attitude configuration file")
    print("2. Test responses using the training examples")
    print("3. Integrate with Sisi Lola AI system")
    print("4. Fine-tune based on user interactions")
    
    print("\nKEY ATTITUDE ELEMENTS:")
    print("• Confidence: High but approachable")
    print("• Language: English-Pidgin mix")
    print("• Style: Empowering sister energy")
    print("• Culture: Proud Nigerian identity")
    print("• Authenticity: Real talk, no pretense")

if __name__ == "__main__":
    main()