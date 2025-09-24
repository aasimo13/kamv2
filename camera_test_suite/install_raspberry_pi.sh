#!/bin/bash
# USB Camera Tester - Raspberry Pi 3B Optimized Installer
# Specifically optimized for ARM7 architecture and Pi hardware

set -e

echo "🍓 USB Camera Tester - Raspberry Pi 3B Installer"
echo "================================================"
echo "Optimized for ARM7 architecture and Pi hardware"
echo ""

# Detect Pi model
PI_MODEL=""
if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "Unknown Pi")
    echo "Detected: $PI_MODEL"
fi

# System info
echo "System Information:"
echo "  Architecture: $(uname -m)"
echo "  Kernel: $(uname -r)"
echo "  Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo ""

# Check if we need sudo
if [ "$EUID" -ne 0 ]; then
    echo "This installer needs sudo privileges for system packages."
    echo "Please run: sudo $0"
    exit 1
fi

# Get the actual user who ran sudo
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"
echo ""

# Update package lists
echo "📦 Updating package lists..."
apt update

# Install system dependencies optimized for Pi
echo "📦 Installing system dependencies (Pi optimized)..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    v4l-utils \
    uvcdynctrl \
    guvcview \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libfontconfig1 \
    libxkbcommon-x11-0 \
    libgtk-3-0 \
    libqt5gui5 \
    libqt5core5a \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    pkg-config \
    cmake \
    build-essential

# Install Pi-specific camera tools
echo "📹 Installing Raspberry Pi camera tools..."
apt install -y \
    raspberrypi-kernel-headers \
    libraspberrypi-dev \
    libraspberrypi-bin

# Set up installation directory
INSTALL_DIR="/opt/usb-camera-tester"
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy source files
echo "📂 Copying application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

# Create Python virtual environment
echo "🐍 Creating optimized Python environment for ARM7..."
cd "$INSTALL_DIR"
python3 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
python -m pip install --upgrade pip wheel setuptools

# Install Python packages optimized for Pi 3B
echo "🔧 Installing Python dependencies (ARM optimized)..."

# Use piwheels for faster ARM installation
echo "[global]" > pip.conf
echo "extra-index-url=https://www.piwheels.org/simple" >> pip.conf

# Install numpy first (critical for Pi performance)
echo "Installing numpy (piwheels ARM binary)..."
pip install numpy==1.26.4 --no-cache-dir

# Install OpenCV (use headless version for Pi)
echo "Installing OpenCV (Pi optimized)..."
pip install opencv-python-headless==4.8.1.78 --no-cache-dir

# Install PyQt6 (may take time on Pi 3B)
echo "Installing PyQt6 (this may take several minutes on Pi 3B)..."
pip install PyQt6==6.6.1 --no-cache-dir

# Install additional packages
echo "Installing additional dependencies..."
pip install reportlab Pillow --no-cache-dir

# Set up GPU memory split for better camera performance
echo "🎮 Optimizing GPU memory for camera performance..."
GPU_MEM=$(vcgencmd get_mem gpu | cut -d= -f2 | cut -dM -f1)
if [ "$GPU_MEM" -lt 128 ]; then
    echo "Increasing GPU memory split to 128MB..."
    echo "gpu_mem=128" >> /boot/config.txt
    echo "⚠️  GPU memory increased. Reboot required for changes to take effect."
fi

# Enable camera interface if not already enabled
echo "📹 Ensuring camera interface is enabled..."
raspi-config nonint do_camera 0

# Create optimized launcher for Pi
echo "🚀 Creating Pi-optimized launcher..."
cat > "$INSTALL_DIR/launch_pi_camera_tester.sh" << 'EOF'
#!/bin/bash
# USB Camera Tester Launcher - Raspberry Pi Optimized

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🍓 USB Camera Tester - Raspberry Pi Edition"
echo "=========================================="

# Check Pi model
if [ -f /proc/device-tree/model ]; then
    echo "Pi Model: $(cat /proc/device-tree/model)"
fi

echo "Architecture: $(uname -m)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo ""

# Check camera permissions
if ! groups | grep -q video; then
    echo "⚠️  Adding user to video group for camera access..."
    sudo usermod -a -G video $USER
    echo "✅ Added to video group. Please log out and back in."
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set Pi-specific environment variables
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORM_PLUGIN_PATH="$SCRIPT_DIR/venv/lib/python*/site-packages/PyQt6/Qt6/plugins"

# Optimize for Pi performance
export OMP_NUM_THREADS=4
export OPENCV_LOG_LEVEL=ERROR

# Check V4L2 tools and cameras
echo "📹 Camera Detection:"
if command -v v4l2-ctl >/dev/null 2>&1; then
    v4l2-ctl --list-devices 2>/dev/null || echo "No V4L2 cameras found"
    echo ""

    # Show available camera formats
    for dev in /dev/video*; do
        if [ -c "$dev" ]; then
            echo "Formats for $dev:"
            v4l2-ctl --device="$dev" --list-formats-ext 2>/dev/null | head -10
            echo ""
        fi
    done
else
    echo "❌ V4L2 tools not available"
fi

# Check for CSI camera
if [ -e /dev/video0 ] && dmesg | grep -q "mmal"; then
    echo "✅ Raspberry Pi CSI camera detected"
fi

# Launch application with Pi optimizations
echo "🚀 Starting USB Camera Tester (Pi optimized)..."
cd "$SCRIPT_DIR"

# Run with lower priority to prevent system lockup on heavy processing
nice -n 5 python main_pyqt6.py "$@"

echo "Application closed."
EOF

chmod +x "$INSTALL_DIR/launch_pi_camera_tester.sh"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
cat > "/usr/share/applications/usb-camera-tester-pi.desktop" << EOF
[Desktop Entry]
Version=1.0
Name=USB Camera Tester (Pi)
Comment=Professional USB Camera Testing - Raspberry Pi Edition
Exec=$INSTALL_DIR/launch_pi_camera_tester.sh
Icon=$INSTALL_DIR/icons/app_icon.png
Terminal=true
Type=Application
Categories=AudioVideo;Photography;
Keywords=camera;usb;test;v4l2;raspberry;pi;
EOF

# Create system command
echo "📟 Creating system command..."
cat > "/usr/local/bin/pi-camera-tester" << EOF
#!/bin/bash
exec "$INSTALL_DIR/launch_pi_camera_tester.sh" "\$@"
EOF
chmod +x "/usr/local/bin/pi-camera-tester"

# Set up user permissions
echo "👤 Setting up user permissions..."
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
usermod -a -G video "$ACTUAL_USER"

# Create quick camera test script
echo "🔧 Creating camera test utility..."
cat > "$INSTALL_DIR/test_camera_pi.sh" << 'EOF'
#!/bin/bash
# Quick camera test for Raspberry Pi

echo "🍓 Pi Camera Quick Test"
echo "====================="

echo "System info:"
echo "  Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
echo "  GPU Memory: $(vcgencmd get_mem gpu)"
echo "  Camera detect: $(vcgencmd get_camera)"
echo ""

echo "V4L2 devices:"
ls -la /dev/video* 2>/dev/null || echo "No video devices found"
echo ""

echo "USB cameras:"
lsusb | grep -i camera || echo "No USB cameras found"
echo ""

echo "V4L2 camera list:"
v4l2-ctl --list-devices 2>/dev/null || echo "V4L2 tools not available"
echo ""

# Test camera capture if available
if [ -c /dev/video0 ]; then
    echo "Testing capture from /dev/video0..."
    timeout 3 v4l2-ctl --device /dev/video0 --stream-mmap --stream-count=1 --stream-to=/tmp/test.raw 2>/dev/null
    if [ $? -eq 0 ] && [ -f /tmp/test.raw ]; then
        echo "✅ Camera capture test successful"
        echo "   Captured $(wc -c < /tmp/test.raw) bytes"
        rm -f /tmp/test.raw
    else
        echo "❌ Camera capture test failed"
    fi
fi
EOF

chmod +x "$INSTALL_DIR/test_camera_pi.sh"

# Set proper permissions
chmod -R 755 "$INSTALL_DIR"

echo ""
echo "🎉 Raspberry Pi Installation Complete!"
echo "====================================="
echo ""
echo "📍 Installation: $INSTALL_DIR"
echo ""
echo "🚀 Launch Options:"
echo "   Command: pi-camera-tester"
echo "   Script: $INSTALL_DIR/launch_pi_camera_tester.sh"
echo "   Desktop: Look for 'USB Camera Tester (Pi)' in menu"
echo ""
echo "🔧 Tools:"
echo "   Camera test: $INSTALL_DIR/test_camera_pi.sh"
echo "   V4L2 list: v4l2-ctl --list-devices"
echo "   USB check: lsusb | grep -i camera"
echo ""
echo "🍓 Pi-Specific Features:"
echo "   • V4L2 professional camera controls"
echo "   • ARM-optimized OpenCV installation"
echo "   • GPU memory optimization (128MB)"
echo "   • Performance-tuned for Pi 3B"
echo "   • CSI camera detection"
echo ""
echo "💡 Post-installation:"
echo "   1. Reboot to apply GPU memory changes"
echo "   2. Log out/in to apply video group membership"
echo "   3. Run: $INSTALL_DIR/test_camera_pi.sh"
echo ""

# Test installation
echo "🧪 Testing installation..."
source "$INSTALL_DIR/venv/bin/activate"
cd "$INSTALL_DIR"

if python -c "import cv2, numpy, PyQt6; print('✅ All modules working on Pi')" 2>/dev/null; then
    echo "✅ Installation test passed!"
else
    echo "❌ Installation test failed. Please check the logs above."
fi

echo ""
echo "🎯 Ready to test USB cameras on your Raspberry Pi!"
echo "   Reboot recommended for optimal performance."