#!/usr/bin/env python3
"""
Build a proper macOS App Bundle installer for USB Camera Test Suite
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_installer_app():
    """Create a proper .app bundle installer"""

    print("🚀 Creating USB Camera Tester Installer App Bundle...")

    project_dir = Path(__file__).parent
    installer_script = project_dir / "USB_Camera_Tester_Simple_Installer.py"

    # Create app bundle structure
    app_name = "USB Camera Tester Installer"
    app_bundle = project_dir / f"{app_name}.app"

    # Remove existing bundle
    if app_bundle.exists():
        shutil.rmtree(app_bundle)

    # Create bundle directories
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    macos_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)

    print(f"📁 Created app bundle structure: {app_bundle}")

    # Create the executable launcher script
    launcher_script = f'''#!/bin/bash
cd "$(dirname "$0")/../Resources"

# Find Python 3 - try common locations
PYTHON_CMD=""
for python_path in python3 /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3; do
    if command -v "$python_path" >/dev/null 2>&1; then
        if "$python_path" --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="$python_path"
            echo "Using Python: $PYTHON_CMD"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    osascript -e 'display dialog "Python 3 is required but not found.\\n\\nPlease install Python from python.org first, then run this installer again." buttons {{"Install Python", "Cancel"}} default button "Install Python"'
    if [ $? -eq 0 ]; then
        open "https://python.org/downloads/"
    fi
    exit 1
fi

# Run the installer
exec "$PYTHON_CMD" "USB_Camera_Tester_Simple_Installer.py" "$@"
'''

    # Write the launcher script
    launcher_path = macos_dir / app_name
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)

    # Make it executable
    os.chmod(launcher_path, 0o755)
    print("✓ Created executable launcher script")

    # Copy the installer Python script to Resources
    shutil.copy2(installer_script, resources_dir / "USB_Camera_Tester_Simple_Installer.py")
    print("✓ Copied installer script to Resources")

    # Create Info.plist
    info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.usb-camera-tester.installer</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>4.0</string>
    <key>CFBundleShortVersionString</key>
    <string>4.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
</dict>
</plist>'''

    plist_path = contents_dir / "Info.plist"
    with open(plist_path, 'w') as f:
        f.write(info_plist)
    print("✓ Created Info.plist")

    # Copy icon if available
    icon_source = project_dir / "camera_test_suite" / "icons" / "app_icon.icns"
    if icon_source.exists():
        icon_dest = resources_dir / "app_icon.icns"
        shutil.copy2(icon_source, icon_dest)
        print("✓ Added app icon")

        # Update Info.plist to reference icon
        with open(plist_path, 'r') as f:
            plist_content = f.read()

        plist_content = plist_content.replace(
            '<key>LSApplicationCategoryType</key>',
            '<key>CFBundleIconFile</key>\n    <string>app_icon</string>\n    <key>LSApplicationCategoryType</key>'
        )

        with open(plist_path, 'w') as f:
            f.write(plist_content)

    print(f"🎉 Created installer app bundle: {app_bundle}")
    print(f"📦 Size: {get_directory_size(app_bundle):.1f} KB")

    return app_bundle

def get_directory_size(path):
    """Calculate directory size in KB"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total += os.path.getsize(file_path)
    return total / 1024

def create_installer_dmg():
    """Create DMG with the app bundle installer"""

    print("📦 Creating installer DMG...")

    project_dir = Path(__file__).parent

    # Create the app bundle first
    app_bundle = create_installer_app()

    # Create DMG contents directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        dmg_contents = Path(temp_dir) / "USB_Camera_Tester_v4_Installer"
        dmg_contents.mkdir()

        # Copy app bundle to DMG contents
        shutil.copytree(app_bundle, dmg_contents / app_bundle.name)

        # Create README
        readme_content = """USB Camera Hardware Test Suite v4.0 - Professional PyQt6 Edition

🚀 INSTALLATION INSTRUCTIONS:

1. Double-click "USB Camera Tester Installer.app"
2. The installer will:
   • Check for Python 3 (install from python.org if needed)
   • Download the latest PyQt6 version from GitHub
   • Install all dependencies automatically
   • Create a professional macOS application

3. Launch from Applications folder when complete

FEATURES:
• Professional PyQt6 native GUI interface
• Comprehensive camera testing suite
• Non-blocking threaded operations
• Export test results to JSON
• Native macOS integration

REQUIREMENTS:
• macOS 10.14 or later
• Python 3.8+ (installer will guide you if needed)

TROUBLESHOOTING:
• If "Python 3 required" appears, install from python.org first
• Grant camera permissions in System Preferences when prompted
• Ensure camera is not in use by other applications

Version 4.0 - September 2025
Professional Camera Testing Suite"""

        readme_path = dmg_contents / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(readme_content)

        # Create Applications alias
        try:
            applications_link = dmg_contents / "Applications"
            applications_link.symlink_to("/Applications")
        except Exception as e:
            print(f"⚠️  Could not create Applications link: {e}")

        # Create DMG
        dmg_name = "USB_Camera_Tester_v4.0_PyQt6_Installer.dmg"
        dmg_path = project_dir / dmg_name

        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()

        # Create DMG using hdiutil
        cmd = [
            "hdiutil", "create",
            "-srcfolder", str(dmg_contents),
            "-volname", "USB Camera Tester v4.0 Installer",
            "-fs", "HFS+",
            "-format", "UDZO",
            str(dmg_path)
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Get DMG size
            size_mb = dmg_path.stat().st_size / (1024 * 1024)

            print(f"✅ SUCCESS!")
            print(f"📦 DMG created: {dmg_path}")
            print(f"💾 Size: {size_mb:.1f} MB")
            print(f"🚀 Ready for distribution!")

            return dmg_path

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create DMG: {e}")
            print(f"Error output: {e.stderr}")
            return None

if __name__ == "__main__":
    dmg_path = create_installer_dmg()
    if dmg_path:
        print(f"\n🎯 DISTRIBUTION READY:")
        print(f"Send this file to colleagues: {dmg_path.name}")
        print(f"They can double-click the .app to install!")
    else:
        sys.exit(1)