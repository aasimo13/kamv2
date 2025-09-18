#!/usr/bin/env python3
"""
Create DMG installer for USB Camera Test Suite v4.0 PyQt6
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

def create_dmg():
    """Create DMG installer"""

    print("🚀 Creating USB Camera Test Suite v4.0 DMG Installer...")

    # Paths
    project_dir = Path(__file__).parent
    installer_script = project_dir / "USB_Camera_Tester_Simple_Installer.py"

    # Create temporary directory for DMG contents
    with tempfile.TemporaryDirectory() as temp_dir:
        dmg_contents = Path(temp_dir) / "USB_Camera_Tester_v4_PyQt6"
        dmg_contents.mkdir()

        print(f"📁 Preparing DMG contents in {dmg_contents}")

        # Copy installer script
        installer_dest = dmg_contents / "USB Camera Tester Installer.py"
        shutil.copy2(installer_script, installer_dest)
        os.chmod(installer_dest, 0o755)
        print("✓ Copied installer script")

        # Create README
        readme_content = """USB Camera Hardware Test Suite v4.0 - PyQt6 Professional Version

🚀 NEW: Professional native PyQt6 GUI interface!

INSTALLATION:
1. Double-click "USB Camera Tester Installer.py"
2. Click "Install" when prompted
3. The installer will automatically:
   • Download the latest PyQt6 version
   • Install Python dependencies (including PyQt6)
   • Create a professional macOS application
   • Install to your Applications folder

FEATURES:
• Professional native GUI with PyQt6
• Non-blocking threaded camera operations
• Resizable panels and modern styling
• Comprehensive camera testing suite
• Export test results to JSON
• Native macOS dialogs and integration

REQUIREMENTS:
• macOS 10.14 or later
• Python 3.8+ (installer will install if needed)
• Camera permissions in System Preferences

SUPPORT:
If you encounter issues, check:
1. System Preferences > Security & Privacy > Camera
2. Camera is not in use by another application
3. USB connection is secure

For technical support, run the installer from Terminal for detailed logs.

Version 4.0 - September 2025
Professional Camera Testing Suite
"""

        readme_path = dmg_contents / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print("✓ Created README")

        # Create alias to Applications folder
        print("📁 Creating Applications alias...")
        try:
            # Create symlink to Applications
            applications_link = dmg_contents / "Applications"
            applications_link.symlink_to("/Applications")
            print("✓ Created Applications symlink")
        except Exception as e:
            print(f"⚠️  Could not create Applications link: {e}")

        # Create DMG
        dmg_name = "USB_Camera_Tester_v4.0_PyQt6.dmg"
        dmg_path = project_dir / dmg_name

        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()

        print(f"🔨 Creating DMG: {dmg_name}")

        # Use hdiutil to create DMG
        cmd = [
            "hdiutil", "create",
            "-srcfolder", str(dmg_contents),
            "-volname", "USB Camera Tester v4.0",
            "-fs", "HFS+",
            "-format", "UDZO",
            str(dmg_path)
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ DMG created successfully")

            # Get DMG size
            size_mb = dmg_path.stat().st_size / (1024 * 1024)
            print(f"📦 DMG size: {size_mb:.1f} MB")

            print(f"\n🎉 SUCCESS!")
            print(f"📦 DMG created: {dmg_path}")
            print(f"🚀 Ready for distribution!")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create DMG: {e}")
            print(f"Error output: {e.stderr}")
            return False

if __name__ == "__main__":
    success = create_dmg()
    sys.exit(0 if success else 1)