# SISI LOLA AVATAR EXPORT INSTRUCTIONS

**Status**: ACTION REQUIRED  
**Priority**: HIGH

---

## PROBLEM IDENTIFIED

Current Wav2Lip video uses:
- ❌ Static reference sheet PNG (not beautiful avatar)
- ❌ No podcast scene/visual background
- ✅ Correct Yoruba voice sample (locked)

---

## SOLUTION: EXPORT HEYGEN AVATAR FRAME

### Step 1: Access HeyGen Dashboard
1. Go to: https://app.heygen.com
2. Login with your account
3. Navigate to "Avatars" section

### Step 2: Find Sisi Lola Avatar
**Avatar ID**: `046a63da7b20403c8c6bb51dbda12f65`

If this ID doesn't work:
- Look for "Sisi Lola" by name
- Look for avatar in 2-piece ankara/damask attire
- Look for professional, front-facing female avatar

### Step 3: Export Clean Frame
**Option A - From HeyGen Dashboard**:
1. Select the Sisi Lola avatar
2. Generate a 1-second test video
3. Download the video
4. Extract first frame with FFmpeg:
   ```bash
   ffmpeg -i heygen_video.mp4 -vf "select=eq(n\,0)" -vframes 1 sisi_lola_heygen_frame.jpg
   ```

**Option B - Screenshot Method**:
1. Open avatar preview in HeyGen
2. Take high-quality screenshot (1920x1080)
3. Crop to show only avatar (front-facing, centered)
4. Save as JPG

### Step 4: Save to Correct Location
**Required Path**:
```
c:\Users\POK28\Dropbox\Sisi_Lola\01_AVATAR_DNA\sisi_lola_heygen_frame.jpg
```

**Specifications**:
- Format: JPG
- Resolution: 1920x1080 (or higher)
- Content: Front-facing Sisi Lola in ankara attire
- Background: Clean (will be used for lip-sync)

---

## ALTERNATIVE: USE HEYGEN DIRECTLY

If avatar export is difficult, use HeyGen API directly:

**Pros**:
- Beautiful avatar ✅
- Professional quality ✅
- Lip-sync built-in ✅

**Cons**:
- Cost: $1/video
- Voice: May not support Yoruba accent perfectly
- Length: Limited to HeyGen's constraints

**Command**:
```bash
python heygen_custom_avatar_now.py
```

---

## VOICE SOURCE - ALREADY LOCKED ✅

**File**: `04_AUDIO_CORE/voice_samples/sisi_lola_yorunglish_female_LONG.wav`
- Duration: 6.6 minutes
- Language: Yoruba/Yorunglish/Pidgin mix
- Accent: Natural Nigerian
- Status: APPROVED ✅

---

## NEXT STEPS

1. **Export HeyGen avatar frame** (15 minutes)
2. **Save to**: `01_AVATAR_DNA/sisi_lola_heygen_frame.jpg`
3. **Run**: `python production_pipeline_locked.py`
4. **Result**: Beautiful Sisi Lola + Yoruba voice + lip-sync

---

**Current Blocker**: Need HeyGen avatar frame export  
**Estimated Time**: 15 minutes  
**Impact**: Will produce production-quality videos with beautiful avatar
