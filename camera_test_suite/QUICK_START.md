# USB Camera Tester - Quick Start Guide

## 🚀 ONE-CLICK Installation (Recommended)

**For ANY Raspberry Pi (3B, 4, 5):**

1. **Transfer files to Pi:**
   ```bash
   # From your computer:
   scp -r camera_test_suite pi@your-pi-ip:~/
   ```

2. **Run one-click installer:**
   ```bash
   # On the Pi:
   cd camera_test_suite
   chmod +x pi_one_click_setup.sh
   ./pi_one_click_setup.sh
   ```

3. **Launch the app:**
   - **Desktop Icon**: Double-click "USB Camera Tester" on desktop
   - **File Manager**: Go to `~/camera-tester/` → double-click `RUN_CAMERA_TESTER.sh`
   - **Terminal**: Type `camera-tester`

## ✅ What You Get

After the one-click installation:
- ✅ **Desktop icon** for easy launching
- ✅ **Auto-detects** your Pi model and optimizes accordingly
- ✅ **PyQt5/PyQt6** compatibility handled automatically
- ✅ **V4L2 camera controls** for professional settings
- ✅ **PDF export** functionality
- ✅ **Dark theme** for better readability

## 🎥 Testing Your Camera

1. **Connect your USB camera**
2. **Launch the app** (desktop icon or `camera-tester`)
3. **Click "Auto-Detect Camera"**
4. **Run tests** to verify all functions work
5. **Use V4L2 settings** to optimize camera (Linux exclusive!)

## 📋 Quick Troubleshooting

**If installation fails:**
```bash
# Fix file permissions
sudo apt install dos2unix
dos2unix *.sh *.py
chmod +x *.sh *.py
./pi_one_click_setup.sh
```

**If app won't start:**
```bash
# Check what's installed
python3 -c "import cv2, numpy; print('Core modules OK')"

# Run directly
cd ~/camera-tester
python3 main_pyqt6.py  # Auto-adapts to available Qt version
```

**If no cameras detected:**
```bash
# Check USB connection
lsusb | grep -i camera

# Check V4L2 devices
v4l2-ctl --list-devices

# Check permissions
groups | grep video  # Should show 'video' group
```

## 🔧 Advanced Features

### V4L2 Professional Controls (Linux Only)
- **Brightness, Contrast, Saturation** adjustment
- **Auto-focus and Auto-exposure** controls
- **Power line frequency** optimization (50Hz/60Hz)
- **High-resolution capture** at 4000×3000 pixels

### Testing Tools
```bash
# Test V4L2 functionality
python3 test_v4l2_linux.py

# System diagnostics
./camera_diagnostics_linux.sh

# Quick camera test
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK!' if cap.isOpened() else 'No camera')"
```

## 📊 Performance by Pi Model

| Pi Model | Installation Time | Max Resolution | Expected FPS |
|----------|------------------|----------------|--------------|
| **Pi 3B** | 5 minutes | 1920×1080 | 15-30 fps |
| **Pi 4** | 5 minutes | 4000×3000 | 30-60 fps |
| **Pi 5** | 5 minutes | 4000×3000 | 60+ fps |

## 🆘 Need Help?

1. **Check the logs:** Installation shows detailed error messages
2. **Run diagnostics:** `./camera_diagnostics_linux.sh`
3. **Test components:** `~/camera-tester/test_setup.py`
4. **Check documentation:** `README_LINUX.md` for detailed troubleshooting

## 🎯 Key Advantages of One-Click Installer

- **No compilation** needed (uses system packages)
- **Auto-detection** of Pi model and capabilities
- **Desktop integration** with icon and shortcuts
- **PyQt compatibility** handled automatically
- **Comprehensive testing** tools included
- **Professional V4L2 controls** ready to use

The one-click installer eliminates all the common issues (compilation failures, module conflicts, permission problems) and gets you up and running in minutes!