#!/usr/bin/env python3
"""
HuggingFace Login Helper
Simplifies the login process for N-ATLaS access
"""

from huggingface_hub import login
import sys

print("=" * 60)
print("HUGGINGFACE LOGIN")
print("=" * 60)
print("\nGet your token from: https://huggingface.co/settings/tokens")
print("\nPaste your token below (input will be hidden):")

try:
    token = input().strip()
    
    if not token:
        print("\n[X] No token provided. Exiting.")
        sys.exit(1)
    
    print("\nLogging in...")
    login(token=token, add_to_git_credential=True)
    
    print("\n" + "=" * 60)
    print("[✓] Successfully logged in to HuggingFace!")
    print("=" * 60)
    print("\nNext step: Run 'python verify_natlas_access.py'")
    
except KeyboardInterrupt:
    print("\n\n[X] Login cancelled.")
    sys.exit(1)
except Exception as e:
    print(f"\n[X] Login failed: {e}")
    sys.exit(1)
