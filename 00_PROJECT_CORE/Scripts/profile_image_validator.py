"""
Profile Image Specification and Validator
Ensures all profile images and banners meet platform requirements
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import io


@dataclass
class ImageSpec:
    """Image specification for a platform"""
    platform: str
    image_type: str  # "profile" or "banner"
    width: int
    height: int
    max_file_size_mb: float
    format: str  # "PNG", "JPEG", or "both"
    circular_crop: bool = False
    safe_area: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    notes: str = ""


class ProfileImageValidator:
    """Validate and prepare images for social media platforms"""
    
    SPECS = [
        # Profile Pictures
        ImageSpec("YouTube", "profile", 800, 800, 10, "both", True, 
                 notes="Displays as circle, min 98x98"),
        ImageSpec("Instagram", "profile", 320, 320, 10, "both", True,
                 notes="Displays at 110x110, circular crop"),
        ImageSpec("TikTok", "profile", 200, 200, 10, "both", True,
                 notes="Minimum 20x20"),
        ImageSpec("Facebook", "profile", 320, 320, 10, "both", True,
                 notes="Minimum 180x180, circular display"),
        ImageSpec("Twitch", "profile", 256, 256, 10, "both", True,
                 notes="Circular display"),
        ImageSpec("Reddit", "profile", 256, 256, 10, "both", True,
                 notes="Circular display"),
        ImageSpec("Vumistream", "profile", 320, 320, 10, "both", False,
                 notes="African platform"),
        ImageSpec("Twiva", "profile", 320, 320, 10, "both", False,
                 notes="African platform"),
        ImageSpec("Wowzi", "profile", 320, 320, 10, "both", False,
                 notes="African platform"),
        
        # Banners
        ImageSpec("YouTube", "banner", 2560, 1440, 6, "both", False,
                 safe_area=(507, 423, 1546, 423),
                 notes="Safe area: 1546x423 centered"),
        ImageSpec("Facebook", "banner", 820, 312, 10, "both", False,
                 notes="Cover photo"),
        ImageSpec("Twitch", "banner", 1200, 480, 10, "both", False,
                 notes="Channel banner"),
        ImageSpec("Twitter", "banner", 1500, 500, 10, "both", False,
                 notes="Header image"),
        ImageSpec("Universal_African", "banner", 1920, 1080, 10, "both", False,
                 notes="For Vumistream, Twiva, Wowzi"),
    ]
    
    def __init__(self):
        self.specs_dict = {
            f"{spec.platform}_{spec.image_type}": spec 
            for spec in self.SPECS
        }
    
    def validate_image(self, image_path: Path, platform: str, 
                      image_type: str) -> Tuple[bool, List[str]]:
        """
        Validate an image against platform requirements
        Returns (is_valid, list_of_issues)
        """
        spec_key = f"{platform}_{image_type}"
        
        if spec_key not in self.specs_dict:
            return False, [f"No specification found for {platform} {image_type}"]
        
        spec = self.specs_dict[spec_key]
        issues = []
        
        try:
            img = Image.open(image_path)
        except Exception as e:
            return False, [f"Cannot open image: {str(e)}"]
        
        # Check dimensions
        if img.width != spec.width or img.height != spec.height:
            issues.append(
                f"Incorrect dimensions: {img.width}x{img.height}, "
                f"expected {spec.width}x{spec.height}"
            )
        
        # Check file size
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > spec.max_file_size_mb:
            issues.append(
                f"File too large: {file_size_mb:.2f}MB, "
                f"max {spec.max_file_size_mb}MB"
            )
        
        # Check format
        img_format = img.format
        if spec.format != "both":
            if img_format not in spec.format.split(","):
                issues.append(
                    f"Wrong format: {img_format}, expected {spec.format}"
                )
        
        return len(issues) == 0, issues
    
    def resize_image(self, image_path: Path, platform: str, 
                    image_type: str, output_path: Path = None) -> Path:
        """
        Resize image to meet platform requirements
        """
        spec_key = f"{platform}_{image_type}"
        
        if spec_key not in self.specs_dict:
            raise ValueError(f"No specification found for {platform} {image_type}")
        
        spec = self.specs_dict[spec_key]
        
        img = Image.open(image_path)
        
        # Resize to exact dimensions
        resized = img.resize((spec.width, spec.height), Image.Resampling.LANCZOS)
        
        # Determine output path
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_{platform}_{image_type}{image_path.suffix}"
        
        # Save with optimization
        if spec.format == "PNG" or image_path.suffix.lower() == ".png":
            resized.save(output_path, "PNG", optimize=True)
        else:
            resized.save(output_path, "JPEG", quality=95, optimize=True)
        
        return output_path
    
    def create_circular_preview(self, image_path: Path, 
                               output_path: Path = None) -> Path:
        """
        Create a circular preview of the image (shows how it will look on platforms)
        """
        img = Image.open(image_path).convert("RGBA")
        
        # Create circular mask
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.width, img.height), fill=255)
        
        # Apply mask
        img.putalpha(mask)
        
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_circular_preview.png"
        
        img.save(output_path, "PNG")
        return output_path
    
    def batch_resize_for_all_platforms(self, source_image: Path, 
                                       output_dir: Path,
                                       image_type: str = "profile") -> Dict[str, Path]:
        """
        Create resized versions for all platforms from a master image
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for spec_key, spec in self.specs_dict.items():
            if spec.image_type != image_type:
                continue
            
            output_path = output_dir / f"sisilola_{spec.platform.lower()}_{image_type}.png"
            
            try:
                resized_path = self.resize_image(
                    source_image, 
                    spec.platform, 
                    image_type, 
                    output_path
                )
                results[spec.platform] = resized_path
                
                # Create circular preview for circular platforms
                if spec.circular_crop:
                    preview_path = output_dir / f"sisilola_{spec.platform.lower()}_{image_type}_preview.png"
                    self.create_circular_preview(resized_path, preview_path)
                    
            except Exception as e:
                print(f"Error processing {spec.platform}: {str(e)}")
        
        return results
    
    def generate_specification_document(self, output_path: Path):
        """Generate a markdown document with all specifications"""
        lines = []
        lines.append("# Social Media Image Specifications for Sisi Lola\n")
        lines.append(f"Generated: {Path(__file__).name}\n")
        lines.append("---\n")
        
        # Profile pictures
        lines.append("## Profile Pictures\n")
        for spec in self.SPECS:
            if spec.image_type == "profile":
                lines.append(f"### {spec.platform}")
                lines.append(f"- **Dimensions:** {spec.width} x {spec.height} pixels")
                lines.append(f"- **Max File Size:** {spec.max_file_size_mb}MB")
                lines.append(f"- **Format:** {spec.format}")
                lines.append(f"- **Circular Crop:** {'Yes' if spec.circular_crop else 'No'}")
                if spec.notes:
                    lines.append(f"- **Notes:** {spec.notes}")
                lines.append("")
        
        # Banners
        lines.append("\n## Banners / Cover Images\n")
        for spec in self.SPECS:
            if spec.image_type == "banner":
                lines.append(f"### {spec.platform}")
                lines.append(f"- **Dimensions:** {spec.width} x {spec.height} pixels")
                lines.append(f"- **Max File Size:** {spec.max_file_size_mb}MB")
                lines.append(f"- **Format:** {spec.format}")
                if spec.safe_area:
                    lines.append(f"- **Safe Area:** {spec.safe_area[2]} x {spec.safe_area[3]} pixels")
                if spec.notes:
                    lines.append(f"- **Notes:** {spec.notes}")
                lines.append("")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
    
    def create_template_with_guides(self, width: int, height: int, 
                                   output_path: Path,
                                   circular: bool = False,
                                   safe_area: Tuple[int, int, int, int] = None):
        """
        Create a template image with guidelines
        """
        # Create image with light gray background
        img = Image.new("RGBA", (width, height), (240, 240, 240, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([(0, 0), (width-1, height-1)], outline=(100, 100, 100), width=2)
        
        # Draw center lines
        draw.line([(width//2, 0), (width//2, height)], fill=(200, 200, 200), width=1)
        draw.line([(0, height//2), (width, height//2)], fill=(200, 200, 200), width=1)
        
        # Draw circular guide if needed
        if circular:
            draw.ellipse([(0, 0), (width, height)], outline=(255, 100, 100), width=3)
            # Draw safe circle (80% of size)
            margin = int(width * 0.1)
            draw.ellipse(
                [(margin, margin), (width-margin, height-margin)], 
                outline=(100, 255, 100), 
                width=2
            )
        
        # Draw safe area if specified
        if safe_area:
            x, y, w, h = safe_area
            draw.rectangle(
                [(x, y), (x + w, y + h)], 
                outline=(100, 100, 255), 
                width=3
            )
        
        # Add dimension text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = f"{width} x {height}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            ((width - text_width) // 2, (height - text_height) // 2),
            text,
            fill=(100, 100, 100),
            font=font
        )
        
        img.save(output_path, "PNG")
        return output_path


def main():
    """Generate templates and documentation"""
    validator = ProfileImageValidator()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "05_BRANDING_ARTIFACTS" / "image_templates"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating image specification document...")
    spec_doc_path = output_dir / "IMAGE_SPECIFICATIONS.md"
    validator.generate_specification_document(spec_doc_path)
    print(f"Created: {spec_doc_path}")
    
    print("\nGenerating template images...")
    
    # Generate key templates
    templates = [
        ("profile_800x800_master", 800, 800, True, None),
        ("profile_320x320", 320, 320, True, None),
        ("banner_youtube", 2560, 1440, False, (507, 508, 1546, 423)),
        ("banner_facebook", 820, 312, False, None),
        ("banner_universal", 1920, 1080, False, None),
    ]
    
    for name, width, height, circular, safe_area in templates:
        output_path = output_dir / f"template_{name}.png"
        validator.create_template_with_guides(width, height, output_path, circular, safe_area)
        print(f"Created: {output_path}")
    
    print("\n✓ Image templates and specifications generated successfully!")
    print(f"Location: {output_dir}")


if __name__ == "__main__":
    main()
