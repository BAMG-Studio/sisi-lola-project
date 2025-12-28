"""
TEST SISI PRODUCTION - THE DNA LOCK
===================================
1. Extracts high-quality frames from existing videos (Dataset Forge)
2. Packs them into a DNA Zip
3. Sends them to the Modal "Wizard" to lock Sisi's Character consistency.
"""

import os
import io
import zipfile
import asyncio
from pathlib import Path
import modal

# Import the forge logic
import sys
project_root = Path(__file__).parent
sys.path.append(str(project_root))
from ml_training.scripts.dataset_forge import forge_dataset

async def run_dna_lock():
    print("🚀 STARTING SISI LOLA DNA LOCK...")
    
    # 1. Forge Dataset
    video_dir = str(project_root / "03_MEDIA_ASSETS" / "generated")
    frame_dir = str(project_root / "ml_training" / "datasets" / "sisi_dna_frames")
    
    forge_dataset(video_dir, frame_dir)
    
    # 2. Zip the frames
    print("📦 Zipping DNA frames...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for frame in Path(frame_dir).glob("*.png"):
            zip_file.write(frame, frame.name)
            
    zip_bytes = zip_buffer.getvalue()
    
    # 3. Connect to Modal Wizard
    print("📡 Connecting to Sisi Lola's Creative HQ on Modal...")
    f = modal.Cls.from_name("sisi-lola-production", "SisiLolaProducer")
    
    try:
        wizard = f()
        success = await wizard.train_character_dna.remote.aio(zip_bytes)
        
        if success:
            print("✅ SUCCESS: Sisi Lola's character is now LOCKED in the cloud!")
            print("✨ She will now look consistent 24/7 without third-party fees.")
            
            # test generation
            print("📸 Generating test cinematic shot with the new Lock...")
            image_bytes = await wizard.generate_cinematic_photo.remote.aio(
                "Sisi Lola sitting in a Lagos studio, hosting a live podcast, laughing, looking at comments on a screen",
                aspect_ratio="16:9"
            )
            
            output_path = project_root / "03_MEDIA_ASSETS" / "generated" / "locked_sisi_sample.png"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"🖼️ Sample saved to: {output_path}")
            
    except Exception as e:
        print(f"❌ ERROR: DNA Lock failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_dna_lock())
