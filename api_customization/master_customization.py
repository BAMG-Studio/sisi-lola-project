#!/usr/bin/env python3
"""
Master API Customization Script
Orchestrates all customization tasks
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_path, description):
    """Run a customization script"""
    print("\n" + "=" * 60)
    print(f"RUNNING: {description}")
    print("=" * 60)
    
    result = subprocess.run(['python', script_path], capture_output=False)
    
    if result.returncode == 0:
        print(f"✓ {description} completed successfully")
        return True
    else:
        print(f"✗ {description} failed")
        return False

def main():
    print("=" * 60)
    print("SISI LOLA - API CUSTOMIZATION MASTER")
    print("=" * 60)
    print("\nThis will customize all API services for Sisi Lola:")
    print("1. ElevenLabs Voice Cloning")
    print("2. HeyGen Avatar Creation")
    print("3. OpenAI GPT Fine-tuning")
    print("4. Cohere Fine-tuning")
    print("5. Prompt Engineering Setup")
    
    response = input("\nProceed with full customization? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("Customization cancelled")
        return 0
    
    results = {}
    
    # 1. Voice Cloning
    results['voice'] = run_script(
        'api_customization/voice_cloning/elevenlabs_voice_clone.py',
        'ElevenLabs Voice Cloning'
    )
    
    # 2. Avatar Creation
    results['avatar'] = run_script(
        'api_customization/avatar_creation/heygen_avatar_create.py',
        'HeyGen Avatar Creation'
    )
    
    # 3. OpenAI Fine-tuning
    results['openai'] = run_script(
        'api_customization/fine_tuning/openai_finetune.py',
        'OpenAI GPT Fine-tuning'
    )
    
    # 4. Cohere Fine-tuning
    results['cohere'] = run_script(
        'api_customization/fine_tuning/cohere_finetune.py',
        'Cohere Fine-tuning'
    )
    
    # 5. Prompt Engineering
    results['prompts'] = run_script(
        'api_customization/prompt_engineering/prompt_templates.py',
        'Prompt Engineering Setup'
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("CUSTOMIZATION SUMMARY")
    print("=" * 60)
    
    for task, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{task.upper()}: {status}")
    
    total = len(results)
    successful = sum(results.values())
    
    print(f"\nCompleted: {successful}/{total} tasks")
    
    if successful == total:
        print("\n🎉 All customizations completed successfully!")
        print("\nNext steps:")
        print("1. Test custom voice with ElevenLabs API")
        print("2. Test custom avatar with HeyGen API")
        print("3. Test fine-tuned models")
        print("4. Update API calls to use custom IDs")
        print("5. Deploy to production")
    else:
        print("\n⚠️ Some customizations failed. Check logs above.")
    
    return 0 if successful == total else 1

if __name__ == '__main__':
    sys.exit(main())
