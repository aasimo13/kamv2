#!/bin/bash
# ONE-CLICK USB Camera Tester for Raspberry Pi
# Works on ANY Pi (3B, 4, 5) with automatic detection

set -e

echo "🎥 ONE-CLICK USB Camera Tester Setup"
echo "===================================="
echo "Automatic installation for ANY Raspberry Pi"
echo ""

# Detect Pi model and choose strategy
PI_MODEL="Unknown"
if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(cat /proc/device-tree/model)
    echo "✅ Detected: $PI_MODEL"
fi

# Get system info
ARCH=$(uname -m)
MEM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
echo "Architecture: $ARCH"
echo "Total RAM: ${MEM_TOTAL}MB"
echo ""

# Install system packages (works on all Pi models)
echo "📦 Installing system packages (this works on ALL Pi models)..."
sudo apt update
sudo apt install -y \
    python3 \
    python3-opencv \
    python3-numpy \
    python3-pyqt5 \
    python3-pip \
    v4l-utils \
    fswebcam \
    || {
    echo "⚠️  Some packages failed, continuing..."
}

# Try to install PyQt6, fall back to PyQt5
echo "🎨 Setting up GUI framework..."
if python3 -c "import PyQt6" 2>/dev/null; then
    echo "✅ PyQt6 already installed"
    QT_VERSION="PyQt6"
elif sudo apt install -y python3-pyqt6 2>/dev/null; then
    echo "✅ PyQt6 installed"
    QT_VERSION="PyQt6"
elif pip3 install PyQt6 --break-system-packages 2>/dev/null; then
    echo "✅ PyQt6 installed via pip"
    QT_VERSION="PyQt6"
else
    echo "ℹ️  PyQt6 not available, using PyQt5"
    QT_VERSION="PyQt5"
    sudo apt install -y python3-pyqt5 || true
fi

# Install reportlab for PDF export
echo "📄 Installing PDF support..."
pip3 install reportlab --break-system-packages 2>/dev/null || {
    sudo apt install -y python3-reportlab 2>/dev/null || {
        echo "⚠️  PDF export won't be available"
    }
}

# Create installation directory
INSTALL_DIR="$HOME/camera-tester"
echo "📁 Installing to: $INSTALL_DIR"
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
cp -r * "$INSTALL_DIR/" 2>/dev/null || {
    echo "⚠️  Some files couldn't be copied"
}

# Fix PyQt imports if needed
if [ "$QT_VERSION" = "PyQt5" ]; then
    echo "🔧 Adapting for PyQt5..."
    cd "$INSTALL_DIR"

    # Create a compatibility version
    cp main_pyqt6.py main_qt.py

    # Fix imports
    sed -i 's/from PyQt6/from PyQt5/g' main_qt.py
    sed -i 's/PyQt6/PyQt5/g' main_qt.py
    sed -i 's/Format\.Format_/Format_/g' main_qt.py
    sed -i 's/AspectRatioMode\./Qt./g' main_qt.py
    sed -i 's/TransformationMode\./Qt./g' main_qt.py
    sed -i 's/Qt\.KeepAspectRatio/Qt.AspectRatioMode.KeepAspectRatio/g' main_qt.py 2>/dev/null || true
    sed -i 's/Qt\.SmoothTransformation/Qt.TransformationMode.SmoothTransformation/g' main_qt.py 2>/dev/null || true

    MAIN_SCRIPT="main_qt.py"
else
    MAIN_SCRIPT="main_pyqt6.py"
fi

# Add user to video group
if ! groups | grep -q video; then
    echo "👤 Adding user to video group..."
    sudo usermod -a -G video $USER
    echo "✅ Added to video group (may need to log out/in)"
fi

# Create the ONE-CLICK launcher
echo "🚀 Creating one-click launcher..."
cat > "$INSTALL_DIR/RUN_CAMERA_TESTER.sh" << EOF
#!/bin/bash
# ONE-CLICK LAUNCHER - Just double-click this file!

echo "🎥 USB Camera Tester"
echo "==================="
echo ""

# Check cameras
echo "📹 Detecting cameras..."
if command -v v4l2-ctl >/dev/null 2>&1; then
    v4l2-ctl --list-devices 2>/dev/null || echo "No V4L2 cameras found"
else
    echo "V4L2 tools not available"
fi

echo ""
echo "🔌 USB devices:"
lsusb | grep -i camera || echo "No USB cameras in lsusb"

echo ""
echo "📁 Video devices:"
ls -la /dev/video* 2>/dev/null || echo "No /dev/video* devices"

echo ""
echo "🚀 Starting camera tester..."
cd "\$(dirname "\$0")"

# Try to run the appropriate version
if [ -f "$MAIN_SCRIPT" ]; then
    python3 $MAIN_SCRIPT 2>&1 || {
        echo ""
        echo "❌ Error running application!"
        echo "Try running: python3 $MAIN_SCRIPT"
        read -p "Press Enter to exit..."
    }
else
    echo "❌ Application file not found!"
    read -p "Press Enter to exit..."
fi
EOF

chmod +x "$INSTALL_DIR/RUN_CAMERA_TESTER.sh"

# Create desktop shortcut
DESKTOP_FILE="$HOME/Desktop/USB-Camera-Tester.desktop"
echo "🖥️  Creating desktop shortcut..."
mkdir -p "$HOME/Desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=USB Camera Tester
Comment=Test USB cameras with professional tools
Exec=$INSTALL_DIR/RUN_CAMERA_TESTER.sh
Icon=camera-video
Terminal=true
Categories=AudioVideo;Video;Photography;
StartupNotify=false
EOF

chmod +x "$DESKTOP_FILE"
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true

# Create command-line launcher
echo "📟 Creating command-line launcher..."
cat > "$HOME/.local/bin/camera-tester" << EOF
#!/bin/bash
exec "$INSTALL_DIR/RUN_CAMERA_TESTER.sh"
EOF
chmod +x "$HOME/.local/bin/camera-tester"

# Create test script
echo "🧪 Creating test script..."
cat > "$INSTALL_DIR/test_setup.py" << 'EOF'
#!/usr/bin/env python3
import sys
print("🧪 Testing Python environment...")

# Test imports
modules = {
    'numpy': None,
    'cv2': 'opencv',
    'PyQt6': 'PyQt6',
    'PyQt5': 'PyQt5',
    'reportlab': 'reportlab'
}

working = []
missing = []

for module, name in modules.items():
    try:
        __import__(module)
        working.append(module)
        print(f"✅ {module} is working")
    except ImportError:
        missing.append(module)
        print(f"❌ {module} is missing")

print("\n📊 Summary:")
print(f"Working modules: {', '.join(working)}")
if missing:
    print(f"Missing modules: {', '.join(missing)}")

# Check Qt version
qt_version = None
if 'PyQt6' in working:
    qt_version = 'PyQt6'
elif 'PyQt5' in working:
    qt_version = 'PyQt5'

if qt_version:
    print(f"✅ GUI will use: {qt_version}")
else:
    print("❌ No Qt framework available!")
    sys.exit(1)

# Test camera
try:
    import cv2
    print("\n📹 Testing camera access...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ Camera 0 is accessible")
        cap.release()
    else:
        print("⚠️  Camera 0 cannot be opened")
except:
    print("⚠️  Cannot test camera")

print("\n✅ Setup test complete!")
EOF

chmod +x "$INSTALL_DIR/test_setup.py"

# Final setup info
echo ""
echo "========================================"
echo "✅ ONE-CLICK INSTALLATION COMPLETE!"
echo "========================================"
echo ""
echo "📍 Installed to: $INSTALL_DIR"
echo ""
echo "🚀 THREE WAYS TO RUN:"
echo ""
echo "1️⃣  DESKTOP (easiest):"
echo "    Look for 'USB Camera Tester' on your desktop"
echo "    Just double-click it!"
echo ""
echo "2️⃣  FILE MANAGER:"
echo "    Navigate to: $INSTALL_DIR"
echo "    Double-click: RUN_CAMERA_TESTER.sh"
echo ""
echo "3️⃣  TERMINAL:"
echo "    Type: camera-tester"
echo "    Or: $INSTALL_DIR/RUN_CAMERA_TESTER.sh"
echo ""
echo "========================================"
echo ""

# Test the setup
echo "🧪 Testing installation..."
cd "$INSTALL_DIR"
python3 test_setup.py

echo ""
echo "🎉 Ready to test your USB cameras!"
echo ""
read -p "Press Enter to launch now, or Ctrl+C to exit..."

# Launch immediately
exec "$INSTALL_DIR/RUN_CAMERA_TESTER.sh"