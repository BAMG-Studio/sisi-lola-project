#!/usr/bin/env python3
"""
Unified Training Orchestrator for Sisi Lola
Coordinates brain (LLM) + voice (TTS) training pipeline
"""
import os
import sys
import yaml
import json
import argparse
from datetime import datetime
from pathlib import Path

# Import training modules
from train_nigerian_brain import NigerianBrainTrainer
try:
    from train_nigerian_voice import NigerianVoiceTrainer
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class SisiLolaTrainingOrchestrator:
    def __init__(self, config_path="ml_training/configs/nigerian_models_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.training_log = []
        
    def log_event(self, stage, status, details=None):
        """Log training events"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "status": status,
            "details": details or {}
        }
        self.training_log.append(event)
        print(f"[{event['timestamp']}] {stage}: {status}")
        
    def check_prerequisites(self):
        """Verify all requirements are met"""
        self.log_event("Prerequisites", "Checking")
        
        checks = {
            "huggingface_token": os.getenv("HUGGINGFACE_TOKEN"),
            "voice_samples": len(list(Path("04_AUDIO_CORE/voice_samples").glob("*.wav"))),
            "personality_data": Path("ml_training/datasets/sisi_lola_personality.txt").exists(),
            "gpu_available": __import__('torch').cuda.is_available()
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
        
        if not all([checks["huggingface_token"], checks["voice_samples"] >= 5]):
            raise ValueError("Prerequisites not met. Need HF token and 5+ voice samples")
        
        self.log_event("Prerequisites", "Passed", checks)
        return checks
    
    def train_brain(self, skip_if_exists=False):
        """Train Nigerian LLM brain"""
        output_dir = "ml_training/checkpoints/natlas_lora"
        
        if skip_if_exists and Path(output_dir).exists():
            self.log_event("Brain Training", "Skipped (exists)")
            return output_dir
        
        self.log_event("Brain Training", "Starting")
        
        try:
            trainer = NigerianBrainTrainer()
            adapter_path = trainer.train(output_dir)
            self.log_event("Brain Training", "Completed", {"path": adapter_path})
            return adapter_path
        except Exception as e:
            self.log_event("Brain Training", "Failed", {"error": str(e)})
            raise
    
    def train_voice(self, skip_if_exists=False):
        """Train Nigerian voice TTS"""
        if not VOICE_AVAILABLE:
            print("⚠️  TTS library not available - skipping voice training")
            self.log_event("Voice Training", "Skipped (TTS not installed)")
            return None
            
        output_dir = "ml_training/checkpoints/xtts_sisi_lola"
        
        if skip_if_exists and Path(output_dir).exists():
            self.log_event("Voice Training", "Skipped (exists)")
            return output_dir
        
        self.log_event("Voice Training", "Starting")
        
        try:
            trainer = NigerianVoiceTrainer()
            model_path = trainer.train(output_dir)
            self.log_event("Voice Training", "Completed", {"path": model_path})
            return model_path
        except Exception as e:
            self.log_event("Voice Training", "Failed", {"error": str(e)})
            raise
    
    def create_deployment_config(self, brain_path, voice_path):
        """Generate production deployment config"""
        config = {
            "sisi_lola_production": {
                "brain": {
                    "base_model": "NCAIR1/N-ATLaS-8B",
                    "adapter_path": brain_path,
                    "system_prompt": self.config['system_prompts']['sisi_lola_core'],
                    "languages": ["yoruba", "pidgin", "nigerian_english"]
                },
                "voice": {
                    "model": "XTTS-v2",
                    "checkpoint_path": voice_path,
                    "speaker": "sisi_lola",
                    "style": self.config['voice_style']
                },
                "deployment": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "status": "ready"
                }
            }
        }
        
        config_path = "ml_training/outputs/production_config.json"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_event("Deployment Config", "Created", {"path": config_path})
        return config_path
    
    def save_training_report(self):
        """Save comprehensive training report"""
        report_path = f"ml_training/logs/training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        report = {
            "training_session": {
                "started": self.training_log[0]["timestamp"] if self.training_log else None,
                "completed": datetime.now().isoformat(),
                "events": self.training_log
            },
            "models": {
                "brain": self.config['brain_models'],
                "voice": self.config['voice_models']
            },
            "status": "completed"
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Training report saved: {report_path}")
        return report_path
    
    def run_full_training(self, skip_existing=False):
        """Execute complete training pipeline"""
        print("=" * 60)
        print("🚀 SISI LOLA TRAINING ORCHESTRATOR")
        print("=" * 60)
        
        # Check prerequisites
        self.check_prerequisites()
        
        # Train brain
        print("\n" + "=" * 60)
        print("🧠 PHASE 1: BRAIN TRAINING (N-ATLaS LLM)")
        print("=" * 60)
        brain_path = self.train_brain(skip_if_exists=skip_existing)
        
        # Train voice
        print("\n" + "=" * 60)
        print("🎤 PHASE 2: VOICE TRAINING (XTTS-v2)")
        print("=" * 60)
        voice_path = self.train_voice(skip_if_exists=skip_existing)
        
        # Create deployment config
        print("\n" + "=" * 60)
        print("📦 PHASE 3: DEPLOYMENT PREPARATION")
        print("=" * 60)
        config_path = self.create_deployment_config(brain_path, voice_path)
        
        # Save report
        report_path = self.save_training_report()
        
        print("\n" + "=" * 60)
        print("✅ TRAINING COMPLETE!")
        print("=" * 60)
        print(f"Brain (LLM): {brain_path}")
        print(f"Voice (TTS): {voice_path}")
        print(f"Config: {config_path}")
        print(f"Report: {report_path}")
        
        return {
            "brain": brain_path,
            "voice": voice_path,
            "config": config_path,
            "report": report_path
        }

def main():
    parser = argparse.ArgumentParser(description="Sisi Lola Training Orchestrator")
    parser.add_argument("--mode", choices=["full", "brain", "voice"], default="full")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    
    orchestrator = SisiLolaTrainingOrchestrator()
    
    if args.mode == "full":
        orchestrator.run_full_training(skip_existing=args.skip_existing)
    elif args.mode == "brain":
        orchestrator.train_brain(skip_if_exists=args.skip_existing)
    elif args.mode == "voice":
        orchestrator.train_voice(skip_if_exists=args.skip_existing)

if __name__ == "__main__":
    main()
