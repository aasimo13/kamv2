#!/usr/bin/env python3
"""
USB Camera Hardware Test Application - FIXED VERSION
Simplified to eliminate grey screen issues
"""

import os
import sys
import platform

# Simplified GUI environment check
if os.environ.get('CLAUDECODE') or os.environ.get('SSH_CLIENT'):
    print("Headless environment detected - GUI not available")
    sys.exit(1)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import subprocess
from pathlib import Path

@dataclass
class TestResult:
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    timestamp: str
    details: Dict = None

class CameraHardwareTester:
    def __init__(self):
        # Create window with simple, direct approach
        self.root = tk.Tk()
        self.root.title("USB Camera Hardware Test Suite - WN-L2307k368 48MP")
        self.root.geometry("1400x900")

        # Camera properties
        self.camera = None
        self.camera_index = None
        self.is_testing = False
        self.test_results = []
        self.current_frame = None
        self.test_image_path = None

        # Camera specifications for WN-L2307k368
        self.camera_specs = {
            "max_resolution": (8000, 6000),
            "max_fps": 8,
            "sensor": "Samsung S5KGM1ST ISOCELL GM1",
            "pixel_size": 0.8,
            "fov": 79,
            "interface": "USB2.0",
            "formats": ["MJPEG", "YUY2"],
            "optical_format": "1/2 inch",
            "effective_resolution": (4000, 3000),
            "autofocus_type": "PDAF",
            "color_filter": "RGB Bayer",
            "analog_gain_max": 16,
            "operating_temp": (-20, 70),
            "hdr_support": True,
            "binning_support": True,
            "wdr_support": True
        }

        # Simple, direct UI setup
        self.setup_ui()
        self.setup_styles()

        # Simple camera detection for macOS
        if platform.system() == "Darwin":
            self.log_message("macOS detected. Camera access may require permissions.")
            self.log_message("Use 'Connect Camera' button when ready to test cameras.")
        else:
            self.auto_detect_usb_cameras()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
            self.log_message("Using 'clam' theme")
        except Exception as e:
            try:
                style.theme_use('default')
                self.log_message(f"Clam theme failed, using 'default' theme")
            except Exception as e2:
                self.log_message(f"Theme setup failed: {e2}")

    def setup_ui(self):
        self.log_message("Starting UI setup...")

        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.create_camera_tab()
        self.create_tests_tab()
        self.create_results_tab()
        self.create_settings_tab()

        self.log_message("UI setup complete")

    def log_message(self, message):
        """Log message to test output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        print(log_line.strip())

        # Only write to UI if test_output exists
        if hasattr(self, 'test_output') and self.test_output:
            self.test_output.insert(tk.END, log_line)
            self.test_output.see(tk.END)

    def create_camera_tab(self):
        # Camera Control Tab
        self.camera_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.camera_frame, text="Camera Control")

        # Connection section
        conn_frame = ttk.LabelFrame(self.camera_frame, text="Camera Connection")
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(conn_frame, text="Auto-Detect USB Cameras",
                  command=self.auto_detect_usb_cameras).pack(side="left", padx=5, pady=5)
        ttk.Button(conn_frame, text="Manual Connect",
                  command=self.manual_connect_camera).pack(side="left", padx=5, pady=5)
        ttk.Button(conn_frame, text="Disconnect",
                  command=self.disconnect_camera).pack(side="left", padx=5, pady=5)

        # Status
        self.status_label = ttk.Label(conn_frame, text="Status: No camera connected")
        self.status_label.pack(side="right", padx=5, pady=5)

        # Camera preview
        preview_frame = ttk.LabelFrame(self.camera_frame, text="Live Preview")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_label = ttk.Label(preview_frame, text="No camera connected")
        self.preview_label.pack(expand=True)

    def create_tests_tab(self):
        # Tests Tab
        self.tests_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tests_frame, text="Hardware Tests")

        # Test selection
        selection_frame = ttk.LabelFrame(self.tests_frame, text="Test Selection")
        selection_frame.pack(fill="x", padx=10, pady=5)

        self.test_vars = {}
        tests = [
            "Basic Connection", "Resolution Test", "Frame Rate Test",
            "Autofocus Test", "Exposure Test", "White Balance Test"
        ]

        for i, test in enumerate(tests):
            var = tk.BooleanVar(value=True)
            self.test_vars[test] = var
            ttk.Checkbutton(selection_frame, text=test, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=5, pady=2)

        # Test controls
        control_frame = ttk.Frame(self.tests_frame)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="Run Selected Tests",
                  command=self.run_tests).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Run All Tests",
                  command=self.run_all_tests).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Stop Tests",
                  command=self.stop_tests).pack(side="left", padx=5)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=5)

    def create_results_tab(self):
        # Results Tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Test Results")

        # Results display
        results_display_frame = ttk.LabelFrame(self.results_frame, text="Test Results")
        results_display_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create treeview for results
        columns = ("Test", "Status", "Message", "Timestamp")
        self.results_tree = ttk.Treeview(results_display_frame, columns=columns, show="headings")

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)

        self.results_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Output area
        output_frame = ttk.LabelFrame(self.results_frame, text="Test Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.test_output = tk.Text(output_frame, height=10)
        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.test_output.yview)
        self.test_output.configure(yscrollcommand=output_scrollbar.set)

        self.test_output.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        output_scrollbar.pack(side="right", fill="y")

        # Results controls
        results_control_frame = ttk.Frame(self.results_frame)
        results_control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(results_control_frame, text="Export Results",
                  command=self.export_results).pack(side="left", padx=5)
        ttk.Button(results_control_frame, text="Clear Results",
                  command=self.clear_results).pack(side="left", padx=5)

    def create_settings_tab(self):
        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

        ttk.Label(self.settings_frame, text="Settings will be implemented here",
                 font=("Arial", 12)).pack(pady=50)

    # Placeholder methods
    def auto_detect_usb_cameras(self):
        self.log_message("Auto-detecting USB cameras...")

    def manual_connect_camera(self):
        self.log_message("Manual camera connection...")

    def disconnect_camera(self):
        self.log_message("Disconnecting camera...")

    def run_tests(self):
        self.log_message("Running selected tests...")

    def run_all_tests(self):
        self.log_message("Running all tests...")

    def stop_tests(self):
        self.log_message("Stopping tests...")

    def export_results(self):
        self.log_message("Exporting results...")

    def clear_results(self):
        self.log_message("Clearing results...")

    def run(self):
        """Start the application - SIMPLE VERSION"""
        self.log_message("Starting application...")
        self.root.mainloop()

def main():
    """Main entry point for the application"""
    app = CameraHardwareTester()
    app.run()

if __name__ == "__main__":
    main()