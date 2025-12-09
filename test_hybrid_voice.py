#!/usr/bin/env python3
"""Test the hybrid voice stack"""
import asyncio
import sys
from pathlib import Path

# Add the voice training path
sys.path.insert(0, str(Path(__file__).parent / "04_AUDIO_CORE" / "voice_training"))

async def test_hybrid_voice():
    from hybrid_voice_stack import HybridVoiceStack, LanguageRouter
    
    print("=" * 60)
    print("SISI LOLA HYBRID VOICE STACK TEST")
    print("=" * 60)
    
    # Test language routing
    print("\n1. Testing Language Router...")
    router = LanguageRouter()
    
    test_texts = [
        "How you dey? I hope say everything dey kampe!",
        "Good morning! [YO]Ẹ kú àárọ̀[/YO] How are you today?",
        "[NP]Wetin dey happen na?[/NP] Tell me everything!",
    ]
    
    for text in test_texts:
        print(f"\n   Input: {text[:50]}...")
        segments = router.parse_text(text)
        for seg in segments:
            print(f"   → [{seg.language.value.upper()}] {seg.text[:35]}...")
    
    # Test voice synthesis
    print("\n2. Testing Voice Synthesis...")
    stack = HybridVoiceStack()
    
    print("\n   Available engines by language:")
    for lang, engine in stack.get_available_engines().items():
        print(f"   → {lang}: {engine}")
    
    # Synthesize test audio
    output_dir = Path("voice_outputs")
    output_dir.mkdir(exist_ok=True)
    
    synthesis_tests = [
        ("How you dey? I be Sisi Lola!", "hybrid_english.mp3"),
        ("[NP]Wetin dey happen na? Abeg tell me o![/NP]", "hybrid_pidgin.mp3"),
        ("Welcome! [YO]Ẹ kú àárọ̀[/YO] Let's go!", "hybrid_mixed.mp3"),
    ]
    
    for text, filename in synthesis_tests:
        output_path = str(output_dir / filename)
        print(f"\n   Synthesizing: {text[:40]}...")
        try:
            result = await stack.synthesize(text, output_path)
            print(f"   ✓ Output: {result}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nCheck voice_outputs/ folder for generated audio files.")

if __name__ == "__main__":
    asyncio.run(test_hybrid_voice())
