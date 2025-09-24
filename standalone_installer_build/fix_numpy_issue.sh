#!/bin/bash

echo "🔧 USB Camera Tester - Numpy Fix Script"
echo "======================================="
echo ""
echo "This script fixes the common numpy import error."
echo ""

# Find Python
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$python_path" &> /dev/null; then
        PYTHON_CMD="$python_path"
        echo "✅ Found Python: $python_path"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Get pip command
PIP_CMD=""
if "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
    PIP_CMD="$PYTHON_CMD -m pip"
    echo "✅ Found pip via python -m pip"
else
    for pip_candidate in "${PYTHON_CMD%/*}/pip3" "${PYTHON_CMD%/*}/pip" pip3 pip; do
        if command -v "$pip_candidate" >/dev/null 2>&1 && "$pip_candidate" --version >/dev/null 2>&1; then
            PIP_CMD="$pip_candidate"
            echo "✅ Found pip: $pip_candidate"
            break
        fi
    done
fi

if [ -z "$PIP_CMD" ]; then
    echo "❌ pip not found"
    exit 1
fi

echo ""
echo "🔧 Fixing Python module installations..."
echo "This may take a few moments..."

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"
echo ""

# Uninstall problematic modules
echo "1. Uninstalling existing modules..."
eval "$PIP_CMD uninstall -y numpy opencv-python opencv-contrib-python opencv-python-headless" >/dev/null 2>&1

echo "2. Clearing pip cache..."
eval "$PIP_CMD cache purge" >/dev/null 2>&1

echo "3. Installing compatible numpy version..."
# CRITICAL: Install numpy<2 for opencv compatibility
if eval "$PIP_CMD install --user --force-reinstall --no-cache-dir 'numpy<2'" >/dev/null 2>&1; then
    echo "✅ numpy installed successfully (version <2 for opencv)"
else
    echo "Trying numpy 1.26.4 specifically..."
    if eval "$PIP_CMD install --user --force-reinstall --no-cache-dir 'numpy==1.26.4'" >/dev/null 2>&1; then
        echo "✅ numpy 1.26.4 installed successfully"
    else
        echo "❌ numpy installation failed"
        exit 1
    fi
fi

echo "4. Reinstalling opencv-python..."
# Let pip automatically find the best compatible version
if eval "$PIP_CMD install --user --force-reinstall --no-cache-dir opencv-python" >/dev/null 2>&1; then
    echo "✅ opencv-python installed successfully"
else
    echo "⚠️  Trying specific version 4.11.0.86..."
    if eval "$PIP_CMD install --user --force-reinstall --no-cache-dir 'opencv-python==4.11.0.86'" >/dev/null 2>&1; then
        echo "✅ opencv-python 4.11.0.86 installed successfully"
    else
        echo "❌ opencv-python installation failed"
        exit 1
    fi
fi

echo "5. Reinstalling PyQt6..."
if eval "$PIP_CMD install --user --no-cache-dir 'PyQt6>=6.4.0,<6.8.0'" >/dev/null 2>&1; then
    echo "✅ PyQt6 reinstalled successfully (compatible version)"
else
    echo "⚠️  Trying fallback version..."
    if eval "$PIP_CMD install --user --no-cache-dir PyQt6" >/dev/null 2>&1; then
        echo "✅ PyQt6 installed successfully (fallback)"
    else
        echo "❌ PyQt6 installation failed"
        exit 1
    fi
fi

echo "6. Testing module imports..."
if "$PYTHON_CMD" -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
    echo "✅ numpy is working correctly!"
else
    echo "❌ numpy still has issues"
    exit 1
fi

if "$PYTHON_CMD" -c "import cv2; print('✅ opencv version:', cv2.__version__)" 2>/dev/null; then
    echo "✅ opencv-python is working correctly!"
else
    echo "❌ opencv-python still has issues"
    exit 1
fi

if "$PYTHON_CMD" -c "import PyQt6; print('✅ PyQt6 imported successfully')" 2>/dev/null; then
    echo "✅ PyQt6 is working correctly!"
else
    echo "❌ PyQt6 still has issues"
    exit 1
fi

echo ""
echo "🎉 All modules fixed! USB Camera Tester is ready to use."
echo ""
echo "🚀 Launch options:"
echo "   • 🎥 Launch USB Camera Tester.command (on Desktop)"
echo "   • 🎥 Launch USB Camera Tester.command (in Applications folder)"
echo "   • USB Camera Tester.app (in Applications folder)"