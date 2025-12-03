#!/usr/bin/env python3
"""
Sisi Lola Nigerian Inference Engine
Combines N-ATLaS brain + XTTS voice for production inference
"""
import os
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from TTS.api import TTS
import soundfile as sf
from datetime import datetime

class SisiLolaInference:
    def __init__(self, config_path="ml_training/outputs/production_config.json"):
        import json
        with open(config_path) as f:
            self.config = json.load(f)['sisi_lola_production']
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.brain = None
        self.voice = None
        
    def load_brain(self):
        """Load N-ATLaS with LoRA adapter"""
        brain_cfg = self.config['brain']
        
        print(f"🧠 Loading brain: {brain_cfg['base_model']}")
        
        # Load base model
        tokenizer = AutoTokenizer.from_pretrained(
            brain_cfg['base_model'],
            trust_remote_code=True,
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            brain_cfg['base_model'],
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        
        # Load LoRA adapter
        if os.path.exists(brain_cfg['adapter_path']):
            print(f"🔧 Loading adapter: {brain_cfg['adapter_path']}")
            model = PeftModel.from_pretrained(model, brain_cfg['adapter_path'])
        
        self.brain = {"model": model, "tokenizer": tokenizer}
        print("✅ Brain loaded")
        
    def load_voice(self):
        """Load XTTS voice model"""
        voice_cfg = self.config['voice']
        
        print(f"🎤 Loading voice: {voice_cfg['model']}")
        
        # Load XTTS
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        
        # Load fine-tuned checkpoint if available
        if os.path.exists(voice_cfg['checkpoint_path']):
            print(f"🔧 Loading checkpoint: {voice_cfg['checkpoint_path']}")
            # Load custom checkpoint
            # tts.load_checkpoint(voice_cfg['checkpoint_path'])
        
        self.voice = tts
        print("✅ Voice loaded")
        
    def generate_text(self, prompt, max_length=256, temperature=0.8):
        """Generate text response using N-ATLaS"""
        if self.brain is None:
            self.load_brain()
        
        system_prompt = self.config['brain']['system_prompt']
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        
        inputs = self.brain['tokenizer'](
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.brain['model'].generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1
            )
        
        response = self.brain['tokenizer'].decode(outputs[0], skip_special_tokens=True)
        
        # Extract assistant response
        if "<|assistant|>" in response:
            response = response.split("<|assistant|>")[-1].strip()
        
        return response
    
    def generate_speech(self, text, output_path=None, language="yo"):
        """Generate speech using XTTS"""
        if self.voice is None:
            self.load_voice()
        
        # Use reference voice sample
        speaker_wav = "04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav"
        
        if not os.path.exists(speaker_wav):
            # Fallback to any available sample
            import glob
            samples = glob.glob("04_AUDIO_CORE/voice_samples/*.wav")
            if samples:
                speaker_wav = samples[0]
        
        # Generate speech
        wav = self.voice.tts(
            text=text,
            speaker_wav=speaker_wav,
            language=language
        )
        
        # Save if path provided
        if output_path:
            sf.write(output_path, wav, 22050)
            return output_path
        
        return wav
    
    def chat(self, user_input, generate_audio=True, language="yo"):
        """Complete chat interaction: text + voice"""
        print(f"\n👤 User: {user_input}")
        
        # Generate text response
        response_text = self.generate_text(user_input)
        print(f"🤖 Sisi Lola: {response_text}")
        
        # Generate audio if requested
        audio_path = None
        if generate_audio:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"ml_training/outputs/response_{timestamp}.wav"
            self.generate_speech(response_text, audio_path, language)
            print(f"🔊 Audio saved: {audio_path}")
        
        return {
            "text": response_text,
            "audio": audio_path
        }

def main():
    """Interactive demo"""
    print("=" * 60)
    print("🎭 SISI LOLA - Nigerian Virtual Host")
    print("=" * 60)
    
    sisi = SisiLolaInference()
    
    # Test prompts
    test_prompts = [
        "Bawo ni? Tell me about Lagos nightlife",
        "Wetin be your favorite Nigerian food?",
        "Explain blockchain technology in Yorunglish"
    ]
    
    for prompt in test_prompts:
        result = sisi.chat(prompt, generate_audio=True, language="yo")
        print("\n" + "-" * 60)

if __name__ == "__main__":
    main()
