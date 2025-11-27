#!/usr/bin/env python3
"""
Sample Profile Image Generator for Sisi Lola
Creates placeholder profile images and banners for all platforms

Uses PIL/Pillow to generate branded template images
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys


def create_gradient_background(width, height, color1=(138, 43, 226), color2=(75, 0, 130)):
    """Create a purple gradient background"""
    image = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(image)
    
    # Create vertical gradient
    for i in range(height):
        ratio = i / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    return image


def add_text_to_image(image, text, position, font_size=60, color=(255, 255, 255)):
    """Add text to image"""
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text if position is 'center'
    if position == 'center':
        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2
        position = (x, y)
    
    draw.text(position, text, fill=color, font=font)
    return image


def create_profile_picture(size, output_path):
    """Create a profile picture"""
    # Create gradient background
    img = create_gradient_background(size, size)
    
    # Add circular overlay
    draw = ImageDraw.Draw(img)
    center = size // 2
    radius = size // 3
    
    # Draw circle
    draw.ellipse(
        [(center - radius, center - radius), (center + radius, center + radius)],
        fill=(255, 215, 0, 128),  # Gold
        outline=(255, 255, 255),
        width=8
    )
    
    # Add text
    img = add_text_to_image(img, "SL", 'center', font_size=size // 3)
    
    # Save
    img.save(output_path, quality=95)
    print(f"✓ Created: {output_path}")


def create_banner(width, height, output_path, platform_name):
    """Create a banner image"""
    # Create gradient background
    img = create_gradient_background(width, height)
    
    # Add text
    img = add_text_to_image(img, "SISI LOLA", (50, height // 3), font_size=min(width // 10, 120))
    img = add_text_to_image(img, "AI Voice of Africa", (50, height // 2), font_size=min(width // 20, 60))
    img = add_text_to_image(img, f"@sisilola", (50, height * 2 // 3), font_size=min(width // 25, 40))
    
    # Save
    img.save(output_path, quality=95)
    print(f"✓ Created: {output_path}")


def main():
    """Generate all profile images and banners"""
    workspace_root = Path(__file__).parent.parent.parent
    
    # Create output directories
    profile_dir = workspace_root / "05_BRANDING_ARTIFACTS/profile_pictures"
    banner_dir = workspace_root / "05_BRANDING_ARTIFACTS/banners"
    
    profile_dir.mkdir(parents=True, exist_ok=True)
    banner_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🎨 SISI LOLA SAMPLE IMAGE GENERATOR")
    print("=" * 60)
    print()
    
    # Profile pictures
    print("Creating profile pictures...")
    profile_specs = [
        ("master_800x800.png", 800),
        ("youtube_800x800.png", 800),
        ("instagram_320x320.png", 320),
        ("tiktok_200x200.png", 200),
        ("facebook_180x180.png", 180),
        ("twitch_256x256.png", 256),
        ("reddit_256x256.png", 256),
        ("vumistream_400x400.png", 400),
        ("twiva_400x400.png", 400),
        ("wowzi_400x400.png", 400),
    ]
    
    for filename, size in profile_specs:
        output_path = profile_dir / filename
        create_profile_picture(size, output_path)
    
    print()
    
    # Banners
    print("Creating banner images...")
    banner_specs = [
        ("youtube_2560x1440.png", 2560, 1440, "YouTube"),
        ("facebook_820x312.png", 820, 312, "Facebook"),
        ("twitch_1200x480.png", 1200, 480, "Twitch"),
        ("reddit_1920x384.png", 1920, 384, "Reddit"),
        ("vumistream_1920x1080.png", 1920, 1080, "Vumistream"),
        ("twiva_1920x1080.png", 1920, 1080, "Twiva"),
    ]
    
    for filename, width, height, platform in banner_specs:
        output_path = banner_dir / filename
        create_banner(width, height, output_path, platform)
    
    print()
    print("=" * 60)
    print("✅ ALL IMAGES GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nProfile Pictures: {profile_dir}")
    print(f"Banners: {banner_dir}")
    print("\n⚠️  IMPORTANT: These are placeholder templates!")
    print("Replace with professional branded designs before launch.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ ERROR: Pillow (PIL) is not installed")
        print("\nTo install:")
        print("  1. Create virtual environment: python3 -m venv venv")
        print("  2. Activate: source venv/bin/activate")
        print("  3. Install: pip install Pillow")
        print("  4. Run this script again")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
