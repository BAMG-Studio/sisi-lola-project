"""
SISI LOLA DATASET FORGE
========================
Extracts high-quality character frames from existing video assets
to prepare for LoRA (Character Locking) training.
"""

import cv2
import os
from pathlib import Path

def forge_dataset(video_dir: str, output_dir: str):
    print(f"🔥 FORGE: Extracting DNA from videos in {video_dir}...")
    
    video_path = Path(video_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    video_files = list(video_path.glob("*.mp4"))
    
    frame_count = 0
    for v_file in video_files:
        print(f"📹 Processing: {v_file.name}")
        cap = cv2.VideoCapture(str(v_file))
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Extract 5 high-quality frames per video evenly spaced
        intervals = [int(total_frames * (i/6)) for i in range(1, 6)]
        
        for idx, frame_no in enumerate(intervals):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if ret:
                # Save as high-quality PNG
                frame_name = f"sisi_dna_{v_file.stem}_{idx}.png"
                cv2.imwrite(str(output_path / frame_name), frame)
                frame_count += 1
                
        cap.release()
        
    print(f"✅ FORGE COMPLETE: {frame_count} frames extracted to {output_dir}")

if __name__ == "__main__":
    # Point to the existing generated videos
    video_dir = "c:/Users/POK28/Dropbox/Sisi_Lola/03_MEDIA_ASSETS/generated"
    output_dir = "c:/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/sisi_dna_frames"
    forge_dataset(video_dir, output_dir)
