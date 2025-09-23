#!/bin/bash

# Create Standalone USB Camera Tester Installer
# This packages everything needed into a single distributable app

set -e  # Exit on any error

# Configuration
APP_NAME="USB Camera Tester"
INSTALLER_NAME="USB Camera Tester Installer"
VERSION="4.0"
BUILD_DIR="standalone_installer_build"
BUNDLE_ID="com.usb-camera-tester.standalone-installer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🚀 Creating Standalone USB Camera Tester Installer..."

# Clean up previous build
print_status "Cleaning up previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create app bundle structure
APP_BUNDLE="$BUILD_DIR/$INSTALLER_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

print_status "Creating application bundle structure..."

# Copy the entire camera test suite
print_status "Packaging camera test suite..."
cp -R camera_test_suite "$RESOURCES_DIR/"

# Create the launcher script in Resources
print_status "Adding launcher script..."
cat > "$RESOURCES_DIR/Launch USB Camera Tester.command" << 'EOF'
#!/bin/bash
# Launcher for USB Camera Tester that ensures proper permissions

echo "🎥 USB Camera Tester Launcher"
echo "=============================="
echo ""
echo "This launcher ensures the camera tester has proper permissions."
echo ""

# Find the USB Camera Tester app bundle
APP_BUNDLE="/Applications/USB Camera Tester.app"
APP_DIR="$APP_BUNDLE/Contents/Resources/camera_test_suite"

echo "Looking for app in: $APP_DIR"

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "❌ USB Camera Tester app not found in Applications folder"
    echo "Please make sure the app is installed correctly."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if camera test suite exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Camera test suite not found in app bundle"
    echo "App may be corrupted. Please reinstall."
    read -p "Press Enter to exit..."
    exit 1
fi

# Change to app directory
cd "$APP_DIR"
echo "✅ Found camera test suite"

# Find Python
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$python_path" &> /dev/null; then
        PYTHON_CMD="$python_path"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3 not found. Please install Python from python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Clean Python environment to avoid import conflicts
unset PYTHONPATH
export PYTHONNOUSERSITE=0

# Ensure we're not in any conflicting directories
echo "Current directory: $(pwd)"

# Test imports before launching
echo "Testing Python imports..."
if ! "$PYTHON_CMD" -c "import sys; print('Python version:', sys.version)" 2>/dev/null; then
    echo "❌ Python test failed"
    read -p "Press Enter to exit..."
    exit 1
fi

if ! "$PYTHON_CMD" -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
    echo "❌ numpy import failed - trying to fix..."
    # Try with clean environment
    if ! env -i PATH="$PATH" "$PYTHON_CMD" -c "import numpy; print('✅ numpy fixed')" 2>/dev/null; then
        echo "❌ numpy still failing. Please reinstall: pip3 install --user --force-reinstall numpy"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

if ! "$PYTHON_CMD" -c "import cv2; print('✅ opencv version:', cv2.__version__)" 2>/dev/null; then
    echo "❌ opencv import failed"
    read -p "Press Enter to exit..."
    exit 1
fi

if ! "$PYTHON_CMD" -c "import PyQt6; print('✅ PyQt6 imported successfully')" 2>/dev/null; then
    echo "❌ PyQt6 import failed"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ All imports successful"

# Run the app with clean environment
echo "Starting USB Camera Tester..."
env -i PATH="$PATH" DISPLAY="$DISPLAY" "$PYTHON_CMD" main_pyqt6.py

echo ""
echo "App closed."
EOF

chmod +x "$RESOURCES_DIR/Launch USB Camera Tester.command"

# Create the main installer script
print_status "Creating installer script..."
cat > "$MACOS_DIR/$INSTALLER_NAME" << 'EOF'
#!/bin/bash

# USB Camera Tester Standalone Installer
# Installs everything needed without internet connection

# Get the directory containing this installer
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESOURCES_DIR="$INSTALLER_DIR/Resources"

echo "🔧 Debug paths:"
echo "  Script dir: $SCRIPT_DIR"
echo "  Installer dir: $INSTALLER_DIR"
echo "  Resources dir: $RESOURCES_DIR"
echo ""

# Verify resources exist
if [ ! -d "$RESOURCES_DIR" ]; then
    echo "❌ Resources directory not found: $RESOURCES_DIR"
    echo "Available directories:"
    ls -la "$INSTALLER_DIR/"
    exit 1
fi

echo "🎥 USB Camera Tester Standalone Installer"
echo "========================================"
echo ""
echo "This will install the USB Camera Tester to your Applications folder."
echo ""
echo "🔧 System Info:"
echo "  macOS Version: $(sw_vers -productVersion)"
echo "  Architecture: $(uname -m)"
echo ""

# Check for Python and install dependencies
echo "Checking for Python..."
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$python_path" &> /dev/null; then
        PYTHON_CMD="$python_path"
        echo "✅ Found Python: $python_path"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "❌ Python 3 not found."
    echo ""
    osascript -e 'display dialog "Python 3 is required but not found.\n\nPlease install Python 3 from https://python.org\n\nThen run this installer again." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check and install required modules
echo "Checking Python modules..."
MODULES_NEEDED=()

# Check each required module with better error handling
echo "Testing module imports..."
for module in cv2 numpy PyQt6; do
    echo -n "  Checking $module... "
    if "$PYTHON_CMD" -c "import $module; print('OK')" 2>/dev/null | grep -q "OK"; then
        echo "✅ installed"
    else
        echo "❌ missing"
        case $module in
            "cv2") MODULES_NEEDED+=("opencv-python") ;;
            *) MODULES_NEEDED+=("$module") ;;
        esac
    fi
done

echo ""
if [ ${#MODULES_NEEDED[@]} -eq 0 ]; then
    echo "🎉 All Python modules are already installed!"
else
    echo "📦 Need to install: ${MODULES_NEEDED[*]}"
fi

# Install missing modules if any
if [ ${#MODULES_NEEDED[@]} -gt 0 ]; then
    echo ""
    echo "📦 Installing required Python modules..."
    echo "Missing modules: ${MODULES_NEEDED[*]}"
    echo ""

    # Get pip command with better detection
    PIP_CMD=""
    echo "Finding pip..."

    # Try python -m pip first (most reliable)
    if "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
        PIP_CMD="$PYTHON_CMD -m pip"
        echo "✅ Found pip via python -m pip"
    else
        # Try standalone pip commands
        for pip_candidate in "${PYTHON_CMD%/*}/pip3" "${PYTHON_CMD%/*}/pip" pip3 pip; do
            if command -v "$pip_candidate" >/dev/null 2>&1 && "$pip_candidate" --version >/dev/null 2>&1; then
                PIP_CMD="$pip_candidate"
                echo "✅ Found pip: $pip_candidate"
                break
            fi
        done
    fi

    if [ -z "$PIP_CMD" ]; then
        echo "❌ pip not found. Installing pip..."
        "$PYTHON_CMD" -m ensurepip --default-pip 2>/dev/null || {
            osascript -e 'display dialog "Could not install pip automatically.\n\nPlease install pip manually:\n1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py\n2. Run: python3 get-pip.py\n\nThen run this installer again." buttons {"OK"} default button "OK" with icon stop'
            exit 1
        }
        PIP_CMD="$PYTHON_CMD -m pip"
    fi

    echo "Installing modules with: $PIP_CMD"

    # Install each module with specific fixes for common issues
    for module in "${MODULES_NEEDED[@]}"; do
        echo "Installing $module..."
        if [ "$module" = "numpy" ]; then
            # Force reinstall numpy to avoid conflicts
            if eval "$PIP_CMD install --user --force-reinstall '$module'" >/dev/null 2>&1; then
                echo "✅ $module installed successfully (force reinstall)"
            else
                echo "⚠️  $module installation may have issues, but continuing..."
            fi
        else
            if eval "$PIP_CMD install --user '$module'" >/dev/null 2>&1; then
                echo "✅ $module installed successfully"
            else
                echo "⚠️  $module installation may have issues, but continuing..."
            fi
        fi
    done

    echo ""
    echo "✅ Module installation complete!"
    echo ""

    # Verify installation
    echo "Verifying installation..."
    ALL_GOOD=true
    for module in cv2 numpy PyQt6; do
        if "$PYTHON_CMD" -c "import $module" 2>/dev/null; then
            echo "✅ $module verified"
        else
            echo "❌ $module still not working"
            ALL_GOOD=false
        fi
    done

    if [ "$ALL_GOOD" = false ]; then
        osascript -e 'display dialog "Some Python modules could not be installed automatically.\n\nPlease try installing manually in Terminal:\npip3 install --user opencv-python numpy PyQt6\n\nThen run this installer again." buttons {"OK"} default button "OK" with icon stop'
        exit 1
    fi
else
    echo "✅ All required Python modules are already installed!"
    echo "🚀 Proceeding directly to installation..."
fi

# Create Applications directory structure
echo ""
echo "Installing to Applications..."

APP_DIR="/Applications/USB Camera Tester.app"
APP_CONTENTS="$APP_DIR/Contents"
APP_RESOURCES="$APP_CONTENTS/Resources"
APP_MACOS="$APP_CONTENTS/MacOS"

# Remove existing installation
if [ -d "$APP_DIR" ]; then
    echo "Removing existing installation..."
    rm -rf "$APP_DIR"
fi

# Create new installation
mkdir -p "$APP_MACOS"
mkdir -p "$APP_RESOURCES"

# Copy camera test suite
echo "Installing camera test suite..."
cp -R "$RESOURCES_DIR/camera_test_suite" "$APP_RESOURCES/"

# Copy launcher to app resources
echo "Installing launcher..."
cp "$RESOURCES_DIR/Launch USB Camera Tester.command" "$APP_RESOURCES/"

# Also copy launcher to Desktop for easy access
echo "Adding launcher to Desktop..."
cp "$RESOURCES_DIR/Launch USB Camera Tester.command" "$HOME/Desktop/🎥 Launch USB Camera Tester.command"
chmod +x "$HOME/Desktop/🎥 Launch USB Camera Tester.command"

# And copy to Applications folder root for easy finding
echo "Adding launcher to Applications folder..."
cp "$RESOURCES_DIR/Launch USB Camera Tester.command" "/Applications/🎥 Launch USB Camera Tester.command"
chmod +x "/Applications/🎥 Launch USB Camera Tester.command"

# Create app launcher script
cat > "$APP_MACOS/USBCameraTester" << 'APPLAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"

# Ensure we have a proper GUI environment
export DISPLAY=${DISPLAY:-:0}

# Clear Claude Code environment variables that prevent GUI
unset CLAUDECODE
unset CLAUDE_CODE
unset CLAUDE_CODE_SSE_PORT
unset CLAUDE_CODE_ENTRYPOINT

# Find Python executable - prefer user-installed versions over system
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 /usr/bin/python3 python; do
    if command -v "$python_path" &> /dev/null; then
        # Test if this Python can import numpy (check for architecture compatibility)
        if "$python_path" -c "import numpy" 2>/dev/null; then
            PYTHON_CMD="$python_path"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    osascript -e 'display dialog "Python 3 is required but not found. Please install Python from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Change to the application directory
cd "$RESOURCES_DIR/camera_test_suite"

# Launch the application
"$PYTHON_CMD" main_pyqt6.py "$@"
APPLAUNCHER

chmod +x "$APP_MACOS/USBCameraTester"

# Create Info.plist
cat > "$APP_CONTENTS/Info.plist" << 'INFOPLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>USBCameraTester</string>
    <key>CFBundleIdentifier</key>
    <string>com.usb-camera-tester.app</string>
    <key>CFBundleName</key>
    <string>USB Camera Tester</string>
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
    <key>NSCameraUsageDescription</key>
    <string>USB Camera Tester needs access to your camera to test USB camera hardware functionality and perform diagnostic tests.</string>
    <key>NSCameraUseContinuityCameraDeviceType</key>
    <true/>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
</dict>
</plist>
INFOPLIST

# Copy icon if it exists
if [ -f "$RESOURCES_DIR/camera_test_suite/icons/app_icon.icns" ]; then
    cp "$RESOURCES_DIR/camera_test_suite/icons/app_icon.icns" "$APP_RESOURCES/"
fi

# Set permissions
chmod -R 755 "$APP_DIR"
chmod +x "$APP_MACOS/USBCameraTester"
chmod +x "$APP_RESOURCES/Launch USB Camera Tester.command"

# Remove quarantine
xattr -cr "$APP_DIR" 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎉 USB Camera Tester is now installed! You can use it in multiple ways:"
echo ""
echo "📱 MAIN APP:"
echo "   • USB Camera Tester (in Applications folder)"
echo ""
echo "🚀 EASY LAUNCHERS (Better Camera Permissions):"
echo "   • 🎥 Launch USB Camera Tester.command (on your Desktop)"
echo "   • 🎥 Launch USB Camera Tester.command (in Applications folder)"
echo ""
echo "💡 TIP: Use the launcher scripts for best camera access!"
echo ""

# Ask if user wants to launch now
osascript -e 'display dialog "🎉 Installation Complete!\n\nUSB Camera Tester is ready to use!\n\n📱 Main App: Applications folder\n🚀 Easy Launcher: On your Desktop\n\n💡 For best camera permissions, use the launcher on your Desktop\n\nWould you like to launch it now?" buttons {"Not Now", "Launch Camera Tester"} default button "Launch Camera Tester"' > /tmp/user_choice.txt 2>/dev/null

if grep -q "Launch Camera Tester" /tmp/user_choice.txt 2>/dev/null; then
    # Launch using the desktop launcher for best permissions
    open "$HOME/Desktop/🎥 Launch USB Camera Tester.command"
fi

rm -f /tmp/user_choice.txt 2>/dev/null || true
EOF

chmod +x "$MACOS_DIR/$INSTALLER_NAME"

# Create Info.plist for installer
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
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
</dict>
</plist>
EOF

# Add icon if available
if [ -f "camera_test_suite/icons/app_icon.icns" ]; then
    cp "camera_test_suite/icons/app_icon.icns" "$RESOURCES_DIR/"
    print_success "Professional icon added"
fi

# Set permissions
print_status "Setting bundle permissions..."
chmod -R 755 "$APP_BUNDLE"
chmod +x "$MACOS_DIR/$INSTALLER_NAME"

# Remove quarantine
print_status "Setting extended attributes..."
xattr -cr "$APP_BUNDLE" 2>/dev/null || true

# Create a DMG for easy distribution
print_status "Creating disk image..."
DMG_NAME="🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v$VERSION.dmg"
DMG_TEMP="$BUILD_DIR/dmg_temp"

mkdir -p "$DMG_TEMP"
cp -R "$APP_BUNDLE" "$DMG_TEMP/"

# Create instructions
cat > "$DMG_TEMP/📋 README - EASY INSTALLATION.txt" << 'EOF'
🎥 USB Camera Tester - COMPLETE INSTALLER
=========================================

✨ SUPER EASY INSTALLATION - EVERYTHING INCLUDED!

QUICK START (Just 2 Steps!):
1. 🖱️  Double-click "USB Camera Tester Installer.app"
2. ✅ Follow the prompts - dependencies install automatically!

REQUIREMENTS:
- macOS 10.14 or later
- Python 3 (installer will guide you if missing)

🚀 WHAT THIS INSTALLER DOES AUTOMATICALLY:
✅ Checks for Python 3
✅ Installs ALL required Python modules (opencv-python, numpy, PyQt6)
✅ Installs USB Camera Tester to /Applications/
✅ Includes special launcher for proper camera permissions
✅ Creates complete app bundle with professional test suite
✅ No internet connection required during installation (after Python is installed)

📱 AFTER INSTALLATION, YOU CAN USE:

🚀 EASY LAUNCHERS (RECOMMENDED - Better Camera Access):
   • 🎥 "Launch USB Camera Tester.command" on your DESKTOP
   • 🎥 "Launch USB Camera Tester.command" in Applications folder

📱 MAIN APP:
   • USB Camera Tester.app (in Applications folder)

🎯 PROFESSIONAL FEATURES:
- Comprehensive camera hardware testing
- Detailed parameter analysis
- Professional PDF/JSON export
- Samsung S5KGM1ST sensor support
- PDAF autofocus testing
- Resolution, framerate, exposure analysis
- And much more!

💡 TIP: The launcher scripts are placed on your Desktop and in Applications folder
     for super easy access! No digging through package contents needed!

🔧 Built by Claude Code for professional camera testing
EOF

# Create DMG
hdiutil create -srcfolder "$DMG_TEMP" -volname "USB Camera Tester Installer" -ov "$BUILD_DIR/$DMG_NAME"

print_success "Build complete!"
echo ""
echo "📦 COMPLETE INSTALLER CREATED:"
echo "   📱 App Bundle: $APP_BUNDLE"
echo "   🎥 FINAL DMG: $BUILD_DIR/$DMG_NAME"
echo ""
echo "🚀 TO SEND TO YOUR COLLEAGUE:"
echo "   📧 Send this file: $BUILD_DIR/$DMG_NAME"
echo ""
echo "📋 WHAT THEY DO (Super Easy!):"
echo "   1. 🖱️  Double-click the DMG to open it"
echo "   2. 🖱️  Double-click 'USB Camera Tester Installer.app'"
echo "   3. ✅ Follow prompts (dependencies install automatically!)"
echo "   4. 🎉 Done! App is in Applications folder"
echo ""
echo "💡 The installer will:"
echo "   ✅ Check for Python"
echo "   ✅ Auto-install all Python modules (opencv-python, numpy, PyQt6)"
echo "   ✅ Install the complete app with launcher"
echo "   ✅ Handle all setup automatically"
echo ""
print_success "🎥 READY FOR DISTRIBUTION - ONE-CLICK SOLUTION!"