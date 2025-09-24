#!/usr/bin/env python3
"""
Launcher for PyQt6 Camera Test Suite
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the PyQt6 version
from main_pyqt6 import main

if __name__ == "__main__":
    print("Launching USB Camera Professional Test Suite v4.0 (PyQt6)")
    main()