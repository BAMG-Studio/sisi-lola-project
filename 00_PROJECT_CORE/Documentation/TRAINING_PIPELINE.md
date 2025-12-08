# SISI LOLA TRAINING PIPELINE

## Overview
Continuous ML training system for Sisi Lola's personality, humor, and charisma.

## Training Workflows

### 1. Personality Training Pipeline
**File**: `.github/workflows/personality_training.yml`

**Triggers**:
- Manual dispatch with intensity selection (light/moderate/intensive)
- Push to personality config files
- Weekly schedule (Monday 3 AM UTC)

**Steps**:
1. Train personality model with latest data
2. Fine-tune with OpenAI GPT-3.5-turbo
3. Validate personality configuration
4. Test integration with API
5. Deploy to production

### 2. ML Training Orchestration
**File**: `.github/workflows/ml_training.yml`

**Triggers**:
- Manual dispatch with mode selection
- Weekly schedule (Sunday 2 AM UTC)
- Push to asset directories

**Models Trained**:
- N-ATLAS audio model
- Avatar vision model
- Content classifier
- Personality model

## Training Datasets

### Personality Training Data
**File**: `ml_training/datasets/personality_training_data.json`

**Contents**:
- Personality profile scores
- Training examples with labels
- Response patterns
- Humor techniques
- Charisma tactics

**Example Training Pair**:
```json
{
  "input": "I'm nervous about my presentation",
  "output": "Abeg o! You too prepared to fail! Listen, you know your stuff pass anybody in that room. Make you breathe, smile, and show them wetin you made of. Na your time be this! Las las, we go dey alright! 💪",
  "labels": ["confidence_boost", "empowerment", "humor", "charisma"]
}
```

## Training Scripts

### 1. Fine-tune Personality
**File**: `ml_training/scripts/finetune_personality.py`

**Usage**:
```bash
python ml_training/scripts/finetune_personality.py \
  --dataset ml_training/datasets/personality_training_data.json \
  --intensity moderate
```

**Intensity Levels**:
- Light: 3 epochs
- Moderate: 5 epochs
- Intensive: 10 epochs

### 2. Validate Personality
**File**: `ml_training/scripts/validate_personality.py`

**Usage**:
```bash
python ml_training/scripts/validate_personality.py \
  --config 00_PROJECT_CORE/Config/sisi_attitude.py
```

**Validations**:
- Personality scores in range (0-10)
- Humor level >= 8.0
- Charisma level >= 8.5
- Required response patterns present
- Minimum catchphrases count

### 3. Run Attitude Training
**File**: `00_PROJECT_CORE/Scripts/run_attitude_training.py`

**Usage**:
```bash
python 00_PROJECT_CORE/Scripts/run_attitude_training.py
```

**Outputs**:
- Personality profile JSON
- Training scenarios
- Attitude configuration
- Database updates

## Monitoring & Validation

### Training Artifacts
Uploaded to GitHub Actions artifacts:
- Training logs
- Model checkpoints
- Validation reports
- Test results

**Retention**: 30-90 days

### Success Criteria
- ✅ All validations pass
- ✅ Humor level >= 8.5/10
- ✅ Charisma level >= 9.0/10
- ✅ API tests successful
- ✅ Response quality maintained

### Monitoring Dashboard
View training status:
- GitHub Actions: `.github/workflows/`
- Training logs: `ml_training/logs/`
- Model checkpoints: `ml_training/checkpoints/`

## Continuous Improvement

### Data Collection
- User interactions logged
- Response quality metrics tracked
- Humor effectiveness measured
- Charisma impact analyzed

### Model Updates
- Weekly automatic retraining
- Manual intensive training on demand
- A/B testing of personality variations
- Feedback loop integration

### Version Control
- Personality config versioned in Git
- Training data tracked with timestamps
- Model checkpoints archived
- Rollback capability maintained

## Manual Training Trigger

### Via GitHub Actions UI
1. Go to Actions tab
2. Select "Personality Training Pipeline"
3. Click "Run workflow"
4. Choose intensity level
5. Monitor progress

### Via GitHub CLI
```bash
gh workflow run personality_training.yml \
  -f training_intensity=moderate
```

## Production Deployment

### Automatic Deployment
On successful training:
1. Models validated
2. Tests pass
3. Config updated
4. Changes committed
5. API restarted

### Manual Deployment
```bash
# Update production config
python ml_training/scripts/update_production_config.py \
  --models ml_training/checkpoints/ \
  --config sisi_lola_api/.env

# Restart API
cd sisi_lola_api
uvicorn app.main:app --reload
```

## Troubleshooting

### Training Fails
- Check OpenAI API key
- Verify dataset format
- Review validation errors
- Check logs in artifacts

### Validation Fails
- Review personality scores
- Check required fields
- Verify data structure
- Update config as needed

### Deployment Issues
- Verify environment variables
- Check API connectivity
- Review deployment logs
- Rollback if necessary

## Next Steps

1. ✅ Initial training complete
2. 🔄 Monitor weekly training runs
3. 🔄 Collect user feedback
4. 🔄 Expand training dataset
5. 🔄 Fine-tune based on metrics
6. 🔄 Add voice personality training
7. 🔄 Integrate video expression training

## Resources

- Training config: `ml_training/configs/training_config.yaml`
- Personality config: `00_PROJECT_CORE/Config/sisi_attitude.py`
- API integration: `sisi_lola_api/app/services/personality_engine.py`
- Documentation: `00_PROJECT_CORE/Documentation/PERSONALITY_INTEGRATION.md`
