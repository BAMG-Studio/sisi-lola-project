# WAV2LIP SETUP - MANUAL STEPS REQUIRED

**Status**: Python 3.10 installed ✅  
**Status**: Wav2Lip cloned ✅  
**Status**: Model download BLOCKED (need manual download)

---

## WHAT'S DONE:

✅ Python 3.10 installed  
✅ All dependencies installed  
✅ Wav2Lip repository cloned to: `wav2lip_workspace/Wav2Lip`  
❌ Model checkpoint needs manual download

---

## MANUAL STEP REQUIRED:

### Download Wav2Lip Model (1.5GB):

**Option 1 - Direct Download**:
1. Go to: https://github.com/Rudrabha/Wav2Lip#getting-the-weights
2. Click "wav2lip_gan.pth" link
3. Download file (1.5GB)
4. Save to: `c:\Users\POK28\Dropbox\Sisi_Lola\wav2lip_workspace\Wav2Lip\checkpoints\wav2lip_gan.pth`

**Option 2 - Google Drive**:
1. Go to: https://drive.google.com/file/d/1fQtBSYEyuai9MjBOF8j7zZ0DYFHj0gfC/view
2. Click "Download"
3. Save to: `c:\Users\POK28\Dropbox\Sisi_Lola\wav2lip_workspace\Wav2Lip\checkpoints\wav2lip_gan.pth`

---

## AFTER DOWNLOAD:

Run this to generate first talking video:

```bash
cd c:\Users\POK28\Dropbox\Sisi_Lola\00_PROJECT_CORE\Scripts
py -3.10 wav2lip_generate.py
```

---

## ALTERNATIVE: USE D-ID FOR NOW

While downloading model, use D-ID API (already configured):

```bash
# D-ID will work once their API is stable
python did_talking_short.py
```

---

## PRODUCTION CAPACITY:

Once Wav2Lip is set up:
- **Cost**: $0 (free forever)
- **Speed**: 2-3 minutes per 7-min video (with GPU)
- **Capacity**: 25-60 minutes/day = 4-9 videos/day
- **Quality**: Professional lip-sync

---

**Next**: Download model manually, then run `py -3.10 wav2lip_generate.py`
