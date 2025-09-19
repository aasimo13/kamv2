#!/bin/bash

# USB Camera Tester - Professional macOS Installer Builder
# Creates a distributable .app bundle for the installer

set -e

echo "🚀 Building USB Camera Tester Installer for macOS..."

# Configuration
INSTALLER_NAME="USB Camera Tester Installer"
BUNDLE_ID="com.usb-camera-tester.installer"
VERSION="2.0"
BUILD_DIR="installer_build"
INSTALLER_SCRIPT="USB_Camera_Tester_Simple_Installer.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Clean up any existing build
if [ -d "$BUILD_DIR" ]; then
    print_status "Cleaning up previous build..."
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"

# Check if installer script exists
if [ ! -f "$INSTALLER_SCRIPT" ]; then
    print_error "Installer script not found: $INSTALLER_SCRIPT"
    exit 1
fi

print_status "Creating application bundle structure..."

# Create app bundle structure
APP_BUNDLE="$BUILD_DIR/$INSTALLER_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy the installer scripts
cp "$INSTALLER_SCRIPT" "$RESOURCES_DIR/"
cp "USB_Camera_Tester_Simple_Installer.py" "$RESOURCES_DIR/"

# Create the launcher script
print_status "Creating launcher script..."

cat > "$MACOS_DIR/$INSTALLER_NAME" << 'EOF'
#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"

# Change to resources directory
cd "$RESOURCES_DIR"

# Launch the simple native installer
if command -v python3 &> /dev/null; then
    python3 USB_Camera_Tester_Simple_Installer.py "$@"
elif command -v python &> /dev/null; then
    python USB_Camera_Tester_Simple_Installer.py "$@"
else
    osascript -e 'display dialog "Python is required but not installed. Please install Python 3.8 or later from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi
EOF

# Make launcher executable
chmod +x "$MACOS_DIR/$INSTALLER_NAME"

# Create Info.plist
print_status "Creating Info.plist..."

cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$INSTALLER_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleName</key>
    <string>$INSTALLER_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$INSTALLER_NAME</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2025 USB Camera Tester. All rights reserved.</string>
    <key>CFBundleDocumentTypes</key>
    <array/>
    <key>NSAppleEventsUsageDescription</key>
    <string>This installer needs to access system events to properly install the USB Camera Tester application.</string>
</dict>
</plist>
EOF

# Copy professional icon
print_status "Adding application icon..."

# Copy the professionally created icon
if [ -f "camera_test_suite/icons/app_icon.icns" ]; then
    cp "camera_test_suite/icons/app_icon.icns" "$RESOURCES_DIR/"
    echo "✓ Professional icon added"
else
    echo "⚠️  Icon not found, creating placeholder..."
    # Fallback - create simple icon
    cd "$RESOURCES_DIR"
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (512, 512), '#007AFF')
draw = ImageDraw.Draw(img)
draw.text((256, 256), '📹', anchor='mm', font_size=200)
img.save('app_icon.icns')
" 2>/dev/null || true
    cd - > /dev/null
fi

print_status "Setting bundle permissions..."

# Set proper permissions
chmod -R 755 "$APP_BUNDLE"
chmod +x "$MACOS_DIR/$INSTALLER_NAME"

# Try to set extended attributes (quarantine removal)
print_status "Setting extended attributes..."
xattr -cr "$APP_BUNDLE" 2>/dev/null || true

# Create a disk image for distribution
print_status "Creating disk image for distribution..."

DMG_NAME="USB_Camera_Tester_Installer_v$VERSION.dmg"
DMG_TEMP="$BUILD_DIR/dmg_temp"

mkdir -p "$DMG_TEMP"
cp -R "$APP_BUNDLE" "$DMG_TEMP/"

# Create README for the DMG
cat > "$DMG_TEMP/README.txt" << 'EOF'
USB Camera Hardware Test Suite - Professional Installer

INSTALLATION INSTRUCTIONS:
1. Double-click "USB Camera Tester Installer.app"
2. Follow the on-screen instructions
3. The installer will automatically:
   - Download the latest version
   - Install all dependencies
   - Create the application bundle
   - Add to your Applications folder

SYSTEM REQUIREMENTS:
- macOS 10.14 or later
- Python 3.8 or later (will be prompted if missing)
- Administrator privileges for installation

WHAT'S INCLUDED:
- Comprehensive PDAF autofocus testing
- White balance and exposure validation
- Image quality analysis with sharpness metrics
- USB interface performance testing
- Automated report generation (PDF, JSON, CSV)
- Cross-platform compatibility

For support or issues, please visit:
https://github.com/aasimo13/Kam

© 2025 USB Camera Tester. All rights reserved.
EOF

# Create the DMG with better presentation
if command -v hdiutil &> /dev/null; then
    # Create a temporary DMG first
    TEMP_DMG="$BUILD_DIR/temp_${DMG_NAME}"

    hdiutil create -format UDRW -volname "USB Camera Tester Installer" -srcfolder "$DMG_TEMP" "$TEMP_DMG"

    # Mount the temporary DMG
    MOUNT_POINT=$(hdiutil attach "$TEMP_DMG" | grep -o '/Volumes/[^"]*')

    # Set DMG window properties to make it more user-friendly
    if [ -n "$MOUNT_POINT" ]; then
        # Create a .DS_Store to set window properties
        osascript << EOF
tell application "Finder"
    set dmg_window to make new Finder window to folder ("$MOUNT_POINT" as POSIX file)
    set current view of dmg_window to icon view
    set toolbar visible of dmg_window to false
    set statusbar visible of dmg_window to false
    set the bounds of dmg_window to {100, 100, 600, 400}
    set icon size of icon view options of dmg_window to 72
    set arrangement of icon view options of dmg_window to not arranged
    set position of item "USB Camera Tester Installer.app" of dmg_window to {150, 200}
    set position of item "README.txt" of dmg_window to {350, 200}
    close dmg_window
end tell
EOF

        # Unmount the temporary DMG
        hdiutil detach "$MOUNT_POINT"
    fi

    # Convert to final compressed DMG
    hdiutil convert "$TEMP_DMG" -format UDZO -o "$BUILD_DIR/$DMG_NAME"
    rm "$TEMP_DMG"

    print_success "Disk image created: $BUILD_DIR/$DMG_NAME"
else
    print_warning "hdiutil not available, skipping DMG creation"
fi

# Clean up temp DMG folder
rm -rf "$DMG_TEMP"

print_success "Installation package built successfully!"

echo ""
echo "📦 Build Complete!"
echo "   App Bundle: $APP_BUNDLE"
echo "   Disk Image: $BUILD_DIR/$DMG_NAME"
echo ""
echo "🚀 To distribute:"
echo "   1. Share the .dmg file for easy installation"
echo "   2. Or share the .app bundle directly"
echo ""
echo "💡 The installer will:"
echo "   • Download latest version from GitHub"
echo "   • Install all Python dependencies"
echo "   • Create professional app bundle"
echo "   • Add to Applications folder"
echo "   • Set up desktop integration"
echo ""

# Test the installer (optional)
read -p "Would you like to test the installer now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Launching installer for testing..."
    open "$APP_BUNDLE"
fi

print_success "Build process complete! 🎉"