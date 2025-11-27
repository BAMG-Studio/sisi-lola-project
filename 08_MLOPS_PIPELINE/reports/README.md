# Model Evaluation Reports

This directory contains evaluation reports for all Sisi Lola models:

- Whisper ASR (Automatic Speech Recognition)
- XTTS TTS (Text-to-Speech)
- Video Actor/Characterization

## Report Structure
- `whisper_eval.json`: ASR model metrics (WER, accuracy)
- `xtts_eval.json`: TTS model metrics (MOS, intelligibility)
- `video_actor_eval.json`: Video actor metrics (accuracy, expressiveness)

## Usage
Run the evaluation scripts in `evaluation/` to generate these reports after model training and integration tests.
