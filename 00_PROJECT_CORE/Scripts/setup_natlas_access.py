#!/usr/bin/env python3
"""
Setup N-ATLaS Model Access
Authenticate and download the model for Sisi Lola training
"""
import os
import subprocess
from pathlib import Path

def setup_huggingface_auth():
    """Setup HuggingFace authentication"""
    print("=" * 60)
    print("N-ATLaS MODEL ACCESS SETUP")
    print("=" * 60)
    
    print("\n[STEP 1] HuggingFace Authentication")
    print("You need a HuggingFace account with access to N-ATLaS model")
    print("\nInstructions:")
    print("1. Go to: https://huggingface.co/NCAIR1/N-ATLaS")
    print("2. Click 'Request Access' if not already granted")
    print("3. Get your access token from: https://huggingface.co/settings/tokens")
    print("4. Run: huggingface-cli login")
    print("5. Paste your token when prompted")
    
    print("\n[STEP 2] Clone Repository")
    print("After authentication, run:")
    print("  git clone https://huggingface.co/NCAIR1/N-ATLaS")
    
    print("\n[STEP 3] Use Model")
    print("Once cloned, the model will be available locally")
    
    # Check if huggingface-cli is installed
    try:
        result = subprocess.run(['huggingface-cli', '--version'], 
                              capture_output=True, text=True)
        print(f"\n[OK] HuggingFace CLI installed: {result.stdout.strip()}")
    except FileNotFoundError:
        print("\n[INSTALL] Installing HuggingFace CLI...")
        subprocess.run(['pip', 'install', 'huggingface_hub[cli]'])
    
    print("\n" + "=" * 60)
    print("Run: huggingface-cli login")
    print("=" * 60)

if __name__ == '__main__':
    setup_huggingface_auth()
