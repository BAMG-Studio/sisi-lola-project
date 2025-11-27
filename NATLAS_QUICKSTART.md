# N-ATLaS QUICK START GUIDE
## 517 African Languages Support

### IMMEDIATE ACTIONS (Do Now)

#### Step 1: Request Model Access
1. Go to: https://huggingface.co/NCAIR1/N-ATLaS
2. Click "Request Access" button
3. Fill out the form (research/commercial use)
4. Wait for approval email (24-48 hours)

#### Step 2: HuggingFace Authentication
```bash
# Install HuggingFace CLI (if not installed)
pip install huggingface_hub

# Login to HuggingFace
huggingface-cli login
```

When prompted, paste your token from: https://huggingface.co/settings/tokens

#### Step 3: Verify Access
```bash
cd c:\Users\POK28\Dropbox\Sisi_Lola\00_PROJECT_CORE\Scripts
python verify_natlas_access.py
```

#### Step 4: Train Sisi Lola Voice (Once Access Granted)
```bash
python natlas_multilingual_trainer.py
```

---

## WHAT N-ATLaS GIVES YOU

### Priority Languages for Sisi Lola:
- **Yoruba** (yor_Latn) - Primary
- **Nigerian Pidgin** (pcm_Latn) - Secondary
- **English** (eng_Latn) - Tertiary
- **Igbo** (ibo_Latn) - Expansion
- **Hausa** (hau_Latn) - Expansion
- **Swahili** (swa_Latn) - Pan-African reach
- **Amharic** (amh_Ethi) - Ethiopian market
- **French** (fra_Latn) - West African francophone

### Total: 517 African Languages Available

---

## CURRENT STATUS

✓ **240 training samples generated** (using Facebook MMS-TTS-YOR)
✓ **HeyGen upload package ready** (10 curated samples)
✓ **Platform training complete** (6 platforms × 40 samples)
✓ **Scripts ready** (natlas_multilingual_trainer.py)

⏳ **Waiting for N-ATLaS access approval**

---

## FALLBACK PLAN (If Access Delayed)

Continue using existing Facebook MMS-TTS-YOR model:
- Already generating high-quality Yoruba samples
- 240 samples available for immediate use
- Can deploy to platforms now while waiting for N-ATLaS

---

## TROUBLESHOOTING

### "401 Unauthorized" Error
- Access not yet granted
- Check email for approval notification
- Re-run: `python verify_natlas_access.py`

### "Not logged in" Error
- Run: `huggingface-cli login`
- Paste token from: https://huggingface.co/settings/tokens

### Token Not Found
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "Sisi Lola N-ATLaS"
4. Type: "Read"
5. Copy token and paste when prompted

---

## NEXT STEPS AFTER ACCESS

1. ✓ Verify access: `python verify_natlas_access.py`
2. Train voice: `python natlas_multilingual_trainer.py`
3. Generate 517-language samples
4. Upload to HeyGen for custom voice
5. Deploy to all platforms

---

**Status**: Waiting for HuggingFace approval
**ETA**: 24-48 hours
**Action**: Request access at https://huggingface.co/NCAIR1/N-ATLaS
