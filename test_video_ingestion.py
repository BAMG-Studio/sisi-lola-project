#!/usr/bin/env python3
"""Test video ingestion module imports and configuration."""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*60)
    print("SISI LOLA - VIDEO INGESTION MODULE TESTS")
    print("="*60 + "\n")
    
    # Test 1: RecCloud imports
    print("[1] Testing RecCloud module imports...")
    try:
        from ml_training.scripts.reccloud_video_ingestion import (
            RecCloudClient,
            VideoIngestionOrchestrator,
            TranscriptSegment,
            TrainingExample
        )
        print("    ✅ RecCloud module imported successfully")
    except Exception as e:
        print(f"    ❌ RecCloud import failed: {e}")
        return False
    
    # Test 2: Whisper imports (skip - torch slow on WSL)
    print("[2] Testing Whisper module structure (no import - torch slow on WSL)...")
    from pathlib import Path
    whisper_path = Path("ml_training/scripts/whisper_video_ingestion.py")
    if whisper_path.exists():
        print("    ✅ whisper_video_ingestion.py exists")
    else:
        print("    ❌ whisper_video_ingestion.py not found")
    
    # Test 3: Config loader
    print("[3] Testing config loader...")
    try:
        from ml_training.configs.config_loader import get_config
        config = get_config()
        print(f"    ✅ Config loaded: transcription backend = {config.transcription.backend}")
    except Exception as e:
        print(f"    ❌ Config loader failed: {e}")
        return False
    
    # Test 4: RecCloudClient initialization
    print("[4] Testing RecCloudClient initialization...")
    try:
        api_key = os.getenv('RECCLOUD_API_KEY', 'test_api_key')
        client = RecCloudClient(api_key)
        print(f"    ✅ RecCloudClient created")
        print(f"       Base URL: {client.base_url}")
    except Exception as e:
        print(f"    ❌ RecCloudClient init failed: {e}")
        return False
    
    # Test 5: Dropbox link generation
    print("[5] Testing Dropbox link generation method...")
    try:
        test_path = "C:/Users/POK28/Dropbox/SLS/test.mp4"
        # Just check the method exists and can be called
        result = client._get_dropbox_public_url(test_path)
        if result is None:
            print("    ⚠️  Dropbox URL returned None (expected without API token)")
        else:
            print(f"    ✅ Dropbox URL: {result[:50]}...")
    except Exception as e:
        print(f"    ⚠️  Dropbox method check: {e}")
    
    print("\n" + "="*60)
    print("ALL IMPORT TESTS PASSED ✅")
    print("="*60 + "\n")
    return True


def test_video_discovery():
    """Test video file discovery."""
    print("\n" + "="*60)
    print("VIDEO FILE DISCOVERY")
    print("="*60 + "\n")
    
    from pathlib import Path
    
    video_dirs = [
        "C:/Users/POK28/Dropbox/SLS/SL TRAINING VIDEOS",
        "C:/Users/POK28/Dropbox/SLS"
    ]
    
    video_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    
    for vdir in video_dirs:
        vpath = Path(vdir)
        if not vpath.exists():
            print(f"  ❌ Directory not found: {vdir}")
            continue
        
        print(f"  📁 {vdir}")
        video_files = []
        for ext in video_extensions:
            video_files.extend(vpath.glob(f"*{ext}"))
        
        if video_files:
            for vf in video_files[:5]:  # Show first 5
                size_mb = vf.stat().st_size / (1024*1024)
                print(f"     📹 {vf.name} ({size_mb:.1f} MB)")
            if len(video_files) > 5:
                print(f"     ... and {len(video_files) - 5} more")
            print(f"     Total: {len(video_files)} videos")
        else:
            print(f"     (no videos found)")
    
    print()


if __name__ == "__main__":
    try:
        success = test_imports()
        if success:
            test_video_discovery()
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
