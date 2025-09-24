# USB Camera Tester - Linux Installation Guide

## Raspberry Pi 3B Setup

This professional USB camera testing suite is optimized for Linux systems, particularly Raspberry Pi 3B, with full V4L2 support for advanced camera controls.

### Features on Linux

- **V4L2 Integration**: Advanced camera controls and settings optimization
- **Professional Photo Capture**: High-resolution 4000×3000 image capture
- **Regional Optimization**: Auto-detection of power line frequency (50Hz/60Hz)
- **Hardware Verification**: Automatic camera model detection
- **PDF Export**: Professional test reports with statistics
- **Dark Theme UI**: High-contrast interface optimized for readability

### Quick Installation

**⚠️ IMPORTANT for Raspberry Pi:** Use system packages to avoid long compilation times!

```bash
# Raspberry Pi 3B (RECOMMENDED - uses system packages, 5 minutes)
chmod +x install_pi_system_only.sh
sudo ./install_pi_system_only.sh

# Alternative Pi installer (uses some pip packages)
chmod +x install_pi_fast.sh
sudo ./install_pi_fast.sh

# Generic Linux (may compile packages - can take hours on Pi)
chmod +x install_linux.sh
sudo ./install_linux.sh
```

**If files aren't executable after transfer:**
```bash
# Fix line endings and permissions
sudo apt install dos2unix
dos2unix *.sh *.py
chmod +x *.sh *.py
```

### Manual Installation

#### 1. System Dependencies (Raspberry Pi/Debian)

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    v4l-utils uvcdynctrl \
    libgl1-mesa-glx libglib2.0-0 \
    libxcb-xinerama0 libfontconfig1 \
    libxkbcommon-x11-0 libgtk-3-0 \
    libjpeg-dev libpng-dev cmake build-essential
```

#### 2. Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements_linux.txt
```

#### 3. Camera Permissions

```bash
# Add user to video group for camera access
sudo usermod -a -G video $USER

# Log out and back in, or run:
newgrp video
```

### Running the Application

#### GUI Mode
```bash
./launch_camera_tester.sh
```

#### Command Line
```bash
usb-camera-tester
```

#### From Applications Menu
Look for "USB Camera Tester" in your desktop environment's applications menu.

### V4L2 Camera Controls

The Linux version includes professional camera controls:

#### Optimal Settings for WN-L2307k368 Camera
- **Brightness**: 15
- **Contrast**: 34
- **Saturation**: 32
- **Gamma**: 32
- **Auto White Balance**: Enabled
- **Auto Exposure**: Enabled
- **Auto Focus**: Enabled
- **Power Line Frequency**: Regional auto-detection

#### Camera Control Commands
```bash
# List cameras
v4l2-ctl --list-devices

# View current settings
v4l2-ctl -d /dev/video0 --all

# Apply optimal settings (done automatically by app)
v4l2-ctl -d /dev/video0 --set-ctrl=brightness=15,contrast=34,saturation=32
```

### Raspberry Pi Specific Setup

#### 1. Enable Camera Support
```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
sudo reboot
```

#### 2. Check Camera Connection
```bash
# List USB devices
lsusb

# Check V4L2 cameras
v4l2-ctl --list-devices

# Test camera capture
v4l2-ctl --device /dev/video0 --stream-mmap --stream-count=1 --stream-to=test.raw
```

#### 3. Performance Optimization
```bash
# Increase GPU memory split
sudo raspi-config
# Advanced Options > Memory Split > 128 or 256

# Enable hardware acceleration
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt
```

### Troubleshooting

#### Installation Issues on Raspberry Pi

**OpenCV compilation stuck/failed:**
```bash
# Kill the installation
Ctrl+C

# Use system packages instead (much faster)
sudo apt install python3-opencv python3-numpy python3-pyqt6
python3 -c "import cv2, numpy, PyQt6; print('All working!')"
```

**"Command not found" errors:**
```bash
# Files may need Unix line endings
sudo apt install dos2unix
dos2unix *.sh *.py
chmod +x *.sh *.py

# Or run with bash explicitly
sudo bash install_pi_system_only.sh
```

**Pi runs out of memory during compilation:**
```bash
# Use system packages only - no compilation needed
sudo ./install_pi_system_only.sh

# Or increase swap (temporary fix)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### Camera Not Detected
```bash
# Check USB connection
lsusb | grep -i camera

# Check V4L2 devices
ls -la /dev/video*

# Test with simple capture
ffmpeg -f v4l2 -list_formats all -i /dev/video0
```

#### Permission Issues
```bash
# Check video group membership
groups | grep video

# Fix permissions
sudo chmod 666 /dev/video*

# Add to video group permanently
sudo usermod -a -G video $USER
newgrp video  # Apply immediately
```

#### Python Module Issues
```bash
# Test system packages first
python3 -c "import cv2, numpy, PyQt6; print('All modules OK')"

# If using virtual environment
source venv/bin/activate
python -c "import cv2, numpy, PyQt6; print('All modules OK')"

# Reinstall problematic modules (last resort)
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless --no-cache-dir
```

### Advanced Configuration

#### Custom V4L2 Settings
Create `~/.camera_settings.conf`:
```ini
[camera]
brightness=15
contrast=34
saturation=32
gamma=32
power_line_frequency=2  # 0=auto, 1=50Hz, 2=60Hz
```

#### High-Resolution Capture
The application supports professional photo capture at:
- **Resolution**: 4000×3000 pixels
- **Format**: JPEG with automatic 3:2 aspect ratio cropping
- **Quality**: Professional photobooth grade

### System Requirements

#### Minimum (Raspberry Pi 3B)
- **CPU**: ARM Cortex-A53 quad-core 1.2GHz
- **RAM**: 1GB
- **Storage**: 8GB SD card (Class 10 recommended)
- **USB**: USB 2.0 for camera connection

#### Recommended
- **RAM**: 2GB+ (Pi 4B recommended)
- **Storage**: 16GB+ SD card (U1/Class 10)
- **Display**: 1024×768 minimum resolution
- **USB**: USB 3.0 for higher bandwidth cameras

### File Structure

```
usb-camera-tester/
├── main_pyqt6.py              # Main GUI application
├── v4l2_settings.py           # V4L2 camera controls
├── launch_camera_tester.sh    # Launcher script
├── requirements_linux.txt     # Python dependencies
├── icons/                     # Application icons
├── test_images/              # Sample test images
└── venv/                     # Python virtual environment
```

### Performance Notes

- **OpenCV**: Uses `opencv-python-headless` for better ARM performance
- **Memory**: Virtual environment isolates dependencies
- **V4L2**: Direct hardware access for optimal camera control
- **GUI**: PyQt6 with hardware acceleration when available

### Support

For Raspberry Pi specific issues:
- Check `/var/log/syslog` for hardware messages
- Monitor `dmesg` for USB camera detection
- Use `htop` to monitor CPU/memory usage during testing