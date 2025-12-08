"""
SISI LOLA VOICE TESTER - Quick Voice Generation Test
=====================================================
Test voice generation locally before deploying.

Usage:
    python test_voice_local.py                    # Test with default phrases
    python test_voice_local.py "Your text here"  # Test with custom text
    python test_voice_local.py --play             # Generate and play audio
"""

import os
import sys
from pathlib import Path
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "04_AUDIO_CORE" / "voice_training"))

def test_voice(text: str = None, play: bool = False):
    """Test Sisi Lola voice generation"""
    
    print("🎤 SISI LOLA VOICE TESTER")
    print("=" * 50)
    
    # Check dependencies
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch not installed!")
        print("   Run: pip install torch torchaudio")
        return
    
    try:
        from transformers import VitsModel, AutoTokenizer
        print("✅ Transformers: Available")
    except ImportError:
        print("❌ Transformers not installed!")
        print("   Run: pip install transformers")
        return
    
    try:
        import soundfile
        print("✅ Soundfile: Available")
    except ImportError:
        print("❌ Soundfile not installed!")
        print("   Run: pip install soundfile")
        return
    
    # Initialize voice engine
    print("\n🔧 Loading Sisi Lola voice model...")
    try:
        from sisi_lola_voice_lock import SisiLolaVoiceLock
        voice = SisiLolaVoiceLock()
        print(f"✅ Model loaded: {voice.model_id}")
        print(f"   Device: {voice.device}")
        print(f"   Voice seed: {voice.voice_seed}")
    except Exception as e:
        print(f"❌ Failed to load voice model: {e}")
        return
    
    # Test phrases
    test_phrases = [
        text if text else "Ẹ káàbọ̀! Mo ni Sisi Lola. How you dey today?",
        "Omo see gobe! This thing na serious matter o!",
        "Make we do this thing together. E go sweet die!",
    ]
    
    output_dir = project_root / "04_AUDIO_CORE" / "voice_training" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🎵 Generating voice samples...")
    print(f"   Output: {output_dir}")
    print("-" * 50)
    
    for i, phrase in enumerate(test_phrases[:1] if text else test_phrases):
        output_path = output_dir / f"test_voice_{i+1}.wav"
        print(f"\n📝 Text: {phrase[:60]}...")
        
        try:
            voice.generate_speech(phrase, str(output_path))
            print(f"✅ Generated: {output_path.name}")
            
            # Get file size
            size_kb = output_path.stat().st_size / 1024
            print(f"   Size: {size_kb:.1f} KB")
            
            # Play if requested
            if play:
                print("🔊 Playing audio...")
                import platform
                system = platform.system()
                
                if system == "Windows":
                    os.system(f'start "" "{output_path}"')
                elif system == "Darwin":
                    os.system(f'afplay "{output_path}"')
                else:
                    os.system(f'aplay "{output_path}" 2>/dev/null')
                    
        except Exception as e:
            print(f"❌ Generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Voice test complete!")
    print(f"📁 Audio files saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Test Sisi Lola voice locally")
    parser.add_argument('text', nargs='?', help='Custom text to generate')
    parser.add_argument('--play', action='store_true', help='Play generated audio')
    args = parser.parse_args()
    
    test_voice(args.text, args.play)


if __name__ == "__main__":
    main()
