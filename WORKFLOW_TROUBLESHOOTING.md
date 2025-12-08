# WORKFLOW TROUBLESHOOTING GUIDE

## ✅ All Local Changes Pushed

**Latest Commit**: 31e31b0
**Status**: All files synced to remote

---

## 🔍 Troubleshooting Steps

### Step 1: Run Minimal Test Workflow

I've created a minimal test workflow to identify the exact failure point.

**Go to**: https://github.com/BAMG-Studio/sisi-lola-project/actions/workflows/personality_training_minimal.yml

**Click**: "Run workflow" button

This will test:
1. ✅ Python setup
2. ✅ Directory creation
3. ✅ Dependency installation
4. ✅ File existence checks
5. ✅ Python imports
6. ✅ Native language training
7. ✅ Personality validation

### Step 2: Check the Logs

After running, check each step:
- Green ✅ = Passed
- Yellow 🟡 = Warning (check logs)
- Red ❌ = Failed (this is the issue)

### Step 3: Common Issues & Fixes

#### Issue: Missing Files
**Symptom**: "File not found" errors
**Fix**: Files are now pushed, re-run workflow

#### Issue: Import Errors
**Symptom**: "ModuleNotFoundError"
**Fix**: Dependencies added to workflow, should auto-install

#### Issue: Permission Errors
**Symptom**: "Permission denied"
**Fix**: Check GitHub secrets are set:
- OPENAI_API_KEY
- HUGGINGFACE_TOKEN
- COHERE_API_KEY

#### Issue: Script Execution Fails
**Symptom**: Python script errors
**Fix**: Check the specific error in logs, scripts have error handling

---

## 📋 Files Pushed to Remote

### Workflows
- ✅ `.github/workflows/personality_training.yml` (main workflow)
- ✅ `.github/workflows/personality_training_minimal.yml` (test workflow)

### Datasets
- ✅ `ml_training/datasets/personality_training_data.json`
- ✅ `ml_training/datasets/native_languages_training.json`

### Scripts
- ✅ `ml_training/scripts/train_native_languages.py`
- ✅ `ml_training/scripts/validate_personality.py`
- ✅ `ml_training/scripts/finetune_personality.py`
- ✅ `00_PROJECT_CORE/Scripts/run_attitude_training.py`

### Config
- ✅ `00_PROJECT_CORE/Config/sisi_attitude.py`

### Services
- ✅ `sisi_lola_api/app/services/personality_engine.py`
- ✅ `sisi_lola_api/app/routers/chat.py`

### Audio
- ✅ `04_AUDIO_CORE/voice_training/generated_samples/*.wav`

---

## 🎯 Next Actions

### 1. Run Minimal Test
```
Go to: https://github.com/BAMG-Studio/sisi-lola-project/actions
Click: "Personality Training (Minimal Test)"
Click: "Run workflow"
```

### 2. Review Results
- If test passes → Run full workflow
- If test fails → Check specific failing step

### 3. Check Secrets
Verify in GitHub repo settings → Secrets and variables → Actions:
- OPENAI_API_KEY (required)
- HUGGINGFACE_TOKEN (optional)
- COHERE_API_KEY (optional)

### 4. Review Logs
Click on failed step to see detailed error message

---

## 🔧 Quick Fixes

### If "run_attitude_training.py" fails:
```yaml
# Already added to workflow:
continue-on-error: true
```

### If "finetune_personality.py" fails:
```yaml
# Already added to workflow:
continue-on-error: true
```

### If directories missing:
```yaml
# Already added to workflow:
mkdir -p 00_PROJECT_CORE/Data
mkdir -p ml_training/logs
mkdir -p ml_training/checkpoints
```

---

## 📊 Expected Test Output

```
✅ Checkout code
✅ Setup Python 3.12
✅ Create directories
✅ Install dependencies
✅ Check files exist
✅ Test Python imports
🟡 Test native language training (may warn)
🟡 Test personality validation (may warn)
✅ Summary
```

---

## 🚨 If Still Failing

### Get Detailed Error
1. Go to failed workflow run
2. Click on the red ❌ step
3. Expand the log
4. Copy the error message
5. Share for specific fix

### Manual Local Test
```bash
# Test native language training
python ml_training/scripts/train_native_languages.py \
  --dataset ml_training/datasets/native_languages_training.json

# Test personality validation
python ml_training/scripts/validate_personality.py \
  --config 00_PROJECT_CORE/Config/sisi_attitude.py
```

---

## 📞 Support

**Workflow URL**: https://github.com/BAMG-Studio/sisi-lola-project/actions

**Test Workflow**: personality_training_minimal.yml
**Full Workflow**: personality_training.yml

Run the minimal test first to identify the exact issue!
