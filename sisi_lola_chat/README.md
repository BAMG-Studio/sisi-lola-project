# Sisi Lola Chat Interface

Interactive chat with Sisi Lola - your AI bestie from Naija! 🇳🇬

## Quick Start

### Text Chat (No Voice)
```bash
cd sisi_lola_chat
python chat_with_sisi.py
```

### Chat with Voice Responses
```bash
python chat_with_sisi.py --voice
```

## Features

| Feature | Command | Description |
|---------|---------|-------------|
| Text Chat | `python chat_with_sisi.py` | Chat with Sisi Lola in text |
| Voice Output | `--voice` | Sisi speaks her responses |
| Test Voice | `python test_voice_local.py` | Test voice generation |
| Test with Audio | `python test_voice_local.py --play` | Generate and play audio |

## In-Chat Commands

| Command | Action |
|---------|--------|
| `/clear` | Clear conversation history |
| `/save` | Save conversation to JSON |
| `/help` | Show help |
| `exit` | Exit chat |

## Requirements

For text-only chat:
```bash
pip install openai python-dotenv
```

For voice features:
```bash
pip install torch torchaudio transformers soundfile
```

## Personality

Sisi Lola is configured with:
- **Confidence**: 8.5/10
- **Humor**: 8.5/10 (She's FUNNY!)
- **Charisma**: 9.0/10
- **Authenticity**: 9.0/10

She mixes English and Nigerian Pidgin naturally, uses expressions like:
- "Omo!"
- "E choke!"
- "Na so we see am o!"
- "Las las, we go dey alright!"

## Audio Output

Voice responses are saved to:
```
04_AUDIO_CORE/chat_responses/sisi_response_YYYYMMDD_HHMMSS.wav
```
