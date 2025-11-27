"""
N-ATLaS Access Verification & Quick Start
Verifies HuggingFace authentication and N-ATLaS model access
"""

from huggingface_hub import HfApi, login
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def verify_access():
    """Verify HuggingFace login and N-ATLaS access"""
    
    print("=" * 60)
    print("N-ATLaS ACCESS VERIFICATION")
    print("=" * 60)
    
    try:
        # Check if already logged in
        api = HfApi()
        user_info = api.whoami()
        print(f"[OK] Logged in as: {user_info['name']}")
        print(f"[OK] Email: {user_info.get('email', 'N/A')}")
        
        # Try to access N-ATLaS model
        model_id = "NCAIR1/N-ATLaS"
        print(f"\nChecking access to {model_id}...")
        
        try:
            model_info = api.model_info(model_id)
            print(f"[OK] ACCESS GRANTED to N-ATLaS")
            print(f"[OK] Model ID: {model_info.id}")
            print(f"[OK] Downloads: {model_info.downloads}")
            print("\n" + "=" * 60)
            print("STATUS: READY TO TRAIN")
            print("=" * 60)
            print("\nNext step: python natlas_multilingual_trainer.py")
            return True
            
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                print("[X] ACCESS DENIED to N-ATLaS")
                print("\n" + "=" * 60)
                print("ACTION REQUIRED:")
                print("=" * 60)
                print("1. Request access: https://huggingface.co/NCAIR1/N-ATLaS")
                print("2. Wait for approval email (usually 24-48 hours)")
                print("3. Run this script again")
                return False
            else:
                raise
                
    except Exception as e:
        print("[X] Not logged in to HuggingFace")
        print("\n" + "=" * 60)
        print("ACTION REQUIRED:")
        print("=" * 60)
        print("1. Run: huggingface-cli login")
        print("2. Paste your token from: https://huggingface.co/settings/tokens")
        print("3. Run this script again")
        return False

if __name__ == "__main__":
    verify_access()
