#!/bin/bash
# Test script to simulate the app bundle launcher

echo "=== Testing App Bundle Launcher ==="

# Simulate the app bundle environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$SCRIPT_DIR"

# Clear Claude Code environment variables
unset CLAUDECODE
unset CLAUDE_CODE
unset CLAUDE_CODE_SSE_PORT
unset CLAUDE_CODE_ENTRYPOINT

echo "Environment cleared"

# Find Python executable
PYTHON_CMD=""
for python_path in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 python3 python; do
    if command -v "$python_path" &> /dev/null; then
        PYTHON_CMD="$python_path"
        echo "Found Python: $PYTHON_CMD"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: No Python found"
    exit 1
fi

# Test the application
cd "$RESOURCES_DIR/camera_test_suite"
echo "Testing: $PYTHON_CMD main.py"
"$PYTHON_CMD" main.py