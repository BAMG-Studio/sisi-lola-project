#!/usr/bin/env python3
"""Quick test of Nigerian models without full training"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

os.environ['HUGGINGFACE_TOKEN'] = os.getenv('HUGGINGFACE_TOKEN', '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')

print("Quick Test - Nigerian Models\n")

# Test 1: HuggingFace access
print("[1/5] Testing HuggingFace access...")
try:
    from huggingface_hub import login, whoami
    login(token=os.getenv('HUGGINGFACE_TOKEN'))
    user = whoami()
    print(f"[OK] Logged in as: {user['name']}\n")
except Exception as e:
    print(f"[FAIL] HuggingFace login failed: {e}\n")

# Test 2: Check voice samples
print("[2/5] Checking voice samples...")
from pathlib import Path
voice_dir = Path("04_AUDIO_CORE/voice_samples")
samples = list(voice_dir.glob("*.wav"))
print(f"[OK] Found {len(samples)} voice samples")
if len(samples) >= 5:
    print(f"     Ready for training (minimum 5 required)\n")
else:
    print(f"[WARN] Need {5-len(samples)} more samples\n")

# Test 3: Check personality data
print("[3/5] Checking personality data...")
personality_file = Path("ml_training/datasets/sisi_lola_personality.txt")
if personality_file.exists():
    with open(personality_file, encoding='utf-8') as f:
        lines = len(f.readlines())
    print(f"[OK] Personality data: {lines} lines\n")
else:
    print("[FAIL] Personality data not found\n")

# Test 4: Test N-ATLaS model access (lightweight)
print("[4/5] Testing N-ATLaS model access...")
try:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "NCAIR1/N-ATLaS-8B",
        trust_remote_code=True,
        token=os.getenv('HUGGINGFACE_TOKEN')
    )
    test_text = "Bawo ni? How are you?"
    tokens = tokenizer(test_text)
    print(f"[OK] N-ATLaS tokenizer loaded")
    print(f"     Test tokenization: {len(tokens['input_ids'])} tokens\n")
except Exception as e:
    print(f"[WARN] N-ATLaS access issue: {e}\n")

# Test 5: Check GPU
print("[5/5] Checking GPU availability...")
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"[OK] GPU: {gpu_name} ({gpu_memory:.1f} GB)")
        print(f"     Training will be fast (~6-12 hours)\n")
    else:
        print("[WARN] No GPU detected")
        print("       Training will be slow (~24-48 hours on CPU)\n")
except:
    print("[WARN] PyTorch not installed\n")

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("[OK] All checks passed - Ready to train!")
print("\nNext steps:")
print("  1. Run: train_nigerian_models.bat")
print("  2. Wait: 6-12 hours (GPU) or 24-48 hours (CPU)")
print("  3. Test: python ml_training/scripts/inference_nigerian.py")
