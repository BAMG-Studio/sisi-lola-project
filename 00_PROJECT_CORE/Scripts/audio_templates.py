#!/usr/bin/env python3
"""
AUDIO ASSET GENERATION TEMPLATES
Sisi Lola Project - Voice, Music, and Sound Design Automation
"""

import json
from pathlib import Path

# ============================================================================
# VOICE CLONING SCRIPTS (ELEVENLABS / PROFESSIONAL RECORDING)
# ============================================================================

VOICE_SCRIPTS = {
    "professional_introduction": {
        "context": "Professional podcast introduction",
        "tone": "Warm, authoritative, welcoming",
        "duration": "30-45 seconds",
        "script": """
        Hello and welcome. I'm Sisi Lola, and you're tuning into a space where 
        technology meets culture, where innovation intersects with tradition, 
        and where the future of our digital world takes shape. Whether you're 
        here for the first time or you're a returning friend, I'm thrilled to 
        have you. Today, we're exploring something truly fascinating, so let's 
        dive in together.
        """
    },
    
    "casual_conversational": {
        "context": "Casual chat, relatable content",
        "tone": "Friendly, energetic, approachable",
        "duration": "20-30 seconds",
        "script": """
        Okay, so you know how everyone's been buzzing about AI lately? Like, 
        it's everywhere! But here's the thing—most people don't actually know 
        what's happening behind the scenes. So, let me break it down for you 
        in a way that actually makes sense, because trust me, once you get it, 
        you'll be hooked.
        """
    },
    
    "nigerian_pidgin_authentic": {
        "context": "Cultural connection, humor",
        "tone": "Playful, authentic, relatable",
        "duration": "15-25 seconds",
        "script": """
        Ah ah! Wetin dey happen? See this technology thing oh, e don change 
        everything for this world! No be small thing. Make I tell you something—
        the way things dey go now, if you no sabi tech, you go just dey look 
        like mumu. But no worry, I go explain am for you sotay you go understand well well.
        """
    },
    
    "excited_announcement": {
        "context": "Product launch, major news",
        "tone": "High energy, enthusiastic, infectious",
        "duration": "15-20 seconds",
        "script": """
        Okay, okay, okay! Listen, I am SO excited about this! Like, genuinely, 
        this is one of those moments where everything just clicks. Are you ready? 
        Because what I'm about to show you is absolutely game-changing. Let's go!
        """
    },
    
    "thoughtful_analysis": {
        "context": "Deep dive, educational content",
        "tone": "Contemplative, measured, intelligent",
        "duration": "40-60 seconds",
        "script": """
        When we think about artificial intelligence, it's easy to get caught up 
        in the hype—the sci-fi scenarios, the dystopian fears. But what if we 
        took a step back and really examined what's happening right now, today, 
        in this moment? The reality is far more nuanced, far more interesting, 
        and honestly, far more human than we often give it credit for. Let me 
        explain what I mean.
        """
    },
    
    "empathetic_support": {
        "context": "Addressing challenges, offering help",
        "tone": "Compassionate, understanding, supportive",
        "duration": "25-35 seconds",
        "script": """
        I know this can feel overwhelming. Technology moves fast, and sometimes 
        it feels like we're all just trying to keep up. But here's what I want 
        you to remember: you're not alone in this. We're all learning, we're all 
        growing, and it's okay to take it one step at a time. Let's figure this 
        out together.
        """
    },
    
    "humorous_anecdote": {
        "context": "Entertainment, personality showcase",
        "tone": "Light, funny, self-aware",
        "duration": "30-40 seconds",
        "script": """
        So, funny story. Last week I was trying to explain NFTs to my cousin, 
        right? And halfway through, she just looked at me and said, 'Sisi, you're 
        speaking English, but I don't understand a single word.' And honestly? 
        Fair. That's when I realized we need to do better at making this stuff 
        accessible. So here's NFTs, but like, for real people.
        """
    },
    
    "call_to_action": {
        "context": "Engagement prompt, subscription drive",
        "tone": "Encouraging, direct, friendly",
        "duration": "15-20 seconds",
        "script": """
        If you found this valuable, do me a favor—share it with someone who 
        needs to hear it. Hit that subscribe button, drop a comment with your 
        thoughts, and let's keep this conversation going. I'll see you in the 
        next one!
        """
    },
    
    "meditation_asmr": {
        "context": "Calming content, ASMR variant",
        "tone": "Whispered, soothing, slow",
        "duration": "60-90 seconds",
        "script": """
        Take a deep breath with me... in... and out. Feel the weight of the day 
        slowly lifting from your shoulders. In this moment, there's nowhere else 
        you need to be. The technology, the notifications, the endless scroll—
        they can all wait. Right now, it's just you, your breath, and this quiet 
        space we've created together. Let yourself relax... completely... deeply... 
        peacefully.
        """
    },
    
    "tech_review_intro": {
        "context": "Product review opening",
        "tone": "Professional, curious, analytical",
        "duration": "20-30 seconds",
        "script": """
        Today we're taking a closer look at something that's been generating a 
        lot of buzz in the tech community. I've been testing this for the past 
        two weeks, and I have thoughts—some good, some not so good. So let's 
        cut through the marketing hype and talk about what this actually does, 
        and more importantly, who it's actually for.
        """
    }
}

# ============================================================================
# MUSIC BED SPECIFICATIONS (SUNO AI / UDIO / LICENSED)
# ============================================================================

MUSIC_BEDS = {
    "afrofuture_intro_1": {
        "genre": "Afrobeat + Synthwave Fusion",
        "tempo": "128 BPM",
        "duration": "3 minutes (loopable)",
        "mood": "Energetic, futuristic, optimistic",
        "instruments": "Talking drums, synth bass, electric piano, electronic percussion",
        "structure": "Intro (8 bars) → A section (16 bars) → B section (16 bars) → Bridge (8 bars) → Loop",
        "prompt_for_ai": "Afrobeat instrumental fused with synthwave, 128 BPM, talking drums, warm synth bass, electric piano chords, electronic hi-hats, futuristic yet organic, podcast intro music, loopable, energetic and optimistic mood, no vocals",
        "usage": "Podcast intros, transitions, background during segments"
    },
    
    "afrofuture_chill_2": {
        "genre": "Afro-Electronic Downtempo",
        "tempo": "95 BPM",
        "duration": "4 minutes (loopable)",
        "mood": "Relaxed, sophisticated, contemplative",
        "instruments": "Kalimba, ambient pads, subtle percussion, soft bass",
        "structure": "Ambient intro (16 bars) → Groove section (24 bars) → Breakdown (8 bars) → Loop",
        "prompt_for_ai": "Downtempo afro-electronic music, 95 BPM, kalimba melody, warm ambient pads, soft bass, subtle African percussion, relaxed and sophisticated, perfect for background conversation, loopable, instrumental only",
        "usage": "Interview backgrounds, thoughtful discussions, educational content"
    },
    
    "afrofuture_hype_3": {
        "genre": "Afro-Trap / Hip-Hop",
        "tempo": "140 BPM",
        "duration": "2 minutes 30 seconds",
        "mood": "Hype, confident, powerful",
        "instruments": "808 bass, trap hi-hats, djembe, brass stabs, synth leads",
        "structure": "Buildup (4 bars) → Drop (16 bars) → Break (8 bars) → Final drop (16 bars)",
        "prompt_for_ai": "Afro-trap instrumental, 140 BPM, heavy 808 bass, rapid hi-hats, djembe accents, brass stabs, powerful and confident, hype energy, suitable for announcements and climactic moments, no vocals",
        "usage": "Announcements, product reveals, high-energy segments"
    },
    
    "afrofuture_ambient_4": {
        "genre": "Ambient Afro-Electronic",
        "tempo": "70 BPM",
        "duration": "5 minutes (loopable)",
        "mood": "Ethereal, spacious, meditative",
        "instruments": "Synth pads, distant vocals (wordless), soft percussion, nature sounds",
        "structure": "Evolving ambient texture with subtle rhythmic elements",
        "prompt_for_ai": "Ambient electronic music with African influence, 70 BPM, lush synth pads, distant wordless vocals, soft hand percussion, nature sounds, ethereal and meditative, spacious production, long evolving textures, loopable",
        "usage": "Meditation content, calm intros, reflective segments"
    },
    
    "afrofuture_funk_5": {
        "genre": "Afro-Funk / Nu-Disco",
        "tempo": "118 BPM",
        "duration": "3 minutes 30 seconds",
        "mood": "Groovy, fun, danceable",
        "instruments": "Funk guitar, slap bass, horns, congas, wah-wah effects",
        "structure": "Intro (8 bars) → Groove A (16 bars) → Groove B (16 bars) → Solo section (8 bars) → Outro",
        "prompt_for_ai": "Afro-funk instrumental, 118 BPM, groovy guitar riffs, slap bass, horn section, congas, wah-wah effects, danceable and fun, Nu-disco influence, retro-futuristic, no vocals",
        "usage": "Upbeat segments, lifestyle content, fun product reviews"
    }
}

# ============================================================================
# SOUNDSCAPE SPECIFICATIONS
# ============================================================================

SOUNDSCAPES = {
    "studio_ambient_quiet": {
        "duration": "5 minutes (seamless loop)",
        "elements": [
            "Subtle HVAC/air conditioning hum (20 Hz low pass)",
            "Distant computer fans (very quiet)",
            "Occasional holographic interface beeps (sparse)",
            "Room tone (professional studio quality)"
        ],
        "mix": "All elements at -40dB to -30dB, very subtle",
        "purpose": "Fill silence in studio recordings without distraction"
    },
    
    "lagos_street_morning": {
        "duration": "3 minutes (seamless loop)",
        "elements": [
            "Distant traffic (cars, okadas/motorcycles)",
            "Market vendor calls (unintelligible, atmospheric)",
            "Birds chirping (African species)",
            "Gentle breeze with fabric rustling",
            "Occasional horn honks (far away)"
        ],
        "mix": "Natural outdoor ambience, -18dB to -12dB",
        "purpose": "On-location content, cultural authenticity"
    },
    
    "tech_lab_hum": {
        "duration": "4 minutes (seamless loop)",
        "elements": [
            "Server room white noise",
            "Electrical hum (60Hz and harmonics)",
            "Occasional hard drive clicks",
            "LED indicator beeps (very sparse)",
            "Cooling fan oscillation"
        ],
        "mix": "Technical, clean, modern, -30dB to -24dB",
        "purpose": "Tech review segments, lab environments"
    },
    
    "luxury_lounge_subtle": {
        "duration": "5 minutes (seamless loop)",
        "elements": [
            "Soft jazz in far distance (barely audible)",
            "Quiet conversation murmur (unintelligible)",
            "Glass clinks (very occasional)",
            "Soft footsteps on carpet",
            "Gentle ambient music (luxurious)"
        ],
        "mix": "Sophisticated, -28dB to -20dB",
        "purpose": "Interview settings, conversation backgrounds"
    },
    
    "cyber_club_neon": {
        "duration": "2 minutes (loop)",
        "elements": [
            "Distant electronic music (muffled bass)",
            "Neon sign buzzing",
            "Holographic ad sound effects",
            "Crowd energy (distant)",
            "Urban nightlife atmosphere"
        ],
        "mix": "Vibrant, energetic, -20dB to -15dB",
        "purpose": "Nightlife content, urban culture segments"
    }
}

# ============================================================================
# BINAURAL SOUND EFFECTS
# ============================================================================

BINAURAL_EFFECTS = {
    "hologram_appear": {
        "description": "Holographic interface appearing",
        "duration": "1.5 seconds",
        "spatial": "Appears 2m in front, slightly above eye level",
        "characteristics": "Crystalline shimmer, digital particles, ascending pitch"
    },
    
    "hologram_dismiss": {
        "description": "Holographic interface closing",
        "duration": "1 second",
        "spatial": "Collapses to center point",
        "characteristics": "Reverse shimmer, descending pitch, fade out"
    },
    
    "teleport_whoosh": {
        "description": "VR teleportation sound",
        "duration": "0.8 seconds",
        "spatial": "Surrounds user, moves from back to front",
        "characteristics": "Whoosh, spatial displacement, brief silence, arrival tone"
    },
    
    "button_press": {
        "description": "UI button activation",
        "duration": "0.2 seconds",
        "spatial": "Localized to button position",
        "characteristics": "Soft click, satisfying feedback, minimal reverb"
    },
    
    "notification_ping": {
        "description": "Incoming message/notification",
        "duration": "0.5 seconds",
        "spatial": "Appears from right side, 45° angle",
        "characteristics": "Pleasant chime, not intrusive, clear pitch"
    }
}

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_voice_scripts(output_dir):
    """Export voice scripts to individual text files"""
    voice_dir = Path(output_dir) / "01_Voice_Samples"
    voice_dir.mkdir(parents=True, exist_ok=True)
    
    for key, data in VOICE_SCRIPTS.items():
        filename = voice_dir / f"SCRIPT_{key}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {key.replace('_', ' ').title()}\n\n")
            f.write(f"**Context:** {data['context']}\n")
            f.write(f"**Tone:** {data['tone']}\n")
            f.write(f"**Duration:** {data['duration']}\n\n")
            f.write("---\n\n")
            f.write("## SCRIPT:\n\n")
            f.write(data['script'].strip())
            f.write("\n\n---\n\n")
            f.write("## DIRECTION NOTES:\n\n")
            f.write("- Pace: Natural, conversational (not rushed)\n")
            f.write("- Accent: Nigerian-British (Lagos to London)\n")
            f.write("- Emphasis: Let emotion guide delivery\n")
            f.write("- Breath: Natural pauses, don't over-edit\n")
            f.write("- Energy: Match the tone specified above\n")
    
    print(f"✓ Exported {len(VOICE_SCRIPTS)} voice scripts to {voice_dir}")

def export_music_specs(output_dir):
    """Export music bed specifications"""
    music_dir = Path(output_dir) / "04_Music_Beds"
    music_dir.mkdir(parents=True, exist_ok=True)
    
    filename = music_dir / "MUSIC_SPECIFICATIONS.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(MUSIC_BEDS, f, indent=2)
    
    # Also create readable markdown
    md_filename = music_dir / "MUSIC_GUIDE.md"
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write("# MUSIC BED SPECIFICATIONS\n\n")
        for key, data in MUSIC_BEDS.items():
            f.write(f"## {key.replace('_', ' ').title()}\n\n")
            for field, value in data.items():
                f.write(f"**{field.replace('_', ' ').title()}:** {value}\n\n")
            f.write("---\n\n")
    
    print(f"✓ Exported {len(MUSIC_BEDS)} music specifications to {music_dir}")

def export_soundscape_specs(output_dir):
    """Export soundscape specifications"""
    soundscape_dir = Path(output_dir) / "03_Soundscapes_Ambient"
    soundscape_dir.mkdir(parents=True, exist_ok=True)
    
    filename = soundscape_dir / "SOUNDSCAPE_SPECS.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(SOUNDSCAPES, f, indent=2)
    
    print(f"✓ Exported {len(SOUNDSCAPES)} soundscape specs to {soundscape_dir}")

def export_binaural_effects(output_dir):
    """Export binaural effect specifications"""
    effects_dir = Path(output_dir) / "05_Binaural_Effects"
    effects_dir.mkdir(parents=True, exist_ok=True)
    
    filename = effects_dir / "BINAURAL_EFFECTS.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(BINAURAL_EFFECTS, f, indent=2)
    
    print(f"✓ Exported {len(BINAURAL_EFFECTS)} binaural effect specs to {effects_dir}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_templates.py <output_directory>")
        print("Example: python audio_templates.py ../04_AUDIO_CORE")
        sys.exit(1)
    
    output_directory = sys.argv[1]
    
    print("=" * 80)
    print("SISI LOLA AUDIO ASSET TEMPLATE GENERATOR")
    print("=" * 80)
    
    export_voice_scripts(output_directory)
    export_music_specs(output_directory)
    export_soundscape_specs(output_directory)
    export_binaural_effects(output_directory)
    
    print("\n" + "=" * 80)
    print("EXPORT COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review voice scripts for recording sessions")
    print("2. Use music prompts in Suno AI / Udio")
    print("3. Source or create soundscapes matching specs")
    print("4. Design binaural effects in spatial audio tools")
    print("=" * 80)
