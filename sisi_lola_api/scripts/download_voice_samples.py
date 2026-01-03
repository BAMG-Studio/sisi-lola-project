#!/usr/bin/env python3
"""
=============================================================================
🇳🇬 NIGERIAN VOICE SAMPLES DOWNLOADER & ORGANIZER
=============================================================================
Downloads and organizes authentic Nigerian voice samples for voice cloning.

Languages:
1. Yorunglish (Nigerian Pidgin English) - PRIORITY! Sisi Lola's default
2. Yoruba - Native language
3. Igbo - Eastern Nigeria
4. Hausa - Northern Nigeria

Sources:
- OpenSLR (Google's Speech Resources)
- Hugging Face Datasets

Run: python -m sisi_lola_api.scripts.download_voice_samples
=============================================================================
"""

import os
import subprocess
import shutil
from pathlib import Path
import urllib.request
import zipfile
import json

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_SAMPLES_ROOT = PROJECT_ROOT / "03_MEDIA_ASSETS" / "voice_samples"

# Create organized folder structure
FOLDERS = {
    "yorunglish_pidgin": "Yorunglish/Nigerian Pidgin English - Sisi Lola's DEFAULT voice",
    "yoruba_female": "Yoruba Female - Native Yoruba language",
    "yoruba_male": "Yoruba Male - For reference",
    "igbo_female": "Igbo Female - Eastern Nigeria",
    "igbo_male": "Igbo Male - For reference",
    "hausa_female": "Hausa Female - Northern Nigeria",
    "hausa_male": "Hausa Male - For reference",
    "selected_best": "SELECTED BEST SAMPLES - Ready for voice cloning",
}

# Download sources
DOWNLOADS = {
    # Yoruba Female (already downloaded)
    "yoruba_female": {
        "url": "https://openslr.trmal.net/resources/86/yo_ng_female.zip",
        "filename": "yo_ng_female.zip",
        "description": "Yoruba Female - OpenSLR SLR86"
    },
    # Yoruba Male
    "yoruba_male": {
        "url": "https://openslr.trmal.net/resources/86/yo_ng_male.zip",
        "filename": "yo_ng_male.zip",
        "description": "Yoruba Male - OpenSLR SLR86"
    },
    # Igbo Female (OpenSLR SLR70)
    "igbo_female": {
        "url": "https://openslr.trmal.net/resources/70/ig_ng_female.zip",
        "filename": "ig_ng_female.zip",
        "description": "Igbo Female - OpenSLR SLR70"
    },
    # Igbo Male
    "igbo_male": {
        "url": "https://openslr.trmal.net/resources/70/ig_ng_male.zip",
        "filename": "ig_ng_male.zip",
        "description": "Igbo Male - OpenSLR SLR70"
    },
    # Hausa Female (OpenSLR SLR65)
    "hausa_female": {
        "url": "https://openslr.trmal.net/resources/65/ha_ng_female.zip",
        "filename": "ha_ng_female.zip",
        "description": "Hausa Female - OpenSLR SLR65"
    },
    # Hausa Male
    "hausa_male": {
        "url": "https://openslr.trmal.net/resources/65/ha_ng_male.zip",
        "filename": "ha_ng_male.zip",
        "description": "Hausa Male - OpenSLR SLR65"
    },
}


def create_folder_structure():
    """Create organized folder structure"""
    print("\n📁 Creating organized folder structure...")
    
    for folder_name, description in FOLDERS.items():
        folder_path = VOICE_SAMPLES_ROOT / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Create README in each folder
        readme_path = folder_path / "README.txt"
        if not readme_path.exists():
            with open(readme_path, "w") as f:
                f.write(f"# {folder_name.upper()}\n\n")
                f.write(f"Description: {description}\n\n")
                f.write("Contents:\n")
                f.write("- .wav files: Audio samples\n")
                f.write("- Transcriptions may be in TSV files\n")
        
        print(f"  ✅ {folder_name}/")
    
    print(f"\n📍 Voice samples location: {VOICE_SAMPLES_ROOT}")


def download_file(url: str, dest_path: Path, description: str):
    """Download a file with progress indicator"""
    if dest_path.exists():
        print(f"  ⏭️ Already exists: {dest_path.name}")
        return True
    
    print(f"  📥 Downloading: {description}")
    print(f"     URL: {url}")
    
    try:
        # Use wget for better progress
        subprocess.run(
            ["wget", "-q", "--show-progress", "-O", str(dest_path), url],
            check=True
        )
        print(f"  ✅ Downloaded: {dest_path.name}")
        return True
    except subprocess.CalledProcessError:
        print(f"  ❌ Failed to download: {dest_path.name}")
        return False
    except FileNotFoundError:
        # wget not available, use urllib
        print(f"  📥 Using urllib (no progress bar)...")
        try:
            urllib.request.urlretrieve(url, dest_path)
            print(f"  ✅ Downloaded: {dest_path.name}")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False


def extract_zip(zip_path: Path, extract_to: Path):
    """Extract a zip file"""
    if not zip_path.exists():
        print(f"  ⏭️ Zip not found: {zip_path.name}")
        return False
    
    # Check if already extracted
    wav_files = list(extract_to.glob("*.wav"))
    if wav_files:
        print(f"  ⏭️ Already extracted: {len(wav_files)} files in {extract_to.name}")
        return True
    
    print(f"  📦 Extracting: {zip_path.name}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Count extracted files
        wav_files = list(extract_to.glob("*.wav"))
        print(f"  ✅ Extracted: {len(wav_files)} audio files")
        return True
    except Exception as e:
        print(f"  ❌ Extract failed: {e}")
        return False


def organize_existing_yoruba():
    """Move existing Yoruba files to proper folder"""
    print("\n📂 Organizing existing Yoruba files...")
    
    # Check for existing extracted files
    existing_wavs = list(VOICE_SAMPLES_ROOT.glob("*.wav"))
    if existing_wavs:
        yoruba_female_folder = VOICE_SAMPLES_ROOT / "yoruba_female"
        yoruba_female_folder.mkdir(exist_ok=True)
        
        moved = 0
        for wav_file in existing_wavs:
            if wav_file.name.startswith("yof_"):  # Yoruba female
                dest = yoruba_female_folder / wav_file.name
                if not dest.exists():
                    shutil.move(str(wav_file), str(dest))
                    moved += 1
        
        if moved:
            print(f"  ✅ Moved {moved} Yoruba female files to yoruba_female/")
        else:
            print(f"  ℹ️ Files already organized")


def download_pidgin_english():
    """Download Nigerian Pidgin English samples from Hugging Face"""
    print("\n📥 Setting up Nigerian Pidgin English (Yorunglish)...")
    
    pidgin_folder = VOICE_SAMPLES_ROOT / "yorunglish_pidgin"
    pidgin_folder.mkdir(exist_ok=True)
    
    info_file = pidgin_folder / "DOWNLOAD_INFO.txt"
    
    # Create info file with instructions
    info_content = """
# NIGERIAN PIDGIN ENGLISH (YORUNGLISH) SAMPLES
# =============================================

This is Sisi Lola's DEFAULT voice language!

SOURCE OPTIONS:

1. HUGGING FACE DATASET (Recommended):
   - Dataset: asr-nigerian-pidgin/nigerian-pidgin-1.0
   - Contains: 3,000+ audio recordings with transcriptions
   - Download: https://huggingface.co/datasets/asr-nigerian-pidgin/nigerian-pidgin-1.0
   
   To download via Python:
   ```
   from datasets import load_dataset
   dataset = load_dataset("asr-nigerian-pidgin/nigerian-pidgin-1.0")
   ```

2. AFRICAN VOICES:
   - Website: https://africanvoices.io
   - Contains: Mixed Nigerian languages including Pidgin

3. NIGERIAN VOICE BANK:
   - Website: https://nigerianvoicebank.com
   - Allows filtering by language and gender

INSTRUCTIONS FOR VOICE CLONING:
1. Select 3-5 minutes of clear, high-quality female voice
2. Ensure consistent speaker (same person throughout)
3. Avoid background noise and music
4. Save selected clips to ../selected_best/ folder

"""
    
    with open(info_file, "w") as f:
        f.write(info_content)
    
    print(f"  ✅ Created info file with download instructions")
    print(f"  📍 Location: {pidgin_folder}")
    
    # Try to download using huggingface_hub if available
    try:
        print(f"  🔄 Attempting to download from Hugging Face...")
        
        # First check if datasets library is available
        result = subprocess.run(
            ["pip", "show", "datasets"],
            capture_output=True, text=True
        )
        
        if "Name: datasets" not in result.stdout:
            print(f"  ℹ️ Installing 'datasets' library...")
            subprocess.run(["pip", "install", "datasets"], check=True)
        
        # Create a download script
        download_script = pidgin_folder / "download_pidgin.py"
        script_content = '''
#!/usr/bin/env python3
"""Download Nigerian Pidgin English dataset from Hugging Face"""

from datasets import load_dataset
import soundfile as sf
from pathlib import Path

output_dir = Path(__file__).parent

print("Loading Nigerian Pidgin dataset from Hugging Face...")
dataset = load_dataset("asr-nigerian-pidgin/nigerian-pidgin-1.0", split="train")

print(f"Found {len(dataset)} samples")

# Save first 100 samples (for testing)
saved = 0
for i, sample in enumerate(dataset):
    if i >= 100:  # Limit for initial download
        break
    
    audio = sample["audio"]
    text = sample.get("text", sample.get("sentence", ""))
    
    # Save audio
    audio_path = output_dir / f"pidgin_{i:04d}.wav"
    sf.write(audio_path, audio["array"], audio["sampling_rate"])
    
    saved += 1
    if saved % 10 == 0:
        print(f"Saved {saved} samples...")

print(f"Done! Saved {saved} samples to {output_dir}")
'''
        with open(download_script, "w") as f:
            f.write(script_content)
        
        print(f"  ✅ Created download script: download_pidgin.py")
        print(f"  ℹ️ Run manually: python {download_script}")
        
    except Exception as e:
        print(f"  ⚠️ Could not set up auto-download: {e}")
        print(f"  ℹ️ Please download manually from Hugging Face")


def download_all_languages():
    """Download all language datasets"""
    print("\n🌍 Downloading Nigerian language datasets...")
    print("=" * 60)
    
    for lang_key, info in DOWNLOADS.items():
        print(f"\n[{lang_key.upper()}]")
        
        # Determine destination folder
        dest_folder = VOICE_SAMPLES_ROOT / lang_key
        dest_folder.mkdir(exist_ok=True)
        
        # Download zip
        zip_path = VOICE_SAMPLES_ROOT / info["filename"]
        if download_file(info["url"], zip_path, info["description"]):
            # Extract
            extract_zip(zip_path, dest_folder)


def select_best_samples():
    """Analyze and suggest best samples for voice cloning"""
    print("\n🎯 Analyzing samples for voice cloning...")
    
    best_folder = VOICE_SAMPLES_ROOT / "selected_best"
    best_folder.mkdir(exist_ok=True)
    
    selection_guide = best_folder / "SELECTION_GUIDE.txt"
    
    guide_content = """
# 🎙️ VOICE CLONING SELECTION GUIDE
# =================================

FOR SISI LOLA VOICE:
Primary: Yorunglish/Pidgin English (this is her default!)
Secondary: Yoruba (for authentic greetings)

REQUIREMENTS FOR ELEVENLABS VOICE CLONING:
1. At least 1 minute of clear audio (3 minutes recommended)
2. Single speaker throughout
3. No background noise or music
4. Consistent audio quality
5. Natural speaking voice (not reading)

RECOMMENDED SELECTION:
1. Listen to samples from yorunglish_pidgin/ folder
2. Find a speaker with:
   - Warm, friendly tone
   - Clear pronunciation
   - Natural rhythm
   - Good energy (not monotone)
3. Select 10-20 of their best clips
4. Copy to this folder (selected_best/)

ELEVENLABS CLONING:
1. Go to: https://elevenlabs.io/voice-lab
2. Click "Add Generative or Cloned Voice"
3. Select "Instant Voice Cloning" or "Professional Voice Cloning"
4. Upload your selected samples
5. Name it "Sisi Lola"
6. Copy the Voice ID to .env file

"""
    
    with open(selection_guide, "w") as f:
        f.write(guide_content)
    
    print(f"  ✅ Created selection guide: {selection_guide}")
    
    # Count available samples
    sample_counts = {}
    for folder in VOICE_SAMPLES_ROOT.iterdir():
        if folder.is_dir() and folder.name in FOLDERS:
            wav_count = len(list(folder.glob("*.wav")))
            if wav_count > 0:
                sample_counts[folder.name] = wav_count
    
    if sample_counts:
        print("\n📊 AVAILABLE SAMPLES:")
        print("-" * 40)
        for folder, count in sorted(sample_counts.items()):
            print(f"  {folder}: {count} audio files")
    
    return sample_counts


def create_summary():
    """Create a summary of all voice samples"""
    print("\n📋 Creating summary...")
    
    summary = {
        "created_at": "2025-12-31",
        "purpose": "Nigerian voice samples for Sisi Lola voice cloning",
        "folders": {},
        "total_samples": 0
    }
    
    for folder in VOICE_SAMPLES_ROOT.iterdir():
        if folder.is_dir() and folder.name in FOLDERS:
            wav_files = list(folder.glob("*.wav"))
            summary["folders"][folder.name] = {
                "description": FOLDERS.get(folder.name, ""),
                "sample_count": len(wav_files),
                "path": str(folder)
            }
            summary["total_samples"] += len(wav_files)
    
    summary_file = VOICE_SAMPLES_ROOT / "SAMPLES_SUMMARY.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ Summary saved: {summary_file}")
    
    return summary


def main():
    print("=" * 60)
    print("🇳🇬 NIGERIAN VOICE SAMPLES DOWNLOADER & ORGANIZER")
    print("=" * 60)
    
    # Step 1: Create folder structure
    create_folder_structure()
    
    # Step 2: Organize existing files
    organize_existing_yoruba()
    
    # Step 3: Download all language datasets
    download_all_languages()
    
    # Step 4: Set up Pidgin English (special handling)
    download_pidgin_english()
    
    # Step 5: Analyze and suggest best samples
    sample_counts = select_best_samples()
    
    # Step 6: Create summary
    summary = create_summary()
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(f"📍 Voice samples location: {VOICE_SAMPLES_ROOT}")
    print(f"📁 Folders created: {len(FOLDERS)}")
    print(f"🎙️ Total samples: {summary['total_samples']}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Listen to samples (especially yorunglish_pidgin/)")
    print("2. Select best female voice clips")
    print("3. Copy selected clips to selected_best/")
    print("4. Upload to ElevenLabs for voice cloning")
    
    print("\n" + "=" * 60)
    print("✅ VOICE SAMPLES ORGANIZED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
