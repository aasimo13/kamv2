# USB Camera Tester - Installation Guide

## 🎯 One-Click Installation

### For End Users (Simplest Method)

1. **Download the installer DMG:**
   - File: `🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v4.0.dmg`

2. **Install the application:**
   - Double-click the DMG file to mount it
   - Double-click `USB Camera Tester Installer.app`
   - Follow the prompts - everything installs automatically!

3. **Launch the application:**
   - Look for `🎥 Launch USB Camera Tester.command` on your **DESKTOP**
   - Double-click it to start the app
   - Grant camera permissions when prompted

## ✅ What Gets Installed

- **Desktop:** `🎥 Launch USB Camera Tester.command` (main launcher)
- **Applications folder:**
  - `USB Camera Tester.app` (main application)
  - `🎥 Launch USB Camera Tester.command` (backup launcher)
- **Python dependencies:** numpy<2, opencv-python, PyQt6 (automatically installed)

## 🔧 Troubleshooting

### If you see module errors:
```bash
# Run the included fix script
bash fix_numpy_issue.sh
```

### Manual dependency fix:
```bash
# Critical: numpy must be <2 for opencv compatibility
pip3 uninstall -y numpy opencv-python
pip3 install "numpy<2" opencv-python PyQt6
```

## 📱 System Requirements

- **macOS:** 10.14 or later
- **Architecture:** Works on both Intel (x86_64) and Apple Silicon (ARM64)
- **Python:** 3.8 or later (3.13 recommended)
- **RAM:** 4GB minimum

## 🎯 Key Points for ARM Macs

The installer automatically:
- Detects ARM64 architecture
- Installs numpy 1.26.4 (not 2.x which breaks opencv)
- Installs compatible opencv-python version
- Places launcher prominently on Desktop

## 📦 For Developers

To build your own installer:
```bash
git clone [repository]
cd kamv2
./create_standalone_installer.sh
```

This creates `standalone_installer_build/🎥_USB_Camera_Tester_COMPLETE_INSTALLER_v4.0.dmg`

## ⚡ Quick Test

After installation, test dependencies:
```python
import numpy, cv2, PyQt6
print(f"numpy {numpy.__version__}")  # Should be 1.26.x
print(f"opencv {cv2.__version__}")    # Should be 4.11.x
print("All modules OK!")
```

## 💡 Important Notes

1. **Always use the launcher script** (`🎥 Launch USB Camera Tester.command`) for best camera access
2. **numpy must be version 1.x** (not 2.x) for opencv compatibility
3. **The Desktop launcher is the primary way to start the app**
4. **Camera permissions** are handled automatically through the launcher

---

**Support:** Create an issue on GitHub if you encounter problems
**Version:** 4.0 (September 2024)