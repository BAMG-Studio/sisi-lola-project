"""
Annotate video clips for Sisi Lola acting/characterization dataset.
- Loads video clips and annotation tool
- Saves labels in structured format (CSV)

Usage:
    python annotate_video_clips.py --input-dir data/video_processed --output-csv data/video_annotated/annotations.csv
"""
import argparse
import csv
from pathlib import Path

LABELS = [
    "activity", "attitude", "role", "emotion", "cultural_marker"
]


def annotate_clip(clip_path):
    print(f"Annotating {clip_path.name}")
    activity = input("Activity (e.g. dancing, reading): ")
    attitude = input("Attitude (e.g. confident, playful): ")
    role = input("Role (e.g. influencer, journalist): ")
    emotion = input("Emotion (e.g. happy, sad): ")
    cultural_marker = input("Cultural marker (e.g. greeting, slang): ")
    return {
        "filename": clip_path.name,
        "activity": activity,
        "attitude": attitude,
        "role": role,
        "emotion": emotion,
        "cultural_marker": cultural_marker
    }


def main():
    parser = argparse.ArgumentParser(description="Annotate video clips")
    parser.add_argument("--input-dir", type=str, required=True, help="Processed video directory")
    parser.add_argument("--output-csv", type=str, required=True, help="CSV to save annotations")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_csv = Path(args.output_csv)
    clips = list(input_dir.glob("*.mp4"))
    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename"] + LABELS)
        writer.writeheader()
        for clip in clips:
            annotation = annotate_clip(clip)
            writer.writerow(annotation)
    print(f"Annotations saved to {output_csv}")

if __name__ == "__main__":
    main()
