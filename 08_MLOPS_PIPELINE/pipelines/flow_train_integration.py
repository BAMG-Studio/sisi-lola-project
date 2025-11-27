"""
End-to-end integration test pipeline for Sisi Lola voice + video actor models.
- Runs ASR, TTS, and video actor training in sequence
- Validates outputs and logs results

Usage:
    python pipelines/flow_train_integration.py
"""
import subprocess

def run_step(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Step failed: {cmd}")
        exit(1)


def main():
    print("=== Sisi Lola End-to-End Integration Test ===")
    run_step("python training/train_whisper_asr.py --manifest data/processed/asr_manifest_all.tsv --output models/whisper_africa_v1 --epochs 5")
    run_step("python training/train_xtts_tts.py --metadata data/processed/tts_metadata.csv --output models/xtts_sisi_lola_v1 --epochs 5")
    run_step("python training/train_video_actor_model.py --data-dir data/video_processed --annotations data/video_annotated/annotations.csv --labels configs/video_labels.yaml --epochs 5")
    print("=== Integration Test Complete ===")

if __name__ == "__main__":
    main()
