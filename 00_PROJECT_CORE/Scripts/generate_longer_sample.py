#!/usr/bin/env python3
"""
Generate longer Yoruba voice sample (3-5 minutes)
"""
from yoruba_tts_engine import SisiLolaVoiceEngine
from pathlib import Path

LONG_SCRIPT = """Ẹ káàbọ̀! Sisi Lola ni mo jẹ́! Mo dúpẹ́ pé ẹ wá sí channel mi.

Lónií, a máa sọ̀rọ̀ nípa àṣà Áfríkà, innovation, àti ohun gbogbo tó ń ṣẹlẹ̀ ní continent wa.

Ẹ mọ̀ pé Áfríkà ni ilẹ̀ tó ní culture tó pọ̀ jù lọ ní gbogbo ayé? A ní languages tó lé ní ẹgbẹ̀rún méjì. A ní music tó ń jó, fashion tó ń shine, àti innovation tó ń ṣe àyípadà.

Ẹ wo Afrobeats! Music yìí ti di global phenomenon. From Fela Kuti to Burna Boy, Wizkid, Davido, Tiwa Savage - àwọn artists wa ń ṣe waves ní gbogbo ayé.

Àti technology nko? Ẹ ti gbọ́ nípa M-Pesa? Innovation yìí ti ṣe àyípadà sí bí àwọn ènìyàn ṣe ń fi owó ránṣẹ́ ní Africa. Fintech startups wa ń solve problems tó pọ̀.

E choke! This one sweet me die! Àbí ẹ̀yin ò rí i bẹ́ẹ̀?

Ẹ wo fashion wa! Ankara, Adire, Aso-oke - àwọn fabrics yìí ti di international. Fashion designers wa ń showcase ní Paris, Milan, New York. We dey represent!

Àti food nko? Jollof rice debate yìí - Ghana versus Nigeria - e don tey wey e dey hot! But make we no lie, Nigerian jollof sweet pass! Ẹ gbọ́ ọ̀rọ̀ yìí o!

Innovation tó ń ṣẹlẹ̀ ní tech hubs across Africa - Lagos, Nairobi, Cape Town, Accra - e plenty! Startups ń solve African problems with African solutions.

Àwa ló máa ṣe é! We go do am! Áfríkà tó ń bọ̀ yìí máa dára gan-an!

So ẹ subscribe sí channel mi o! Ẹ má gbàgbé láti like àti share. Ẹ comment, tell me where you're watching from. Lagos? Ibadan? Abuja? Or you dey abroad?

Every week, a máa bring fresh content about African culture, innovation, music, fashion, food - everything wey dey make Africa special.

This na just the beginning. We get plenty stories to tell, plenty innovations to showcase, plenty culture to celebrate.

Ẹ ṣeun gan-an! Thank you plenty! Má ríi yín lọ́la. Until next time, keep celebrating Africa!

One love! Ubuntu! I am because we are!"""

def generate_long_sample():
    print("[GENERATE] Creating 3-5 minute Yoruba sample...")
    
    engine = SisiLolaVoiceEngine()
    output_path = Path(__file__).parent.parent.parent / '04_AUDIO_CORE' / 'voice_samples' / 'sisi_lola_long_intro.wav'
    
    result = engine.generate_speech(LONG_SCRIPT, output_path)
    
    print(f"[OK] Long sample generated: {result}")
    print(f"[INFO] Script length: {len(LONG_SCRIPT)} characters")
    
    return result

if __name__ == '__main__':
    generate_long_sample()
