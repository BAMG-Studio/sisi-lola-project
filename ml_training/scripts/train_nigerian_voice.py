#!/usr/bin/env python3
"""
Sisi Lola Nigerian Voice Training - XTTS-v2 Fine-tuning
Trains cross-lingual TTS with Nigerian accent and voice cloning
"""
import os
import yaml
import torch
import torchaudio
# Try to use soundfile backend to avoid torchcodec dependency
try:
    torchaudio.set_audio_backend("soundfile")
except RuntimeError:
    pass  # Backend already set or not available
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs
import json
from pathlib import Path
from datetime import datetime

class NigerianVoiceTrainer:
    def __init__(self, config_path="ml_training/configs/nigerian_models_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def prepare_voice_samples(self):
        """Prepare Sisi Lola voice samples for training"""
        voice_dir = Path("04_AUDIO_CORE/voice_samples")
        samples = []
        
        for wav_file in voice_dir.glob("*.wav"):
            # Load and validate audio
            waveform, sr = torchaudio.load(wav_file)
            
            # Resample to 22050 Hz if needed
            if sr != 22050:
                resampler = torchaudio.transforms.Resample(sr, 22050)
                waveform = resampler(waveform)
            
            # Get corresponding transcript
            txt_file = wav_file.with_suffix('.txt')
            if txt_file.exists():
                with open(txt_file) as f:
                    text = f.read().strip()
            else:
                # Use script files
                script_name = wav_file.stem.replace('sisi_lola_', 'SCRIPT_')
                script_file = Path("04_AUDIO_CORE/01_Voice_Samples") / f"{script_name}.txt"
                if script_file.exists():
                    with open(script_file) as f:
                        text = f.read().strip()
                else:
                    continue
            
            samples.append({
                "audio_file": str(wav_file),
                "text": text,
                "speaker_name": "sisi_lola",
                "language": "yo-NG"  # Yoruba-Nigeria
            })
        
        return samples
    
    def create_training_manifest(self, samples, output_path="ml_training/datasets/voice_manifest.json"):
        """Create XTTS training manifest"""
        manifest = {
            "audio_files": [],
            "speaker_name": "sisi_lola",
            "language": "yo-NG",
            "style": self.config['voice_style']
        }
        
        for sample in samples:
            manifest["audio_files"].append({
                "audio_file": sample["audio_file"],
                "text": sample["text"],
                "speaker_name": sample["speaker_name"]
            })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_xtts_model(self):
        """Load pre-trained XTTS-v2 for fine-tuning"""
        model_id = self.config['voice_models']['primary']['model_id']
        
        config = XttsConfig()
        config.load_json("https://huggingface.co/coqui/XTTS-v2/resolve/main/config.json")
        
        model = Xtts.init_from_config(config)
        model.load_checkpoint(
            config,
            checkpoint_dir="models/xtts-v2",
            eval=False,
            use_deepspeed=False
        )
        
        return model, config
    
    def train(self, output_dir="ml_training/checkpoints/xtts_sisi_lola"):
        """Execute XTTS fine-tuning"""
        print("🎤 Preparing Sisi Lola voice samples...")
        samples = self.prepare_voice_samples()
        
        if len(samples) < 5:
            raise ValueError(f"Need at least 5 voice samples, found {len(samples)}")
        
        print(f"✅ Found {len(samples)} voice samples")
        
        manifest_path = self.create_training_manifest(samples)
        print(f"📝 Created training manifest: {manifest_path}")
        
        print("🔊 Loading XTTS-v2 model...")
        model, config = self.load_xtts_model()
        
        # Configure training
        cfg = self.config['training']['voice']
        
        trainer_args = TrainerArgs(
            output_path=output_dir,
            epochs=cfg['fine_tune_steps'] // len(samples),
            batch_size=cfg['batch_size'],
            learning_rate=cfg['learning_rate'],
            save_step=500,
            print_step=50,
            mixed_precision=True
        )
        
        trainer = Trainer(
            trainer_args,
            config,
            output_path=output_dir,
            model=model,
            train_samples=samples
        )
        
        print("🚀 Starting voice training...")
        trainer.fit()
        
        # Save metadata
        metadata = {
            "model": "XTTS-v2",
            "speaker": "Sisi Lola",
            "trained_on": datetime.now().isoformat(),
            "languages": ["yoruba", "nigerian_english", "pidgin"],
            "accent": "Lagos Nigerian",
            "samples_used": len(samples),
            "style": self.config['voice_style']
        }
        
        with open(f"{output_dir}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return output_dir

if __name__ == "__main__":
    trainer = NigerianVoiceTrainer()
    model_path = trainer.train()
    print(f"✅ Voice training complete! Model saved to: {model_path}")
