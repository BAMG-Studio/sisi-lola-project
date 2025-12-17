"""
Test Voice Generation - Generate sample audio with Nigerian phrases
Uses the trained XTTS-v2 model with Sisi Lola's voice
"""

import modal
import os
from pathlib import Path

app = modal.App("sisi-lola-voice-test")

# Use the same voice image from training
voice_image = modal.Image.debian_slim(python_version="3.10").apt_install(
    "espeak-ng",
    "ffmpeg",
).pip_install(
    "packaging",
).pip_install(
    "torch==2.3.1",
    "torchaudio==2.3.1",
    "transformers==4.33.3",
    "accelerate>=0.27.0",
    "huggingface_hub>=0.22.0",
    "librosa>=0.10.0",
    "soundfile",
    "pydub",
    "numpy<2.0",
    "pyyaml",
    "tqdm",
    "rich",
).pip_install(
    "TTS>=0.22.0",
    "phonemizer",
    "unidecode",
).env({
    "COQUI_TOS_AGREED": "1",
})

# Volumes
model_volume = modal.Volume.from_name("sisi-lola-models-v2", create_if_missing=True)
data_volume = modal.Volume.from_name("sisi-lola-training-data", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface-secret")

# Nigerian phrases to test
NIGERIAN_PHRASES = [
    # Pidgin English
    ("pidgin_greeting", "How you dey? I hope say everything dey alright for your side.", "en"),
    ("pidgin_welcome", "You are very welcome to this program. Make yourself comfortable.", "en"),
    ("pidgin_excited", "Chai! This one na correct gist! I dey very happy to share am with you.", "en"),
    
    # Standard English with Nigerian flavor
    ("english_intro", "Hello everyone! I am Sisi Lola, your virtual Nigerian host. Welcome to the show!", "en"),
    ("english_culture", "Nigerian culture is rich and diverse. From the colorful festivals to the delicious jollof rice.", "en"),
    ("english_music", "Afrobeats is taking over the world! From Burna Boy to Wizkid, Nigerian music is everywhere.", "en"),
    
    # Mixed code-switching
    ("mixed_greeting", "Good morning o! How una dey today? I hope say una ready for today's episode.", "en"),
    ("mixed_farewell", "Thank you for watching! Make una no forget to subscribe. See you next time, bye bye!", "en"),
]


@app.function(
    image=voice_image,
    gpu="A100",
    timeout=1800,
    secrets=[hf_secret],
    volumes={"/models": model_volume, "/data": data_volume},
)
def generate_voice_samples():
    """Generate voice samples with Nigerian phrases."""
    import torch
    from TTS.api import TTS
    from pathlib import Path
    import json
    from datetime import datetime
    
    print("=" * 70)
    print("🎤 SISI LOLA VOICE TESTING")
    print("=" * 70)
    
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    
    # Output directory for test samples
    output_dir = Path("/models/voice_samples_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load XTTS-v2
    print("\n📦 Loading XTTS-v2 model...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    
    # Find reference audio
    speaker_ref_dir = Path("/data/voice_samples/speaker_reference")
    reference_files = list(speaker_ref_dir.glob("*.wav")) if speaker_ref_dir.exists() else []
    
    if not reference_files:
        return {"status": "error", "message": "No reference audio files found"}
    
    # Use first reference
    reference_audio = str(reference_files[0])
    print(f"📎 Using reference: {reference_audio}")
    
    # Generate all samples
    results = []
    print(f"\n🎙️ Generating {len(NIGERIAN_PHRASES)} voice samples...\n")
    
    for name, text, lang in NIGERIAN_PHRASES:
        print(f"  🔊 {name}: {text[:50]}...")
        output_file = output_dir / f"{name}.wav"
        
        try:
            tts.tts_to_file(
                text=text,
                file_path=str(output_file),
                speaker_wav=reference_audio,
                language=lang,
            )
            results.append({
                "name": name,
                "text": text,
                "language": lang,
                "file": str(output_file),
                "status": "success"
            })
            print(f"     ✅ Generated: {output_file.name}")
        except Exception as e:
            results.append({
                "name": name,
                "text": text,
                "error": str(e),
                "status": "error"
            })
            print(f"     ❌ Error: {e}")
    
    # Save manifest
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "reference_audio": reference_audio,
        "samples": results
    }
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Commit volume
    model_volume.commit()
    
    print("\n" + "=" * 70)
    print("🎤 VOICE TESTING COMPLETE")
    print("=" * 70)
    print(f"✅ Generated {sum(1 for r in results if r['status'] == 'success')} samples")
    print(f"📁 Output directory: {output_dir}")
    
    return {
        "status": "success",
        "samples_generated": sum(1 for r in results if r['status'] == 'success'),
        "output_dir": str(output_dir),
        "manifest": manifest
    }


@app.function(
    image=voice_image,
    timeout=300,
    volumes={"/models": model_volume},
)
def download_audio_samples():
    """Download generated audio samples as bytes."""
    from pathlib import Path
    import base64
    
    output_dir = Path("/models/voice_samples_test")
    voice_xtts_dir = Path("/models/voice_xtts")
    
    files = {}
    
    # Get test samples
    if output_dir.exists():
        for wav_file in output_dir.glob("*.wav"):
            with open(wav_file, "rb") as f:
                files[wav_file.name] = base64.b64encode(f.read()).decode()
    
    # Get the original voice_test.wav
    original_test = voice_xtts_dir / "voice_test.wav"
    if original_test.exists():
        with open(original_test, "rb") as f:
            files["voice_test_original.wav"] = base64.b64encode(f.read()).decode()
    
    return files


@app.local_entrypoint()
def main():
    """Run voice generation and download samples."""
    import base64
    from pathlib import Path
    
    print("\n🚀 Starting voice sample generation...\n")
    
    # Generate samples
    result = generate_voice_samples.remote()
    print(f"\n📊 Result: {result}")
    
    if result.get("status") == "success":
        print("\n📥 Downloading audio samples...")
        
        # Download all audio files
        audio_files = download_audio_samples.remote()
        
        # Save locally
        local_output = Path("voice_samples_output")
        local_output.mkdir(exist_ok=True)
        
        for filename, b64_data in audio_files.items():
            output_path = local_output / filename
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64_data))
            print(f"  ✅ Saved: {output_path}")
        
        print(f"\n🎉 All samples saved to: {local_output.absolute()}")
