# 🚀 Starting Sisi Lola Nigerian Training

## Current Status
✅ All prerequisites met
✅ 11 voice samples ready
✅ Training scripts configured
✅ API integration complete
✅ HuggingFace exploration done

## Training Command

### Windows
```cmd
train_nigerian_models.bat
```

### Linux/Mac
```bash
chmod +x train_nigerian_models.sh
./train_nigerian_models.sh
```

## What Will Happen

### Phase 1: Setup (5 mins)
- Install dependencies
- Download N-ATLaS-8B model
- Download XTTS-v2 model
- Validate voice samples

### Phase 2: Brain Training (2-4 hours)
- Load N-ATLaS-8B with 4-bit quantization
- Configure LoRA adapter (rank 16, alpha 32)
- Train on NaijaSenti + personality data
- Save adapter to `ml_training/checkpoints/natlas_lora/`

### Phase 3: Voice Training (4-8 hours)
- Load XTTS-v2 model
- Prepare 11 voice samples
- Fine-tune for Lagos Nigerian accent
- Save model to `ml_training/checkpoints/xtts_sisi_lola/`

### Phase 4: Deployment (5 mins)
- Generate production config
- Register models
- Create training report

## Expected Outputs

```
ml_training/
├── checkpoints/
│   ├── natlas_lora/              # Brain adapter (~500MB)
│   └── xtts_sisi_lola/           # Voice model (~1.5GB)
├── outputs/
│   ├── production_config.json    # Deployment config
│   └── model_registry.json       # Version tracking
└── logs/
    └── training_report_*.json    # Training logs
```

## Timeline

| Phase | Time (GPU) | Time (CPU) |
|-------|-----------|-----------|
| Setup | 5 mins | 5 mins |
| Brain | 2-4 hours | 12-24 hours |
| Voice | 4-8 hours | 12-24 hours |
| Deploy | 5 mins | 5 mins |
| **Total** | **6-12 hours** | **24-48 hours** |

## Monitoring

### Check Progress
```bash
# View training logs
type ml_training\logs\training_*.log

# Check GPU usage (if available)
nvidia-smi
```

### Expected Console Output
```
============================================================
SISI LOLA TRAINING ORCHESTRATOR
============================================================

[Prerequisites] Checking...
  ✓ HuggingFace access: sisilolalive
  ✓ Voice samples: 11 found
  ✓ Personality data: 20 lines

============================================================
PHASE 1: BRAIN TRAINING (N-ATLaS LLM)
============================================================
Loading N-ATLaS-8B...
Preparing LoRA adapter...
Loading training data...
Starting training...
[Progress bar will show here]

============================================================
PHASE 2: VOICE TRAINING (XTTS-v2)
============================================================
Preparing voice samples...
Loading XTTS-v2...
Starting training...
[Progress bar will show here]

============================================================
TRAINING COMPLETE!
============================================================
Brain: ml_training/checkpoints/natlas_lora
Voice: ml_training/checkpoints/xtts_sisi_lola
```

## After Training

### Test Inference
```python
from ml_training.scripts.inference_nigerian import SisiLolaInference

sisi = SisiLolaInference()
result = sisi.chat("Bawo ni? Tell me about Lagos", generate_audio=True)
print(result['text'])
# Audio saved to result['audio']
```

### Start API
```bash
cd sisi_lola_api
uvicorn app.main:app --reload
```

### Test API
```bash
python test_nigerian_api.py
```

## Troubleshooting

### If Training Fails
1. Check logs: `ml_training/logs/training_*.log`
2. Verify HuggingFace token
3. Check disk space (need 50GB+)
4. Reduce batch size if GPU memory error

### If Too Slow
- Training on CPU is 4x slower than GPU
- Consider cloud GPU (Google Colab, AWS, etc.)
- Or let it run overnight

## Ready to Start?

Run this command now:
```cmd
train_nigerian_models.bat
```

The training will run automatically. You can leave it running and check back in 6-12 hours.

---

**Note**: Training can be interrupted and resumed. Models are saved at checkpoints.
