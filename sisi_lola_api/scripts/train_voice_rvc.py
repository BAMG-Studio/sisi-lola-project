#!/usr/bin/env python3
"""
=============================================================================
🎙️ REPLICATE RVC VOICE CLONING TRAINER
=============================================================================
Trains a voice clone using Replicate's RVC (Realistic Voice Cloning) model.

Model: zsxkib/realistic-voice-cloning
Docs: https://replicate.com/zsxkib/realistic-voice-cloning

Run: python -m sisi_lola_api.scripts.train_voice_rvc
=============================================================================
"""

import os
import sys
import json
import base64
import time
import httpx
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_SAMPLES_ROOT = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples"
SELECTED_FOLDER = VOICE_SAMPLES_ROOT / "selected_best"
OUTPUT_FOLDER = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_models"

# Replicate API
REPLICATE_API_TOKEN = "r8_V7hyzBNwBGzhQax9O43wpb3CqInl5g22WaIhE"

# Create output folder
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def get_audio_files(folder: Path, limit: int = 30) -> list:
    """Get audio files from folder"""
    files = list(folder.glob("*.wav"))[:limit]
    return files


def file_to_base64(file_path: Path) -> str:
    """Convert file to base64 data URI"""
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:audio/wav;base64,{data}"


def combine_audio_files(files: list, output_path: Path) -> Path:
    """
    Combine multiple WAV files into one for training.
    Uses simple concatenation (assumes same format).
    """
    import wave
    
    if not files:
        return None
    
    # Read first file to get parameters
    with wave.open(str(files[0]), 'rb') as first:
        params = first.getparams()
    
    # Combine all files
    with wave.open(str(output_path), 'wb') as output:
        output.setparams(params)
        
        for wav_file in files:
            try:
                with wave.open(str(wav_file), 'rb') as w:
                    output.writeframes(w.readframes(w.getnframes()))
            except Exception as e:
                print(f"  ⚠️ Skipping {wav_file.name}: {e}")
    
    return output_path


def train_rvc_voice():
    """Train RVC voice model on Replicate"""
    
    print("=" * 60)
    print("🎙️ REPLICATE RVC VOICE CLONING")
    print("=" * 60)
    
    # Check for samples
    audio_files = get_audio_files(SELECTED_FOLDER, limit=30)
    
    if not audio_files:
        print("\n❌ No audio files found in selected_best/")
        print("   Run: python -m sisi_lola_api.scripts.select_best_voices")
        return
    
    print(f"\n📁 Found {len(audio_files)} audio samples")
    
    # Combine audio files into one training file
    print("\n🔧 Combining audio samples for training...")
    combined_path = OUTPUT_FOLDER / "sisi_lola_training_audio.wav"
    combine_audio_files(audio_files, combined_path)
    
    # Get file size
    file_size_mb = combined_path.stat().st_size / (1024 * 1024)
    print(f"   📦 Combined file: {file_size_mb:.1f} MB")
    
    # Check if file is too large (Replicate has limits)
    if file_size_mb > 50:
        print("   ⚠️ File too large, using fewer samples...")
        audio_files = audio_files[:15]
        combine_audio_files(audio_files, combined_path)
        file_size_mb = combined_path.stat().st_size / (1024 * 1024)
        print(f"   📦 Reduced to: {file_size_mb:.1f} MB")
    
    # For RVC, we typically need to use their training endpoint
    # But first, let's test with their inference endpoint using the audio
    
    print("\n" + "=" * 60)
    print("🚀 UPLOADING TO REPLICATE...")
    print("=" * 60)
    
    # Convert to base64 for API
    print("\n📤 Encoding audio for upload...")
    audio_base64 = file_to_base64(combined_path)
    
    # Create Replicate prediction
    # Note: zsxkib/realistic-voice-cloning is for INFERENCE
    # For TRAINING, we might need a different approach
    
    # Let's check what models are available for voice cloning training
    print("\n📡 Connecting to Replicate API...")
    
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # For now, let's use the TTS approach with voice reference
    # This uses XTTS-v2 which can clone from a reference audio
    
    print("\n🎯 Using XTTS-v2 for voice cloning (6-second clone)...")
    
    # XTTS-v2 can clone voice from just 6 seconds of audio!
    # Model: lucataco/xtts-v2
    
    # Get a good 6-second sample (take first sample)
    if audio_files:
        reference_audio = audio_files[0]
        reference_base64 = file_to_base64(reference_audio)
        
        # Test the clone with a sample text
        test_text = "Hello my people! Na Sisi Lola dey talk to you. How you dey today? Make we yarn about wetin dey happen for Naija!"
        
        payload = {
            "version": "684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
            "input": {
                "text": test_text,
                "speaker": reference_base64,
                "language": "en"
            }
        }
        
        print(f"\n📝 Test text: \"{test_text[:50]}...\"")
        print("\n⏳ Sending to Replicate (this may take 1-3 minutes)...")
        
        try:
            response = httpx.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 201:
                result = response.json()
                prediction_id = result.get("id")
                print(f"\n✅ Prediction created: {prediction_id}")
                print("   Status: Processing...")
                
                # Poll for completion
                poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                
                for i in range(60):  # Max 5 minutes
                    time.sleep(5)
                    poll_response = httpx.get(poll_url, headers=headers)
                    status_data = poll_response.json()
                    status = status_data.get("status")
                    
                    print(f"   [{i*5}s] Status: {status}")
                    
                    if status == "succeeded":
                        output_url = status_data.get("output")
                        print(f"\n🎉 SUCCESS!")
                        print(f"   🎵 Audio URL: {output_url}")
                        
                        # Download the audio
                        if output_url:
                            audio_response = httpx.get(output_url)
                            output_file = OUTPUT_FOLDER / f"sisi_lola_voice_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                            with open(output_file, "wb") as f:
                                f.write(audio_response.content)
                            print(f"   💾 Saved to: {output_file}")
                        break
                        
                    elif status == "failed":
                        error = status_data.get("error")
                        print(f"\n❌ Failed: {error}")
                        break
                        
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"\n❌ Request error: {e}")
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS")
    print("=" * 60)
    print("""
If the test audio sounds good:
1. ✅ Sisi Lola voice is ready!
2. Use this voice for video generation

If you want to try RVC training manually:
1. Go to: https://replicate.com/zsxkib/realistic-voice-cloning
2. Upload the combined audio file
3. Train the model
4. Get the model ID for inference
""")
    
    print("\n💾 Files created:")
    print(f"   📁 Training audio: {combined_path}")
    print(f"   📁 Output folder: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    train_rvc_voice()
