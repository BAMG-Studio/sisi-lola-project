#!/usr/bin/env python3
"""
VIDEO ASSET BATCH PROCESSOR
Automates video generation workflow for Sisi Lola Project
Integrates with Runway ML, Kling AI, and other video generation platforms
"""

import csv
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# VIDEO GENERATION TEMPLATES
# ============================================================================

VIDEO_TEMPLATES = {
    "commercial_30sec": {
        "format": "16:9",
        "resolution": "3840x2160",
        "framerate": "60fps",
        "duration": "30 seconds",
        "codec": "H.265 (HEVC)",
        "audio": "Stereo 48kHz AAC",
        "typical_structure": [
            {"time": "0-3s", "content": "Hook/Attention grabber"},
            {"time": "3-8s", "content": "Product introduction"},
            {"time": "8-20s", "content": "Key features/benefits"},
            {"time": "20-27s", "content": "Call to action"},
            {"time": "27-30s", "content": "Logo/branding"}
        ]
    },
    
    "podcast_intro_15sec": {
        "format": "16:9",
        "resolution": "3840x2160",
        "framerate": "60fps",
        "duration": "15 seconds",
        "codec": "H.265 (HEVC)",
        "audio": "Stereo 48kHz AAC",
        "typical_structure": [
            {"time": "0-2s", "content": "Transition/fade in"},
            {"time": "2-7s", "content": "Host entrance/greeting"},
            {"time": "7-12s", "content": "Episode title reveal"},
            {"time": "12-15s", "content": "Settle into main content"}
        ]
    },
    
    "social_vertical_60sec": {
        "format": "9:16 (Vertical)",
        "resolution": "1080x1920",
        "framerate": "60fps",
        "duration": "15-60 seconds",
        "codec": "H.264 (compatibility)",
        "audio": "Stereo 48kHz AAC",
        "typical_structure": [
            {"time": "0-2s", "content": "HOOK (critical for retention)"},
            {"time": "2-10s", "content": "Problem/question setup"},
            {"time": "10-45s", "content": "Solution/answer/entertainment"},
            {"time": "45-55s", "content": "Payoff/conclusion"},
            {"time": "55-60s", "content": "CTA (like/follow/share)"}
        ],
        "optimization": {
            "captions": "Mandatory (85% watch without sound)",
            "text_size": "Large and readable on mobile",
            "pacing": "Fast cuts (2-4 second shots max)",
            "thumbnail": "First frame must be compelling"
        }
    },
    
    "transition_5sec": {
        "format": "16:9",
        "resolution": "3840x2160",
        "framerate": "60fps",
        "duration": "3-5 seconds",
        "codec": "ProRes 4444 (with alpha)",
        "audio": "Optional sound effect",
        "notes": "Should work on any background, include alpha channel"
    }
}

# ============================================================================
# RUNWAY GEN-3 PROMPT TEMPLATES
# ============================================================================

RUNWAY_PROMPTS = {
    "host_walking_confident": """
Smooth tracking shot following Sisi Lola as she walks confidently through 
a modern high-tech studio. She's wearing an elegant afrofuturist purple 
blazer. Camera moves steadily alongside her. Cinematic lighting with warm 
tones. She turns to camera and smiles. Professional broadcast quality. 
4k resolution, 60fps, shallow depth of field.
""",
    
    "host_podcast_welcome": """
Medium shot of Sisi Lola sitting in a luxury podcast studio with floating 
holographic displays in background. She looks up from notes and makes warm 
eye contact with camera, smiling welcomingly. Soft dolly zoom in. 
Professional studio lighting. Cinematic color grading. Smooth camera movement. 
4k 60fps.
""",
    
    "product_reveal_dramatic": """
Dramatic reveal shot starting on Sisi Lola's face showing curiosity, camera 
pulls back to reveal she's holding a futuristic tech product. Holographic 
information appears around the product. Studio lighting with dramatic shadows. 
Black background. Camera rotates 15 degrees during shot. 4k cinematic quality.
""",
    
    "transition_holographic": """
Holographic particle transition effect. Sisi Lola begins to dissolve into 
glowing geometric particles that swirl and reform into the next scene. 
Purple and blue color scheme. Magical but tech-inspired aesthetic. Smooth 
animation. Alpha channel friendly. 3 seconds duration.
""",
    
    "social_media_hook": """
Vertical video (9:16). Extreme close-up of Sisi Lola's eyes widening with 
surprise, quick zoom out to medium shot as she points at camera. Text space 
at top and bottom for captions. High energy. Bright, colorful lighting. 
Fast-paced movement. Mobile-optimized framing. 2 seconds.
"""
}

# ============================================================================
# VIDEO EDITING TIMELINE TEMPLATES (JSON for DaVinci Resolve / Premiere)
# ============================================================================

def generate_podcast_intro_timeline():
    """Generate timeline structure for podcast intro"""
    return {
        "timeline_name": "Podcast_Intro_Template_v01",
        "duration": "15 seconds",
        "resolution": "3840x2160",
        "framerate": 60,
        "tracks": {
            "video": [
                {
                    "track_number": 1,
                    "clips": [
                        {"in": "00:00:00:00", "out": "00:00:03:00", "type": "Background Gradient"},
                        {"in": "00:00:03:00", "out": "00:00:15:00", "type": "Studio Environment"}
                    ]
                },
                {
                    "track_number": 2,
                    "clips": [
                        {"in": "00:00:02:00", "out": "00:00:15:00", "type": "Sisi Lola Video", "notes": "Green screen keyed"}
                    ]
                },
                {
                    "track_number": 3,
                    "clips": [
                        {"in": "00:00:00:00", "out": "00:00:02:00", "type": "Logo Animation"},
                        {"in": "00:00:07:00", "out": "00:00:12:00", "type": "Episode Title Graphic"}
                    ]
                },
                {
                    "track_number": 4,
                    "clips": [
                        {"in": "00:00:04:00", "out": "00:00:15:00", "type": "Holographic UI Overlay", "opacity": 70}
                    ]
                }
            ],
            "audio": [
                {
                    "track_number": 1,
                    "clips": [
                        {"in": "00:00:00:00", "out": "00:00:15:00", "type": "Music Bed", "volume": -18}
                    ]
                },
                {
                    "track_number": 2,
                    "clips": [
                        {"in": "00:00:02:00", "out": "00:00:15:00", "type": "Voiceover/Host", "volume": -6}
                    ]
                },
                {
                    "track_number": 3,
                    "clips": [
                        {"in": "00:00:00:00", "out": "00:00:02:00", "type": "Whoosh SFX", "volume": -12},
                        {"in": "00:00:07:00", "out": "00:00:08:00", "type": "Title Appear SFX", "volume": -12}
                    ]
                }
            ]
        },
        "effects": {
            "color_grading": "LUT_AfroFuture_Warm.cube",
            "transitions": ["Dissolve (1s)", "Holographic wipe (0.5s)"],
            "motion_graphics": "Title animation with particle effects"
        }
    }

# ============================================================================
# BATCH PROCESSING FUNCTIONS
# ============================================================================

def extract_video_assets_from_manifest(manifest_csv_path):
    """Parse manifest and extract all video asset requirements"""
    video_assets = []
    
    with open(manifest_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'].lower() == 'video':
                video_assets.append(row)
    
    return video_assets

def generate_batch_prompt_file(video_assets, output_path):
    """Create a batch file of prompts ready for video generation"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# SISI LOLA VIDEO GENERATION PROMPTS\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# Total Videos: {len(video_assets)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, asset in enumerate(video_assets, 1):
            f.write(f"## VIDEO {i}/{len(video_assets)}\n")
            f.write(f"**ID:** {asset.get('ID', 'N/A')}\n")
            f.write(f"**Filename:** {asset['Filename']}\n")
            f.write(f"**Category:** {asset['Category']}\n")
            f.write(f"**Resolution:** {asset.get('Resolution', '4K 60fps')}\n\n")
            f.write(f"**PROMPT:**\n```\n{asset['Prompt']}\n```\n\n")
            f.write("**CHECKLIST:**\n")
            f.write("- [ ] Generated\n")
            f.write("- [ ] Downloaded\n")
            f.write("- [ ] Renamed correctly\n")
            f.write("- [ ] Quality approved\n")
            f.write("- [ ] Moved to correct folder\n\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"✓ Created batch prompt file: {output_path}")
    print(f"  Contains {len(video_assets)} video generation prompts")

def create_video_generation_workflow_guide(output_path):
    """Create step-by-step guide for video asset generation"""
    guide = """# VIDEO ASSET GENERATION WORKFLOW GUIDE
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
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✓ Created workflow guide: {output_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("VIDEO ASSET BATCH PROCESSOR - SISI LOLA PROJECT")
    print("=" * 80)
    
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    manifest_path = project_root / "MASTER_ASSET_MANIFEST.csv"
    output_dir = project_root / "03_MEDIA_ASSETS"
    
    # Extract video assets
    print("\nExtracting video assets from manifest...")
    video_assets = extract_video_assets_from_manifest(manifest_path)
    print(f"✓ Found {len(video_assets)} video assets")
    
    # Generate batch prompt file
    print("\nGenerating batch prompt file...")
    prompt_file = output_dir / "VIDEO_GENERATION_PROMPTS.md"
    generate_batch_prompt_file(video_assets, prompt_file)
    
    # Create workflow guide
    print("\nCreating workflow guide...")
    workflow_file = output_dir / "VIDEO_WORKFLOW_GUIDE.md"
    create_video_generation_workflow_guide(workflow_file)
    
    # Export timeline template
    print("\nGenerating timeline template...")
    timeline_template = generate_podcast_intro_timeline()
    timeline_file = output_dir / "PODCAST_INTRO_TIMELINE_TEMPLATE.json"
    with open(timeline_file, 'w', encoding='utf-8') as f:
        json.dump(timeline_template, f, indent=2)
    print(f"✓ Created timeline template: {timeline_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VIDEO BATCH PROCESSING SETUP COMPLETE")
    print("=" * 80)
    print(f"Total video assets to generate: {len(video_assets)}")
    print(f"\nFiles created:")
    print(f"  - {prompt_file}")
    print(f"  - {workflow_file}")
    print(f"  - {timeline_file}")
    print("\nNext steps:")
    print("  1. Review VIDEO_WORKFLOW_GUIDE.md")
    print("  2. Set up accounts on video generation platforms")
    print("  3. Start with Priority 1 assets")
    print("  4. Use VIDEO_GENERATION_PROMPTS.md for batch work")
    print("=" * 80)

if __name__ == "__main__":
    main()
