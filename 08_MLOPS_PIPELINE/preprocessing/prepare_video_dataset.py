"""
Prepare video dataset for Sisi Lola acting/characterization model.
- Extracts frames and audio from raw video clips
- Normalizes resolution, duration, and format
- Saves processed data for training

Usage:
    python prepare_video_dataset.py --input-dir data/video_raw --output-dir data/video_processed --frame-rate 25 --duration 10
"""
import os
import cv2
import argparse
from pathlib import Path


def process_video(video_path, output_dir, frame_rate=25, duration=10):
    """
    Extract frames and audio from video, normalize resolution and duration.
    """
    vidcap = cv2.VideoCapture(str(video_path))
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frames_to_extract = min(int(fps * duration), total_frames)
    basename = video_path.stem
    frame_dir = output_dir / f"{basename}_frames"
    frame_dir.mkdir(exist_ok=True)
    count = 0
    while count < frames_to_extract:
        success, image = vidcap.read()
        if not success:
            break
        if count % int(fps // frame_rate) == 0:
            frame_path = frame_dir / f"frame_{count:04d}.jpg"
            cv2.imwrite(str(frame_path), image)
        count += 1
    vidcap.release()
    # Audio extraction (requires ffmpeg)
    audio_path = output_dir / f"{basename}.wav"
    os.system(f"ffmpeg -y -i '{video_path}' -vn -acodec pcm_s16le -ar 16000 -ac 1 '{audio_path}'")
    print(f"Processed {video_path.name}: {frames_to_extract} frames, audio saved to {audio_path}")


def main():
    parser = argparse.ArgumentParser(description="Prepare video dataset for model training")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory with raw video clips")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save processed data")
    parser.add_argument("--frame-rate", type=int, default=25, help="Frame extraction rate")
    parser.add_argument("--duration", type=int, default=10, help="Max duration per clip (seconds)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    for video_file in input_dir.glob("*.mp4"):
        process_video(video_file, output_dir, frame_rate=args.frame_rate, duration=args.duration)

if __name__ == "__main__":
    main()
