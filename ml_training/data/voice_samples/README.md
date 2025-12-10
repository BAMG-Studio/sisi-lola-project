# Speaker Reference Audio

This directory should contain the reference audio file for XTTS-v2 voice cloning.

## Required File

Place your speaker reference audio file here:

```
speaker_reference.wav
```

## Audio Requirements

For best voice cloning results:

1. **Duration:** 10-60 seconds of clean speech
2. **Format:** WAV (16-bit, mono or stereo)
3. **Sample Rate:** 22050 Hz or 44100 Hz
4. **Quality:** 
   - No background noise
   - No music or sound effects
   - Clear, natural speech
   - Consistent volume level

## Recording Tips

- Use a quiet room with minimal echo
- Speak naturally at a consistent pace
- Include a variety of sentences for better voice capture
- Keep the microphone at a consistent distance

## Example Script

Record yourself reading this sample text:

> "Hello, my name is Sisi Lola. I'm here to help you with anything you need today.
> Whether you want to chat, learn something new, or just have a conversation,
> I'm always happy to assist. How are you doing today?"

## What Happens Next

When you run the training pipeline, the voice trainer will:

1. Load this reference audio
2. Extract speaker embeddings using XTTS-v2
3. Save the embeddings to HuggingFace Hub
4. The chat system will use these embeddings to synthesize speech in your voice

## File Naming

The training pipeline looks for these files:
- `speaker_reference.wav` (primary)
- `speaker_reference.mp3` (alternative)
- `reference_audio.wav` (fallback)
