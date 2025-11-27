#!/usr/bin/env python3
"""
Test N-ATLaS access using token from .env file
Bypasses the need for huggingface-cli login
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / "sisi_lola_api" / ".env"
load_dotenv(env_path)

print("=" * 60)
print("N-ATLaS ACCESS TEST (Token-Based)")
print("=" * 60)

# Get token from .env
token = os.getenv("HUGGINGFACE_TOKEN")

if not token or token == "your_token_here":
    print("\n[!] HuggingFace token not configured")
    print("\nSteps to configure:")
    print("1. Get token from: https://huggingface.co/settings/tokens")
    print("2. Open: sisi_lola_api/.env")
    print("3. Replace 'your_token_here' with your actual token")
    print("4. Run this script again")
    exit(1)

print(f"\n[✓] Token found: {token[:10]}...{token[-10:]}")

try:
    from huggingface_hub import login, HfApi
    
    # Login with token
    print("\n[→] Logging in to HuggingFace...")
    login(token=token, add_to_git_credential=False)
    print("[✓] Successfully authenticated")
    
    # Test API access
    print("\n[→] Testing API access...")
    api = HfApi()
    user_info = api.whoami(token=token)
    print(f"[✓] Logged in as: {user_info['name']}")
    
    # Check N-ATLaS model access
    model_id = os.getenv("NATLAS_MODEL_ID", "nvidia/N-ATLaS")
    print(f"\n[→] Checking access to {model_id}...")
    
    try:
        model_info = api.model_info(model_id, token=token)
        print(f"[✓] Model accessible: {model_info.modelId}")
        print(f"    Downloads: {model_info.downloads:,}")
        print(f"    Likes: {model_info.likes:,}")
        
        print("\n" + "=" * 60)
        print("SUCCESS! N-ATLaS is ready to use")
        print("=" * 60)
        
    except Exception as e:
        if "401" in str(e) or "403" in str(e):
            print(f"[!] Access denied to {model_id}")
            print("\nRequest access at: https://huggingface.co/nvidia/N-ATLaS")
        else:
            print(f"[X] Error: {e}")
    
except ImportError:
    print("\n[X] huggingface_hub not installed")
    print("\nInstall with: pip install huggingface_hub")
    
except Exception as e:
    print(f"\n[X] Error: {e}")
