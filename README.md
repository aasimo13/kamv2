# USB Camera Tester v4.0 (PyQt6)

🎥 **Professional USB camera hardware testing suite with modern PyQt6 interface**

## Latest Updates (September 2024)
- ✅ **Architecture-aware installer**: Automatic detection of ARM64 vs x86_64 for proper module installation
- ✅ **Version compatibility management**: Ensures numpy, opencv-python, and PyQt6 versions work together
- ✅ **Standalone installer**: Complete one-click solution that installs all dependencies automatically
- ✅ **Enhanced camera permissions**: Multiple launcher options for better macOS camera access
- ✅ **Fix script included**: Quickly resolve any module compatibility issues

## 🚀 Quick Install

### Option 1: Standalone Installer (Recommended for non-technical users)
**For colleagues who just want to run the app on macOS:**
1. Download the latest `USB Camera Tester` DMG from the
   [Releases page](https://github.com/aasimo13/kamv2/releases)
2. Double-click the DMG file to mount it
3. Double-click `USB Camera Tester Installer.app`
4. Follow the prompts - all dependencies install automatically!

> The prebuilt `.dmg` is distributed via GitHub Releases rather than being
> committed to the repository. Build it yourself with `./create_standalone_installer.sh`
> (see Option 2) and attach the resulting DMG to a Release.

### Option 2: Build Your Own Installer
```bash
# Clone the repository
git clone https://github.com/aasimo13/kamv2.git
cd kamv2

# Build the standalone installer
./create_standalone_installer.sh
```

### Option 3: Manual Install
```bash
# Clone the repository
git clone https://github.com/aasimo13/kamv2.git
cd kamv2

# Install dependencies with compatible versions
pip3 install --user "numpy>=1.21.0,<2.3.0" "opencv-python>=4.8.0,<4.10.0" "PyQt6>=6.4.0,<6.8.0"

# Run the application
python3 camera_test_suite/main_pyqt6.py
```

## 🧪 Test Capabilities

The suite runs the following tests (defined in `camera_test_suite/main_pyqt6.py`).
You can run them individually or all at once:

- **Connection & Detection**: Enumerate connected USB cameras and confirm capture
- **Resolution Validation**: Probe supported resolutions and verify frame size
- **Frame Rate Analysis**: Measure actual vs reported FPS with frame timing
- **PDAF Autofocus System**: Phase-detection autofocus checks
- **Exposure Control**: Exposure setting / response checks
- **White Balance**: White-balance behavior checks
- **Image Sharpness**: Sharpness measurement on captured frames
- **Noise Analysis**: Image noise measurement
- **USB Performance**: USB throughput / bandwidth observations
- **S5KGM1ST Sensor**: Sensor-specific checks for the target module
- **V4L2 Optimal Settings**: Recommended V4L2 settings (Linux/Raspberry Pi)

Results can be exported to JSON, and a PDF report can be generated (via `reportlab`).

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

## 📦 Distribution

### Standalone Installer
The macOS `.dmg` installer is a build artifact and is **not** committed to this
repository. Build it locally with `./create_standalone_installer.sh`, then attach
the resulting DMG to a [GitHub Release](https://github.com/aasimo13/kamv2/releases)
so non-technical users can download a single file - no GitHub or technical
knowledge required.

### Support Scripts
- **fix_numpy_issue.sh**: Fixes numpy/opencv module compatibility issues
- **create_standalone_installer.sh**: Builds the macOS standalone installer / DMG

## 📁 Project Structure

```
kamv2/
├── camera_test_suite/              # Main application source
│   ├── main_pyqt6.py               # PyQt6 desktop application (primary)
│   ├── main.py                     # Earlier Tkinter-based version
│   ├── cli.py                      # Command-line entry point
│   ├── v4l2_settings.py            # Linux/Raspberry Pi V4L2 helpers
│   ├── icons/                      # Application icons
│   └── *.sh / *_GUIDE.md           # Linux / Raspberry Pi install + guides
├── assets/                         # macOS Info.plist, .desktop entry
├── create_standalone_installer.sh  # Build script (produces the DMG)
├── fix_numpy_issue.sh              # Module fix script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

> Build output (`standalone_installer_build/`, `*.app`, `*.dmg`), generated test
> images, and test-result JSON files are intentionally git-ignored.

## 🔧 Development

### Building from Source
```bash
git clone https://github.com/aasimo13/kamv2.git
cd kamv2
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

## 📊 Status

Working (v4.0). The PyQt6 desktop app and the test suite run today. The macOS
standalone installer builds via `create_standalone_installer.sh`. Linux and
Raspberry Pi are supported through the scripts and guides in `camera_test_suite/`.

## 📄 License

Released under the [MIT License](LICENSE) - free to use, modify, and distribute.

## 📞 Support

For technical support or questions, please create an issue on GitHub with detailed information about your testing requirements.

---

**Built for reliable USB camera validation** 📸✨