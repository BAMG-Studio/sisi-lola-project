"""
Run all model evaluation scripts and aggregate results.
- Evaluates Whisper ASR, XTTS TTS, and Video Actor models
- Aggregates metrics into a single summary report

Usage:
    python run_all_evaluations.py --asr-manifest data/processed/asr_manifest_test.tsv --asr-model models/whisper_africa_v1 \
        --tts-metadata data/processed/tts_metadata_test.csv --tts-model models/xtts_sisi_lola_v1 \
        --video-data-dir data/video_processed --video-annotations data/video_annotated/annotations_test.csv --video-model models/video_actor_v1 \
        --output reports/aggregate_eval.json
"""
import argparse
import subprocess
import json
from pathlib import Path

def run_evaluation(cmd: list[str]):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Run all model evaluations and aggregate results")
    parser.add_argument("--asr-manifest", type=str, required=True)
    parser.add_argument("--asr-model", type=str, required=True)
    parser.add_argument("--tts-metadata", type=str, required=True)
    parser.add_argument("--tts-model", type=str, required=True)
    parser.add_argument("--video-data-dir", type=str, required=True)
    parser.add_argument("--video-annotations", type=str, required=True)
    parser.add_argument("--video-model", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    # Paths for intermediate reports
    asr_report = "reports/whisper_eval.json"
    tts_report = "reports/xtts_eval.json"
    video_report = "reports/video_actor_eval.json"

    # Run evaluations
    run_evaluation(["python", "evaluation/evaluate_whisper_asr.py", "--manifest", args.asr_manifest, "--model", args.asr_model, "--output", asr_report])
    run_evaluation(["python", "evaluation/evaluate_xtts_tts.py", "--metadata", args.tts_metadata, "--model", args.tts_model, "--output", tts_report])
    run_evaluation(["python", "evaluation/evaluate_video_actor.py", "--data-dir", args.video_data_dir, "--annotations", args.video_annotations, "--model", args.video_model, "--output", video_report])

    # Aggregate results
    results = {}
    for report_path in [asr_report, tts_report, video_report]:
        with open(report_path) as f:
            results[Path(report_path).stem] = json.load(f)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Aggregate evaluation report saved to {args.output}")

if __name__ == "__main__":
    main()
