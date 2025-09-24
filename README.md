# USB Camera Tester v4.0 (PyQt6)

🎥 **Professional USB camera hardware testing suite with modern PyQt6 interface**

## Latest Updates (September 2024)
- ✅ **Architecture-aware installer**: Automatic detection of ARM64 vs x86_64 for proper module installation
- ✅ **Version compatibility management**: Ensures numpy, opencv-python, and PyQt6 versions work together
- ✅ **Standalone installer**: Complete one-click solution that installs all dependencies automatically
- ✅ **Enhanced camera permissions**: Multiple launcher options for better macOS camera access
- ✅ **Fix script included**: Quickly resolve any module compatibility issues

## 🚀 Quick Install

### Option 1: Standalone Installer (Recommended for Distribution)
**For colleagues or users without GitHub access:**
1. Download: `🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v4.0.dmg`
2. Double-click the DMG file to mount it
3. Double-click `USB Camera Tester Installer.app`
4. Follow the prompts - all dependencies install automatically!

### Option 2: Build Your Own Installer
```bash
# Clone the repository
git clone https://github.com/YourUsername/usb-camera-tester.git
cd usb-camera-tester

# Build the standalone installer
./create_standalone_installer.sh
```

### Option 3: Manual Install
```bash
# Clone the repository
git clone https://github.com/YourUsername/usb-camera-tester.git
cd usb-camera-tester

# Install dependencies with compatible versions
pip3 install --user "numpy>=1.21.0,<2.3.0" "opencv-python>=4.8.0,<4.10.0" "PyQt6>=6.4.0,<6.8.0"

# Run the application
python3 camera_test_suite/main_pyqt6.py
```

## 🧪 Test Capabilities (with Detailed Parameters)

### Hardware Tests
- **Camera Detection**: Enumerate all connected USB cameras with vendor/product IDs
- **Resolution Testing**: Test all supported resolutions with bandwidth calculations
- **Frame Rate Analysis**: Measure actual vs reported FPS with frame timing statistics
- **USB Bandwidth**: Monitor data transfer rates (MB/s) and USB version detection
- **Power Consumption**: Estimate power usage based on resolution and framerate
- **Latency Testing**: Measure capture delays in milliseconds with percentile analysis
- **Stability Testing**: Long-duration reliability tests with dropout detection
- **Multi-Camera**: Test multiple cameras simultaneously with load balancing
- **Image Quality**: Comprehensive sharpness, noise, and color accuracy analysis
- **Autofocus Testing**: PDAF validation with speed and accuracy measurements

All tests now show comprehensive technical parameters and measurements!

## 📋 System Requirements

- **OS**: macOS 10.14+ / Windows 10+ / Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher (3.13 recommended)
- **Architecture**: ARM64 (Apple Silicon) or x86_64 (Intel) - both supported!
- **RAM**: 4GB minimum (8GB recommended)
- **USB**: USB 2.0 minimum (USB 3.0+ recommended)
- **Dependencies** (automatically installed with correct versions):
  - OpenCV (`opencv-python>=4.8.0,<4.10.0`)
  - NumPy (`numpy>=1.21.0,<2.3.0`)
  - PyQt6 (`PyQt6>=6.4.0,<6.8.0`)

## 🎯 Target Hardware

**WN-L2307k368 48MP Camera Module**

| Specification | Value |
|---------------|-------|
| **Sensor** | Samsung S5KGM1ST ISOCELL GM1 |
| **Resolution** | 8000×6000 (48MP), 4000×3000 (12MP binned) |
| **Pixel Size** | 0.8μm |
| **Optical Format** | 1/2 inch |
| **Interface** | USB 2.0 |
| **Autofocus** | PDAF (Phase Detection) |
| **Frame Rate** | Up to 8fps @ 48MP |
| **Formats** | MJPEG, YUY2 |

## 🛠️ Troubleshooting

### Camera Not Detected
1. Check camera permissions in System Settings
2. Use the launcher script for better permissions: `🎥 Launch USB Camera Tester.command`
3. Try disconnecting and reconnecting the camera
4. Restart the application

### Module Import Errors (numpy/opencv compatibility)
```bash
# Run the fix script (included in the installer)
bash fix_numpy_issue.sh

# Or manually install compatible versions
pip3 install --user --force-reinstall "numpy>=1.21.0,<2.3.0"
pip3 install --user --force-reinstall "opencv-python>=4.8.0,<4.10.0"
pip3 install --user --force-reinstall "PyQt6>=6.4.0,<6.8.0"
```

### Architecture Issues (Apple Silicon)
The installer automatically detects ARM64 vs x86_64 and installs appropriate binaries. If you still have issues:
```bash
# For ARM64 Macs (Apple Silicon)
pip3 install --user --force-reinstall --only-binary=all opencv-python
```

## 📦 Distribution Files

### Standalone Installer (Recommended)
- **File**: `standalone_installer_build/🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v4.0.dmg`
- **Size**: ~3MB
- **Contents**: Complete installer with all dependencies
- **Usage**: Send this single DMG file to colleagues - no GitHub or technical knowledge required!

### Support Scripts
- **fix_numpy_issue.sh**: Fixes module compatibility issues
- **create_standalone_installer.sh**: Builds new installer packages

## 📁 Project Structure

```
kamv2/
├── camera_test_suite/          # Main application source
│   ├── main_pyqt6.py          # Modern PyQt6 application
│   └── icons/                  # Application icons
├── standalone_installer_build/ # Current installer build
│   ├── 🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v4.0.dmg
│   ├── USB Camera Tester Installer.app/
│   └── fix_numpy_issue.sh
├── create_standalone_installer.sh  # Build script
├── fix_numpy_issue.sh          # Module fix script
└── README.md                   # This file
```

## 🔧 Development

### Building from Source
```bash
git clone https://github.com/YourUsername/usb-camera-tester.git
cd usb-camera-tester
./create_standalone_installer.sh  # Build complete installer
```

### Running Directly
```bash
cd camera_test_suite
python3 main_pyqt6.py  # Run PyQt6 version directly
```

## 📈 Version History

### v4.0 (September 2024) - Enhanced Compatibility
- 🔧 **Architecture Detection** - Automatic ARM64/x86_64 module installation
- 📦 **Standalone Installer** - Complete one-click solution with all dependencies
- 🔍 **Version Management** - Compatible module versions for numpy/opencv/PyQt6
- 📊 **Enhanced Test Output** - Detailed technical parameters for all tests
- 🚀 **Multiple Launchers** - Desktop and Applications folder access

### v3.0 - PyQt6 Professional Edition
- 🎨 **Complete GUI Rewrite** - Modern PyQt6 native interface
- 🧵 **Non-blocking UI** - Threaded camera and test operations
- 📏 **Responsive Design** - Resizable panels and professional layout

## 📄 License

Professional hardware testing tool for commercial applications.

## 📞 Support

For technical support or questions, please create an issue on GitHub with detailed information about your testing requirements.

---

**Built for reliable USB camera validation** 📸✨