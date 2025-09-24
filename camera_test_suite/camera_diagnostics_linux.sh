#!/bin/bash
# Camera Diagnostics for Linux - Comprehensive system check
# Useful for troubleshooting camera issues on Raspberry Pi and other Linux systems

echo "🔧 Linux Camera Diagnostics"
echo "==========================="
echo ""

# System information
echo "📋 System Information"
echo "--------------------"
echo "Hostname: $(hostname)"
echo "OS: $(uname -s -r)"
echo "Architecture: $(uname -m)"
echo "Distribution: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2 2>/dev/null || echo "Unknown")"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}' || echo "Unknown")"
echo "Uptime: $(uptime | cut -d',' -f1 | cut -d' ' -f4-)"

# Check if on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "Pi Model: $(cat /proc/device-tree/model)"
    echo "GPU Memory: $(vcgencmd get_mem gpu 2>/dev/null || echo "Unknown")"
    echo "Camera detect: $(vcgencmd get_camera 2>/dev/null || echo "N/A")"
fi

echo ""

# User and permissions
echo "👤 User and Permissions"
echo "----------------------"
echo "Current user: $USER"
echo "User groups: $(groups | tr ' ' '\n' | sort | tr '\n' ' ')"

if groups | grep -q video; then
    echo "✅ User is in video group (camera access OK)"
else
    echo "❌ User NOT in video group (camera access limited)"
    echo "   Fix: sudo usermod -a -G video $USER"
    echo "   Then log out and back in"
fi

echo ""

# USB devices and cameras
echo "🔌 USB Devices"
echo "-------------"
if command -v lsusb >/dev/null 2>&1; then
    echo "All USB devices:"
    lsusb | while read -r line; do
        echo "  $line"
    done

    echo ""
    echo "USB cameras detected:"
    if lsusb | grep -i -E "(camera|webcam|usb.*video)" >/dev/null; then
        lsusb | grep -i -E "(camera|webcam|usb.*video)" | while read -r line; do
            echo "  ✅ $line"
        done
    else
        echo "  ❌ No USB cameras found"
    fi
else
    echo "❌ lsusb not available"
fi

echo ""

# V4L2 devices
echo "📹 V4L2 Video Devices"
echo "--------------------"
if ls /dev/video* >/dev/null 2>&1; then
    echo "Video device files:"
    ls -la /dev/video* | while read -r line; do
        echo "  $line"
    done

    # Check permissions on video devices
    echo ""
    echo "Video device permissions:"
    for device in /dev/video*; do
        if [ -c "$device" ]; then
            perms=$(ls -la "$device" | awk '{print $1, $3, $4}')
            echo "  $device: $perms"

            # Check if device is accessible
            if [ -r "$device" ] && [ -w "$device" ]; then
                echo "    ✅ Read/Write access OK"
            else
                echo "    ❌ Access denied (check permissions)"
            fi
        fi
    done
else
    echo "❌ No /dev/video* devices found"
fi

echo ""

# V4L2 tools and capabilities
echo "🛠️  V4L2 Tools"
echo "------------"
if command -v v4l2-ctl >/dev/null 2>&1; then
    echo "✅ v4l2-ctl available: $(which v4l2-ctl)"

    echo ""
    echo "V4L2 device list:"
    v4l2-ctl --list-devices 2>/dev/null | while IFS= read -r line; do
        echo "  $line"
    done

    echo ""
    echo "Testing each video device:"
    for device in /dev/video*; do
        if [ -c "$device" ]; then
            echo ""
            echo "  📸 Testing $device:"

            # Basic device info
            if v4l2-ctl --device="$device" --info >/dev/null 2>&1; then
                echo "    ✅ Device responds to v4l2-ctl"

                # Get device info
                driver_info=$(v4l2-ctl --device="$device" --info 2>/dev/null | head -5)
                echo "    Driver info:"
                echo "$driver_info" | while IFS= read -r line; do
                    echo "      $line"
                done

                # List formats (first few)
                echo "    Supported formats:"
                v4l2-ctl --device="$device" --list-formats 2>/dev/null | head -10 | while IFS= read -r line; do
                    echo "      $line"
                done

            else
                echo "    ❌ Device does not respond to v4l2-ctl"
            fi
        fi
    done

else
    echo "❌ v4l2-ctl not found"
    echo "   Install with: sudo apt install v4l-utils"
    echo "   Or: sudo pacman -S v4l-utils"
    echo "   Or: sudo dnf install v4l-utils"
fi

echo ""

# Python and dependencies
echo "🐍 Python Environment"
echo "--------------------"
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Python 3: $(python3 --version) at $(which python3)"

    echo ""
    echo "Testing Python modules:"

    # Test numpy
    if python3 -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
        :  # Success message already printed
    else
        echo "❌ numpy not available"
        echo "   Install: pip3 install numpy"
    fi

    # Test OpenCV
    if python3 -c "import cv2; print('✅ OpenCV version:', cv2.__version__)" 2>/dev/null; then
        :  # Success message already printed
    else
        echo "❌ OpenCV not available"
        echo "   Install: pip3 install opencv-python"
        echo "   Or for Pi: pip3 install opencv-python-headless"
    fi

    # Test PyQt6
    if python3 -c "import PyQt6; from PyQt6.QtCore import QT_VERSION_STR; print('✅ PyQt6 version:', QT_VERSION_STR)" 2>/dev/null; then
        :  # Success message already printed
    else
        echo "❌ PyQt6 not available"
        echo "   Install: pip3 install PyQt6"
    fi

    # Test reportlab
    if python3 -c "import reportlab; print('✅ reportlab version:', reportlab.Version)" 2>/dev/null; then
        :  # Success message already printed
    else
        echo "❌ reportlab not available (PDF export won't work)"
        echo "   Install: pip3 install reportlab"
    fi

else
    echo "❌ Python 3 not found"
    echo "   Install: sudo apt install python3"
fi

echo ""

# Camera testing with simple tools
echo "🎥 Camera Testing"
echo "---------------"

if command -v fswebcam >/dev/null 2>&1; then
    echo "✅ fswebcam available for testing"

    for device in /dev/video*; do
        if [ -c "$device" ]; then
            echo "  Testing $device with fswebcam..."
            if timeout 5 fswebcam -d "$device" --no-banner -r 320x240 /tmp/test_capture.jpg >/dev/null 2>&1; then
                if [ -f /tmp/test_capture.jpg ] && [ -s /tmp/test_capture.jpg ]; then
                    echo "    ✅ Successfully captured image ($(wc -c < /tmp/test_capture.jpg) bytes)"
                    rm -f /tmp/test_capture.jpg
                else
                    echo "    ❌ Capture created empty file"
                fi
            else
                echo "    ❌ Capture failed or timed out"
            fi
        fi
    done
else
    echo "ℹ️  fswebcam not available (install with: sudo apt install fswebcam)"
fi

# Test with ffmpeg if available
if command -v ffmpeg >/dev/null 2>&1; then
    echo ""
    echo "📺 Testing with ffmpeg:"

    for device in /dev/video*; do
        if [ -c "$device" ]; then
            echo "  Testing $device formats with ffmpeg..."
            if timeout 3 ffmpeg -f v4l2 -list_formats all -i "$device" 2>&1 | grep -q "Compressed\|Raw"; then
                echo "    ✅ Device supports video formats"
                # Show first few formats
                ffmpeg -f v4l2 -list_formats all -i "$device" 2>&1 | grep -E "(Compressed|Raw)" | head -3 | while read -r line; do
                    echo "      $line"
                done
            else
                echo "    ❌ No supported formats or device error"
            fi
        fi
    done
fi

echo ""

# System resources and performance
echo "⚡ System Resources"
echo "-----------------"
echo "CPU usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 || echo "Unknown")% busy"
echo "Memory usage: $(free | awk '/^Mem:/ {printf("%.1f%%", $3/$2 * 100.0)}' || echo "Unknown")"
echo "Disk usage: $(df / | tail -1 | awk '{print $5}' || echo "Unknown") of root partition"

# Temperature on Pi
if command -v vcgencmd >/dev/null 2>&1; then
    temp=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2)
    echo "Pi temperature: ${temp:-Unknown}"
fi

echo ""

# Display environment
echo "🖥️  Display Environment"
echo "---------------------"
if [ -n "$DISPLAY" ]; then
    echo "✅ X11 display: $DISPLAY"
elif [ -n "$WAYLAND_DISPLAY" ]; then
    echo "✅ Wayland display: $WAYLAND_DISPLAY"
else
    echo "❌ No display environment detected"
    echo "   GUI applications may not work"
fi

# Check if running over SSH
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "⚠️  Connected via SSH - X11 forwarding may be needed for GUI"
    if [ -n "$DISPLAY" ]; then
        echo "   X11 forwarding appears to be active"
    else
        echo "   Enable with: ssh -X username@hostname"
    fi
fi

echo ""

# Final recommendations
echo "💡 Recommendations"
echo "-----------------"

# Check critical issues
issues=0

if ! groups | grep -q video; then
    echo "❌ Add user to video group: sudo usermod -a -G video $USER"
    ((issues++))
fi

if ! command -v v4l2-ctl >/dev/null 2>&1; then
    echo "❌ Install V4L2 tools: sudo apt install v4l-utils"
    ((issues++))
fi

if ! python3 -c "import cv2" >/dev/null 2>&1; then
    echo "❌ Install OpenCV: pip3 install opencv-python-headless"
    ((issues++))
fi

if ! python3 -c "import PyQt6" >/dev/null 2>&1; then
    echo "❌ Install PyQt6: pip3 install PyQt6"
    ((issues++))
fi

if [ "$issues" -eq 0 ]; then
    echo "✅ System looks good for USB camera testing!"

    # Suggest next steps
    echo ""
    echo "🚀 Ready to run USB Camera Tester:"
    echo "   • GUI mode: ./launch_linux.sh"
    echo "   • Test V4L2: python3 test_v4l2_linux.py"
    echo "   • System install: sudo ./install_linux.sh"
else
    echo ""
    echo "⚠️  Found $issues issue(s) that should be resolved first."
fi

echo ""
echo "📊 Diagnostic complete!"
echo "Report saved to: /tmp/camera_diagnostics_$(date +%Y%m%d_%H%M%S).log"

# Save diagnostic output to log file
{
    echo "Camera Diagnostics Report"
    echo "Generated: $(date)"
    echo "========================="
    echo ""
    bash "$0" 2>&1
} > "/tmp/camera_diagnostics_$(date +%Y%m%d_%H%M%S).log" 2>/dev/null || true