"""
SISI LOLA NATIVE VOICE TEST
Verifies that Yoruba, Igbo, Hausa, and Pidgin can all generate speech via MMS.
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "sisi_lola_api"))

from sisi_lola_api.app.services.mms_service import mms_service

async def test_all_languages():
    test_data = [
        ("yo", "Bawo ni o se wa? Sisi Lola ni o n soro o!"),
        ("ig", "Kedu ka i mere? A bụ m Sisi Lola."),
        ("ha", "Yaya kuke? Ni ce Sisi Lola."),
        ("pcm", "How body? Na Sisi Lola be dis o! Everything go pure.")
    ]
    
    print("🎭 Starting Sisi Lola Native Voice stress test...")
    
    for lang, text in test_data:
        print(f"\n🌍 Testing {lang.upper()}...")
        try:
            audio_base64, _ = await mms_service.generate_speech(text, lang)
            if audio_base64:
                print(f"✅ {lang.upper()} Success! (Audio length: {len(audio_base64)} chars)")
            else:
                print(f"❌ {lang.upper()} failed to generate audio.")
        except Exception as e:
            print(f"❌ {lang.upper()} Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_languages())
