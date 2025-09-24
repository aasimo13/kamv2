#!/bin/bash
# Raspberry Pi installer using ONLY system packages (no pip compilation)

set -e

echo "🍓 USB Camera Tester - System Packages Only"
echo "=========================================="
echo "Uses only apt packages - no compilation required!"
echo ""

# Update packages
echo "📦 Updating package lists..."
sudo apt update

# Install everything from system packages
echo "📦 Installing all dependencies via apt..."
sudo apt install -y \
    python3 \
    python3-numpy \
    python3-opencv \
    python3-pyqt6 \
    python3-pip \
    python3-reportlab \
    v4l-utils \
    uvcdynctrl \
    guvcview \
    fswebcam

echo "✅ All packages installed!"

# Create simple launcher that uses system packages
INSTALL_DIR="$HOME/usb-camera-tester"
echo "📁 Creating user installation: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || {
    echo "ℹ️  Copying available files..."
    cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/" 2>/dev/null || true
}

# Create simple launcher
cat > "$INSTALL_DIR/run_camera_tester.sh" << 'EOF'
#!/bin/bash
# Simple system-package launcher

echo "🍓 USB Camera Tester (System Packages)"
echo "====================================="

# Check video group
if ! groups | grep -q video; then
    echo "⚠️  Adding to video group..."
    sudo usermod -a -G video $USER
    echo "Please log out and back in, then run again."
    exit 1
fi

# Check cameras
echo "📹 Available cameras:"
v4l2-ctl --list-devices 2>/dev/null || echo "No cameras found"

# Test imports
echo "🧪 Testing Python modules..."
python3 -c "
try:
    import numpy
    print('✅ numpy:', numpy.__version__)
except ImportError:
    print('❌ numpy not available')

try:
    import cv2
    print('✅ OpenCV:', cv2.__version__)
except ImportError:
    print('❌ OpenCV not available')

try:
    import PyQt6
    print('✅ PyQt6 available')
except ImportError:
    print('❌ PyQt6 not available')

try:
    import reportlab
    print('✅ reportlab available')
except ImportError:
    print('❌ reportlab not available')
"

echo ""
echo "🚀 Starting camera tester..."
cd "$(dirname "$0")"
python3 main_pyqt6.py "$@"
EOF

chmod +x "$INSTALL_DIR/run_camera_tester.sh"

# Add user to video group
echo "👤 Adding user to video group..."
sudo usermod -a -G video "$USER"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📍 Location: $INSTALL_DIR"
echo "🚀 Run with: $INSTALL_DIR/run_camera_tester.sh"
echo ""
echo "💡 Next steps:"
echo "   1. Log out and back in (for video group)"
echo "   2. Connect your USB camera"
echo "   3. Run: $INSTALL_DIR/run_camera_tester.sh"
echo ""

# Test
echo "🔧 Quick test..."
cd "$INSTALL_DIR"
python3 -c "print('✅ Python working')"
python3 -c "import numpy; print('✅ numpy working')" 2>/dev/null || echo "❌ numpy issue"
python3 -c "import cv2; print('✅ OpenCV working')" 2>/dev/null || echo "❌ OpenCV issue"

echo ""
echo "🎯 Ready to test cameras!"