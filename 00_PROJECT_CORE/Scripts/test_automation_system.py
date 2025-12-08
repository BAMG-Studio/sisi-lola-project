"""
Test Automation System - Verify all components are ready
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

def check_youtube_oauth():
    """Check YouTube OAuth status"""
    token_file = Path(__file__).parent / 'token_youtube.json'
    
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            has_token = 'token' in token_data
            has_refresh = 'refresh_token' in token_data
            
            return {
                "status": "OK" if (has_token and has_refresh) else "INCOMPLETE",
                "file": str(token_file),
                "size": token_file.stat().st_size,
                "has_access_token": has_token,
                "has_refresh_token": has_refresh
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    else:
        return {
            "status": "NOT_FOUND",
            "message": "Run youtube_oauth_complete.py to set up"
        }

def check_openai_key():
    """Check OpenAI API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        return {
            "status": "OK",
            "key_length": len(api_key),
            "key_preview": api_key[:10] + "..." if len(api_key) > 10 else "***"
        }
    else:
        return {
            "status": "NOT_FOUND",
            "message": "Add OPENAI_API_KEY to .env file"
        }

def check_platform_credentials():
    """Check other platform credentials"""
    platforms = {
        "Twitter/X": ["TWITTER_API_KEY", "TWITTER_API_SECRET"],
        "Reddit": ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"],
        "Instagram": ["INSTAGRAM_ACCESS_TOKEN"],
        "TikTok": ["TIKTOK_ACCESS_TOKEN"],
        "Facebook": ["FACEBOOK_ACCESS_TOKEN"]
    }
    
    results = {}
    
    for platform, keys in platforms.items():
        configured = all(os.getenv(key) for key in keys)
        results[platform] = {
            "status": "OK" if configured else "NOT_CONFIGURED",
            "required_keys": keys,
            "configured_keys": [key for key in keys if os.getenv(key)]
        }
    
    return results

def check_file_structure():
    """Check required files exist"""
    base_path = Path(__file__).parent
    
    files = {
        "Content Generator": base_path / "sisi_lola_content_generator.py",
        "Multi-Platform Poster": base_path / "multi_platform_poster.py",
        "Automation Master": base_path / "sisi_lola_automation_master.py",
        "YouTube OAuth": base_path / "youtube_oauth_complete.py",
        "Quick Start Guide": base_path / "AUTOMATION_QUICKSTART.md"
    }
    
    results = {}
    
    for name, filepath in files.items():
        results[name] = {
            "status": "OK" if filepath.exists() else "MISSING",
            "path": str(filepath),
            "size": filepath.stat().st_size if filepath.exists() else 0
        }
    
    return results

def check_output_directories():
    """Check output directories exist"""
    base_path = Path(__file__).parent.parent.parent
    
    dirs = {
        "Content Queue": base_path / "03_MEDIA_ASSETS" / "content_queue",
        "Generated Media": base_path / "03_MEDIA_ASSETS" / "generated",
        "Render Output": base_path / "06_RENDER_OUTPUT"
    }
    
    results = {}
    
    for name, dirpath in dirs.items():
        if dirpath.exists():
            file_count = len(list(dirpath.glob("*")))
            results[name] = {
                "status": "OK",
                "path": str(dirpath),
                "file_count": file_count
            }
        else:
            results[name] = {
                "status": "MISSING",
                "path": str(dirpath),
                "action": "Will be created automatically"
            }
    
    return results

def main():
    """Run all checks"""
    
    print("="*70)
    print("SISI LOLA AUTOMATION SYSTEM - STATUS CHECK")
    print("="*70)
    
    # YouTube OAuth
    print("\n[1] YOUTUBE OAUTH")
    print("-" * 70)
    youtube_status = check_youtube_oauth()
    print(f"Status: {youtube_status['status']}")
    if youtube_status['status'] == 'OK':
        print(f"  Token File: {youtube_status['file']}")
        print(f"  File Size: {youtube_status['size']} bytes")
        print(f"  Access Token: {'Yes' if youtube_status['has_access_token'] else 'No'}")
        print(f"  Refresh Token: {'Yes' if youtube_status['has_refresh_token'] else 'No'}")
    else:
        print(f"  Message: {youtube_status.get('message', youtube_status.get('error', 'Unknown'))}")
    
    # OpenAI
    print("\n[2] OPENAI API")
    print("-" * 70)
    openai_status = check_openai_key()
    print(f"Status: {openai_status['status']}")
    if openai_status['status'] == 'OK':
        print(f"  Key Preview: {openai_status['key_preview']}")
    else:
        print(f"  Message: {openai_status['message']}")
    
    # Platform Credentials
    print("\n[3] PLATFORM CREDENTIALS")
    print("-" * 70)
    platform_status = check_platform_credentials()
    for platform, status in platform_status.items():
        symbol = "[OK]" if status['status'] == 'OK' else "[--]"
        print(f"{symbol} {platform:15} {status['status']}")
        if status['configured_keys']:
            print(f"     Configured: {', '.join(status['configured_keys'])}")
    
    # File Structure
    print("\n[4] CORE FILES")
    print("-" * 70)
    file_status = check_file_structure()
    for name, status in file_status.items():
        symbol = "[OK]" if status['status'] == 'OK' else "[!!]"
        size_kb = status['size'] / 1024 if status['size'] > 0 else 0
        print(f"{symbol} {name:25} {status['status']:10} ({size_kb:.1f} KB)")
    
    # Output Directories
    print("\n[5] OUTPUT DIRECTORIES")
    print("-" * 70)
    dir_status = check_output_directories()
    for name, status in dir_status.items():
        symbol = "[OK]" if status['status'] == 'OK' else "[--]"
        if status['status'] == 'OK':
            print(f"{symbol} {name:20} {status['file_count']} files")
        else:
            print(f"{symbol} {name:20} {status['action']}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    youtube_ok = youtube_status['status'] == 'OK'
    openai_ok = openai_status['status'] == 'OK'
    files_ok = all(s['status'] == 'OK' for s in file_status.values())
    
    print(f"YouTube OAuth:     {'[OK]' if youtube_ok else '[!!] SETUP REQUIRED'}")
    print(f"OpenAI API:        {'[OK]' if openai_ok else '[!!] KEY REQUIRED'}")
    print(f"Core Files:        {'[OK]' if files_ok else '[!!] FILES MISSING'}")
    
    platforms_configured = sum(1 for s in platform_status.values() if s['status'] == 'OK')
    print(f"Platforms Ready:   {platforms_configured}/5")
    
    print("\n" + "="*70)
    
    if youtube_ok and openai_ok and files_ok:
        print("STATUS: [READY] System is ready for content generation and posting!")
        print("\nNEXT STEPS:")
        print("  1. Run: python sisi_lola_content_generator.py")
        print("  2. Run: python sisi_lola_automation_master.py")
    elif youtube_ok and files_ok:
        print("STATUS: [PARTIAL] YouTube ready, but OpenAI key needed for content generation")
        print("\nNEXT STEPS:")
        print("  1. Add OPENAI_API_KEY to 00_PROJECT_CORE/.env")
        print("  2. Run: python sisi_lola_content_generator.py")
    else:
        print("STATUS: [SETUP REQUIRED] Complete setup steps below")
        print("\nNEXT STEPS:")
        if not youtube_ok:
            print("  1. Run: python youtube_oauth_complete.py")
        if not openai_ok:
            print("  2. Add OPENAI_API_KEY to 00_PROJECT_CORE/.env")
        print("  3. Run this test again: python test_automation_system.py")
    
    print("="*70)

if __name__ == "__main__":
    main()
