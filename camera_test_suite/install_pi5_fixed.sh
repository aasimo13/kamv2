#!/bin/bash
# USB Camera Tester - Raspberry Pi 5 Fixed Installer
# Uses pre-built wheels from piwheels to avoid compilation issues

set -e

echo "🚀 USB Camera Tester - Raspberry Pi 5 Fixed Installer"
echo "====================================================="
echo "Using pre-built wheels for faster installation"
echo ""

# Check Pi model
if [ -f /proc/device-tree/model ]; then
    echo "Pi Model: $(cat /proc/device-tree/model)"
fi

echo "Architecture: $(uname -m)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo ""

# Check sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with: sudo $0"
    exit 1
fi

ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")

# Install missing build dependencies
echo "📦 Installing missing dependencies..."
apt update
apt install -y \
    autoconf \
    automake \
    libtool \
    build-essential \
    cmake \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-numpy \
    python3-opencv \
    v4l-utils \
    libatlas-base-dev \
    libhdf5-dev \
    libjasper-dev \
    libqt5gui5 \
    libqt5test5 \
    libqtgui4

# Install directory
INSTALL_DIR="/opt/usb-camera-tester-pi5"
echo "📁 Setting up installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true

cd "$INSTALL_DIR"

# Create virtual environment with system packages
echo "🐍 Creating virtual environment..."
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Configure pip to use piwheels
echo "🔧 Configuring for piwheels (ARM optimized packages)..."
cat > pip.conf << 'EOF'
[global]
extra-index-url = https://www.piwheels.org/simple
trusted-host = pypi.org files.pythonhosted.org www.piwheels.org
EOF

export PIP_CONFIG_FILE="$PWD/pip.conf"

# Upgrade pip
python -m pip install --upgrade pip wheel setuptools

# Install packages using pre-built wheels
echo "📦 Installing Python packages (using pre-built wheels)..."

# Install numpy (use wheel, not source)
echo "  Installing numpy..."
pip install numpy --prefer-binary --no-cache-dir || {
    echo "  Falling back to system numpy..."
    apt install -y python3-numpy
}

# Install OpenCV (prefer pre-built)
echo "  Installing OpenCV..."
pip install opencv-python --prefer-binary --no-cache-dir || {
    echo "  Trying headless version..."
    pip install opencv-python-headless --prefer-binary --no-cache-dir || {
        echo "  Using system OpenCV..."
        apt install -y python3-opencv
    }
}

# Install PyQt6
echo "  Installing PyQt6..."
pip install PyQt6 --prefer-binary --no-cache-dir || {
    echo "  Trying PyQt5 as fallback..."
    pip install PyQt5 --prefer-binary --no-cache-dir || {
        echo "  Using system Qt packages..."
        apt install -y python3-pyqt5
    }
}

# Install additional packages
echo "  Installing additional packages..."
pip install reportlab Pillow matplotlib --prefer-binary --no-cache-dir

# GPU configuration
echo "🎮 Configuring GPU..."
if ! grep -q "gpu_mem=256" /boot/firmware/config.txt 2>/dev/null; then
    if [ -f /boot/firmware/config.txt ]; then
        echo "gpu_mem=256" >> /boot/firmware/config.txt
    elif [ -f /boot/config.txt ]; then
        echo "gpu_mem=256" >> /boot/config.txt
    fi
    echo "✅ GPU memory set to 256MB"
fi

# Enable camera
raspi-config nonint do_camera 0 2>/dev/null || true

# Create launcher
echo "🚀 Creating launcher..."
cat > "$INSTALL_DIR/launch_pi5.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 USB Camera Tester - Raspberry Pi 5"
echo "===================================="
echo ""

# System info
echo "Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Temperature: $(vcgencmd measure_temp 2>/dev/null || echo 'N/A')"
echo ""

# Check permissions
if ! groups | grep -q video; then
    echo "Adding to video group..."
    sudo usermod -a -G video $USER
    echo "Please log out and back in."
fi

# Check for virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "ℹ️  Using system Python"
fi

# Environment
export QT_QPA_PLATFORM=xcb
export OPENCV_LOG_LEVEL=ERROR

# Camera detection
echo "📹 Cameras:"
v4l2-ctl --list-devices 2>/dev/null || echo "No V4L2 cameras"
echo ""

# Launch
cd "$SCRIPT_DIR"
python3 main_pyqt6.py "$@"
EOF

chmod +x "$INSTALL_DIR/launch_pi5.sh"

# Create simple test script
cat > "$INSTALL_DIR/test_cameras.py" << 'EOF'
#!/usr/bin/env python3
import cv2
import sys

print("Testing cameras...")

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"✅ Camera {i}: {int(width)}x{int(height)}")
        cap.release()

print("Test complete!")
EOF

chmod +x "$INSTALL_DIR/test_cameras.py"

# Create command
cat > "/usr/local/bin/camera-tester" << EOF
#!/bin/bash
exec "$INSTALL_DIR/launch_pi5.sh" "\$@"
EOF
chmod +x "/usr/local/bin/camera-tester"

# Set permissions
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
usermod -a -G video "$ACTUAL_USER"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📍 Location: $INSTALL_DIR"
echo "🚀 Run: camera-tester"
echo "🚀 Or: $INSTALL_DIR/launch_pi5.sh"
echo ""

# Test installation
echo "🧪 Testing..."
cd "$INSTALL_DIR"
source venv/bin/activate 2>/dev/null || true

echo -n "Python: "
python3 --version

echo -n "Testing imports... "
if python3 -c "import cv2, numpy; print('✅ Core modules OK')" 2>/dev/null; then
    echo ""
else
    echo "⚠️  Some modules may be missing"
fi

if python3 -c "import PyQt6; print('✅ PyQt6 OK')" 2>/dev/null; then
    :
elif python3 -c "import PyQt5; print('✅ PyQt5 OK')" 2>/dev/null; then
    echo "⚠️  Using PyQt5 (fallback)"
fi

echo ""
echo "💡 Next steps:"
echo "   1. Reboot: sudo reboot"
echo "   2. Run: camera-tester"
echo ""
echo "✅ Ready for camera testing!"