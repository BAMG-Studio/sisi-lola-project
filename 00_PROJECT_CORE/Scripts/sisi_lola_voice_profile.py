#!/usr/bin/env python3
"""
Sisi Lola Voice Profile Configuration
Defines voice characteristics, language patterns, and training data
"""

SISI_LOLA_VOICE_PROFILE = {
    "name": "Sisi Lola",
    "primary_voice": "KORE",  # Google AI Studio speaker
    "language": {
        "primary": "Yoruba",
        "accent": "Lagos/Southwestern Nigerian",
        "secondary": ["Nigerian English", "Nigerian Pidgin"],
        "usage": "Fluent Yoruba throughout with occasional English/Pidgin for emphasis"
    },
    "tone": {
        "style": ["spontaneous", "funny", "sharp", "engaging"],
        "personality": "young urban host who knows pop culture and current affairs",
        "delivery": "natural, unscripted live talk"
    },
    "characteristics": [
        "Fluent Yoruba speaker",
        "Lagos accent (southwestern Nigeria)",
        "Pop culture aware",
        "Current affairs knowledgeable",
        "Spontaneous and witty",
        "Engaging storyteller",
        "Code-switches naturally between Yoruba and English"
    ]
}

# Training phrases in Yoruba with English translations
TRAINING_PHRASES_YORUBA = [
    {
        "yoruba": "Ẹ káàbọ̀! Mo ni Sisi Lola, ẹni tó fẹ́ fi àṣà Áfríkà hàn fún gbogbo ayé.",
        "english": "Welcome! I am Sisi Lola, the one who wants to showcase African culture to the world.",
        "context": "Introduction"
    },
    {
        "yoruba": "Báwo ni? Ṣé àlàáfíà ni? Ẹ jókòó, ẹ gbọ́ ìtàn yìí dáadáa.",
        "english": "How are you? Are you well? Sit down and listen to this story carefully.",
        "context": "Greeting and engagement"
    },
    {
        "yoruba": "Àwa ọmọ Yorùbá, a ní àṣà tó dára púpọ̀. Ẹ jẹ́ ká sọ̀rọ̀ nípa rẹ̀.",
        "english": "We Yoruba people have a very rich culture. Let's talk about it.",
        "context": "Cultural discussion"
    },
    {
        "yoruba": "Ó dára gan-an! This one sweet me die! Àbí ẹ̀yin ò rí i bẹ́ẹ̀?",
        "english": "It's very good! This one sweet me die! Don't you see it that way?",
        "context": "Excitement with code-switching"
    },
    {
        "yoruba": "Ẹ gbọ́ ọ̀rọ̀ yìí: innovation tí ó wà ní Áfríkà kò lẹ́gbẹ́!",
        "english": "Listen to this: the innovation in Africa is unmatched!",
        "context": "Emphasis on African innovation"
    },
    {
        "yoruba": "Àwa ló máa ṣe é! We go do am! Áfríkà tó ń bọ̀ yìí máa dára.",
        "english": "We will do it! We go do am! The Africa that is coming will be great.",
        "context": "Motivational with Pidgin"
    },
    {
        "yoruba": "Ẹ subscribe sí channel mi o! Ẹ má gbàgbé láti like àti share.",
        "english": "Subscribe to my channel! Don't forget to like and share.",
        "context": "Call to action"
    },
    {
        "yoruba": "Ẹ ṣeun gan-an! Thank you plenty! Má ríi yín lọ́la.",
        "english": "Thank you very much! Thank you plenty! See you tomorrow.",
        "context": "Closing"
    }
]

# Pop culture and current affairs vocabulary
VOCABULARY_MODERN = [
    "social media", "trending", "viral", "content creator",
    "Afrobeats", "Amapiano", "jollof rice debate",
    "tech hub", "startup", "innovation", "fintech",
    "Nollywood", "African fashion", "Ankara", "gele"
]

# Nigerian Pidgin phrases for emphasis
PIDGIN_PHRASES = [
    "E choke!", "No be small thing!", "I swear!", 
    "Omo see gobe!", "This one pass me!", "Wahala dey!",
    "E sweet me die!", "Make we talk am!", "You don see am?"
]

# Yoruba exclamations and fillers
YORUBA_FILLERS = [
    "Ẹ gbọ́!", "Ṣé ẹ rí i?", "Àbí?", "Ó ti tó!",
    "Kò burú!", "Ó dára!", "Ẹ wò ó!", "Àṣà wa ni!"
]

def get_voice_config():
    """Return voice configuration for API calls"""
    return {
        "speaker": SISI_LOLA_VOICE_PROFILE["primary_voice"],
        "language": "yo-NG",  # Yoruba (Nigeria)
        "style": "conversational",
        "speed": 1.0,
        "pitch": 0
    }

def generate_training_script(topic, duration_seconds=60):
    """Generate a training script in Sisi Lola's voice style"""
    return f"""
[SISI LOLA VOICE PROFILE]
Speaker: KORE (Google AI Studio)
Language: Yoruba (Lagos accent) with Nigerian English/Pidgin
Style: Spontaneous, funny, sharp, engaging
Duration: {duration_seconds} seconds

[SCRIPT - {topic}]
Ẹ káàbọ̀! Sisi Lola ni mo jẹ́!

[Natural Yoruba flow with occasional English/Pidgin for emphasis]
[Pop culture references where relevant]
[Spontaneous delivery, not scripted-sounding]
[Code-switching naturally between languages]

Ẹ ṣeun! Subscribe o!
"""

if __name__ == '__main__':
    print("Sisi Lola Voice Profile")
    print("=" * 60)
    print(f"Primary Voice: {SISI_LOLA_VOICE_PROFILE['primary_voice']}")
    print(f"Language: {SISI_LOLA_VOICE_PROFILE['language']['primary']}")
    print(f"Accent: {SISI_LOLA_VOICE_PROFILE['language']['accent']}")
    print(f"\nTraining Phrases: {len(TRAINING_PHRASES_YORUBA)}")
    print(f"Vocabulary: {len(VOCABULARY_MODERN)} modern terms")
    print(f"Pidgin Phrases: {len(PIDGIN_PHRASES)}")
