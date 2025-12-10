#!/usr/bin/env python3
"""
GITHUB SECRETS SETUP HELPER
============================
Displays instructions for setting up required GitHub secrets
for the unified training pipeline.

Run: python setup_github_secrets.py
"""

import os
import subprocess
import sys

def check_local_env():
    """Check what credentials are available locally"""
    print("=" * 60)
    print("🔍 CHECKING LOCAL ENVIRONMENT")
    print("=" * 60)
    print()
    
    secrets = {
        "HF_TOKEN": os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN"),
        "MODAL_TOKEN_ID": os.environ.get("MODAL_TOKEN_ID"),
        "MODAL_TOKEN_SECRET": os.environ.get("MODAL_TOKEN_SECRET"),
    }
    
    for name, value in secrets.items():
        if value:
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {name}: {masked}")
        else:
            print(f"  ❌ {name}: Not set")
    
    print()
    return secrets


def get_hf_token():
    """Try to get HuggingFace token from various sources"""
    # Check environment
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return token
    
    # Check huggingface-cli config
    try:
        from huggingface_hub import HfFolder
        token = HfFolder.get_token()
        if token:
            return token
    except:
        pass
    
    # Check ~/.huggingface/token
    token_path = os.path.expanduser("~/.huggingface/token")
    if os.path.exists(token_path):
        with open(token_path) as f:
            return f.read().strip()
    
    # Windows path
    token_path = os.path.expanduser("~/.cache/huggingface/token")
    if os.path.exists(token_path):
        with open(token_path) as f:
            return f.read().strip()
    
    return None


def print_setup_instructions():
    """Print instructions for setting up GitHub secrets"""
    print("=" * 60)
    print("📋 GITHUB SECRETS SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("Go to your GitHub repository settings:")
    print("  https://github.com/BAMG-Studio/sisi-lola-project/settings/secrets/actions")
    print()
    print("Add the following secrets:")
    print()
    print("-" * 60)
    
    # HF_TOKEN
    print("1️⃣  HF_TOKEN")
    print("   Description: HuggingFace API token for model uploads")
    print("   Get it from: https://huggingface.co/settings/tokens")
    print("   Permissions needed: Write access to repos")
    hf_token = get_hf_token()
    if hf_token:
        print(f"   Your current token: {hf_token[:8]}...{hf_token[-4:]}")
    print()
    
    # MODAL_TOKEN_ID
    print("2️⃣  MODAL_TOKEN_ID")
    print("   Description: Modal.com token ID for GPU training")
    print("   Get it from: https://modal.com/settings")
    print("   Click 'New Token' and copy the Token ID")
    print()
    
    # MODAL_TOKEN_SECRET
    print("3️⃣  MODAL_TOKEN_SECRET")
    print("   Description: Modal.com token secret for GPU training")
    print("   Get it from: Same page as MODAL_TOKEN_ID")
    print("   Copy the Token Secret (shown only once!)")
    print()
    
    print("-" * 60)
    print()
    print("📌 QUICK SETUP COMMANDS")
    print()
    print("If you have GitHub CLI installed:")
    print()
    
    if hf_token:
        # Escape for shell
        print(f'  gh secret set HF_TOKEN --body "{hf_token}"')
    else:
        print('  gh secret set HF_TOKEN --body "your_hf_token_here"')
    
    print('  gh secret set MODAL_TOKEN_ID --body "your_modal_token_id"')
    print('  gh secret set MODAL_TOKEN_SECRET --body "your_modal_token_secret"')
    print()


def check_modal_setup():
    """Check if Modal is configured"""
    print("=" * 60)
    print("🚀 MODAL.COM SETUP")
    print("=" * 60)
    print()
    
    # Check if modal CLI is installed
    try:
        result = subprocess.run(["modal", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Modal CLI installed: {result.stdout.strip()}")
        else:
            print("  ❌ Modal CLI not working")
    except FileNotFoundError:
        print("  ❌ Modal CLI not installed")
        print()
        print("  Install with: pip install modal")
        print("  Then run: modal token new")
        return
    
    # Check modal token
    try:
        result = subprocess.run(["modal", "token", "show"], capture_output=True, text=True)
        if "Token ID:" in result.stdout:
            print("  ✅ Modal token configured")
            # Extract token ID
            for line in result.stdout.split("\n"):
                if "Token ID:" in line:
                    print(f"  {line.strip()}")
        else:
            print("  ❌ Modal token not configured")
            print("  Run: modal token new")
    except:
        print("  ⚠️ Could not check modal token")
    
    print()


def main():
    print()
    print("🔧 SISI LOLA UNIFIED TRAINING - SECRETS SETUP")
    print("=" * 60)
    print()
    
    check_local_env()
    check_modal_setup()
    print_setup_instructions()
    
    print("=" * 60)
    print("✨ NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Add the secrets to GitHub (instructions above)")
    print("2. Add a speaker reference WAV file:")
    print("   ml_training/data/voice_samples/speaker_reference.wav")
    print("3. Trigger a workflow run:")
    print("   - Go to GitHub Actions tab")
    print("   - Select 'Unified Training Pipeline'")
    print("   - Click 'Run workflow'")
    print()
    print("Or wait for the automatic run (every 2 days at 2 AM UTC)")
    print()


if __name__ == "__main__":
    main()
