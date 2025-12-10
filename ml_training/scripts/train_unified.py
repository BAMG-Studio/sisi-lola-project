#!/usr/bin/env python3
"""
Sisi Lola Unified Training Pipeline
Runs both brain (LLM) and voice (TTS) training in sequence
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

class UnifiedTrainer:
    def __init__(self, output_dir="ml_training/checkpoints"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        
    def run_brain_training(self, model="gpt2"):
        """Train the N-ATLaS brain (LLM with LoRA)"""
        print("\n" + "="*60)
        print("  PHASE 1: BRAIN TRAINING (N-ATLaS LLM)")
        print("="*60 + "\n")
        
        try:
            # Run as subprocess to avoid import issues
            env = os.environ.copy()
            env["BRAIN_MODEL"] = model
            env["PYTHONIOENCODING"] = "utf-8"
            
            result = subprocess.run(
                [sys.executable, "ml_training/scripts/train_nigerian_brain.py",
                 "--output", str(self.output_dir / "natlas_lora")],
                cwd=Path(__file__).parent.parent.parent,  # Project root
                env=env,
                capture_output=False
            )
            
            if result.returncode == 0:
                self.results["brain"] = {
                    "status": "success",
                    "path": str(self.output_dir / "natlas_lora"),
                    "model": model
                }
                print(f"\n✅ Brain training complete: {self.output_dir / 'natlas_lora'}")
                return True
            else:
                self.results["brain"] = {"status": "failed", "error": f"Exit code {result.returncode}"}
                print(f"\n❌ Brain training failed with exit code {result.returncode}")
                return False
        except Exception as e:
            self.results["brain"] = {"status": "failed", "error": str(e)}
            print(f"\n❌ Brain training failed: {e}")
            return False
    
    def run_voice_training(self):
        """Train the Nigerian voice (XTTS/EdgeTTS)"""
        print("\n" + "="*60)
        print("  PHASE 2: VOICE TRAINING (Nigerian TTS)")
        print("="*60 + "\n")
        
        try:
            # Run as subprocess to avoid import issues
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            result = subprocess.run(
                [sys.executable, "ml_training/scripts/train_nigerian_voice.py",
                 "--output", str(self.output_dir / "nigerian_voice")],
                cwd=Path(__file__).parent.parent.parent,  # Project root
                env=env,
                capture_output=False
            )
            
            if result.returncode == 0:
                self.results["voice"] = {
                    "status": "success",
                    "path": str(self.output_dir / "nigerian_voice")
                }
                print(f"\n✅ Voice training complete: {self.output_dir / 'nigerian_voice'}")
                return True
            else:
                self.results["voice"] = {"status": "failed", "error": f"Exit code {result.returncode}"}
                print(f"\n❌ Voice training failed with exit code {result.returncode}")
                return False
        except Exception as e:
            self.results["voice"] = {"status": "failed", "error": str(e)}
            print(f"\n❌ Voice training failed: {e}")
            # Voice training failure is non-fatal - we can use EdgeTTS fallback
            return False
    
    def generate_report(self):
        """Generate training summary report"""
        print("\n" + "="*60)
        print("  TRAINING SUMMARY")
        print("="*60 + "\n")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            "timestamp": timestamp,
            "results": self.results,
            "output_dir": str(self.output_dir)
        }
        
        # Print summary
        print(f"Training completed at: {timestamp}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        for component, result in self.results.items():
            status = "✅ SUCCESS" if result.get("status") == "success" else "❌ FAILED"
            print(f"  {component.upper()}: {status}")
            if result.get("path"):
                print(f"    Path: {result['path']}")
            if result.get("error"):
                print(f"    Error: {result['error']}")
        
        # Save report
        import json
        report_path = self.output_dir / "training_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
        return report
    
    def run_all(self, brain_model="gpt2", skip_voice=False):
        """Run complete training pipeline"""
        print("\n" + "="*60)
        print("  SISI LOLA UNIFIED TRAINING PIPELINE")
        print("="*60)
        print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Brain model: {brain_model}")
        print(f"Skip voice: {skip_voice}")
        print()
        
        # Phase 1: Brain
        brain_success = self.run_brain_training(model=brain_model)
        
        # Phase 2: Voice (optional)
        if not skip_voice:
            voice_success = self.run_voice_training()
        else:
            print("\n⏭️ Skipping voice training (--skip-voice)")
            self.results["voice"] = {"status": "skipped"}
        
        # Generate report
        report = self.generate_report()
        
        # Overall status
        all_success = all(
            r.get("status") in ["success", "skipped"] 
            for r in self.results.values()
        )
        
        if all_success:
            print("\n" + "="*60)
            print("  🎉 ALL TRAINING COMPLETE!")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("  ⚠️ TRAINING COMPLETED WITH ERRORS")
            print("="*60 + "\n")
        
        return all_success, report


def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Unified Training")
    parser.add_argument(
        "--brain-model", 
        default="gpt2",
        help="Base model for brain training (gpt2, TinyLlama/TinyLlama-1.1B-Chat-v1.0)"
    )
    parser.add_argument(
        "--skip-voice",
        action="store_true",
        help="Skip voice training"
    )
    parser.add_argument(
        "--skip-brain",
        action="store_true", 
        help="Skip brain training"
    )
    parser.add_argument(
        "--output-dir",
        default="ml_training/checkpoints",
        help="Output directory for trained models"
    )
    args = parser.parse_args()
    
    trainer = UnifiedTrainer(output_dir=args.output_dir)
    
    if args.skip_brain:
        print("⏭️ Skipping brain training (--skip-brain)")
        trainer.results["brain"] = {"status": "skipped"}
        if not args.skip_voice:
            trainer.run_voice_training()
        trainer.generate_report()
    else:
        success, report = trainer.run_all(
            brain_model=args.brain_model,
            skip_voice=args.skip_voice
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
