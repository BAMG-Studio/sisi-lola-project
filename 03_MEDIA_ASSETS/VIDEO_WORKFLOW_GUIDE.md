# VIDEO ASSET GENERATION WORKFLOW GUIDE
## Sisi Lola Project

---

## PHASE 1: PREPARATION

### 1.1 Review Requirements
- [ ] Open `MASTER_ASSET_MANIFEST.csv`
- [ ] Filter for Type = "Video"
- [ ] Note total count needed
- [ ] Prioritize based on project phase

### 1.2 Set Up Accounts
- [ ] Runway ML (runwayml.com) - For general video generation
- [ ] Kling AI (klingai.com) - For character consistency
- [ ] Pika Labs (pika.art) - For alternative generations
- [ ] HeyGen (heygen.com) - For avatar-based talking head videos

### 1.3 Organize Workspace
- [ ] Create temporary generation folder on desktop
- [ ] Prepare naming convention reference
- [ ] Set up quality control checklist

---

## PHASE 2: CHARACTER CONSISTENCY SETUP

### 2.1 Generate Reference Images First
Before generating videos, ensure you have:
- [ ] At least 10 consistent reference images of Sisi Lola
- [ ] Full body shots from multiple angles
- [ ] Close-up facial expressions
- [ ] Outfit variations

### 2.2 Create Character Model (If Available)
Some platforms allow character training:
- **HeyGen:** Upload 5-10 photos, create avatar
- **Runway:** Use consistent image prompts with same seed/style
- **Kling:** Upload reference images for consistency

### 2.3 Test Generation
- [ ] Generate 3-5 test clips (5 seconds each)
- [ ] Verify face consistency across tests
- [ ] Adjust prompts as needed
- [ ] Document what works best

---

## PHASE 3: BATCH GENERATION

### 3.1 Organize by Priority

**Priority 1 (Do First):**
- Podcast intros (10 videos)
- Simple talking head shots (15 videos)

**Priority 2:**
- Commercial spots (15 videos)
- Social media shorts (25 videos)

**Priority 3:**
- Transitions and effects (10 videos)
- B-roll and environmental shots (remaining)

### 3.2 Generation Process

For each video:

1. **Copy prompt** from batch prompt file
2. **Paste into generation platform**
3. **Adjust settings:**
   - Resolution: 4K (3840x2160) or highest available
   - Duration: As specified (15s, 30s, 60s)
   - Motion: Medium (not too fast, not static)
   - Camera: Specify if needed
4. **Generate** (may take 5-30 minutes per video)
5. **Review output:**
   - Does face match reference?
   - Is motion smooth (no warping)?
   - Is framing correct?
   - Is lighting good?
6. **If acceptable:** Download, rename, move to folder
7. **If not acceptable:** Regenerate with adjusted prompt
8. **Update manifest:** Change status to "Generated"

### 3.3 Bulk Download
- Use browser extensions for batch download if available
- Organize downloads by category before renaming
- Keep originals until quality check passes

---

## PHASE 4: QUALITY CONTROL

### 4.1 Technical Check
For each video, verify:
- [ ] Resolution: 4K minimum (unless specified otherwise)
- [ ] Framerate: 60fps consistent
- [ ] Duration: Matches requirement (±1 second acceptable)
- [ ] Audio: If included, is synchronized
- [ ] Format: MP4 H.265 (convert if needed)

### 4.2 Creative Check
- [ ] Character consistency (Sisi Lola looks the same)
- [ ] No visible AI artifacts (warping, morphing, glitches)
- [ ] Lighting is professional
- [ ] Composition follows brief
- [ ] Overall "broadcast quality" feel

### 4.3 Batch Quality Review
- Watch 10 videos in sequence
- Note any jarring inconsistencies
- Flag for regeneration if needed

---

## PHASE 5: POST-PROCESSING

### 5.1 Upscaling (If Needed)
If platform doesn't support 4K:
- Use **Topaz Video AI** to upscale 1080p → 4K
- Settings: Artemis High Quality, Medium enhancement

### 5.2 Color Grading
Apply consistent look:
- Import into **DaVinci Resolve** or **Premiere Pro**
- Apply LUT: `LUT_AfroFuture_Warm.cube`
- Adjust: Slightly warmer tones, boost saturation 10%
- Export: Same format/codec as input

### 5.3 Audio Sync/Mix (For Videos with Audio)
- Import into **Audacity** or **Adobe Audition**
- Add background music bed (-18dB)
- Add sound effects where appropriate
- Master: Normalize to -6dB peak
- Export: 48kHz 24-bit stereo

### 5.4 Final Export Settings
```
Codec: H.265 (HEVC)
Resolution: 3840x2160 (for 16:9) or 1080x1920 (for 9:16)
Framerate: 60fps constant
Bitrate: 50-80 Mbps (VBR)
Audio: AAC 320kbps stereo
Color Space: Rec.709
```

---

## PHASE 6: ORGANIZATION & ARCHIVING

### 6.1 File Naming
Rename all files according to manifest:
```
Format: [CATEGORY]_[DESCRIPTION]_[VERSION].[EXT]

Examples:
MED-COM-0023_Commercial_CoffeeBrand_30sec.mp4
MED-INTRO-0012_Podcast_Intro_Style02_15sec.mp4
MED-IGSHT-0005_Instagram_Reel_TechTip_60sec.mp4
```

### 6.2 Folder Placement
Move each file to correct subcategory:
- Commercial spots → `03_MEDIA_ASSETS/01_Commercial_Spots/`
- Podcast intros → `03_MEDIA_ASSETS/02_Podcast_Intros/`
- Instagram Reels → `03_MEDIA_ASSETS/04_Social_Shorts_Instagram/`
- Etc.

### 6.3 Create Proxies (For Large Files)
- Generate 1080p H.264 proxies for editing
- Save to `06_RENDER_OUTPUT/Web_Optimized/`
- Keep 4K masters in original folders

### 6.4 Update Manifest
- Open `MASTER_ASSET_MANIFEST.csv`
- Update "Status" column: "Pending Generation" → "Completed"
- Add notes if any deviations from spec
- Save and backup

---

## PHASE 7: INTEGRATION & TESTING

### 7.1 Create Sample Edit
- Import 5-10 completed videos
- Edit together a 2-minute sample
- Test consistency across videos
- Verify color grading matches
- Check for jarring transitions

### 7.2 VR Testing (If Applicable)
- Convert to VR-compatible format
- Test in headset (Quest, PSVR2, etc.)
- Verify comfort (no motion sickness)
- Check resolution holds up in VR

### 7.3 Platform Optimization
Create platform-specific versions:

**Instagram/TikTok:**
- Resolution: 1080x1920
- Duration: 15-60 seconds
- Captions: Burn in or upload SRT
- Cover frame: Compelling first frame

**YouTube:**
- Resolution: 3840x2160
- Thumbnail: Export first frame as PNG
- Chapters: Note timestamps for description

**Website/Portfolio:**
- Resolution: 1920x1080 (web-optimized)
- Bitrate: 10-15 Mbps (faster loading)
- Format: MP4 H.264 (broader compatibility)

---

## TROUBLESHOOTING

### Problem: Character Face Keeps Changing
**Solutions:**
- Use image-to-video instead of text-to-video
- Upload reference image with each generation
- Try different platform (Kling has better consistency)
- Consider creating custom avatar (HeyGen)

### Problem: Motion Looks Unnatural/Warping
**Solutions:**
- Reduce motion complexity in prompt
- Shorter duration (5-10s easier than 30s)
- Use static camera instead of moving camera
- Generate in segments and stitch together

### Problem: Low Resolution Output
**Solutions:**
- Check platform settings (some default to 720p)
- Use upscaling AI tool (Topaz Video AI)
- Try different platform with higher res support

### Problem: Audio Not Syncing
**Solutions:**
- Generate video and audio separately, sync in post
- Use manual lip-sync tools (Wav2Lip, D-ID)
- Consider using HeyGen for talking head videos

---

## PLATFORM-SPECIFIC TIPS

### Runway Gen-3
- **Best for:** General scenes, motion, creativity
- **Character consistency:** Moderate (use img2vid)
- **Max duration:** 10 seconds (extend by gen2gen)
- **Tip:** Describe camera movement first in prompt

### Kling AI
- **Best for:** Character consistency, longer clips
- **Character consistency:** Excellent (best available)
- **Max duration:** 10 seconds
- **Tip:** Upload reference images for each generation

### Pika Labs
- **Best for:** Quick tests, effects, transitions
- **Character consistency:** Low (use for environments)
- **Max duration:** 3 seconds (extendable)
- **Tip:** Great for background/environmental videos

### HeyGen
- **Best for:** Talking head videos, presentations
- **Character consistency:** Perfect (avatar-based)
- **Max duration:** Unlimited (avatar speaks script)
- **Tip:** Create Sisi Lola avatar once, reuse forever

---

## ESTIMATED TIMELINE

**For 50 video assets:**
- Preparation: 2 hours
- Character setup: 3 hours
- Batch generation: 20-40 hours (platform dependent)
- Quality control: 5 hours
- Post-processing: 10 hours
- Organization: 2 hours

**Total: 42-62 hours** (spread over 1-2 weeks with platform wait times)

---

## FINAL CHECKLIST

Before considering video generation complete:
- [ ] All manifest videos generated
- [ ] Quality checks passed
- [ ] Files renamed correctly
- [ ] Organized in proper folders
- [ ] Proxies created for large files
- [ ] Manifest updated
- [ ] Sample edit created
- [ ] Platform-specific versions exported
- [ ] Backup created
- [ ] Ready for content production use

---

**Good luck with video generation! Remember: Consistency is key.**
