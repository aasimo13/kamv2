#!/bin/bash
# Launcher for USB Camera Tester that ensures proper permissions

echo "🎥 USB Camera Tester Launcher"
echo "=============================="
echo ""
echo "This launcher ensures the camera tester has proper permissions."
echo ""

# Find the USB Camera Tester app bundle
APP_BUNDLE="/Applications/USB Camera Tester.app"
APP_DIR="$APP_BUNDLE/Contents/Resources/camera_test_suite"

echo "Looking for app in: $APP_DIR"

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "❌ USB Camera Tester app not found in Applications folder"
    echo "Please make sure the app is installed correctly."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if camera test suite exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Camera test suite not found in app bundle"
    echo "App may be corrupted. Please reinstall."
    read -p "Press Enter to exit..."
    exit 1
fi

# Change to app directory
cd "$APP_DIR"
echo "✅ Found camera test suite"

# Find Python
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$python_path" &> /dev/null; then
        PYTHON_CMD="$python_path"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3 not found. Please install Python from python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Clean Python environment to avoid import conflicts
unset PYTHONPATH
export PYTHONNOUSERSITE=0

# Ensure we're not in any conflicting directories
echo "Current directory: $(pwd)"

# Test imports before launching
echo "Testing Python imports..."
if ! "$PYTHON_CMD" -c "import sys; print('Python version:', sys.version)" 2>/dev/null; then
    echo "❌ Python test failed"
    read -p "Press Enter to exit..."
    exit 1
fi

if ! "$PYTHON_CMD" -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
    echo "❌ numpy import failed - auto-installing correct version..."
    echo "Installing numpy<2 (required for opencv)..."
    "$PYTHON_CMD" -m pip install --user --force-reinstall "numpy<2" >/dev/null 2>&1
    if ! "$PYTHON_CMD" -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
        echo "❌ numpy still failing. Please run: pip3 install --user 'numpy<2'"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

if ! "$PYTHON_CMD" -c "import cv2; print('✅ opencv version:', cv2.__version__)" 2>/dev/null; then
    echo "❌ opencv import failed - auto-installing..."
    "$PYTHON_CMD" -m pip install --user --force-reinstall opencv-python >/dev/null 2>&1
    if ! "$PYTHON_CMD" -c "import cv2; print('✅ opencv version:', cv2.__version__)" 2>/dev/null; then
        echo "❌ opencv still failing. Please run: pip3 install --user opencv-python"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

if ! "$PYTHON_CMD" -c "import PyQt6; print('✅ PyQt6 imported successfully')" 2>/dev/null; then
    echo "❌ PyQt6 import failed - auto-installing..."
    "$PYTHON_CMD" -m pip install --user PyQt6 >/dev/null 2>&1
    if ! "$PYTHON_CMD" -c "import PyQt6; print('✅ PyQt6 imported successfully')" 2>/dev/null; then
        echo "❌ PyQt6 still failing. Please run: pip3 install --user PyQt6"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ All imports successful"

# Run the app normally (no env -i which breaks Python paths)
echo "Starting USB Camera Tester..."
"$PYTHON_CMD" main_pyqt6.py

echo ""
echo "App closed."
