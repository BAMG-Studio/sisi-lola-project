"""
Sisi Lola Voice Lock - Facebook MMS-TTS Yoruba Model
Configures and fine-tunes the model for consistent character voice
"""

import torch
from transformers import VitsModel, AutoTokenizer
import numpy as np
import soundfile as sf
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class SisiLolaVoiceLock:
    def __init__(self):
        self.model_id = "facebook/mms-tts-yor"
        self.model = VitsModel.from_pretrained(self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Voice lock parameters for consistency
        self.voice_seed = 45822  # Same as visual seed
        self.speaking_rate = 1.0
        self.pitch_shift = 0.0
        
    def generate_speech(self, text, output_path):
        """Generate speech with locked voice parameters"""
        torch.manual_seed(self.voice_seed)
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            output = self.model(**inputs).waveform
        
        audio = output.cpu().numpy().squeeze()
        sf.write(output_path, audio, samplerate=16000)
        return output_path
    
    def batch_generate(self, text_list, output_dir):
        """Generate multiple voice samples"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for idx, text in enumerate(text_list):
            output_path = output_dir / f"sisi_lola_voice_{idx:03d}.wav"
            self.generate_speech(text, str(output_path))
            results.append(output_path)
        
        return results

# Sample Yoruba phrases for Sisi Lola
SISI_LOLA_PHRASES = [
    "Ẹ káàbọ̀! Mo ni Sisi Lola",  # Welcome! I am Sisi Lola
    "Báwo ni? Kí ló ń ṣẹlẹ̀?",  # How are you? What's happening?
    "Jẹ́ ká ṣe àwòrán tuntun",  # Let's create something new
    "Mo fẹ́ràn ọ̀",  # I love you
    "Ẹ ṣeun púpọ̀",  # Thank you very much
]

if __name__ == "__main__":
    voice_lock = SisiLolaVoiceLock()
    
    output_dir = Path(__file__).parent / "generated_samples"
    print(f"Generating Sisi Lola voice samples with seed {voice_lock.voice_seed}...")
    
    results = voice_lock.batch_generate(SISI_LOLA_PHRASES, output_dir)
    print(f"[OK] Generated {len(results)} voice samples")
    print(f"[OK] Saved to: {output_dir}")
