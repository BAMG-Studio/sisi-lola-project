# HOW TO TRIGGER PERSONALITY TRAINING WORKFLOW

## ✅ Workflow Fixed and Deployed

**Commit**: 38cf890
**Status**: Ready to run
**Native Languages**: Yoruba, Pidgin, Code-switching included

---

## Method 1: GitHub Actions UI (Recommended)

1. Go to: https://github.com/BAMG-Studio/sisi-lola-project/actions
2. Click on "Personality Training Pipeline" in the left sidebar
3. Click "Run workflow" button (top right)
4. Select branch: `main`
5. Choose training intensity:
   - **light**: 3 epochs (quick test)
   - **moderate**: 5 epochs (standard)
   - **intensive**: 10 epochs (deep training)
6. Click "Run workflow"
7. Monitor progress in real-time

---

## Method 2: Automatic Triggers

The workflow runs automatically on:

### Weekly Schedule
- **Every Monday at 3 AM UTC**
- Runs with moderate intensity
- Trains all datasets

### On Code Push
Triggers when you push changes to:
- `00_PROJECT_CORE/Config/sisi_attitude.py`
- `ml_training/datasets/**` (any dataset)
- `04_AUDIO_CORE/**` (audio samples)
- `sisi_lola_api/app/services/personality_engine.py`

---

## Method 3: GitHub CLI (After Auth)

```bash
# First time setup
gh auth login

# Then trigger workflow
gh workflow run personality_training.yml -f training_intensity=light

# Check status
gh run list --workflow=personality_training.yml
```

---

## What the Workflow Does

### Step 1: Train Personality
- Loads personality configuration
- Processes training examples
- Applies humor and charisma patterns

### Step 2: Train Native Languages
- **Yoruba**: Greetings, phrases, proverbs
- **Pidgin**: Conversational patterns, expressions
- **Code-switching**: Natural language mixing
- Processes 15+ native language samples

### Step 3: Fine-tune with OpenAI
- Uses GPT-3.5-turbo
- Applies training intensity
- Creates personality-aware model

### Step 4: Validate
- Checks personality scores
- Verifies humor >= 8.5
- Confirms charisma >= 9.0
- Validates native language integration

### Step 5: Test Integration
- Starts API server
- Runs personality tests
- Generates test report

### Step 6: Deploy
- Updates production config
- Commits changes
- Pushes to repository

---

## Monitoring the Run

### Real-time Progress
1. Go to Actions tab
2. Click on the running workflow
3. Watch each step complete
4. Green ✅ = Success
5. Yellow 🟡 = Warning (acceptable)
6. Red ❌ = Error (needs fix)

### Check Logs
- Click on any step to see detailed logs
- Download artifacts after completion
- Review training statistics

### Artifacts Generated
- `personality-training-{run_number}`
  - All training data JSON files
  - Training logs
  - Model metadata
  - Native language processing results

---

## Expected Duration

- **Light**: ~5-10 minutes
- **Moderate**: ~10-15 minutes
- **Intensive**: ~20-30 minutes

---

## Success Indicators

### ✅ Training Complete
- All steps show green checkmarks
- Artifacts uploaded successfully
- Config updated in repository

### ✅ Native Languages Trained
- Yoruba samples processed
- Pidgin patterns learned
- Code-switching enabled

### ✅ Personality Enhanced
- Humor: 8.5/10
- Charisma: 9.0/10
- Authenticity: 9.0/10

---

## Troubleshooting

### Workflow Fails
1. Check the logs in GitHub Actions
2. Review error messages
3. Verify secrets are set:
   - OPENAI_API_KEY
   - HUGGINGFACE_TOKEN
   - COHERE_API_KEY

### Training Warnings
- Yellow warnings are acceptable
- Steps continue with `continue-on-error: true`
- Check artifacts for details

### No Changes Committed
- Normal if config unchanged
- Training still completed
- Model updated internally

---

## Next Steps After Training

1. **Test Locally**:
   ```bash
   cd sisi_lola_api
   uvicorn app.main:app --reload
   python test_sisi_personality.py
   ```

2. **Chat with Sisi**:
   ```bash
   curl -X POST "http://localhost:8000/chat/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Teach me some Yoruba!"}'
   ```

3. **Monitor Performance**:
   - User feedback
   - Response quality
   - Language mixing accuracy
   - Humor effectiveness

---

## Manual Trigger Now

**Go to**: https://github.com/BAMG-Studio/sisi-lola-project/actions/workflows/personality_training.yml

Click "Run workflow" and select intensity!

---

**Status**: 🟢 Ready to run
**Native Languages**: ✅ Integrated
**Next Auto-Run**: Monday 3 AM UTC
