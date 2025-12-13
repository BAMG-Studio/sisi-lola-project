#!/usr/bin/env python3
"""
Upload voice samples to Modal volume for training
"""

import modal
import os
from pathlib import Path

# Create/get the volume
volume = modal.Volume.from_name("sisi-lola-training-data", create_if_missing=True)

def upload_voice_samples():
    """Upload prepared training samples to Modal volume."""
    
    base_dir = Path(__file__).parent
    training_ready = base_dir / "ml_training" / "data" / "voice_samples" / "training_ready"
    speaker_refs = base_dir / "ml_training" / "data" / "voice_samples" / "speaker_reference_candidates"
    
    if not training_ready.exists():
        print(f"❌ Training data not found at {training_ready}")
        print("Run voice_training_preprocessor.py first")
        return
    
    print("=" * 60)
    print("   UPLOADING VOICE SAMPLES TO MODAL")
    print("=" * 60)
    
    # Count files
    wav_files = list(training_ready.rglob("*.wav"))
    ref_files = list(speaker_refs.glob("*.wav")) if speaker_refs.exists() else []
    
    print(f"\nTraining samples: {len(wav_files)}")
    print(f"Speaker references: {len(ref_files)}")
    
    # Create upload function
    @modal.function(volumes={"/data": volume})
    def do_upload():
        import shutil
        
        # Create directories in volume
        os.makedirs("/data/voice_samples/training_ready", exist_ok=True)
        os.makedirs("/data/voice_samples/speaker_reference", exist_ok=True)
        
        print("Volume directories created")
        return {"status": "ready"}
    
    # Alternative: Use modal volume put command
    print("\nTo upload files, run these commands:")
    print("-" * 50)
    
    print(f"\n# Upload training samples")
    print(f"modal volume put sisi-lola-training-data {training_ready} /voice_samples/training_ready")
    
    if ref_files:
        print(f"\n# Upload speaker references")
        print(f"modal volume put sisi-lola-training-data {speaker_refs} /voice_samples/speaker_reference")
    
    print("\n# List volume contents")
    print("modal volume ls sisi-lola-training-data /")

if __name__ == "__main__":
    upload_voice_samples()
