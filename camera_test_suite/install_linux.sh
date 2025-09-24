#!/bin/bash
# USB Camera Tester - Linux Installer for Raspberry Pi
# Optimized for Raspberry Pi 3B with ARM architecture

set -e

echo "🎥 USB Camera Tester - Linux Installer"
echo "======================================="
echo "Optimized for Raspberry Pi 3B and ARM Architecture"
echo ""

# Detect system information
ARCH=$(uname -m)
DISTRO=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
fi

echo "System Information:"
echo "  Architecture: $ARCH"
echo "  Distribution: $DISTRO"
echo "  Kernel: $(uname -r)"
echo ""

# Check if running as root for system packages
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root - will install system packages"
    INSTALL_SYSTEM=true
else
    echo "ℹ️  Running as user - will install user packages only"
    INSTALL_SYSTEM=false
fi

# Create installation directory
INSTALL_DIR="/opt/usb-camera-tester"
USER_INSTALL_DIR="$HOME/usb-camera-tester"

if [ "$INSTALL_SYSTEM" = true ]; then
    TARGET_DIR="$INSTALL_DIR"
    echo "Installing to system directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
else
    TARGET_DIR="$USER_INSTALL_DIR"
    echo "Installing to user directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# Update system packages (if running as root)
if [ "$INSTALL_SYSTEM" = true ]; then
    echo "📦 Updating system packages..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update

        # Install system dependencies
        echo "Installing system dependencies..."
        apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            v4l-utils \
            uvcdynctrl \
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
            libtiff-dev \
            libavcodec-dev \
            libavformat-dev \
            libswscale-dev \
            libv4l-dev \
            cmake \
            pkg-config \
            build-essential

    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        pacman -Syu --noconfirm
        pacman -S --noconfirm python python-pip v4l-utils opencv python-pyqt6
    else
        echo "⚠️  Unknown package manager. Please install Python 3, pip, and v4l-utils manually."
    fi
fi

# Find Python command
PYTHON_CMD=""
for python_candidate in python3.11 python3.10 python3.9 python3; do
    if command -v "$python_candidate" >/dev/null 2>&1; then
        PYTHON_CMD="$python_candidate"
        echo "✅ Found Python: $python_candidate"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "Python version: $($PYTHON_CMD --version)"
echo ""

# Create virtual environment for better isolation
echo "🐍 Creating Python virtual environment..."
"$PYTHON_CMD" -m venv "$TARGET_DIR/venv"
source "$TARGET_DIR/venv/bin/activate"

# Upgrade pip in virtual environment
echo "Upgrading pip..."
python -m pip install --upgrade pip wheel setuptools

echo ""
echo "📦 Installing Python dependencies for ARM/Linux..."

# Install dependencies with ARM-specific considerations
echo "Installing numpy (ARM-optimized)..."
if [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "aarch64" ]; then
    # For ARM, install specific versions that work well
    pip install "numpy>=1.21.0,<2.0.0" --no-cache-dir
else
    pip install "numpy<2.0.0" --no-cache-dir
fi

echo "Installing OpenCV for Linux..."
# For Raspberry Pi, use the lighter opencv-python-headless
if [ "$ARCH" = "armv7l" ]; then
    # Raspberry Pi 3B specific
    pip install opencv-python-headless --no-cache-dir
else
    pip install opencv-python --no-cache-dir
fi

echo "Installing PyQt6..."
pip install PyQt6 --no-cache-dir

echo "Installing additional dependencies..."
pip install reportlab --no-cache-dir  # For PDF export

echo ""
echo "📁 Copying application files..."

# Copy the application files
cp -r "$(dirname "$0")"/* "$TARGET_DIR/"

# Create launcher script
echo "🚀 Creating launcher scripts..."

# Create system launcher script
cat > "$TARGET_DIR/launch_camera_tester.sh" << 'EOF'
#!/bin/bash
# USB Camera Tester Launcher for Linux

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎥 USB Camera Tester - Linux"
echo "==========================="
echo ""

# Check for camera permissions
if ! groups | grep -q video; then
    echo "⚠️  Warning: User not in 'video' group. Camera access may be limited."
    echo "   To fix: sudo usermod -a -G video $USER"
    echo "   Then log out and back in."
    echo ""
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set environment variables for better camera access
export QT_QPA_PLATFORM_PLUGIN_PATH="$SCRIPT_DIR/venv/lib/python*/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM=xcb

# Check V4L2 tools
if command -v v4l2-ctl >/dev/null 2>&1; then
    echo "✅ V4L2 tools available - Full camera control enabled"

    # List available cameras
    echo ""
    echo "📹 Detecting cameras..."
    v4l2-ctl --list-devices 2>/dev/null | head -20 || echo "No V4L2 cameras detected"
    echo ""
else
    echo "⚠️  V4L2 tools not found. Install with: sudo apt install v4l-utils"
    echo ""
fi

# Launch the application
echo "Starting USB Camera Tester..."
cd "$SCRIPT_DIR"
python main_pyqt6.py "$@"

echo "Application closed."
EOF

chmod +x "$TARGET_DIR/launch_camera_tester.sh"

# Create desktop entry for GUI environments
if [ "$INSTALL_SYSTEM" = true ]; then
    DESKTOP_FILE="/usr/share/applications/usb-camera-tester.desktop"
else
    mkdir -p "$HOME/.local/share/applications"
    DESKTOP_FILE="$HOME/.local/share/applications/usb-camera-tester.desktop"
fi

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Name=USB Camera Tester
Comment=Professional USB Camera Testing Suite with V4L2 Support
Exec=$TARGET_DIR/launch_camera_tester.sh
Icon=$TARGET_DIR/icons/app_icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Photography;
Keywords=camera;usb;test;v4l2;
EOF

# Create command line launcher
if [ "$INSTALL_SYSTEM" = true ]; then
    cat > "/usr/local/bin/usb-camera-tester" << EOF
#!/bin/bash
exec "$TARGET_DIR/launch_camera_tester.sh" "\$@"
EOF
    chmod +x "/usr/local/bin/usb-camera-tester"
    echo "✅ System command 'usb-camera-tester' created"
else
    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/usb-camera-tester" << EOF
#!/bin/bash
exec "$TARGET_DIR/launch_camera_tester.sh" "\$@"
EOF
    chmod +x "$HOME/.local/bin/usb-camera-tester"
    echo "✅ User command 'usb-camera-tester' created"
    echo "   Add $HOME/.local/bin to PATH if not already there"
fi

# Set proper permissions
chmod -R 755 "$TARGET_DIR"

echo ""
echo "✅ Installation Complete!"
echo "========================"
echo ""
echo "📍 Installation location: $TARGET_DIR"
echo ""
echo "🚀 How to run:"
echo "   GUI: $TARGET_DIR/launch_camera_tester.sh"
echo "   Command: usb-camera-tester"
if [ "$INSTALL_SYSTEM" = false ]; then
    echo "   Desktop: Look for 'USB Camera Tester' in applications menu"
fi
echo ""
echo "🎛️  V4L2 Features (Linux exclusive):"
echo "   • Advanced camera controls"
echo "   • Professional photo capture (4000x3000)"
echo "   • Regional power line frequency optimization"
echo "   • Camera model verification"
echo ""
echo "💡 Tips for Raspberry Pi:"
echo "   • Make sure camera is enabled: sudo raspi-config"
echo "   • Add user to video group: sudo usermod -a -G video $USER"
echo "   • For USB cameras: lsusb to check connection"
echo "   • Check camera: v4l2-ctl --list-devices"
echo ""

# Test the installation
echo "🔧 Testing installation..."
source "$TARGET_DIR/venv/bin/activate"
cd "$TARGET_DIR"

if python -c "import cv2, numpy, PyQt6; print('✅ All modules imported successfully')" 2>/dev/null; then
    echo "✅ Installation test passed!"
else
    echo "❌ Installation test failed. Check dependencies."
    exit 1
fi

echo ""
echo "🎉 Ready to test your USB cameras with professional Linux tools!"