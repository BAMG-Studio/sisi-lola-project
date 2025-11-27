# VR ENVIRONMENT TECHNICAL SPECIFICATIONS
## Sisi Lola Project // Virtual Production Standards

**Version:** 1.0  
**Platform Target:** Unity, Unreal Engine 5, WebXR  
**Classification:** Technical Production Guide

---

## 1. OVERVIEW

Virtual environments for the Sisi Lola project must support:
- 360° VR immersion
- Real-time rendering at 90fps minimum
- Photorealistic quality with optimized performance
- Spatial audio integration
- Multi-platform deployment (Quest, PSVR2, PC VR, WebXR)

---

## 2. ENVIRONMENT CATEGORIES

### 2.1 PRIMARY STUDIO: "The Lounge of Lagos"

**Purpose:** Main podcast/content recording space  
**Mood:** Sophisticated, warm, futuristic yet welcoming  
**Lighting:** Ambient with dramatic accents

#### Technical Specs:
- **Dimensions:** 15m × 12m × 4m (height)
- **Polygon Budget:** 2-5 million triangles
- **Texture Resolution:** 4K for primary surfaces, 2K for secondary
- **Lighting:** Baked GI + real-time dynamic for character
- **HDR Range:** Yes, for realistic glass reflections

#### Key Elements:
1. **Windows (Floor-to-Ceiling):**
   - Curved glass panels (120° arc)
   - View: Futuristic Lagos skyline
   - Night mode (neon/holographic ads)
   - Day mode (sunlight with atmospheric scattering)
   - Parallax cityscape layers (4 depth planes)

2. **Furniture:**
   - Modern white sectional sofa (Scandinavian style)
   - Floating holographic desk/table
   - Accent chairs (ergonomic future design)
   - Coffee table with integrated holographic display

3. **Technology:**
   - 3-5 floating holographic screens (AR overlays)
   - Ambient particle systems (subtle data streams)
   - Interactive control panels
   - RGB accent lighting (programmable)

4. **Nature Elements:**
   - 4-6 bioluminescent plant arrangements
   - Species: African varieties (enhanced)
   - Subtle glow animation
   - Volumetric fog near plants

5. **Audio:**
   - Spatial reverb: Medium room (RT60: 0.4s)
   - Ambient loop: Subtle tech hum + distant city
   - Dynamic wind when near windows

#### Lighting Setup:
```
- Key Light: Soft daylight from windows (color temp: 5500K)
- Fill Light: Warm ambient (color temp: 3200K)
- Accent Lights: RGB programmable (purple/blue default)
- HDRI: Custom Lagos skyline (8K resolution)
- Volumetric Fog: Subtle, density 0.02
```

#### 360° Camera Positions:
1. **Hero Position:** Center of room, 1.6m height (eye level)
2. **Desk View:** Behind Sisi Lola's shoulder
3. **Window Vista:** Near glass, showcasing cityscape
4. **Intimate:** Low angle near seating area
5. **Overhead:** Bird's eye architectural view

---

### 2.2 SECONDARY SPACE: "The Void"

**Purpose:** Tech reviews, product showcases  
**Mood:** Mysterious, high-contrast, minimal distraction  
**Lighting:** Dramatic, cinematic

#### Technical Specs:
- **Dimensions:** Infinite black void (skybox)
- **Polygon Budget:** <500K (minimal geometry)
- **Texture Resolution:** 1K (black materials don't need detail)
- **Lighting:** Single dynamic spotlight system
- **Performance:** Highly optimized for post-processing effects

#### Key Elements:
1. **Background:** Solid black (#000000) or subtle grid
2. **Pedestal:** Floating holographic platform (programmable)
3. **Spotlight:** Dramatic top-down with falloff
4. **Grid Floor:** Subtle, optional, 1m squares
5. **Particle Effects:** Minimal floating dust motes

#### Lighting Setup:
```
- Key Light: Hard spotlight from 45° above (6000K)
- Rim Light: Subtle blue edge light (7000K)
- Ambient: Pitch black (0.0 contribution)
- Fog: None or extremely subtle
```

#### Use Cases:
- Product photography style reviews
- Dramatic announcements
- Minimalist interview setups
- Holographic data visualization

---

### 2.3 VARIABLE LOCATIONS (15+ Environments)

#### A. Cyber Lagos Street
**Description:** Bustling afrofuturist marketplace at night  
**Key Features:** Neon signs (Yoruba text), holographic vendors, flying vehicles  
**Polygon Budget:** 3-8M triangles  
**Lighting:** Neon color variety, dynamic shadows

#### B. Virtual Beach (Sunset)
**Description:** Serene tropical beach with enhanced colors  
**Key Features:** Volumetric sunset, calm water, palm trees  
**Polygon Budget:** 2-4M triangles  
**Lighting:** Golden hour (color temp: 3500K)

#### C. Executive Office
**Description:** High-rise corner office, floor-to-ceiling windows  
**Key Features:** Minimalist luxury, cityscape view, modern furniture  
**Polygon Budget:** 2-5M triangles  
**Lighting:** Natural daylight + accent task lighting

#### D. Rooftop Garden
**Description:** Lush rooftop oasis above city skyline  
**Key Features:** Exotic plants, water features, seating areas  
**Polygon Budget:** 4-7M triangles  
**Lighting:** Daytime natural + evening ambient

---

## 3. 360° VR TECHNICAL STANDARDS

### 3.1 Equirectangular Specifications

**Resolution Options:**
- **High Quality:** 8192 × 4096 (8K)
- **Standard:** 6144 × 3072 (6K)
- **Mobile VR:** 4096 × 2048 (4K)

**Format:** PNG or JPEG (for static) / MP4 H.265 (for video)

**Stitching:** Seamless left-right wrap, avoid visible seams at 0°/360°

### 3.2 Stereoscopic 3D VR

**For Immersive Depth:**
- Over-Under format (Top: Left Eye, Bottom: Right Eye)
- Resolution: 8192 × 8192 (4K per eye)
- Interpupillary Distance (IPD): 64mm standard
- Convergence: Set to 2-3 meters for comfortable viewing

### 3.3 Camera Settings (Unreal/Unity)

```
Field of View: 360° horizontal, 180° vertical
Sensor Size: Full frame equivalent
Near Clip Plane: 0.1m
Far Clip Plane: 1000m
Exposure: Auto with manual override capability
Anti-Aliasing: TAA (Temporal AA) for VR
```

---

## 4. SPATIAL AUDIO SPECIFICATIONS

### 4.1 Binaural Audio Requirements

**Format:** Ambisonics (1st order minimum, 3rd order ideal)  
**Sample Rate:** 48kHz  
**Bit Depth:** 24-bit  
**Channels:** 4 (1st order) or 16 (3rd order)

### 4.2 Sound Design by Environment

#### The Lounge of Lagos:
```
- Ambient Loop: Subtle tech hum, distant Lagos traffic
- Spatial Elements: Wind near windows, hologram buzz
- Reverb: Medium room (decay: 0.4s)
- Dynamic Range: -6dB to -20dB
```

#### The Void:
```
- Ambient Loop: Absolute silence or extremely subtle rumble
- Spatial Elements: Product-specific sounds only
- Reverb: Infinite space simulation (decay: 8s+)
- Dynamic Range: -12dB to -40dB (high contrast)
```

#### Cyber Lagos Street:
```
- Ambient Loop: Market chatter, holographic ads, distant music
- Spatial Elements: Footsteps, vendor calls, flying vehicles
- Reverb: Outdoor urban (decay: 1.2s)
- Dynamic Range: -3dB to -18dB (lively)
```

### 4.3 Voice Integration

- **Sisi Lola's Voice:** Always centered, -6dB, minimal reverb
- **Guest Voices:** Positioned spatially if applicable
- **Narration:** Center channel, -6dB
- **Music Beds:** Stereo width, -18dB to -24dB (background)

---

## 5. PERFORMANCE OPTIMIZATION

### 5.1 Target Frame Rates

| Platform | Resolution | Frame Rate | Render Technique |
|----------|------------|------------|------------------|
| Meta Quest 3 | 2064×2208 per eye | 90fps | Forward Rendering |
| PSVR2 | 2000×2040 per eye | 90-120fps | Forward+ |
| PC VR (High-end) | 2880×1600 per eye | 120fps | Deferred Rendering |
| WebXR | 1920×1080 per eye | 72fps | Forward Mobile |

### 5.2 Optimization Techniques

**LOD (Level of Detail):**
- LOD0: 0-3 meters (full detail)
- LOD1: 3-10 meters (75% detail)
- LOD2: 10-30 meters (50% detail)
- LOD3: 30+ meters (25% detail, billboards)

**Occlusion Culling:**
- Enabled for all opaque objects
- Frustum culling: Aggressive
- Distance culling: Beyond 100m in open scenes

**Texture Streaming:**
- Enabled, 2GB budget minimum
- Mipmap generation: Auto
- Compression: BC7 (PC) / ASTC (Mobile)

**Lighting:**
- Baked lightmaps: 2K-4K resolution
- Real-time lights: Maximum 4 per scene
- Shadows: Cascaded for sun, baked for static objects

---

## 6. MATERIAL & SHADER STANDARDS

### 6.1 PBR (Physically Based Rendering)

**All materials must use:**
- Albedo/Base Color map
- Normal map (for detail)
- Roughness map (for reflectivity control)
- Metallic map (for metal surfaces)
- Ambient Occlusion (baked)

**Holographic Materials:**
```
Shader Type: Custom transparent with Fresnel
Parameters:
  - Base Color: RGB gradient (purple to blue)
  - Opacity: 0.3-0.6
  - Fresnel Intensity: 2.5
  - Rim Light: Enabled (width: 0.8)
  - Distortion: Subtle noise animation
  - Emissive: Mild glow (0.5 intensity)
```

**Glass Materials:**
```
Shader Type: Refractive transparent
Parameters:
  - IOR (Index of Refraction): 1.52 (standard glass)
  - Roughness: 0.02 (very smooth)
  - Reflections: Screen-space or cubemap
  - Thickness: 0.01m for windows
```

**Neon Signs:**
```
Shader Type: Emissive unlit
Parameters:
  - Emissive Color: Vibrant (HDR values 5-10)
  - Bloom: Enabled
  - Animation: UV scroll or pulsing
  - Glow Radius: Medium (for post-process)
```

---

## 7. INTERACTION DESIGN (VR)

### 7.1 Teleportation System

**Movement:** Arc-based teleportation with comfort vignette  
**Indicators:** Glowing ground target, invalid areas in red  
**Boundaries:** Keep user within 10m radius of content  

### 7.2 Hand Interactions

**Supported Actions:**
- Point and select (laser pointer from controller)
- Grab and hold (for movable objects)
- Push/press (for buttons and UI)

**Haptic Feedback:**
- Light tap: UI button press
- Medium vibration: Object grab
- Heavy pulse: Teleport confirmation

### 7.3 UI/UX in VR

**Floating UI Panels:**
- Distance: 1.5-2.5m from user
- Height: Eye level ± 0.3m
- Orientation: Always face user (billboard)
- Font Size: Minimum 24pt at 2m distance
- Contrast: High (white text on dark semi-transparent)

---

## 8. ASSET CREATION PIPELINE

### 8.1 Modeling (Blender/Maya)

1. **Base Mesh:** Model at real-world scale (meters)
2. **UV Unwrapping:** Non-overlapping, efficient packing
3. **LOD Generation:** Create 3-4 LOD levels
4. **Pivot Points:** Set to logical center/base
5. **Export:** FBX (Unity) or USD (Unreal)

### 8.2 Texturing (Substance Painter)

1. **Bake Maps:** Normal, AO, Curvature from high-poly
2. **Material Authoring:** PBR workflow
3. **Resolution:** 4K for hero assets, 2K for background
4. **Export:** PNG (diffuse/normal) + packed textures (ORM)

### 8.3 Lighting (Unreal/Unity)

1. **HDR Skybox:** Custom or curated (8K resolution)
2. **Lightmap Baking:** Medium-high quality
3. **Reflection Probes:** Strategic placement
4. **Light Probes:** Grid coverage for dynamic objects

### 8.4 Testing

1. **Performance Test:** Maintain target framerate
2. **VR Comfort Test:** No motion sickness triggers
3. **Audio Test:** Spatial accuracy verification
4. **Visual Test:** No z-fighting, clipping, or artifacts

---

## 9. PLATFORM-SPECIFIC CONSIDERATIONS

### 9.1 Meta Quest (Standalone Mobile VR)

**Constraints:**
- Polygon limit: 100K-300K total per scene
- Texture memory: 512MB budget
- Draw calls: <100 per frame
- Shaders: Simple, avoid complex transparency

**Optimizations:**
- Aggressive LOD
- Baked lighting only
- Single-pass stereo rendering
- Fixed foveated rendering

### 9.2 PC VR (High-End)

**Advantages:**
- Polygon limit: 2M-5M total per scene
- Texture memory: 2GB+ budget
- Draw calls: <500 per frame
- Shaders: Full PBR with real-time GI

**Features:**
- Dynamic lighting
- High-quality shadows
- Screen-space reflections
- Volumetric fog

### 9.3 WebXR (Browser-Based)

**Constraints:**
- Polygon limit: 200K-500K total
- Texture memory: 256MB budget
- Draw calls: <150 per frame
- No compute shaders

**Format:**
- glTF 2.0 / GLB
- Draco compression for geometry
- Basis Universal for textures

---

## 10. QUALITY ASSURANCE CHECKLIST

### Pre-Deployment:
- [ ] Framerate stable at 90fps minimum
- [ ] No visible LOD popping
- [ ] All textures load correctly
- [ ] Audio synchronized spatially
- [ ] Teleportation boundaries working
- [ ] No comfort issues (tested on 5+ users)
- [ ] Lighting baked without artifacts
- [ ] Reflections appear natural
- [ ] UI readable from all positions
- [ ] Fallback assets loaded (if streaming fails)

### Platform-Specific:
- [ ] Quest: APK under 1GB, battery test (>60min)
- [ ] PSVR2: HDR enabled, adaptive triggers functional
- [ ] PC VR: Graphics settings menu functional
- [ ] WebXR: Loads in <30 seconds on broadband

---

## 11. FILE NAMING CONVENTIONS

```
ENV_[LOCATION]_[ELEMENT]_[LOD]_v[VERSION].[EXT]

Examples:
ENV_LoungeOfLagos_MainRoom_LOD0_v03.fbx
ENV_TheVoid_Pedestal_LOD1_v01.fbx
ENV_CyberLagos_Building_LOD2_v02.glb
ENV_Beach_Skybox_8K_v01.hdr
```

---

## 12. DELIVERY FORMATS

### Unity Package:
- `.unitypackage` with all assets, prefabs, scenes
- Include README with setup instructions
- Version: Unity 2022.3 LTS or newer

### Unreal Project:
- Full project folder or `.uproject`
- Include DataTable with asset manifest
- Version: Unreal Engine 5.3 or newer

### WebXR:
- `.glb` files with embedded textures
- Separate `.hdr` for skybox
- Companion `.json` for scene graph

---

## 13. FUTURE ENHANCEMENTS

### Phase 2 (Interactive AI):
- Real-time environment changes based on conversation
- Weather systems (rain, fog, day/night cycles)
- Audience seating (virtual spectators)

### Phase 3 (Metaverse):
- Multi-user spaces (up to 50 concurrent)
- User-generated content integration
- Cross-platform portability (VRChat, Spatial, Meta Horizon)

### Phase 4 (Full Autonomy):
- Procedural environment generation
- AI-driven camera positioning
- Adaptive performance scaling

---

**Document Version:** 1.0  
**Last Updated:** November 22, 2025  
**Maintained By:** Sisi Lola Technical Production Team
