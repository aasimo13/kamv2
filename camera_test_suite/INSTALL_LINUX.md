# USB Camera Tester - Linux Installation

## Quick Start for Raspberry Pi 3B

The fastest way to get started on Raspberry Pi:

```bash
# For Raspberry Pi 3B (recommended)
sudo ./install_raspberry_pi.sh

# Or for any Linux system
sudo ./install_linux.sh
```

## Installation Files

| File | Purpose | Best For |
|------|---------|----------|
| `install_raspberry_pi.sh` | Pi 3B optimized installer | Raspberry Pi 3B/3B+ |
| `install_linux.sh` | Universal Linux installer | All Linux distributions |
| `launch_linux.sh` | Universal launcher | Manual launches |
| `requirements_linux.txt` | Python dependencies | Manual pip installs |

## What Gets Installed

### System Packages
- **Python 3** with development headers
- **V4L2 utilities** (v4l-utils, uvcdynctrl) for camera control
- **Graphics libraries** (OpenGL, Qt6 support)
- **Build tools** for compiling Python packages
- **Camera tools** (guvcview for testing)

### Python Packages (in virtual environment)
- **numpy** - Optimized for ARM architecture
- **opencv-python-headless** - Computer vision without GUI overhead
- **PyQt6** - Modern GUI framework
- **reportlab** - PDF export functionality

### Application Components
- **main_pyqt6.py** - Main GUI application with dark theme
- **v4l2_settings.py** - Professional V4L2 camera controls
- **Test utilities** - Diagnostic and testing scripts
- **Launchers** - Easy-to-use startup scripts

## Post-Installation

After installation, you'll have:

### Commands
```bash
pi-camera-tester        # Raspberry Pi optimized
usb-camera-tester       # Universal Linux
```

### Desktop Application
Look for "USB Camera Tester (Pi)" in your applications menu

### Test Tools
```bash
# System diagnostics
./camera_diagnostics_linux.sh

# V4L2 testing without GUI
python3 test_v4l2_linux.py

# Pi-specific camera test
./test_camera_pi.sh  # (Pi installer only)
```

## Raspberry Pi Specific Features

### Hardware Optimization
- **GPU memory split** increased to 128MB for camera performance
- **Camera interface** automatically enabled via raspi-config
- **ARM-optimized packages** using piwheels repository
- **Performance tuning** for Pi 3B's quad-core ARM Cortex-A53

### V4L2 Professional Controls
- **WN-L2307k368 camera optimization** with professional settings
- **Regional power line frequency** auto-detection (50Hz/60Hz)
- **High-resolution capture** at 4000×3000 pixels
- **Real-time camera adjustments** (brightness, contrast, saturation, etc.)

### Pi-Specific Diagnostics
- CSI camera detection
- GPU memory monitoring
- Temperature monitoring
- Hardware acceleration status

## Architecture Support

| Architecture | Status | Notes |
|-------------|--------|-------|
| armv7l (Pi 3B) | ✅ Fully optimized | Primary target |
| aarch64 (Pi 4) | ✅ Supported | Full compatibility |
| x86_64 | ✅ Supported | Standard packages |
| i386 | ⚠️ Limited | Basic functionality |

## Dependencies by Distribution

### Debian/Ubuntu/Raspberry Pi OS
```bash
sudo apt install python3 python3-pip v4l-utils
```

### Arch Linux
```bash
sudo pacman -S python python-pip v4l-utils opencv
```

### Fedora/CentOS
```bash
sudo dnf install python3 python3-pip v4l-utils
```

## Troubleshooting

### Common Issues

**Camera not detected:**
```bash
# Check USB connection
lsusb | grep -i camera

# Check V4L2 devices
v4l2-ctl --list-devices

# Check permissions
groups | grep video
```

**Permission denied:**
```bash
# Add to video group
sudo usermod -a -G video $USER

# Log out and back in, or:
newgrp video
```

**GUI won't start over SSH:**
```bash
# Enable X11 forwarding
ssh -X username@hostname

# Or use VNC for better performance
```

**Performance issues on Pi:**
```bash
# Check temperature
vcgencmd measure_temp

# Check GPU memory
vcgencmd get_mem gpu

# Should be 128MB or higher for cameras
```

### Diagnostic Tools

Run comprehensive diagnostics:
```bash
./camera_diagnostics_linux.sh
```

Test V4L2 without GUI:
```bash
python3 test_v4l2_linux.py
```

## Manual Installation

If the automated installers don't work:

```bash
# 1. Install system packages
sudo apt install python3 python3-pip python3-venv v4l-utils

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements_linux.txt

# 4. Add to video group
sudo usermod -a -G video $USER

# 5. Launch
./launch_linux.sh
```

## Performance Optimization

### For Raspberry Pi 3B
- **GPU memory**: 128MB minimum (`gpu_mem=128` in `/boot/config.txt`)
- **Camera interface**: Enabled in raspi-config
- **Swap**: Consider increasing if < 2GB RAM
- **SD card**: Class 10 or better for smooth video

### For Any Linux System
- **V4L2 buffers**: Increase for high-resolution cameras
- **USB bandwidth**: Use USB 3.0 ports when available
- **Process priority**: Run with `nice` for better responsiveness

## Security Notes

- Application runs in user space (no root required after install)
- Virtual environment isolates dependencies
- Camera access via standard video group membership
- No network connections required after installation