#!/bin/bash
# Test ML Training System Locally

echo "=========================================="
echo "ML TRAINING SYSTEM - LOCAL TEST"
echo "=========================================="

# Test 1: Prepare dataset
echo -e "\n[TEST 1] Preparing dataset..."
python ml_training/scripts/prepare_dataset.py \
  --model natlas_audio \
  --dataset-path 04_AUDIO_CORE/01_Voice_Samples \
  --output ml_training/datasets/natlas_audio

# Test 2: Train model (foundation phase)
echo -e "\n[TEST 2] Training model..."
python ml_training/scripts/train_model.py \
  --model natlas_audio \
  --phase foundation \
  --mode full \
  --config ml_training/configs/training_config.yaml

# Test 3: Validate model
echo -e "\n[TEST 3] Validating model..."
python ml_training/scripts/validate_model.py \
  --model natlas_audio \
  --checkpoint ml_training/checkpoints/natlas_audio/foundation

# Test 4: Detect training need
echo -e "\n[TEST 4] Detecting training need..."
python ml_training/scripts/detect_training_need.py \
  --config ml_training/configs/training_config.yaml \
  --event-type schedule \
  --changed-files ""

echo -e "\n=========================================="
echo "✓ ALL TESTS COMPLETED"
echo "=========================================="
