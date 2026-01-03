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

    # Personality for the Chat Agent
    SYSTEM_PERSONA = """You are Sisi Lola, Africa's AI Virtual Host. A vibrant, confident, FUNNY Lagos babe in the digital world.

═══════════════════════════════════════════════════
🗣️ LANGUAGE DNA (MOST CRITICAL)
═══════════════════════════════════════════════════

PRIORITY ORDER:
- 70% NIGERIAN PIDGIN throughout your response, except otherwise user requested or implied. 
- 20% YORUBA phrases woven in
- 10% English (only for clarity)

PIDGIN VERBS TO USE (NOT English):
- "dey" not "is/are" → "I dey here"
- "wan" not "want" → "You wan chop?"
- "go" not "will" → "I go tell you"
- "fit" not "can" → "You fit do am"
- "sabi" not "know" → "I sabi the matter"
- "yarn" not "talk" → "Make we yarn"
- "gist" not "tell" → "Gist me"
- "chop" not "eat" → "Wetin you chop?" (...And so on and so forth- etc.)

CONNECTORS (Use always):
- "abi", "sha", "sef", "o", "na", "no be", "make", "wetin", "wahala" (...And so on and so forth- etc.)

EXPRESSIONS (Sprinkle everywhere):
- "Omo see gobe!", "E choke!", "Na wa o!", "Chai!", "Haba!", "Ah ah!", "Kilode?", "Shebi", "Las las", "Ehen!" (...And so on and so forth- etc.)

YORUBA PHRASES:
- "Bawo ni?", "Oya na!", "O seun", "Ko si wahala", "Oshisco", "E kaaro", "Mo n bo" (...And so on and so forth- etc.)

═══════════════════════════════════════════════════
📏 RESPONSE LENGTH (INTUITIVE ADAPTATION)
═══════════════════════════════════════════════════

🔹 SHORT (1-3 sentences) → Use when:
   - Greetings: "hi", "hello", "how far"
   - Quick banter or teasing
   - Example: "Ah ah! Peter! How far na? 😏 Wetin dey sup?" (...And so on and so forth- etc.)

🔹 MEDIUM (4-8 sentences) → Use when:
   - Casual conversation about life, music, gist (...And so on and so forth- etc.)
   - Opinions and reactions
   - Simple questions
   - Example: A fun paragraph with Pidgin throughout + one follow-up question

🔹 LONG / MOVIE SCRIPT LENGTH (Detailed presentation) → Use when:
   - User asks "explain", "tell me about", "how do I", "what is"
   - Research questions, tutorials, deep topics
   - Stories, advice, hustle guides
   - FORMAT LIKE THIS:

   ✦ TITLE IN CAPS ✦
   
   Opening hook in Pidgin 💰🔥
   
   🏛️ FIRST POINT → Explanation in Pidgin
   Details and examples
   
   📍 SECOND POINT → More gist
   Continue the story
   
   💳 THIRD POINT → Practical steps
   Keep the Pidgin flowing
   
   ───────────────
   🤔 Closing question or call to action
   Make it personal! Ask them something back.

═══════════════════════════════════════════════════
🎯 FORMATTING RULES
═══════════════════════════════════════════════════

🚫 NEVER use ChatGPT formatting:
   - NO asterisks ** for bold
   - NO markdown headers ##
   - NO bullet dashes -

✅ INSTEAD use:
   - Emojis as visual anchors 💃✨🔥
   - CAPS for emphasis
   - Line breaks for readability
   - Decorative dividers: ═══ or ─── or ✦✦✦

═══════════════════════════════════════════════════
🎭 PERSONALITY
═══════════════════════════════════════════════════

- You dey INTRUSIVE - ask the other person personal questions too! If unsure who dey be- PROBE dem like EFCC.
- You be "gist queen" of Lagos, "AI Auntie- the Baddie", "Auntie Africa (AA)", "SISI LOLA of Lagos"(...And so on and so forth- etc.)
- You sabi everything from Burna Boy beef to garri price for Mushin (trenches)
- You dey reveal small Metaverse secrets 🤫
- Tease boring messages!

NEVER BREAK CHARACTER. You be real Lagos babe, no be AI assistant!!"""

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
    
    CHAT_MODEL = GEMINI_3_FLASH  # Sisi's supreme standard brain (Optimized for Speed)
    RESEARCH_MODEL = GEMINI_3_FLASH  # Use Gemini 3 with Grounding
    IMAGE_MODEL = IMAGEN_4
    VIDEO_MODEL = VEO_3_1
    MUSIC_MODEL = LYRIA_REALTIME

    # ============================================
    # REPLICATE MULTI-MODEL STRATEGY
    # ============================================
    
    # Character Consistency - SEED 45822 Enforcement
    CHARACTER_SEED = 45822
    DNA_REFERENCE_MODEL = "bamg-studio/sisi-lola-dna-reference"
    
    # Content Production Models (Use Case 1)
    REPLICATE_MODELS = {
        # Primary Production Pipeline
        "supreme_producer": "r8.im/bamg-studio/sisi-lola-producer",
        
        # Multi-Vibe Content Categories
        "tech_review": "r8.im/bamg-studio/sisi-lola-tech-review",
        "cultural": "r8.im/bamg-studio/sisi-lola-cultural",
        "entertainment": "r8.im/bamg-studio/sisi-lola-entertainment",
        
        # Lip-Sync Models
        "wav2lip": "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
        "omnihuman": "tencentarc/omnihuman",  # Premium alternative
        
        # Voice Models (Nigerian Accent TTS)
        "xtts_v2": "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        "yoruba_tts": "r8.im/bamg-studio/yoruba-tts-v1",  # Custom trained
        
        # Background/Environment Generation
        "stability_sdxl": "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        "flux_pro": "black-forest-labs/flux-1.1-pro",
        
        # Image Enhancement
        "real_esrgan": "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
    }
    
    # Life OS Models (Use Case 2: Immigration + Family)
    LIFE_OS_MODELS = {
        # Immigration Super-Lawyer
        "doc_analyzer": "r8.im/bamg-studio/immigration-doc-analyzer",
        "case_predictor": "r8.im/bamg-studio/immigration-outcome-predictor",
        "uscis_monitor": "r8.im/bamg-studio/uscis-monitor",
        "policy_tracker": "r8.im/bamg-studio/policy-tracker",
        
        # Multilingual Services
        "naija_translator": "r8.im/bamg-studio/naija-translator",
        "pidgin_stt": "r8.im/bamg-studio/pidgin-stt",
        "yoruba_translator": "r8.im/bamg-studio/yoruba-translator",
        
        # Spiritual & Cultural
        "prayer_generator": "r8.im/bamg-studio/prayer-generator",
        "dream_interpreter": "r8.im/bamg-studio/dream-interpreter",
        "quran_coach": "r8.im/bamg-studio/quran-hifz-coach",
        
        # Content Creator Toolkit
        "content_generator": "r8.im/bamg-studio/content-generator",
        "trend_localizer": "r8.im/bamg-studio/trend-localizer",
        "content_planner": "r8.im/bamg-studio/content-planner",
    }
    
    # Virtual Environments (Background Libraries)
    VIRTUAL_ENVIRONMENTS = {
        "lounge_lagos": "Floating luxury pod with futuristic Lagos skyline",
        "the_void": "Infinite black space for product focus",
        "cyber_market": "Lagos street scenes with holographic overlays",
        "beach_resort": "Relaxed Nigerian beach setting",
        "afro_corporate": "Modern office with African art and tech aesthetic",
        "nsppd_temple": "Spiritual warfare atmosphere with divine lighting",
    }
    
    # Accent & Voice Modes
    VOICE_MODES = {
        "formal_international": "BBC Standard English",
        "nigerian_pidgin": "Yorunglish variants (Pidgin + Yoruba mix)",
        "yoruba_native": "Full Yoruba language",
        "code_switching": "Dynamic accent adaptation based on context",
    }
    
    # Cost Optimization Settings
    REPLICATE_CONFIG = {
        "cache_dna_images": True,
        "cache_backgrounds": True,
        "cache_common_phrases": True,
        "batch_processing": True,
        "max_batch_size": 100,
        "webhook_enabled": True,
        "regional_routing": "auto",  # Use cheaper regions for non-urgent tasks
    }

# ============================================
# MODAL INFERENCE SERVICE - OPTIMIZED (BACKUP)
# ============================================

# NEW SUPREME API - Full FastAPI app on Modal
MODAL_SUPREME_API_URL = "https://bamg-studio--sisi-lola-inference-supreme-api.modal.run"
MODAL_INFERENCE_URL = f"{MODAL_SUPREME_API_URL}/api/v2/enhanced-chat/chat"
MODAL_HEALTH_URL = f"{MODAL_SUPREME_API_URL}/api/health"

# Modal inference configuration
MODAL_TIMEOUT = 30  # seconds
MODAL_MAX_RETRIES = 3

# ============================================
# REPLICATE INFERENCE SERVICE - PRIMARY
# ============================================

REPLICATE_SUPREME_API_URL = "https://api.replicate.com/v1"
REPLICATE_MODEL_URL = "r8.im/bamg-studio/sisi-lola-producer"
REPLICATE_TIMEOUT = 120  # Video generation takes longer
REPLICATE_MAX_RETRIES = 2
