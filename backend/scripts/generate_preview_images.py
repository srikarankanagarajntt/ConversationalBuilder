"""
Script to generate preview images from template files.

To use this script:
1. Place your preview image files in the template directory
2. Name them following the pattern: {template-id}-preview.png
3. Run this script to validate they're correctly formatted

Expected files:
  - backend/template/ntt-data-preview.png (for NTT DATA template)
  - backend/template/java-architect-preview.png (for Java Architect template)

Note: Preview images should be PNG format with recommended dimensions:
  - Width: 280-400px
  - Height: 350-450px
  - Size: < 500KB for optimal loading
"""
import os
import base64
from pathlib import Path

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "template")

def validate_preview_image(image_path: str) -> bool:
    """Validate a preview image file."""
    if not os.path.exists(image_path):
        return False
    
    file_size = os.path.getsize(image_path)
    if file_size > 1024 * 1024:  # 1MB limit
        print(f"Warning: {image_path} is {file_size / 1024}KB (recommended < 500KB)")
    
    return True

def list_preview_images():
    """List all available preview images."""
    print("Looking for preview images in:", TEMPLATE_DIR)
    print()
    
    patterns = [
        ("ntt-data-preview.png", "NTT DATA Resume Template"),
        ("java-architect-preview.png", "Java Lead Architect Template"),
    ]
    
    for filename, template_name in patterns:
        filepath = os.path.join(TEMPLATE_DIR, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ Found: {filename}")
            print(f"  Size: {size / 1024:.1f}KB")
            print(f"  Template: {template_name}")
        else:
            print(f"✗ Missing: {filename}")
            print(f"  Expected for: {template_name}")
        print()

def encode_preview_image(image_path: str) -> str:
    """Encode a preview image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if __name__ == "__main__":
    print("=" * 60)
    print("Template Preview Image Validator")
    print("=" * 60)
    print()
    
    list_preview_images()
    
    print()
    print("=" * 60)
    print("To add preview images:")
    print("=" * 60)
    print()
    print("1. Export your template as an image (PNG format)")
    print("   For DOCX: Open in Word → Save as PDF → Convert to PNG")
    print("   For PPTX: Open in PowerPoint → Export first slide as PNG")
    print()
    print("2. Place the images in: backend/template/")
    print("   - ntt-data-preview.png")
    print("   - java-architect-preview.png")
    print()
    print("3. Restart the backend server")
    print()
    print("The preview images will be automatically loaded and displayed")
    print("in the template selection modal.")
