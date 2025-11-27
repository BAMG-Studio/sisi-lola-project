# ML TRAINING ORCHESTRATION SYSTEM

## Overview

Complete infrastructure for automated ML model training with Ansible playbooks and GitHub Actions workflows. Supports intelligent retraining triggers, multiple training modes, and phased training approaches.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER SOURCES                          │
├─────────────────────────────────────────────────────────────┤
│  • Manual (GitHub UI)                                       │
│  • Scheduled (Cron)                                         │
│  • Data Threshold (New samples)                             │
│  • Performance Drop (Metrics)                               │
│  • Git Push (New data files)                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENT DETECTION                          │
├─────────────────────────────────────────────────────────────┤
│  detect_training_need.py                                    │
│  • Analyzes triggers                                        │
│  • Determines models to train                               │
│  • Selects training mode                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│  .github/workflows/ml_training.yml                          │
│  • Setup environment                                        │
│  • Install dependencies                                     │
│  • Execute Ansible playbook                                 │
│  • Upload artifacts                                         │
│  • Send notifications                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ANSIBLE ORCHESTRATION                          │
├─────────────────────────────────────────────────────────────┤
│  ansible/playbooks/ml_training.yml                          │
│  ├── training_full.yml     (Complete retraining)            │
│  ├── training_partial.yml  (Fine-tuning)                    │
│  └── training_phasic.yml   (Phase-specific)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              TRAINING EXECUTION                             │
├─────────────────────────────────────────────────────────────┤
│  ml_training/scripts/                                       │
│  • prepare_dataset.py                                       │
│  • train_model.py                                           │
│  • validate_model.py                                        │
│  • deploy_models.py                                         │
└─────────────────────────────────────────────────────────────┘
```

## Training Modes

### 1. Full Training
Complete model retraining from scratch through all phases.

**Use Cases:**
- Initial model creation
- Major architecture changes
- Complete dataset refresh

**Phases:**
1. Foundation (basic training)
2. Refinement (improved accuracy)
3. Production (final optimization)

**Trigger:**
```bash
# Manual
ansible-playbook ansible/playbooks/ml_training.yml -e "mode=full model=natlas_audio"

# GitHub Actions
# Use workflow_dispatch with mode=full
```

### 2. Partial Training
Fine-tune existing model with new data.

**Use Cases:**
- Regular updates with new samples
- Incremental improvements
- Quick iterations

**Trigger:**
```bash
# Manual
ansible-playbook ansible/playbooks/ml_training.yml -e "mode=partial model=avatar_vision"

# Automatic (on data push)
git add 01_AVATAR_DNA/new_samples/
git commit -m "Add new avatar samples"
git push  # Triggers partial training
```

### 3. Phasic Training
Train specific phase only.

**Use Cases:**
- Phase-specific optimization
- Debugging specific training stage
- Resource-constrained training

**Trigger:**
```bash
# Manual
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=phasic model=content_classifier phase=refinement"

# GitHub Actions
# Use workflow_dispatch with mode=phasic, select phase
```

## Intelligent Retraining Triggers

### Schedule-Based
Automatic weekly retraining on Sundays at 2 AM UTC.

**Configuration:**
```yaml
retrain_triggers:
  - type: "schedule"
    cron: "0 2 * * 0"
```

### Data Threshold
Triggers when new samples exceed threshold.

**Configuration:**
```yaml
retrain_triggers:
  - type: "data_threshold"
    new_samples: 100
```

**Example:**
- Add 100+ new audio files to `04_AUDIO_CORE/`
- Push to GitHub
- Training automatically triggered

### Performance Drop
Triggers when model accuracy falls below threshold.

**Configuration:**
```yaml
retrain_triggers:
  - type: "performance_drop"
    metric: "accuracy"
    threshold: 0.85
```

### Manual Trigger
On-demand training via GitHub Actions UI.

**Steps:**
1. Go to GitHub Actions tab
2. Select "ML Training Orchestration"
3. Click "Run workflow"
4. Choose options:
   - Training mode (full/partial/phasic)
   - Target model (all/specific)
   - Target phase (for phasic mode)

## Model Configuration

### Adding New Models

Edit `ml_training/configs/training_config.yaml`:

```yaml
models:
  your_new_model:
    name: "Your Model Name"
    type: "audio|vision|nlp"
    model_id: "huggingface/model-id"
    dataset_path: "path/to/dataset"
    training_phases:
      - phase: "foundation"
        priority: 1
        samples_required: 100
        epochs: 10
    retrain_triggers:
      - type: "schedule"
        cron: "0 3 * * 0"
      - type: "data_threshold"
        new_samples: 50
```

## Directory Structure

```
Sisi_Lola/
├── .github/
│   └── workflows/
│       └── ml_training.yml          # GitHub Actions workflow
├── ansible/
│   ├── playbooks/
│   │   ├── ml_training.yml          # Main orchestration
│   │   ├── training_full.yml        # Full training mode
│   │   ├── training_partial.yml     # Partial training mode
│   │   └── training_phasic.yml      # Phasic training mode
│   ├── inventory/
│   └── vars/
│       └── secrets.yml              # Encrypted secrets
├── ml_training/
│   ├── configs/
│   │   └── training_config.yaml     # Training configuration
│   ├── scripts/
│   │   ├── detect_training_need.py  # Intelligent detection
│   │   ├── prepare_dataset.py       # Dataset preparation
│   │   ├── train_model.py           # Training execution
│   │   ├── validate_model.py        # Model validation
│   │   └── deploy_models.py         # Deployment
│   ├── datasets/                    # Prepared datasets
│   ├── checkpoints/                 # Model checkpoints
│   ├── logs/                        # Training logs
│   └── requirements.txt             # Python dependencies
```

## Usage Examples

### Example 1: Train N-ATLaS Audio Model (Full)

```bash
# Local execution
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=full" \
  -e "model=natlas_audio" \
  -v

# GitHub Actions
# 1. Go to Actions tab
# 2. Select "ML Training Orchestration"
# 3. Run workflow:
#    - mode: full
#    - model: natlas_audio
```

### Example 2: Fine-tune Avatar Vision (Partial)

```bash
# Add new avatar images
cp new_images/* 01_AVATAR_DNA/02_Expressions/

# Commit and push
git add 01_AVATAR_DNA/
git commit -m "Add new avatar expressions"
git push

# Training automatically triggered!
```

### Example 3: Train Specific Phase

```bash
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=phasic" \
  -e "model=content_classifier" \
  -e "phase=refinement"
```

### Example 4: Train All Models (Scheduled)

Runs automatically every Sunday at 2 AM UTC via GitHub Actions schedule.

## Monitoring & Notifications

### Slack Notifications
Configure webhook in `.env`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Notifications sent for:
- Training start
- Training complete
- Training failed
- Retrain triggered

### Training Logs
Stored in `ml_training/logs/`:
- `full_training_<model>_<timestamp>.json`
- `partial_training_<model>_<timestamp>.json`
- `phasic_training_<model>_<phase>_<timestamp>.json`

### Artifacts
GitHub Actions uploads:
- Training logs (30 days retention)
- Model checkpoints (90 days retention)

## GitHub Secrets Required

Add these secrets in GitHub repository settings:

```
HUGGINGFACE_TOKEN          # HuggingFace API token
SLACK_WEBHOOK_URL          # Slack webhook for notifications
ENV_FILE                   # Complete .env file content
```

## Next Steps

1. **Configure Models**: Edit `ml_training/configs/training_config.yaml`
2. **Add Secrets**: Configure GitHub secrets
3. **Test Locally**: Run Ansible playbook locally first
4. **Enable Workflows**: Push to GitHub to activate workflows
5. **Monitor**: Check GitHub Actions tab for execution

## Advanced Features

### Custom Training Scripts
Add your own training logic in `ml_training/scripts/train_model.py`

### Multi-GPU Support
Configure in `training_config.yaml`:
```yaml
compute_resources:
  local:
    gpu: true
    gpu_count: 4
```

### Cloud Training
Enable cloud training:
```yaml
compute_resources:
  cloud:
    enabled: true
    provider: "aws"
    instance_type: "g4dn.xlarge"
```

### A/B Testing
Train multiple model variants and compare:
```bash
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=full" \
  -e "model=natlas_audio" \
  -e "variant=experimental"
```

---

**Status**: ✅ READY FOR USE
**Last Updated**: 2025-01-XX
**Maintainer**: Sisi Lola Team
