#!/usr/bin/env python3
"""Push trained models to HuggingFace Hub"""
import os
import sys
from pathlib import Path
from datetime import datetime

def load_env():
    """Load environment variables from .env file"""
    env_path = Path("sisi_lola_api/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

def main():
    # Load environment
    load_env()
    
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ No HuggingFace token found in environment")
        print("Please set HF_TOKEN in sisi_lola_api/.env")
        sys.exit(1)
    
    print(f"Token found: {token[:10]}...")
    
    from huggingface_hub import HfApi, login
    
    # Login
    print("Logging in to HuggingFace...")
    login(token=token)
    api = HfApi()
    user = api.whoami()
    print(f"✅ Logged in as: {user['name']}")
    
    # Push brain adapter
    brain_path = Path("ml_training/checkpoints/natlas_lora")
    if brain_path.exists():
        print("\n📤 Pushing brain adapter to HuggingFace...")
        # Use personal namespace since org permissions may be limited
        repo_id = f"{user['name']}/sisi-lola-brain"
        
        try:
            api.create_repo(repo_id, exist_ok=True, private=False)
            api.upload_folder(
                folder_path=str(brain_path),
                repo_id=repo_id,
                commit_message=f"Upload brain adapter - {datetime.now().strftime('%Y%m%d')}"
            )
            print(f"✅ Brain adapter pushed to: https://huggingface.co/{repo_id}")
        except Exception as e:
            print(f"❌ Failed to push brain adapter: {e}")
    else:
        print(f"⚠️ Brain checkpoint not found at {brain_path}")
    
    # Push voice profile
    voice_path = Path("ml_training/checkpoints/xtts_sisi_lola")
    if voice_path.exists():
        print("\n📤 Pushing voice profile to HuggingFace...")
        repo_id = f"{user['name']}/sisi-lola-voice"
        
        try:
            api.create_repo(repo_id, exist_ok=True, private=False)
            api.upload_folder(
                folder_path=str(voice_path),
                repo_id=repo_id,
                commit_message=f"Upload voice profile - {datetime.now().strftime('%Y%m%d')}"
            )
            print(f"✅ Voice profile pushed to: https://huggingface.co/{repo_id}")
        except Exception as e:
            print(f"❌ Failed to push voice profile: {e}")
    else:
        print(f"⚠️ Voice checkpoint not found at {voice_path}")
    
    print("\n🎉 Push complete!")

if __name__ == "__main__":
    main()
