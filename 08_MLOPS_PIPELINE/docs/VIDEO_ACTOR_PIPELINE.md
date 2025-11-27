# Sisi Lola Video Actor/Characterization Model Pipeline

## Overview
This pipeline enables training of a video-acting, mannerisms, and attitude model for Sisi Lola, covering a wide range of performances and expressive behaviors. It is designed for African influencer/actress/podcaster/journalist roles and supports activities like reading, dancing, counseling, sleeping, eating, working out, running, driving, sky-diving, podcasting, and more.

## Pipeline Structure
```
08_MLOPS_PIPELINE/
  data/
    video_raw/           # Original video clips
    video_annotated/     # Annotated clips with labels
    video_processed/     # Preprocessed frames/audio
  preprocessing/
    prepare_video_dataset.py
    annotate_video_clips.py
  training/
    train_video_actor_model.py
  configs/
    video_labels.yaml    # Activity, attitude, role, emotion tags
  tests/
    test_prepare_video_dataset.py
    test_annotate_video_clips.py
    test_train_video_actor_model.py
```

## Steps

### 1. Data Collection
- Curate or record video samples of African performances (influencer, actress, podcaster, journalist).
- Save raw clips in `data/video_raw/`.

### 2. Preprocessing
- Run `prepare_video_dataset.py` to extract frames and audio, normalize resolution/duration.
- Output goes to `data/video_processed/`.

### 3. Annotation
- Run `annotate_video_clips.py` to label each clip with activity, attitude, role, emotion, and cultural markers.
- Save annotations in `data/video_annotated/annotations.csv`.

### 4. Model Training
- Run `train_video_actor_model.py` to fine-tune a video transformer model (e.g., VideoMAE, CLIP) for multi-label classification.
- Use `configs/video_labels.yaml` for label schema.

### 5. Evaluation & Testing
- Use provided unit tests in `tests/` to validate each stage.

## Label Schema Example (video_labels.yaml)
```yaml
activities:
  - reading
  - dancing
  - counseling
  - sleeping
  - eating
  - working_out
  - running
  - driving
  - sky_diving
  - podcasting
  - reporting
  - vlogging
attitudes:
  - confident
  - empathetic
  - energetic
  - calm
  - playful
  - serious
  - dramatic
roles:
  - influencer
  - actress
  - podcaster
  - journalist
emotions:
  - happy
  - sad
  - angry
  - surprised
  - neutral
cultural_markers:
  - greeting
  - slang
  - fashion
  - social_cue
```

## Usage Examples

### Prepare Video Dataset
```bash
python preprocessing/prepare_video_dataset.py --input-dir data/video_raw --output-dir data/video_processed --frame-rate 25 --duration 10
```

### Annotate Video Clips
```bash
python preprocessing/annotate_video_clips.py --input-dir data/video_processed --output-csv data/video_annotated/annotations.csv
```

### Train Model
```bash
python training/train_video_actor_model.py --data-dir data/video_processed --annotations data/video_annotated/annotations.csv --labels configs/video_labels.yaml --epochs 10
```

### Run Unit Tests
```bash
pytest tests/ -v
```

## Notes
- For real model training, integrate with PyTorch, HuggingFace Transformers, or similar.
- Use CVAT or Labelbox for scalable annotation.
- Extend label schema as needed for new activities or attitudes.
- All scripts are modular and can be integrated into larger MLOps workflows.
