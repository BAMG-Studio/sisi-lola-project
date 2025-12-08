#!/usr/bin/env python
"""
Test Voice Output for Sisi Lola
Uses edge-tts (Microsoft Neural TTS) for high-quality voice synthesis.

Available in .venv_coqui environment (Python 3.10)
"""

import asyncio
import os
import sys

# Check if edge_tts is available
try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Run:")
    print("  .venv_coqui\\Scripts\\pip.exe install edge-tts")
    sys.exit(1)


async def list_voices():
    """List all available voices."""
    voices = await edge_tts.list_voices()
    
    # Filter for English and Nigerian voices
    african_voices = [v for v in voices if 'en-NG' in v['ShortName'] or 'en-KE' in v['ShortName'] or 'en-ZA' in v['ShortName']]
    english_voices = [v for v in voices if v['Locale'].startswith('en-')]
    
    print("\n🌍 AFRICAN ENGLISH VOICES:")
    print("-" * 60)
    for v in african_voices:
        print(f"  {v['ShortName']}: {v['Gender']} - {v['Locale']}")
    
    print(f"\n📢 ALL ENGLISH VOICES ({len(english_voices)} total):")
    print("-" * 60)
    for v in english_voices[:15]:  # Show first 15
        print(f"  {v['ShortName']}: {v['Gender']} - {v['Locale']}")
    if len(english_voices) > 15:
        print(f"  ... and {len(english_voices) - 15} more")
    
    return voices


async def generate_speech(text: str, voice: str = "en-NG-EzinneNeural", output_file: str = "output.mp3"):
    """Generate speech from text using edge-tts."""
    print(f"\n🎤 Generating speech with voice: {voice}")
    print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    print(f"✅ Saved to: {output_file}")
    return output_file


async def test_nigerian_pidgin():
    """Test Nigerian Pidgin phrases with Nigerian voice."""
    
    phrases = [
        ("How you dey? E good say you come visit o!", "en-NG-EzinneNeural"),
        ("Wetin dey happen for this side? Everything dey kampe!", "en-NG-EzinneNeural"),
        ("Abeg make we chop first before we yarn about business.", "en-NG-AbeoNeural"),
        ("Na so life be. Sometimes e sweet, sometimes e bitter.", "en-NG-AbeoNeural"),
    ]
    
    print("\n" + "=" * 60)
    print("🇳🇬 TESTING NIGERIAN PIDGIN VOICE OUTPUT")
    print("=" * 60)
    
    output_dir = "voice_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (text, voice) in enumerate(phrases, 1):
        output_file = os.path.join(output_dir, f"pidgin_{i}.mp3")
        await generate_speech(text, voice, output_file)
    
    print(f"\n🎉 Generated {len(phrases)} audio files in '{output_dir}/' folder")
    print("   Play them with your favorite media player!")


async def interactive_tts():
    """Interactive TTS mode."""
    print("\n" + "=" * 60)
    print("🎙️ INTERACTIVE TEXT-TO-SPEECH")
    print("=" * 60)
    
    # Default Nigerian voices
    voices = {
        "1": ("en-NG-EzinneNeural", "Nigerian Female (Ezinne)"),
        "2": ("en-NG-AbeoNeural", "Nigerian Male (Abeo)"),
        "3": ("en-ZA-LeahNeural", "South African Female (Leah)"),
        "4": ("en-KE-AsiliaNeural", "Kenyan Female (Asilia)"),
        "5": ("en-GB-SoniaNeural", "British Female (Sonia)"),
        "6": ("en-US-JennyNeural", "US Female (Jenny)"),
    }
    
    print("\nAvailable voices:")
    for key, (voice_id, name) in voices.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect voice (1-6): ").strip() or "1"
    voice_id, voice_name = voices.get(choice, voices["1"])
    
    text = input(f"\nEnter text to speak (using {voice_name}): ").strip()
    if not text:
        text = "How you dey? Welcome to Sisi Lola chat!"
    
    output_file = "voice_outputs/interactive_output.mp3"
    os.makedirs("voice_outputs", exist_ok=True)
    await generate_speech(text, voice_id, output_file)


async def main():
    """Main function."""
    print("=" * 60)
    print("🔊 SISI LOLA VOICE OUTPUT TEST")
    print("   Using Microsoft Edge TTS (Neural Voices)")
    print("=" * 60)
    
    # List available voices
    await list_voices()
    
    print("\nOptions:")
    print("  1. Test Nigerian Pidgin phrases")
    print("  2. Interactive TTS mode")
    print("  3. Both")
    
    choice = input("\nSelect option (1/2/3): ").strip() or "3"
    
    if choice in ("1", "3"):
        await test_nigerian_pidgin()
    
    if choice in ("2", "3"):
        await interactive_tts()
    
    print("\n✅ Voice output test complete!")
    print("   Audio files are in the 'voice_outputs/' folder")


if __name__ == "__main__":
    asyncio.run(main())
