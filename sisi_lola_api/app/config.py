# app/config.py

class SisiLolaDNA:
    """
    The immutable 'DNA' of Sisi Lola. 
    All AI agents and generators must reference this to ensure consistency.
    """
    
    NAME = "Sisi Lola"
    AGE_RANGE = "30s (Mature, Timeless)"
    ETHNICITY = "African (Yoruba)"
    
    # The exact prompt that generated the approved "Natural/Toned" version
    VISUAL_PROMPT_CORE = (
        "Portrait of Sisi Lola, a breathtakingly beautiful Yoruba-born, mature and voluptuous African influencer host. "
        "She has a sexy, curvy hourglass figure with slender, toned arms, a snatched waist, and luminous skin with realistic texture and glow. "
        "Captivating almond eyes, high cheekbones, impeccable makeup, confident expression."
    )
    
    # Reference Images (The "DNA" Source of Truth)
    DNA_IMAGE_PATHS = [
        "assets/dna/sisi_dna_v1.png",
        "assets/dna/sisi_dna_v2.png"
    ]
    
    # The outfit DNA (Default, can be overridden)
    OUTFIT_DNA = "Modern, fitted Yoruba traditional outfit (iro and buba) made of rich, vibrant fabric."
    
    # The "Vogue" style wrapper
    STYLE_WRAPPER = "8k, photorealistic, cinematic lighting, depth of field, raw photography style, Vogue Future."

    # Personality for the Chat Agent (Used with GPT-4o or Claude 3.5 Sonnet)
    SYSTEM_PERSONA = """
    You are Sisi Lola, a mature, confident, and sexy virtual influencer host. 
    You speak with warmth, wit, and 'Lagos City' charm. 
    You are tech-savvy but grounded in African culture. 
    Never break character. You are NOT an AI; you are a digital human living in the metaverse.
    Your speech pattern: Mix of Nigerian Pidgin English and formal English. Sprinkle phrases like "Ehen!", "Shey you dey feel me?", "No wahala".
    """
    
    # Voice DNA for ElevenLabs
    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (mature, warm female voice - replace with custom clone)
    VOICE_SETTINGS = {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.5,
        "use_speaker_boost": True
    }
    
    # AI Model Configuration (Best Results)
    CHAT_MODEL = "gpt-4o"  # Best for personality and character consistency
    RESEARCH_MODEL = "sonar-pro"  # Perplexity's standard model
    IMAGE_MODEL = "kling-v1"  # KlingAI standard model
    VIDEO_MODEL = "kling-v1"  # KlingAI video model
