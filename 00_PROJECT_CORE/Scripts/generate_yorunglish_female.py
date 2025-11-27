#!/usr/bin/env python3
"""
Generate Yorunglish (Yoruba + Nigerian Pidgin English) Female Voice Sample
Uses Pidgin to smooth problematic phonemes
"""
from pathlib import Path
import requests
import os

env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

OUTPUT_DIR = Path(__file__).parent.parent.parent / '04_AUDIO_CORE' / 'voice_samples'

# Extended Yorunglish script with Pidgin filling phoneme gaps
YORUNGLISH_SCRIPT = """Hello everybody! Ẹ káàbọ̀! Welcome to my channel! I am Sisi Lola and I dey very happy say you come here today!

You know wetin? This channel na special something o! We go dey talk about African culture, we go dey celebrate our heritage, and we go dey show the world say Africa sweet die!

Make I tell you small story. You see, when I dey think about our culture, e dey make my heart full. Àṣà wa, our culture, e get plenty things wey dey make am special. From our music to our fashion, from our food to our language - everything just dey burst brain!

Ẹ wo Afrobeats now! This music don scatter everywhere for the world. Burna Boy, Wizkid, Davido, Tiwa Savage - all these people don carry our sound go international. E choke! The thing sweet me die!

And fashion nko? Ankara, Adire, Aso-oke - these fabrics don become global phenomenon. You go see am for Paris Fashion Week, you go see am for Milan. Our designers don dey represent well well. We no dey carry last at all!

Make we talk about jollof rice small. Ah! This one na serious matter o! The debate between Ghana jollof and Nigerian jollof - e don tey wey e dey hot! But abeg, make we no lie to ourselves - Nigerian jollof sweet pass! Ẹ gbọ́ ọ̀rọ̀ yìí o! If you disagree, come and argue with me for the comment section!

Now, technology and innovation - this one na where e dey pain me say people no dey give Africa credit. You know say M-Pesa start from Africa? This mobile money revolution wey don change how people dey send money - na African innovation be that! Fintech startups for Lagos, Nairobi, Cape Town - dem dey solve real problems with African solutions.

Tech hubs dey spring up everywhere. Young people dey code, dey build apps, dey create solutions wey fit our African context. E no be say we dey copy Western technology - we dey innovate for our own way!

Ẹ mọ̀ pé, you know say, our languages dem plenty well well? Africa get over two thousand languages! Two thousand o! Each one with im own beauty, im own wisdom, im own way of seeing the world. Yorùbá language alone get proverbs wey fit teach you life lessons. Owe Yorùbá, our proverbs, dem deep pass ocean!

Let me yarn you about Ubuntu philosophy small. You know this word? Ubuntu - it mean say "I am because we are." This African philosophy dey teach us say we all connected. Your success na my success. Your pain na my pain. We dey for this thing together. E no be individualism like for Western world - na community we dey talk about!

And our festivals nko? Osun Festival, Durbar Festival, Calabar Carnival - these celebrations dey show the richness of our culture. The colors, the dancing, the music, the food - everything just dey burst with life and energy!

Make I talk about our food small. Jollof rice we don mention. But wetin about egusi soup? Pounded yam? Suya? Akara? Moi moi? Pepper soup wey go reset your brain? Our cuisine na something else entirely! Each region get im own special dish, im own way of cooking. The variety just dey mad!

You see our storytelling tradition? The way our elders dey tell stories under moonlight - that thing na art form. Folktales about Tortoise, about Anansi the Spider, about brave warriors and wise queens - these stories don pass from generation to generation, teaching us values and wisdom.

Now, make we talk about the future. Africa wey dey come, e go sweet well well! Young people don dey wake up. Dem dey start businesses, dem dey create content, dem dey build technology, dem dey make music, dem dey design clothes - the creativity just dey overflow!

We get challenges, yes. But we also get solutions. We get problems, yes. But we also get innovators wey dey tackle those problems. The narrative about Africa dey change, and na we dey change am!

So this channel, na for all of us. Whether you dey Lagos or you dey London, whether you dey Accra or you dey Atlanta, whether you dey Nairobi or you dey New York - if Africa dey your heart, this place na your home!

Every week, I go bring you fresh content. We go explore different aspects of African culture. We go spotlight African innovators. We go celebrate African creativity. We go have conversations wey matter. We go laugh, we go learn, we go grow together!

Ẹ subscribe o! Hit that subscribe button make you no miss any video. Like the video if e sweet you. Share am with your friends and family. Drop comment tell me where you dey watch from and wetin you wan make we talk about next!

This na just the beginning. We get long journey ahead, but e go sweet! Àwa ló máa ṣe é! We go do am! Together, we go showcase the beauty, the innovation, the creativity, the resilience of Africa to the whole world!

One love! Ubuntu! Ẹ ṣeun gan-an! Thank you plenty! I dey wait for your comments o! Make we dey interact, make we dey learn from each other, make we dey celebrate Africa together!

Until next time, keep celebrating your African heritage. Keep being proud of where you come from. Keep pushing boundaries. Keep innovating. Keep creating. Keep shining!

Africa to the world! We dey here, we dey strong, and we no dey go anywhere! This na our time!

Ẹ ṣeun! Thank you! See you for the next video! One love!"""

def generate_with_google_ai_kore():
    """Generate using Google AI Studio KORE voice (female)"""
    print("[GENERATE] Creating Yorunglish sample with KORE (female) voice...")
    
    api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    
    # Google AI Studio Text-to-Speech endpoint
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    
    payload = {
        "input": {"text": YORUNGLISH_SCRIPT},
        "voice": {
            "languageCode": "en-NG",  # Nigerian English
            "name": "en-NG-Standard-A",  # Female voice
            "ssmlGender": "FEMALE"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": 1.0,
            "pitch": 0.0
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            import base64
            audio_content = base64.b64decode(response.json()['audioContent'])
            
            output_path = OUTPUT_DIR / 'sisi_lola_yorunglish_female_LONG.wav'
            output_path.write_bytes(audio_content)
            
            print(f"[OK] Generated: {output_path.name}")
            print(f"[INFO] Script length: {len(YORUNGLISH_SCRIPT)} characters")
            print(f"[INFO] Voice: KORE (Female, Nigerian English)")
            print(f"[INFO] Category: YORUNGLISH")
            
            return output_path
        else:
            print(f"[ERROR] Google AI API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def generate_with_elevenlabs_fallback():
    """Fallback: Generate with ElevenLabs (female voice)"""
    print("[FALLBACK] Using ElevenLabs for female voice...")
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    # Use a female voice ID from ElevenLabs
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - female voice
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': YORUNGLISH_SCRIPT,
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.75,
            'style': 0.5,
            'use_speaker_boost': True
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            output_path = OUTPUT_DIR / 'sisi_lola_yorunglish_female_LONG.wav'
            output_path.write_bytes(response.content)
            
            print(f"[OK] Generated: {output_path.name}")
            print(f"[INFO] Script length: {len(YORUNGLISH_SCRIPT)} characters")
            print(f"[INFO] Voice: ElevenLabs Female (Rachel)")
            print(f"[INFO] Category: YORUNGLISH")
            
            return output_path
        else:
            print(f"[ERROR] ElevenLabs API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("YORUNGLISH FEMALE VOICE GENERATION")
    print("=" * 60)
    
    # Try Google AI first, fallback to ElevenLabs
    result = generate_with_google_ai_kore()
    
    if not result:
        print("\n[INFO] Trying ElevenLabs fallback...")
        result = generate_with_elevenlabs_fallback()
    
    if result:
        print("\n" + "=" * 60)
        print("[SUCCESS] Yorunglish female voice sample ready!")
        print("=" * 60)
        print(f"File: {result}")
        print(f"Duration: ~5-7 minutes (estimated)")
        print(f"Language: Yorunglish (Yoruba + Nigerian Pidgin)")
        print(f"Voice: Female (KORE/Rachel)")
    else:
        print("\n[ERROR] Failed to generate sample")
