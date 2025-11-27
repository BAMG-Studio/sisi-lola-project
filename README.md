# SISI LOLA PROJECT - ASSET GENERATION SYSTEM

## PROJECT INITIALIZED: 20251122_130554

This directory structure contains the complete production pipeline for generating 200+ assets for the Sisi Lola VR/AI virtual host project.

## QUICK START

### 1. Review the Master Manifest
Open `MASTER_ASSET_MANIFEST.csv` to see all 200+ assets planned for generation.

### 2. Generate Assets
Each row in the manifest contains:
- **Prompt**: Ready-to-use prompt for AI generation tools
- **Tool**: Recommended platform (Midjourney, Runway, ElevenLabs, etc.)
- **Resolution**: Technical specifications
- **Category/Subcategory**: Where to save the file

### 3. Recommended Tools
- **Images**: Midjourney v6, DALL-E 3, Stable Diffusion XL
- **Videos**: Runway Gen-3, Kling AI, Pika Labs
- **360 VR**: Skybox AI, Blockade Labs
- **Audio**: ElevenLabs, Suno AI, Udio
- **3D Models**: Blender, Unreal Engine 5 MetaHuman

### 4. Batch Generation Workflow
1. Filter manifest by Category
2. Copy prompts to your AI tool
3. Download generated assets
4. Rename files to match manifest filenames
5. Save to appropriate subcategory folder
6. Update Status column to "Generated"

### 5. Consistency Protocol
**CRITICAL**: For all Sisi Lola character generations, use:
- Seed: `45822`
- Style Reference: Include "same face, character consistency" in all prompts
- Face lock: Use the reference sheets in `01_AVATAR_DNA/01_Reference_Sheets` as style guides

## PROJECT STRUCTURE

```
Sisi_Lola/
├── 00_PROJECT_CORE/          # Documentation & scripts
├── 01_AVATAR_DNA/            # Character assets (60 items)
├── 02_ENVIRONMENTS_VR/       # Environments & 360 backdrops (60 items)
├── 03_MEDIA_ASSETS/          # Videos & commercials (50 items)
├── 04_AUDIO_CORE/            # Voice & music (30 items)
├── 05_BRANDING_ARTIFACTS/    # Logos & UI (20 items)
├── 06_RENDER_OUTPUT/         # Processed finals
└── 07_RAW_WORKSPACE/         # Work in progress
```

## GENERATION PRIORITY

### Phase 1 (Foundation) - DO FIRST
1. Avatar reference sheets (10 items)
2. Main studio environment (10 items)
3. Core logo variations (5 items)
4. Voice samples for cloning (10 items)

### Phase 2 (Expansion)
5. Expression library (15 items)
6. Outfit variations (20 items)
7. Additional environments (50 items)

### Phase 3 (Content Production)
8. Commercial spots (15 items)
9. Social media shorts (25 items)
10. Music beds and soundscapes (20 items)

## QUALITY CONTROL CHECKLIST

For each generated asset:
- [ ] Matches technical specifications (resolution, format)
- [ ] Follows prompt accurately
- [ ] Maintains character consistency (for Sisi Lola)
- [ ] Saved to correct folder with correct filename
- [ ] Status updated in manifest
- [ ] Backup copy saved to cloud storage

## NEXT STEPS

1. Generate Phase 1 assets (35 items)
2. Review for quality and consistency
3. Create style guide from best generations
4. Proceed with Phase 2 & 3
5. Begin content integration into VR platform

## SUPPORT DOCS

See `00_PROJECT_CORE/Documentation/` for:
- Brand guidelines
- Technical specifications
- Prompt engineering best practices
- VR integration workflow

---

**Status**: Ready for generation
**Target**: 200+ assets
**Est. Completion**: Ongoing
