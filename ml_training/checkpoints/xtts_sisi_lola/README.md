---
license: apache-2.0
language:
- en
- pcm
- yo
tags:
- tts
- voice
- nigerian
- african
- speech-synthesis
- edge-tts
pipeline_tag: text-to-speech
---

# Sisi Lola Voice - Nigerian TTS Profile

## Model Details

### Model Description

Sisi Lola Voice is a Nigerian Text-to-Speech voice profile designed for generating natural-sounding Nigerian English speech. This profile configures TTS engines (EdgeTTS, XTTS) with Nigerian voice characteristics including accent, intonation, and cultural speech patterns.

- **Developed by:** BAMG Studio
- **Model type:** TTS Voice Profile / Configuration
- **Language(s):** English (Nigerian accent), Nigerian Pidgin, Yoruba
- **License:** Apache 2.0
- **Compatible with:** EdgeTTS (en-NG voices), XTTS-v2, YarnGPT
- **Repository:** [BAMG-Studio/sisi-lola-project](https://github.com/BAMG-Studio/sisi-lola-project)

### Model Sources

- **Repository:** https://github.com/BAMG-Studio/sisi-lola-project
- **Companion Model:** [sisilolalive/sisi-lola-brain](https://huggingface.co/sisilolalive/sisi-lola-brain)

## Uses

### Direct Use

This voice profile is designed to be used with TTS engines to generate Nigerian-accented speech for virtual assistants, chatbots, and audio content.

**Primary use cases:**
- Voice synthesis for Sisi Lola chatbot
- Nigerian English audio content generation
- Accessibility features with Nigerian accent
- Educational content with authentic Nigerian pronunciation

### Supported TTS Engines

| Engine | Voice | Language |
|--------|-------|----------|
| **EdgeTTS** | en-NG-EzinneNeural | Nigerian English (Female) |
| **EdgeTTS** | en-NG-AbeoNeural | Nigerian English (Male) |
| **XTTS-v2** | Custom cloning | Multi-language |
| **YarnGPT** | Nigerian voices | Yoruba, Pidgin, Igbo, Hausa |

### Out-of-Scope Use

This voice profile should NOT be used for:
- Impersonating real individuals
- Generating misleading audio content
- Deepfake or deceptive purposes
- Any illegal activities

## How to Get Started

### With EdgeTTS (Recommended)

\`\`\`python
import edge_tts
import asyncio

async def speak(text, output_file="output.mp3"):
    communicate = edge_tts.Communicate(
        text, 
        voice="en-NG-EzinneNeural",  # Nigerian female voice
        rate="+5%"
    )
    await communicate.save(output_file)
    print(f"Audio saved to {output_file}")

# Example
asyncio.run(speak("How you dey? Welcome to Lagos!"))
\`\`\`

### With Hybrid Voice Stack

\`\`\`python
from hybrid_voice_stack import HybridVoiceStack

# Initialize with Nigerian language support
voice = HybridVoiceStack()

# Synthesize with automatic language detection
audio = voice.synthesize("Ẹ kú àárọ̀! How you dey today?")
audio.save("greeting.mp3")
\`\`\`

## Technical Specifications

### Voice Profile Configuration

\`\`\`json
{
  "name": "Sisi Lola",
  "accent": "Nigerian",
  "region": "Lagos",
  "primary_language": "en-NG",
  "secondary_languages": ["pcm", "yo"],
  "voice_characteristics": {
    "gender": "female",
    "age_range": "25-35",
    "tone": "warm",
    "style": "conversational"
  }
}
\`\`\`

### Language Routing

The voice profile supports automatic language detection and routing:

| Tag | Language | Engine |
|-----|----------|--------|
| [EN] | Nigerian English | EdgeTTS |
| [NP] | Nigerian Pidgin | YarnGPT/EdgeTTS |
| [YO] | Yoruba | YarnGPT |
| [IG] | Igbo | YarnGPT |
| [HA] | Hausa | YarnGPT |

## Evaluation

### Voice Quality

- Natural Nigerian English intonation
- Clear pronunciation
- Appropriate pacing for conversational use
- Warm, friendly tone

### Limitations

- EdgeTTS requires internet connection
- Limited Yoruba/Pidgin vocabulary in fallback mode
- May not capture all regional Nigerian accents

## Model Card Contact

- **Email:** sisilolalive@gmail.com
- **GitHub:** [BAMG-Studio/sisi-lola-project](https://github.com/BAMG-Studio/sisi-lola-project)
- **HuggingFace:** [sisilolalive](https://huggingface.co/sisilolalive)

---

*Sisi Lola - Your friendly Lagos virtual host* 🇳🇬
