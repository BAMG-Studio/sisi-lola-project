# Sample Profile Images - Setup Instructions

## Status: ⚠️ Awaiting Image Creation

The Sisi Lola brand requires professional profile images and banners for all platforms.

## Required Images

### Profile Pictures Created
- [ ] Master Profile (800×800px) - Source for all resizing
- [ ] YouTube Profile (800×800px)
- [ ] Instagram Profile (320×320px)
- [ ] TikTok Profile (200×200px)
- [ ] Facebook Profile (180×180px)
- [ ] Twitch Profile (256×256px)
- [ ] Reddit Profile (256×256px)
- [ ] Vumistream Profile (400×400px)
- [ ] Twiva Profile (400×400px)
- [ ] Wowzi Profile (400×400px)

### Banner Images Created
- [ ] YouTube Banner (2560×1440px)
- [ ] Facebook Cover (820×312px)
- [ ] Twitch Banner (1200×480px)
- [ ] Reddit Banner (1920×384px)
- [ ] Vumistream Banner (1920×1080px)
- [ ] Twiva Banner (1920×1080px)

## Creation Methods

### Option 1: Use generate_sample_images.py (Requires PIL)

```bash
# Install PIL/Pillow
sudo apt install python3-pil

# Run generator
cd 00_PROJECT_CORE/Scripts
python3 generate_sample_images.py
```

This will create placeholder images with purple gradient backgrounds and "SL" branding.

### Option 2: Design Professional Images (RECOMMENDED)

Use professional design tools:

**Canva (Easiest)**
1. Go to canva.com
2. Create custom sizes for each platform
3. Use brand colors:
   - Primary: Purple (#8A2BE2)
   - Secondary: Gold (#FFD700)
   - Text: White (#FFFFFF)
4. Include "Sisi Lola" text or logo
5. Export as PNG (highest quality)
6. Save to `05_BRANDING_ARTIFACTS/profile_pictures/` and `banners/`

**Adobe Photoshop/Illustrator**
1. Create artboards for each size specification
2. Design with brand guidelines
3. Export optimized for web (PNG)
4. Save to appropriate directories

**Figma**
1. Create frames matching platform specifications
2. Design system with brand colors/fonts
3. Export as PNG
4. Batch download to directories

## Brand Guidelines

### Profile Picture Requirements
- **Subject**: "SL" monogram or Sisi Lola avatar
- **Colors**: Purple gradient background with gold accents
- **Style**: Modern, professional, African-inspired
- **Format**: PNG with transparency where possible
- **Quality**: High resolution, export at 2x actual size

### Banner Requirements
- **Elements**: 
  - "SISI LOLA" text (large, prominent)
  - Tagline: "AI Voice of Africa"
  - Social handle: "@sisilola"
- **Colors**: Consistent with profile (purple/gold)
- **Layout**: Leave safe zones (avoid text near edges)
- **Format**: PNG or JPEG (95% quality)

## Quick Start Template

If you need placeholder images immediately:

1. Use this text-based placeholder for now
2. Create minimal design:
   - Solid purple background (#8A2BE2)
   - White "SL" text in center (bold, sans-serif)
   - No additional elements
3. Upload as temporary profile picture
4. Replace with professional design within 1 week

## Validation

After creating images, run:

```bash
cd 00_PROJECT_CORE/Scripts
python3 profile_image_validator.py
```

This will check:
- ✓ Image dimensions match specifications
- ✓ File sizes are acceptable
- ✓ All required images exist
- ✓ Format is correct (PNG/JPEG)

## Next Steps

1. **IMMEDIATE**: Create master 800×800px profile picture
2. **RECOMMENDED**: Use `profile_image_validator.py` to batch resize
3. **THEN**: Create platform-specific banners
4. **FINALLY**: Upload to all accounts

---

**Status**: Placeholder documentation created  
**Date**: November 25, 2025  
**Action Required**: Create professional branded images
