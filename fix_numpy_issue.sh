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
echo "🔧 Fixing numpy installation..."
echo "This may take a few moments..."
echo ""

# Uninstall and reinstall numpy cleanly
echo "1. Uninstalling numpy..."
eval "$PIP_CMD uninstall -y numpy" >/dev/null 2>&1

echo "2. Clearing pip cache..."
eval "$PIP_CMD cache purge" >/dev/null 2>&1

echo "3. Reinstalling numpy..."
if eval "$PIP_CMD install --user --no-cache-dir numpy" >/dev/null 2>&1; then
    echo "✅ numpy reinstalled successfully"
else
    echo "❌ numpy installation failed"
    exit 1
fi

echo "4. Testing numpy import..."
if "$PYTHON_CMD" -c "import numpy; print('✅ numpy version:', numpy.__version__)" 2>/dev/null; then
    echo "✅ numpy is working correctly!"
else
    echo "❌ numpy still has issues"
    exit 1
fi

echo ""
echo "🎉 Fix complete! You can now launch USB Camera Tester."
echo ""
echo "Use: 🎥 Launch USB Camera Tester.command (on Desktop)"