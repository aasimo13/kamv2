#!/bin/bash
# Fast Raspberry Pi installer - uses pre-built packages to avoid compilation

set -e

echo "🍓 USB Camera Tester - Fast Pi Install"
echo "====================================="
echo "Using pre-built packages to avoid long compilation times"
echo ""

# Check if we're on a Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  This installer is optimized for Raspberry Pi"
fi

# System info
echo "Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
echo "Architecture: $(uname -m)"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')"
echo ""

# Update package list
echo "📦 Updating package lists..."
sudo apt update

# Install system dependencies first
echo "📦 Installing system packages..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-numpy \
    python3-opencv \
    python3-pyqt6 \
    v4l-utils \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    build-essential \
    cmake \
    pkg-config

echo "✅ System packages installed!"

# Create installation directory
INSTALL_DIR="/opt/usb-camera-tester"
echo "📁 Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

# Copy files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📂 Copying application files..."
sudo cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || {
    echo "⚠️  Some files may not have copied. Continuing..."
}

# Change to install directory
cd "$INSTALL_DIR"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
sudo python3 -m venv venv

# Fix ownership
USER_NAME="${SUDO_USER:-$USER}"
sudo chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install packages that are definitely available as wheels
echo "📦 Installing Python packages (using system packages when possible)..."

# Try to use system packages first, then pip as fallback
echo "  Installing numpy..."
if python -c "import numpy" 2>/dev/null; then
    echo "    ✅ numpy available via system packages"
else
    pip install numpy
fi

echo "  Installing OpenCV..."
if python -c "import cv2" 2>/dev/null; then
    echo "    ✅ OpenCV available via system packages"
else
    echo "    Installing OpenCV from pip (this may take time)..."
    pip install opencv-python-headless --no-cache-dir
fi

echo "  Installing PyQt6..."
if python -c "import PyQt6" 2>/dev/null; then
    echo "    ✅ PyQt6 available via system packages"
else
    # For PyQt6, try a known working version
    pip install PyQt6==6.4.0 --no-cache-dir
fi

echo "  Installing reportlab for PDF export..."
pip install reportlab --no-cache-dir

# Test all imports
echo ""
echo "🧪 Testing Python imports..."
if python -c "import numpy, cv2, PyQt6, reportlab; print('✅ All modules imported successfully')" 2>/dev/null; then
    echo "✅ Python environment ready!"
else
    echo "❌ Some modules failed to import. Trying alternative approach..."

    # Alternative: Install everything via apt
    echo "📦 Installing via apt packages only..."
    sudo apt install -y python3-numpy python3-opencv python3-pyqt6 python3-reportlab || {
        echo "⚠️  Some packages not available via apt"
    }
fi

# Create user-friendly launcher
echo "🚀 Creating launcher..."
cat > "$INSTALL_DIR/launch_pi.sh" << 'EOF'
#!/bin/bash
# Simple Pi launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🍓 USB Camera Tester - Raspberry Pi"
echo "================================="
echo ""

# Check camera permissions
if ! groups | grep -q video; then
    echo "⚠️  Adding user to video group..."
    sudo usermod -a -G video $USER
    echo "✅ Added to video group. Please log out and back in."
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "ℹ️  Using system Python"
fi

# Set environment
export QT_QPA_PLATFORM=xcb

echo "📹 Checking cameras..."
v4l2-ctl --list-devices 2>/dev/null || echo "No V4L2 cameras found"

echo ""
echo "🚀 Starting USB Camera Tester..."
cd "$SCRIPT_DIR"
python3 main_pyqt6.py "$@"
EOF

chmod +x "$INSTALL_DIR/launch_pi.sh"

# Create system command
echo "📟 Creating system command..."
sudo ln -sf "$INSTALL_DIR/launch_pi.sh" /usr/local/bin/pi-camera-tester

# Add user to video group
USER_NAME="${SUDO_USER:-$USER}"
echo "👤 Adding user to video group..."
sudo usermod -a -G video "$USER_NAME"

# Set permissions
sudo chown -R "$USER_NAME:$USER_NAME" "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📍 Installation: $INSTALL_DIR"
echo "🚀 Command: pi-camera-tester"
echo "🚀 Direct: $INSTALL_DIR/launch_pi.sh"
echo ""
echo "💡 Important:"
echo "   • Log out and back in to apply video group"
echo "   • Or run: newgrp video"
echo ""

# Final test
echo "🔧 Testing installation..."
cd "$INSTALL_DIR"
source venv/bin/activate 2>/dev/null || true

if python3 -c "import sys; print('Python:', sys.version)" 2>/dev/null; then
    echo "✅ Python working"
else
    echo "❌ Python test failed"
fi

if python3 -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>/dev/null; then
    :
else
    echo "❌ numpy not working"
fi

if python3 -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>/dev/null; then
    :
else
    echo "❌ OpenCV not working"
fi

echo ""
echo "🎯 Ready! Run: pi-camera-tester"