#!/usr/bin/env python3
"""
Create a professional logo for USB Camera Tester app
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_logo():
    """Create a professional logo for the USB Camera Tester app"""

    # Create a 512x512 icon (macOS app icon size)
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background gradient effect - dark blue to light blue
    for y in range(size):
        alpha = int(255 * (1 - y / size * 0.3))
        color = (30 + int(50 * y / size), 60 + int(100 * y / size), 120 + int(120 * y / size), alpha)
        draw.rectangle([(0, y), (size, y+1)], fill=color)

    # Add rounded corners
    corner_radius = 80
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], corner_radius, fill=255)

    # Apply mask for rounded corners
    img.putalpha(mask)

    # Draw camera icon elements
    # Main camera body
    camera_size = size // 3
    camera_x = (size - camera_size) // 2
    camera_y = (size - camera_size) // 2 - 30

    # Camera body (rounded rectangle)
    draw.rounded_rectangle(
        [(camera_x, camera_y), (camera_x + camera_size, camera_y + camera_size - 40)],
        20, fill=(240, 240, 240, 255), outline=(200, 200, 200, 255), width=3
    )

    # Camera lens (circle)
    lens_size = camera_size // 2
    lens_x = camera_x + (camera_size - lens_size) // 2
    lens_y = camera_y + (camera_size - lens_size) // 2 - 20

    # Outer lens ring
    draw.ellipse(
        [(lens_x - 10, lens_y - 10), (lens_x + lens_size + 10, lens_y + lens_size + 10)],
        fill=(60, 60, 60, 255)
    )

    # Inner lens
    draw.ellipse(
        [(lens_x, lens_y), (lens_x + lens_size, lens_y + lens_size)],
        fill=(20, 20, 20, 255)
    )

    # Lens reflection
    reflection_size = lens_size // 3
    draw.ellipse(
        [(lens_x + 15, lens_y + 15), (lens_x + 15 + reflection_size, lens_y + 15 + reflection_size)],
        fill=(100, 150, 200, 180)
    )

    # USB connector
    usb_width = 60
    usb_height = 20
    usb_x = camera_x + camera_size - usb_width - 10
    usb_y = camera_y + camera_size - 30

    draw.rounded_rectangle(
        [(usb_x, usb_y), (usb_x + usb_width, usb_y + usb_height)],
        5, fill=(80, 80, 80, 255)
    )

    # USB symbol
    draw.rectangle([(usb_x + 45, usb_y + 6), (usb_x + 50, usb_y + 14)], fill=(255, 255, 255, 255))

    # Test indicators (small colored dots)
    dot_size = 15
    colors = [(0, 255, 0, 255), (255, 165, 0, 255), (255, 0, 0, 255)]  # Green, Orange, Red
    for i, color in enumerate(colors):
        dot_x = camera_x - 40 + i * 25
        dot_y = camera_y + 20
        draw.ellipse([(dot_x, dot_y), (dot_x + dot_size, dot_y + dot_size)], fill=color)

    # Add text "USB CAM TEST" at bottom
    try:
        # Try to use a system font
        font_size = 32
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    text = "USB CAM TEST"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) // 2
    text_y = camera_y + camera_size + 20

    # Text shadow
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 100), font=font)
    # Main text
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    return img

def create_icon_sizes():
    """Create different icon sizes for macOS app bundle"""
    base_logo = create_app_logo()

    # Standard macOS icon sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    icons_dir = "/Users/aaronsimo/Kam/Kam/camera_test_suite/icons"
    os.makedirs(icons_dir, exist_ok=True)

    for size in sizes:
        resized = base_logo.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f"{icons_dir}/icon_{size}x{size}.png")
        print(f"Created icon_{size}x{size}.png")

    # Save the main icon
    base_logo.save(f"{icons_dir}/app_icon.png")
    print("Created app_icon.png")

    # Create .icns file for macOS (using the 512x512 as base)
    base_logo.save(f"{icons_dir}/app_icon.icns")
    print("Created app_icon.icns")

if __name__ == "__main__":
    print("Creating USB Camera Tester app logo...")
    create_icon_sizes()
    print("Logo creation complete!")