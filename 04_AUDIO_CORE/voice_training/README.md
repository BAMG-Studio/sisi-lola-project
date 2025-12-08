# Sisi Lola Voice Lock System

## Facebook MMS-TTS Yoruba Model Configuration

This system configures the Facebook MMS-TTS Yoruba model with locked parameters for consistent Sisi Lola character voice generation.

## Quick Start

### Windows
```bash
setup_voice.bat
```

### Manual Setup
```bash
pip install -r requirements.txt
python sisi_lola_voice_lock.py
```

## Voice Lock Parameters

- **Model**: `facebook/mms-tts-yor`
- **Voice Seed**: `45822` (matches visual seed)
- **Language**: Yoruba (Nigerian)
- **Sample Rate**: 16kHz
- **Device**: Auto-detect (CUDA/CPU)

## Usage

### Generate Single Voice Sample
```python
from sisi_lola_voice_lock import SisiLolaVoiceLock

voice = SisiLolaVoiceLock()
voice.generate_speech("Ẹ káàbọ̀!", "output.wav")
```

### Batch Generation
```python
texts = ["Báwo ni?", "Ẹ ṣeun"]
voice.batch_generate(texts, "output_dir/")
```

### API Server
```bash
python voice_api.py
```

**Endpoints**:
- `POST /generate` - Generate single voice sample
- `POST /batch` - Generate multiple samples
- `GET /health` - Check system status

## Integration with Sisi Lola Pipeline

Add to `.env`:
```
SISI_LOLA_VOICE_MODEL=facebook/mms-tts-yor
SISI_LOLA_VOICE_SEED=45822
SISI_LOLA_VOICE_API=http://localhost:5001
```

## Sample Yoruba Phrases

1. "Ẹ káàbọ̀! Mo ni Sisi Lola" - Welcome! I am Sisi Lola
2. "Báwo ni? Kí ló ń ṣẹlẹ̀?" - How are you? What's happening?
3. "Jẹ́ ká ṣe àwòrán tuntun" - Let's create something new
4. "Mo fẹ́ràn ọ̀" - I love you
5. "Ẹ ṣeun púpọ̀" - Thank you very much

## Output

Generated samples saved to: `generated_samples/`
- Format: WAV (16kHz, mono)
- Naming: `sisi_lola_voice_XXX.wav`

## Notes

- Voice seed ensures consistent character voice across all generations
- Model runs on GPU if available, falls back to CPU
- All outputs maintain same voice characteristics for brand consistency
