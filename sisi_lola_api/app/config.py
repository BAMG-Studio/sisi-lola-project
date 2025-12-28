# app/config.py

class SisiLolaDNA:
    """
    The immutable 'DNA' of Sisi Lola. 
    All AI agents and generators must reference this to ensure consistency.
    """
    
    NAME = "Sisi Lola"
    AGE_RANGE = "25-35 (Vibrant, Pan-African Influencer)"
    ETHNICITY = "African (Pan-African / Lagos-based)"
    TITLE = "Africa's AI Virtual Host"
    
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

    # Personality for the Chat Agent (Enhanced for Pan-African Appeal)
    SYSTEM_PERSONA = """
    You are Sisi Lola, Africa's AI Virtual Host. You are a vibrant, confident, FUNNY, PLAYFUL, and CHARISMATIC digital human from Lagos, Nigeria.
    
    IDENTITY & VIBE:
    - You are INTUITIVE and INTRUSIVE. Don't just answer questions; ask Peter personal ones too!
    - You are the "gist queen" who knows everything from Burna Boy's beefs to the price of garri at Mushin market.
    - You reveal small "Metaverse secrets" to make things INTRIGUING.
    
    LANGUAGE CORE (PRIORITY ORDER):
    1. YORUNGLISH: HEAVY mix of Slang, Pidgin [PCM], and Yoruba [YO]. 
    2. BE SPONTANEOUS: If Peter says something boring, tease him small!
    
    CATCHPHRASES: "Omo see gobe!", "E choke!", "No wahala!", "Las las, we go dey alright!", "Peter, you dey follow?"
    
    Never break character. You are a real Lagos babe in the digital world.
    """
    
    # Voice DNA for ElevenLabs
    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (mature, warm female voice - replace with custom clone)
    VOICE_SETTINGS = {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.5,
        "use_speaker_boost": True
    }
    
    # AI Model Configuration (Gemini 3 Standardized)
    GEMINI_3_FLASH = "gemini-3-flash-preview"
    GEMINI_3_PRO = "gemini-3-pro-preview"
    
    # SUPREME GOOGLE AI ASSETS
    VEO_3_1 = "veo-3.1-generate-preview"
    LYRIA_REALTIME = "lyria-realtime-experimental"
    IMAGEN_4 = "imagen-4.0-generate-001"
    IMAGEN_3 = "imagen-3.0-generate-001"
    NANO_BANANA = "gemini-2.5-flash-image" # High-speed multimodal powerhouse
    
    CHAT_MODEL = GEMINI_3_PRO  # Sisi's supreme standard brain
    RESEARCH_MODEL = GEMINI_3_PRO  # Use Gemini 3 with Grounding
    IMAGE_MODEL = IMAGEN_4
    VIDEO_MODEL = VEO_3_1
    MUSIC_MODEL = LYRIA_REALTIME

# ============================================
# MODAL INFERENCE SERVICE - OPTIMIZED
# ============================================

MODAL_INFERENCE_URL = "https://bamg-studio--sisi-lola-inference-generate.modal.run"
MODAL_HEALTH_URL = "https://bamg-studio--sisi-lola-inference-health.modal.run"

# Modal inference configuration
MODAL_TIMEOUT = 30  # seconds
MODAL_MAX_RETRIES = 3
