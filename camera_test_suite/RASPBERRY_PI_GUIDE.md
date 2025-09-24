# USB Camera Tester - Raspberry Pi 3B Guide

## Critical Information for Pi Users

### ⚠️ Installation Methods (Choose One)

| Method | Time | Pros | Cons |
|--------|------|------|------|
| **System Packages** ✅ | 5 minutes | Fast, reliable, no compilation | May have older versions |
| **Fast Install** | 15-30 minutes | Newer packages, some pip | Some compilation risk |
| **Full Install** ❌ | 4-6 hours | Latest versions | Often fails, overheats Pi |

### Recommended Installation (Pi 3B)

```bash
# 1. System packages only (RECOMMENDED)
sudo ./install_pi_system_only.sh

# 2. If that fails, try manual
sudo apt update
sudo apt install -y python3 python3-numpy python3-opencv python3-pyqt6 python3-reportlab v4l-utils
python3 main_pyqt6.py
```

## Common Pi 3B Issues & Solutions

### Issue: "Command not found"
**Cause:** Files transferred from Windows/Mac have wrong line endings
**Solution:**
```bash
sudo apt install dos2unix
dos2unix *.sh *.py
chmod +x *.sh *.py
```

### Issue: OpenCV compilation hangs
**Cause:** Pi 3B has insufficient RAM (1GB) for compilation
**Solutions:**
```bash
# Option 1: Use system packages (recommended)
sudo apt install python3-opencv

# Option 2: Increase swap (risky - may kill SD card)
sudo dphys-swapfile swapoff
echo "CONF_SWAPSIZE=2048" | sudo tee -a /etc/dphys-swapfile
sudo dphys-swapfile setup && sudo dphys-swapfile swapon
```

### Issue: "Permission denied" on camera
**Solution:**
```bash
sudo usermod -a -G video $USER
newgrp video  # Apply immediately without logout
```

### Issue: Pi overheats during installation
**Solutions:**
```bash
# Check temperature
vcgencmd measure_temp

# Add cooling or use system packages
sudo ./install_pi_system_only.sh
```

## Pi-Specific Features

### V4L2 Camera Controls
Unlike macOS, Linux gives you **full camera control**:
- Brightness, contrast, saturation adjustment
- Auto-focus and auto-exposure controls
- Power line frequency optimization (50Hz/60Hz)
- Professional photo capture at 4000×3000

### Performance Optimization
```bash
# GPU memory for cameras
echo "gpu_mem=128" | sudo tee -a /boot/config.txt

# Enable camera interface
sudo raspi-config  # Interface Options > Camera > Enable

# Reboot to apply
sudo reboot
```

## Testing Your Installation

### Quick Test
```bash
# Test Python modules
python3 -c "import numpy, cv2, PyQt6; print('✅ All modules working')"

# Test camera detection
v4l2-ctl --list-devices

# Test USB cameras
lsusb | grep -i camera
```

### Full Diagnostic
```bash
./camera_diagnostics_linux.sh
```

## File Structure After Installation

```
/opt/usb-camera-tester/  (or ~/usb-camera-tester/)
├── main_pyqt6.py           # Main GUI application
├── v4l2_settings.py        # V4L2 camera controls
├── launch_pi.sh            # Pi launcher script
├── run_camera_tester.sh    # Simple launcher
├── test_v4l2_linux.py      # V4L2 testing
├── camera_diagnostics_linux.sh
└── venv/                   # Virtual environment (optional)
```

## Running the Application

### Method 1: System Command
```bash
pi-camera-tester
```

### Method 2: Direct Script
```bash
/opt/usb-camera-tester/launch_pi.sh
# or
~/usb-camera-tester/run_camera_tester.sh
```

### Method 3: Direct Python
```bash
cd /opt/usb-camera-tester
python3 main_pyqt6.py
```

## Pi 3B Hardware Limitations

| Component | Pi 3B Spec | Impact |
|-----------|-------------|--------|
| RAM | 1GB | Limits compilation, use system packages |
| CPU | 4×ARM Cortex-A53 1.2GHz | Slow compilation, good for runtime |
| USB | USB 2.0 | Fine for most USB cameras |
| GPU | 400MHz VideoCore IV | Good for camera processing with memory split |

## Recommended Workflow

1. **Fresh Pi setup:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Transfer files:** Use `scp` or USB drive

3. **Fix permissions:**
   ```bash
   dos2unix *.sh *.py
   chmod +x *.sh *.py
   ```

4. **Install (system packages only):**
   ```bash
   sudo ./install_pi_system_only.sh
   ```

5. **Test:**
   ```bash
   python3 -c "import cv2, numpy, PyQt6; print('Ready!')"
   ```

6. **Connect camera and run:**
   ```bash
   pi-camera-tester
   ```

## When Things Go Wrong

### Nuclear Option (Fresh Start)
```bash
# Remove any failed installations
sudo rm -rf /opt/usb-camera-tester
rm -rf ~/usb-camera-tester
rm -rf venv

# Clean Python packages
pip3 uninstall opencv-python opencv-python-headless numpy PyQt6 -y

# Start over with system packages
sudo apt install -y python3-opencv python3-numpy python3-pyqt6
```

### Getting Help
```bash
# Generate diagnostic report
./camera_diagnostics_linux.sh

# Check system resources
htop
vcgencmd measure_temp
free -h
```

The key to success on Pi 3B is **avoiding compilation** by using Debian's pre-built packages!