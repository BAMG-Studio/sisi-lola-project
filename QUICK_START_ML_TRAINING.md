# QUICK START: ML Training Orchestration

## 🚀 Get Started in 5 Minutes

### Step 1: Configure GitHub Secrets

Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add these secrets:
```
HUGGINGFACE_TOKEN = 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
SLACK_WEBHOOK_URL = your_slack_webhook_url (optional)
ENV_FILE = (paste entire contents of sisi_lola_api/.env)
```

### Step 2: Test Locally (Optional)

```bash
# Install Ansible
pip install ansible

# Test the playbook
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=partial" \
  -e "model=natlas_audio" \
  --check
```

### Step 3: Trigger Training

#### Option A: Manual (GitHub UI)
1. Go to **Actions** tab
2. Click **ML Training Orchestration**
3. Click **Run workflow**
4. Select options:
   - Mode: `partial`
   - Model: `natlas_audio`
   - Phase: `foundation`
5. Click **Run workflow**

#### Option B: Automatic (Push Data)
```bash
# Add new training data
cp new_audio_samples/* 04_AUDIO_CORE/01_Voice_Samples/

# Commit and push
git add 04_AUDIO_CORE/
git commit -m "Add new voice samples"
git push

# Training automatically starts!
```

#### Option C: Scheduled (Automatic)
Already configured! Runs every Sunday at 2 AM UTC.

### Step 4: Monitor Progress

1. Go to **Actions** tab
2. Click on running workflow
3. Watch real-time logs
4. Download artifacts when complete

## 📊 Training Modes Explained

### Partial (Recommended for Regular Updates)
- **Speed**: Fast (1-2 hours)
- **Use**: Add new samples, regular updates
- **Cost**: Low compute

### Full (For Major Changes)
- **Speed**: Slow (6-12 hours)
- **Use**: Initial training, major updates
- **Cost**: High compute

### Phasic (For Specific Phases)
- **Speed**: Medium (2-4 hours)
- **Use**: Debug specific phase
- **Cost**: Medium compute

## 🎯 Common Use Cases

### Use Case 1: Add New Voice Samples
```bash
# 1. Add samples
cp samples/*.wav 04_AUDIO_CORE/01_Voice_Samples/

# 2. Push
git add . && git commit -m "New samples" && git push

# 3. Wait for automatic training
# Check Actions tab for progress
```

### Use Case 2: Train New Model
```bash
# 1. Edit config
nano ml_training/configs/training_config.yaml

# 2. Add model configuration
# 3. Trigger full training via GitHub Actions UI
```

### Use Case 3: Emergency Retrain
```bash
# Quick local execution
ansible-playbook ansible/playbooks/ml_training.yml \
  -e "mode=partial" \
  -e "model=all"
```

## 🔧 Troubleshooting

### Training Fails
- Check GitHub Actions logs
- Verify secrets are set correctly
- Ensure dataset path exists

### No Automatic Trigger
- Check if files are in correct directory
- Verify push is to `main` branch
- Check workflow file syntax

### Slow Training
- Use `partial` mode instead of `full`
- Train specific model instead of `all`
- Consider cloud compute (see docs)

## 📚 Next Steps

- Read full documentation: `ML_TRAINING_ORCHESTRATION.md`
- Configure Slack notifications
- Set up cloud training for faster execution
- Add custom models to config

---

**Need Help?** Check the full documentation or open an issue.
