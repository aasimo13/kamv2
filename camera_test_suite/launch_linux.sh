#!/bin/bash
# USB Camera Tester - Universal Linux Launcher
# Compatible with all Linux distributions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎥 USB Camera Tester - Linux Edition"
echo "===================================="
echo ""

# System information
echo "System Info:"
echo "  OS: $(uname -s -r)"
echo "  Architecture: $(uname -m)"
echo "  Distribution: $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown")"
echo ""

# Check if we're in the virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check camera permissions
echo "👤 Checking permissions..."
if groups | grep -q video; then
    echo "✅ User in video group - camera access OK"
else
    echo "❌ User not in video group. Run: sudo usermod -a -G video $USER"
    echo "   Then log out and back in."
fi

# Check V4L2 tools availability
echo ""
echo "🔧 Checking V4L2 tools..."
if command -v v4l2-ctl >/dev/null 2>&1; then
    echo "✅ V4L2 tools available"

    # List cameras
    echo ""
    echo "📹 Available cameras:"
    v4l2-ctl --list-devices 2>/dev/null | while IFS= read -r line; do
        echo "   $line"
    done

else
    echo "❌ V4L2 tools not found"
    echo "   Install with: sudo apt install v4l-utils"
    echo "   Or: sudo pacman -S v4l-utils"
    echo "   Or: sudo dnf install v4l-utils"
fi

# Check USB cameras
echo ""
echo "🔌 USB camera detection:"
if lsusb | grep -i camera >/dev/null 2>&1; then
    lsusb | grep -i camera | while IFS= read -r line; do
        echo "   ✅ $line"
    done
else
    echo "   ❌ No USB cameras detected"
fi

# Set environment variables for better Qt performance
export QT_QPA_PLATFORM_PLUGIN_PATH="$SCRIPT_DIR/venv/lib/python*/site-packages/PyQt6/Qt6/plugins"

# Try different Qt platforms based on environment
if [ -n "$DISPLAY" ]; then
    export QT_QPA_PLATFORM=xcb
elif [ -n "$WAYLAND_DISPLAY" ]; then
    export QT_QPA_PLATFORM=wayland
else
    echo "⚠️  No display environment detected. GUI may not work."
fi

# Additional optimizations
export OPENCV_LOG_LEVEL=ERROR
export PYTHONUNBUFFERED=1

# Change to application directory
cd "$SCRIPT_DIR"

echo ""
echo "🚀 Starting USB Camera Tester..."
echo ""

# Launch the application with error handling
if ! python main_pyqt6.py "$@"; then
    echo ""
    echo "❌ Application failed to start. Common issues:"
    echo ""
    echo "1. Missing dependencies:"
    echo "   pip install -r requirements_linux.txt"
    echo ""
    echo "2. Camera permissions:"
    echo "   sudo usermod -a -G video $USER"
    echo ""
    echo "3. Display issues:"
    echo "   export DISPLAY=:0"
    echo "   xhost +local:"
    echo ""
    echo "4. Check system logs:"
    echo "   journalctl -f"
    echo "   dmesg | grep -i camera"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "✅ Application closed successfully."