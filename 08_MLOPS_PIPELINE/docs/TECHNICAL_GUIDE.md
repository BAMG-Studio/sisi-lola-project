"""
🎯 MLOPS PIPELINE - COMPLETE TECHNICAL GUIDE
============================================

Technical Explanation:
This guide provides detailed technical documentation for the Sisi Lola MLOps pipeline,
covering dataset ingestion, preprocessing, validation, and training preparation.
Designed for ML engineers and developers.

Layman Explanation:
This is the "instruction manual" for the AI training system. It explains how we:
1. Download voice recordings in different African languages
2. Clean and organize them
3. Check quality
4. Prepare them for AI training

Think of it like a factory assembly line - raw materials (voice recordings) go in,
get cleaned and sorted, checked for quality, then packaged for the AI to learn from.

============================================
TABLE OF CONTENTS
============================================

1. Architecture Overview
2. Installation & Setup
3. Dataset Ingestion
4. Data Preprocessing
5. Quality Validation
6. Manifest Building
7. Training Pipeline
8. CLI Commands Reference
9. Troubleshooting

============================================
1. ARCHITECTURE OVERVIEW
============================================

Technical:
The pipeline follows a DAG (Directed Acyclic Graph) architecture:
  
  Raw Data → Ingestion → Preprocessing → Validation → Manifests → Training
      ↓           ↓            ↓             ↓            ↓
   configs/   data/raw/   data/interim/  reports/   data/processed/

Orchestration: Prefect 2.19.8 (workflow management)
CLI: Typer 0.12.5 (command-line interface)
Data: HuggingFace datasets, pandas, librosa
Storage: Local filesystem with versioned directories

Layman:
The system works in stages, like a car assembly line:
1. RAW MATERIALS: Download voice recordings from internet
2. CLEANING: Remove noise, fix formatting
3. QUALITY CHECK: Make sure recordings are clear
4. PACKAGING: Organize into "recipe books" (manifests) for AI
5. TRAINING: Feed to AI to learn languages

Each stage checks the previous one - if quality is bad, it gets rejected.

============================================
2. INSTALLATION & SETUP
============================================

Technical:
Prerequisites:
- Python 3.12+
- Git
- 50GB+ free disk space
- (Optional) GPU for audio processing

Install dependencies:
```bash
cd 08_MLOPS_PIPELINE
pip install -r requirements.txt
```

Configure HuggingFace access:
```bash
huggingface-cli login
# Enter your token from https://huggingface.co/settings/tokens
```

Verify installation:
```bash
python cli/main.py datasets list
```

Layman:
Setting up the system:
1. Make sure you have Python installed (version 3.12 or newer)
2. Install helper tools (pip install -r requirements.txt)
3. Create a free HuggingFace account to download datasets
4. Check everything works with: python cli/main.py datasets list

Need at least 50GB of free disk space (voice files are large!).

============================================
3. DATASET INGESTION
============================================

Technical:
Ingestion pulls datasets from multiple sources:

Datasets Supported:
- MENYO-20k: Yoruba-English parallel corpus (GitHub)
- Fleurs: Multilingual ASR (HuggingFace, subsets: yo_ng, sw_ke, sw_tz, fr_sn)
- MasakhaNER: NER for Yoruba/Hausa/Igbo (HuggingFace)
- Common Voice 17.0: African language subsets (HuggingFace)
- ALFFA: Swahili ASR (manual download)
- Lagos-NWU: Nigerian English (requires access request)

Command:
```bash
# Ingest all configured datasets
python cli/main.py ingest all

# Ingest specific dataset
python cli/main.py ingest menyo20k
python cli/main.py ingest common_voice_africa
```

Implementation:
- ingestion/ingest_registry.py: Contains ingestor functions
- configs/datasets.yaml: Dataset configurations
- Output: data/raw/{dataset_name}/

Layman:
Downloading voice recordings:

The system knows where to find voice recordings online (like downloading
music from different websites). It can get:
- Yoruba speech from Nigeria
- Swahili from Kenya/Tanzania  
- Hausa, Igbo, French from West Africa
- English with Nigerian accent

Run: python cli/main.py ingest all
This downloads everything automatically.

Files are saved in: data/raw/ folder.

============================================
4. DATA PREPROCESSING
============================================

Technical:
Preprocessing normalizes text and segments code-switching:

4.1 Text Normalization (normalize_text.py)
-------------------------------------------
- Unicode NFC normalization (critical for Yoruba diacritics: ẹ, ọ, ṣ)
- Whitespace cleanup (tabs → spaces, multiple spaces → single)
- Optional lowercasing
- Punctuation preservation

Example:
```python
from preprocessing.normalize_text import normalize_text

text = "  Ẹ   káàsán   ,  báwo  ni  ?  "
normalized = normalize_text(text, lowercase=False)
# Output: "Ẹ káàsán , báwo ni ?"
```

4.2 Code-Switching Segmentation (code_switch.py)
-------------------------------------------------
- Detects language boundaries in mixed-language text
- Uses linguistic markers (particles, grammar patterns)
- Outputs segments with language labels + confidence

Example:
```python
from preprocessing.code_switch import segment_code_switching

text = "Ẹ káàsán! How are you doing today?"
segments = segment_code_switching(text)
# [
#   {"text": "Ẹ káàsán!", "language": "yo", "confidence": 0.9},
#   {"text": "How are you doing today?", "language": "en", "confidence": 0.8}
# ]
```

4.3 ASR Corpus Preparation (prepare_asr_corpus.py)
---------------------------------------------------
- Splits long audio into 5-30s chunks (optimal for Whisper)
- Aligns transcriptions with audio segments
- Filters silence/noise

4.4 TTS Corpus Preparation (prepare_tts_corpus.py)
---------------------------------------------------
- Matches audio with script text
- Validates speaker consistency
- Extracts prosody features

Commands:
```bash
# Normalize all Yoruba text
python cli/main.py preprocess --lang yo --lower false

# Segment code-switched text
python preprocessing/code_switch.py --input data/raw/yorunglish_samples.txt
```

Layman:
Cleaning up voice recordings:

After downloading, we need to "clean" the data:

1. TEXT CLEANUP: Fix spelling, spacing, special characters
   - "Ẹ    káàsán" → "Ẹ káàsán" (remove extra spaces)
   - Keep Yoruba special letters (ẹ, ọ, ṣ) intact

2. LANGUAGE DETECTION: Figure out when people switch languages
   - "Ẹ káàsán! How are you?" → Mark first part as Yoruba, second as English

3. AUDIO SPLITTING: Cut long recordings into bite-sized pieces
   - 1 hour podcast → 100+ short clips (5-30 seconds each)

4. QUALITY CHECK: Remove bad recordings
   - Too quiet? → Reject
   - Background noise? → Reject
   - Unclear speech? → Reject

Run: python cli/main.py preprocess --lang yo

============================================
5. QUALITY VALIDATION
============================================

Technical:
Quality validation runs automated checks on preprocessed data:

5.1 Dataset Coverage Report (evaluation/dataset_coverage_report.py)
--------------------------------------------------------------------
Analyzes:
- Language distribution (samples per language, total hours)
- Speaker diversity (unique speakers per language)
- Code-switching rate (% of mixed-language samples)
- Text quality (diacritic coverage for Yoruba, avg length)

Metrics:
- Minimum hours for ASR training: 5 hours per language
- Minimum speakers: 10+ for accent diversity
- Yoruba diacritic coverage: >80% (critical for tone accuracy)

Command:
```bash
python evaluation/dataset_coverage_report.py \\
  --asr-manifest data/processed/asr_manifest_all.tsv \\
  --output reports/coverage.json
```

Output:
```json
{
  "language_distribution": {
    "yo": {"total_samples": 5000, "total_duration_hours": 12.5, "unique_speakers": 25},
    "pcm": {"total_samples": 2000, "total_duration_hours": 4.8, "unique_speakers": 8}
  },
  "recommendations": [
    "⚠️  pcm: Only 4.8 hours. Need at least 5 hours for good ASR."
  ]
}
```

5.2 Audio Quality Report (evaluation/audio_quality_report.py)
-------------------------------------------------------------
Analyzes:
- Sample rate distribution (should be consistent, e.g., 16kHz or 44.1kHz)
- Duration distribution (3-30s ideal for TTS)
- RMS energy (loudness): 0.01-0.95 range
- Clipping detection: max amplitude < 0.99
- SNR estimation (signal-to-noise ratio)

Issues Detected:
- too_quiet: RMS < 0.01
- too_loud: RMS > 0.95
- clipping: max amplitude >= 0.99 (distortion)
- too_short: < 3 seconds
- too_long: > 30 seconds
- low_snr: SNR < 10 dB (noisy background)

Command:
```bash
python evaluation/audio_quality_report.py \\
  --voice-dir ../04_AUDIO_CORE/01_Voice_Samples \\
  --output reports/audio_quality.json
```

Layman:
Checking if recordings are good enough:

The system automatically grades voice recordings like a teacher:

1. COVERAGE CHECK (dataset_coverage_report.py):
   - Do we have enough samples? (Need 5+ hours per language)
   - Do we have enough different voices? (Need 10+ speakers)
   - Is the writing correct? (Yoruba needs special letters: ẹ, ọ, ṣ)
   
   EXAMPLE: If we only have 2 hours of Swahili, it warns us to get more.

2. AUDIO QUALITY CHECK (audio_quality_report.py):
   - Is it loud enough? (Not too quiet/loud)
   - Is it clear? (No static or distortion)
   - Is it the right length? (3-30 seconds)
   
   EXAMPLE: If recording has loud crackling (clipping), it gets rejected.

After running checks, you get a "report card":
- ✅ Good: 850 files
- ⚠️ Warning: 120 files (fixable)
- ❌ Error: 30 files (reject)

Run: python evaluation/dataset_coverage_report.py --asr-manifest data/processed/asr_manifest_all.tsv

============================================
6. MANIFEST BUILDING
============================================

Technical:
Manifests are structured lists of training samples with metadata.

6.1 ASR Manifest (preprocessing/build_asr_manifest.py)
-------------------------------------------------------
Purpose: Prepare data for Whisper ASR fine-tuning

Format: TSV (tab-separated values)
Columns:
- audio_path: Absolute path to audio file
- text: Transcription (normalized)
- language: Language code (yo, pcm, sw, etc.)
- duration_sec: Audio duration in seconds
- speaker_id: Speaker identifier
- split: train | validation | test

Example:
```tsv
audio_path	text	language	duration_sec	speaker_id	split
/data/fleurs/yo/train_001.wav	Ẹ káàsán, báwo ni?	yo	5.2	speaker_yo_01	train
/data/cv/pcm/valid_050.mp3	How far my guy?	pcm	4.8	speaker_pcm_12	validation
```

Command:
```bash
python preprocessing/build_asr_manifest.py \\
  --datasets fleurs common_voice \\
  --output data/processed/asr_manifest_all.tsv
```

6.2 TTS Metadata (preprocessing/build_tts_metadata.py)
-------------------------------------------------------
Purpose: Prepare data for XTTS voice cloning

Format: CSV with pipe delimiter (|)
Columns:
- filename: Audio filename (relative to voice dir)
- text: Script text (what was spoken)
- speaker_id: Speaker identifier
- language: Language code

Example:
```csv
filename|text|speaker_id|language
sisi_lola_yo_001.wav|Ẹ káàsán, ẹ káàbọ̀|sisi_lola|yo
sisi_lola_pcm_015.wav|How far? I dey kampe o|sisi_lola|pcm
```

Audio Validation (optional with --no-validate flag):
- Duration: 3-30 seconds
- RMS energy: 0.01-0.95
- Max amplitude: < 0.99 (no clipping)

Command:
```bash
python preprocessing/build_tts_metadata.py \\
  --voice-dir ../04_AUDIO_CORE/01_Voice_Samples \\
  --speaker-id sisi_lola \\
  --output data/processed/tts_metadata.csv
```

Layman:
Creating "recipe books" for AI training:

After quality checks, we create lists (manifests) that tell the AI:
- Where to find each voice recording
- What was said in each recording
- Which language it's in
- How long it is

TWO TYPES OF RECIPE BOOKS:

1. ASR MANIFEST (for speech-to-text training):
   File: asr_manifest_all.tsv
   
   Like a table in Excel with columns:
   | Audio File Path | What Was Said | Language | Duration | Speaker |
   | /audio/001.wav  | Ẹ káàsán      | Yoruba   | 5.2 sec  | Speaker1|
   
   Used to train AI to understand spoken Yoruba/Pidgin/etc.

2. TTS METADATA (for text-to-speech training):
   File: tts_metadata.csv
   
   Like a playlist:
   | Recording Name | Script Text | Voice Actor | Language |
   | voice_001.wav  | Hello world | Sisi Lola   | English  |
   
   Used to train AI to speak with Sisi Lola's voice.

Run:
- python preprocessing/build_asr_manifest.py --datasets fleurs common_voice
- python preprocessing/build_tts_metadata.py --voice-dir ../04_AUDIO_CORE/01_Voice_Samples

============================================
7. TRAINING PIPELINE
============================================

Technical:
Training pipeline integrates all components:

7.1 Prefect Flow (pipelines/flow_ingest_preprocess.py)
------------------------------------------------------
Orchestrates:
1. Ingest datasets (parallel execution)
2. Normalize text (per language)
3. Build manifests
4. Generate quality reports

Run flow:
```bash
python pipelines/flow_ingest_preprocess.py
```

Flow DAG:
```
ingest_all
    ↓
[normalize_yo, normalize_pcm, normalize_sw] (parallel)
    ↓
build_manifests
    ↓
generate_reports
```

7.2 Training Scripts (not yet implemented)
-------------------------------------------
Planned:
- scripts/train_whisper.py: Fine-tune Whisper on ASR manifest
- scripts/train_xtts.py: Fine-tune XTTS on TTS metadata
- scripts/evaluate_model.py: Run evaluation on test set

Layman:
Putting it all together:

Once all the recipe books (manifests) are ready, we can train the AI.

The PREFECT FLOW is like a factory supervisor that:
1. Starts all download machines (ingest datasets)
2. Starts all cleaning machines (normalize text)
3. Starts packaging machines (build manifests)
4. Runs quality inspection (generate reports)

All automatically! No manual work needed.

Run: python pipelines/flow_ingest_preprocess.py

Then the AI learns:
- WHISPER: How to understand spoken African languages
- XTTS: How to speak with Sisi Lola's voice in any language

Training takes 6-12 hours on a good GPU.

============================================
8. CLI COMMANDS REFERENCE
============================================

Technical:
All commands via cli/main.py (Typer CLI):

datasets list
-------------
List all configured datasets from datasets.yaml

Usage:
```bash
python cli/main.py datasets list
```

ingest [NAME]
-------------
Download and ingest datasets

Usage:
```bash
# Ingest all
python cli/main.py ingest all

# Ingest specific
python cli/main.py ingest menyo20k
python cli/main.py ingest fleurs
python cli/main.py ingest common_voice_africa
```

preprocess
----------
Normalize text for specific language

Usage:
```bash
python cli/main.py preprocess --lang yo --lower false
python cli/main.py preprocess --lang pcm --lower true
```

report coverage
---------------
Generate dataset coverage report

Usage:
```bash
python cli/main.py report coverage
```

Layman:
Command cheat sheet:

Open terminal and run these commands:

1. See available datasets:
   python cli/main.py datasets list

2. Download all voice recordings:
   python cli/main.py ingest all

3. Clean up Yoruba text:
   python cli/main.py preprocess --lang yo

4. Check if we have enough data:
   python cli/main.py report coverage

All commands start with: python cli/main.py

============================================
9. TROUBLESHOOTING
============================================

Technical:

Issue: HuggingFace datasets download fails
------------------------------------------
Error: "ConnectionError" or "Unauthorized"

Fix:
```bash
huggingface-cli login
# Enter token from https://huggingface.co/settings/tokens

# Or set environment variable
export HF_TOKEN="your_token_here"
```

Issue: librosa/soundfile import error
-------------------------------------
Error: "ModuleNotFoundError: No module named 'librosa'"

Fix:
```bash
pip install librosa soundfile numpy
```

Note: Audio validation gracefully degrades if these aren't installed.

Issue: Manifest build shows "0 samples found"
----------------------------------------------
Cause: Datasets not ingested yet

Fix:
```bash
# Ingest first
python cli/main.py ingest all

# Then build manifests
python preprocessing/build_asr_manifest.py
```

Issue: Yoruba diacritics appear broken
--------------------------------------
Error: "E\u0301" instead of "É"

Fix: Ensure terminal supports UTF-8:
```bash
# Linux/Mac
export LANG=en_US.UTF-8

# Windows PowerShell
$OutputEncoding = [System.Text.Encoding]::UTF8
```

Issue: Audio quality report shows all files as "too_quiet"
----------------------------------------------------------
Cause: Microphone gain too low during recording

Fix:
- Re-record with mic closer to speaker
- Increase input gain in recording software
- Use audio normalization:
```bash
ffmpeg -i input.wav -af "volume=2.0" output.wav
```

Layman:

Problem: Can't download datasets
--------------------------------
Error: "Connection failed" or "Not authorized"

Fix:
1. Create free account at huggingface.co
2. Go to Settings → Access Tokens → Create token
3. Run: huggingface-cli login
4. Paste your token

Problem: Missing audio tools
----------------------------
Error: "Can't find librosa"

Fix:
Run: pip install librosa soundfile
(These tools analyze audio quality)

Problem: No voice recordings found
----------------------------------
Fix:
1. Download first: python cli/main.py ingest all
2. Wait for download to finish (may take 10-30 minutes)
3. Then run manifest builder

Problem: Yoruba letters look weird (E\u0301 instead of É)
--------------------------------------------------------
Fix:
Your terminal doesn't support special characters.
- Windows: Use Windows Terminal (not old Command Prompt)
- Mac/Linux: Should work by default

Problem: All recordings flagged as "too quiet"
----------------------------------------------
Fix:
Recordings need to be louder:
1. Re-record with microphone closer to mouth
2. Or use audio software to increase volume
3. Or use ffmpeg to boost: ffmpeg -i quiet.wav -af "volume=2.0" louder.wav

============================================
END OF TECHNICAL GUIDE
============================================

For further support:
- Check README.md in 08_MLOPS_PIPELINE/
- Review architecture docs in 00_PROJECT_CORE/Documentation/
- Run unit tests: pytest tests/ -v

Version: 1.0
Last Updated: 2024
"""