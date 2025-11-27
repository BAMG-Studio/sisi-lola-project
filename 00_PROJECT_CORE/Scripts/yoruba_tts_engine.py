#!/usr/bin/env python3
"""
Yoruba TTS Engine using Facebook MMS-TTS-YOR
Trained for Sisi Lola's voice with Lagos accent
"""
import os
import torch
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from transformers import VitsModel, AutoTokenizer

# Load environment
env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

OUTPUT_DIR = Path(__file__).parent.parent.parent / '04_AUDIO_CORE' / 'voice_samples'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class SisiLolaVoiceEngine:
    def __init__(self):
        print("[INIT] Loading Facebook MMS-TTS Yoruba model...")
        self.model = VitsModel.from_pretrained("facebook/mms-tts-yor")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-yor")
        self.sample_rate = 16000
        print("[OK] Model loaded")
    
    def generate_speech(self, text_yoruba, output_path=None):
        """Generate speech from Yoruba text"""
        print(f"[TTS] Generating: {len(text_yoruba)} chars...")
        
        inputs = self.tokenizer(text_yoruba, return_tensors="pt")
        
        with torch.no_grad():
            output = self.model(**inputs).waveform
        
        if output_path is None:
            from datetime import datetime
            output_path = OUTPUT_DIR / f"sisi_lola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        audio_np = output[0].cpu().numpy()
        wavfile.write(str(output_path), self.sample_rate, audio_np)
        print(f"[OK] Saved: {output_path.name}")
        
        return output_path
    
    def batch_generate(self, text_list):
        """Generate multiple audio files"""
        outputs = []
        for i, text in enumerate(text_list):
            print(f"[BATCH] {i+1}/{len(text_list)}")
            output_path = self.generate_speech(text)
            outputs.append(output_path)
        return outputs

# Training phrases from voice profile
TRAINING_PHRASES = [
    "Ẹ káàbọ̀! Mo ni Sisi Lola, ẹni tó fẹ́ fi àṣà Áfríkà hàn fún gbogbo ayé.",
    "Báwo ni? Ṣé àlàáfíà ni? Ẹ jókòó, ẹ gbọ́ ìtàn yìí dáadáa.",
    "Àwa ọmọ Yorùbá, a ní àṣà tó dára púpọ̀. Ẹ jẹ́ ká sọ̀rọ̀ nípa rẹ̀.",
    "Ó dára gan-an! This one sweet me die! Àbí ẹ̀yin ò rí i bẹ́ẹ̀?",
    "Ẹ gbọ́ ọ̀rọ̀ yìí: innovation tí ó wà ní Áfríkà kò lẹ́gbẹ́!",
    "Àwa ló máa ṣe é! We go do am! Áfríkà tó ń bọ̀ yìí máa dára.",
    "Ẹ subscribe sí channel mi o! Ẹ má gbàgbé láti like àti share.",
    "Ẹ ṣeun gan-an! Thank you plenty! Má ríi yín lọ́la."
]

def train_voice_samples():
    """Generate training samples for Sisi Lola's voice"""
    print("=" * 60)
    print("SISI LOLA VOICE TRAINING")
    print("=" * 60)
    
    engine = SisiLolaVoiceEngine()
    
    print(f"\n[TRAIN] Generating {len(TRAINING_PHRASES)} training samples...")
    outputs = engine.batch_generate(TRAINING_PHRASES)
    
    print("\n[OK] Training complete!")
    print(f"Samples saved to: {OUTPUT_DIR}")
    print(f"Total files: {len(outputs)}")
    
    return outputs

if __name__ == '__main__':
    train_voice_samples()
