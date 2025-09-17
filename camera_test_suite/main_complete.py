#!/usr/bin/env python3
"""
USB Camera Hardware Test Application - COMPLETE VERSION
For WN-L2307k368 48MP BM Camera Module

Full-featured camera testing with working UI
"""

import os
import sys
import platform

# Basic GUI environment check
if os.environ.get('CLAUDECODE') or os.environ.get('SSH_CLIENT'):
    print("Headless environment detected - GUI not available")
    sys.exit(1)

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

@dataclass
class TestResult:
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    timestamp: str
    details: Dict = None

class CameraHardwareTester:
    def __init__(self):
        print("Creating USB Camera Hardware Tester...")

        # Create window
        self.root = tk.Tk()
        self.root.title("USB Camera Hardware Test Suite - WN-L2307k368 48MP")
        self.root.geometry("1400x900")
        self.root.configure(bg='white')

        # Camera properties
        self.camera = None
        self.camera_index = None
        self.preview_running = False
        self.is_testing = False
        self.test_results = []
        self.current_frame = None

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
            "effective_resolution": (4000, 3000),  # 48MP binned to 12MP
            "autofocus_type": "PDAF",  # Phase Detection AutoFocus
            "color_filter": "RGB Bayer",
            "analog_gain_max": 16,
            "operating_temp": (-20, 70),  # Celsius
            "hdr_support": True,
            "binning_support": True,  # Tetrapixel technology
            "wdr_support": True       # Wide Dynamic Range
        }

        # Create UI
        self.create_ui()

        print("Setup complete")

    def create_ui(self):
        """Create comprehensive but simple UI"""
        # Title
        title = tk.Label(self.root, text="USB Camera Hardware Test Suite",
                        font=("Arial", 18, "bold"), bg='white')
        title.pack(pady=5)

        subtitle = tk.Label(self.root, text="WN-L2307k368 48MP BM Camera Module",
                          font=("Arial", 12), bg='white', fg='gray')
        subtitle.pack(pady=(0, 10))

        # Main container
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left side - Controls
        left_frame = tk.Frame(main_frame, bg='white', width=350)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        # Camera controls
        self.create_camera_controls(left_frame)

        # Test controls
        self.create_test_controls(left_frame)

        # Right side - Preview and Output
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side="right", fill="both", expand=True)

        # Preview area
        self.create_preview_area(right_frame)

        # Output and results
        self.create_output_area(right_frame)

        # Initial log
        self.log("USB Camera Hardware Tester initialized")
        self.log("Click 'Auto-Detect Cameras' to begin")

    def create_camera_controls(self, parent):
        """Create camera control section"""
        cam_frame = tk.LabelFrame(parent, text="Camera Control", font=("Arial", 12, "bold"))
        cam_frame.pack(fill="x", pady=(0, 10))

        tk.Button(cam_frame, text="Auto-Detect Cameras", command=self.auto_detect_cameras,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)
        tk.Button(cam_frame, text="Manual Connect", command=self.manual_connect,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)
        tk.Button(cam_frame, text="Disconnect", command=self.disconnect_camera,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

        self.status_label = tk.Label(cam_frame, text="Status: No camera connected",
                                   font=("Arial", 10), fg="red")
        self.status_label.pack(pady=5)

        # Camera info
        info_frame = tk.Frame(cam_frame, bg='white')
        info_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(info_frame, text="Camera Info:", font=("Arial", 10, "bold"), bg='white').pack(anchor="w")
        self.info_text = tk.Text(info_frame, height=6, font=("Courier", 8))
        self.info_text.pack(fill="x")

    def create_test_controls(self, parent):
        """Create test control section"""
        test_frame = tk.LabelFrame(parent, text="Hardware Tests", font=("Arial", 12, "bold"))
        test_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Test selection
        self.test_vars = {}
        tests = [
            ("Basic Connection", self._test_basic_connection),
            ("Resolution Test", self._test_resolution),
            ("Frame Rate Test", self._test_framerate),
            ("Autofocus Test", self._test_autofocus_comprehensive),
            ("Exposure Control", self._test_exposure_control),
            ("White Balance", self._test_white_balance),
            ("S5KGM1ST Sensor", self._test_s5kgm1st_sensor_specific),
            ("Image Quality", self._test_image_quality),
            ("USB Performance", self._test_usb_performance)
        ]

        for test_name, test_func in tests:
            var = tk.BooleanVar(value=True)
            self.test_vars[test_name] = var
            cb = tk.Checkbutton(test_frame, text=test_name, variable=var, bg='white')
            cb.pack(anchor="w", padx=5, pady=1)

        # Test buttons
        button_frame = tk.Frame(test_frame, bg='white')
        button_frame.pack(fill="x", padx=5, pady=10)

        tk.Button(button_frame, text="Run Selected Tests", command=self.run_selected_tests,
                 font=("Arial", 11), bg='lightgreen').pack(fill="x", pady=2)
        tk.Button(button_frame, text="Run All Tests", command=self.run_all_tests,
                 font=("Arial", 11), bg='lightblue').pack(fill="x", pady=2)
        tk.Button(button_frame, text="Stop Tests", command=self.stop_tests,
                 font=("Arial", 11), bg='lightcoral').pack(fill="x", pady=2)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_frame, variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        # Results export
        export_frame = tk.Frame(test_frame, bg='white')
        export_frame.pack(fill="x", padx=5, pady=5)

        tk.Button(export_frame, text="Export Results", command=self.export_results,
                 font=("Arial", 10)).pack(side="left", padx=2)
        tk.Button(export_frame, text="Clear Results", command=self.clear_results,
                 font=("Arial", 10)).pack(side="right", padx=2)

    def create_preview_area(self, parent):
        """Create camera preview area"""
        preview_frame = tk.LabelFrame(parent, text="Camera Preview", font=("Arial", 12, "bold"))
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.preview_label = tk.Label(preview_frame, text="No camera connected",
                                    bg='lightgray', font=("Arial", 14))
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)

    def create_output_area(self, parent):
        """Create output and results area"""
        # Test output
        output_frame = tk.LabelFrame(parent, text="Test Output", font=("Arial", 12, "bold"))
        output_frame.pack(fill="x", pady=0)

        self.output_text = tk.Text(output_frame, height=10, font=("Courier", 9))
        output_scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        self.output_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        output_scrollbar.pack(side="right", fill="y", pady=5)

    def log(self, message):
        """Log message to output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        print(log_line.strip())

        self.output_text.insert(tk.END, log_line)
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def update_camera_info(self):
        """Update camera information display"""
        if not self.camera or not self.camera.isOpened():
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "No camera connected")
            return

        info = f"Camera Index: {self.camera_index}\n"

        try:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.camera.get(cv2.CAP_PROP_FPS)

            info += f"Resolution: {width}x{height}\n"
            info += f"FPS: {fps}\n"
            info += f"Expected: WN-L2307k368\n"
            info += f"Sensor: {self.camera_specs['sensor']}\n"
            info += f"Max Res: {self.camera_specs['max_resolution'][0]}x{self.camera_specs['max_resolution'][1]}"

        except Exception as e:
            info += f"Error getting info: {e}"

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)

    # Camera Connection Methods
    def auto_detect_cameras(self):
        """Auto-detect available cameras"""
        self.log("Scanning for cameras...")

        cameras_found = []
        for i in range(10):  # Check more indices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    # Check if likely USB camera vs built-in
                    is_usb = self.is_likely_usb_camera(i, width, height)
                    cam_type = "USB" if is_usb else "Built-in"

                    cameras_found.append((i, width, height, is_usb))
                    self.log(f"Found camera {i}: {width}x{height} ({cam_type})")
                cap.release()
            except Exception as e:
                self.log(f"Error checking camera {i}: {e}")

        if cameras_found:
            # Prefer USB cameras
            usb_cameras = [c for c in cameras_found if c[3]]
            if usb_cameras:
                self.log(f"Found {len(usb_cameras)} USB camera(s)")
                self.connect_camera(usb_cameras[0][0])
            else:
                self.log(f"Found {len(cameras_found)} camera(s) (no USB detected)")
                self.connect_camera(cameras_found[0][0])
        else:
            self.log("No cameras detected")

    def is_likely_usb_camera(self, index, width, height):
        """Determine if camera is likely USB vs built-in"""
        # Built-in Mac cameras usually at index 0 with standard resolutions
        if index == 0:
            builtin_resolutions = [(1280, 720), (1920, 1080), (640, 480)]
            if (width, height) in builtin_resolutions:
                return False

        # Higher indices more likely USB
        if index > 0:
            return True

        # High resolutions indicate USB cameras
        if width >= 3840 or height >= 2160:  # 4K+
            return True

        return False

    def manual_connect(self):
        """Manual camera connection"""
        index = simpledialog.askinteger("Camera Index",
                                      "Enter camera index (0-9):",
                                      minvalue=0, maxvalue=9, initialvalue=0)
        if index is not None:
            self.connect_camera(index)

    def connect_camera(self, index):
        """Connect to specific camera"""
        try:
            if self.camera:
                self.camera.release()
                self.preview_running = False

            self.camera = cv2.VideoCapture(index)
            if self.camera.isOpened():
                self.camera_index = index
                self.status_label.config(text=f"Status: Connected to camera {index}", fg="green")
                self.log(f"Connected to camera {index}")
                self.update_camera_info()
                self.start_preview()
            else:
                self.log(f"Failed to connect to camera {index}")
                self.status_label.config(text="Status: Connection failed", fg="red")
        except Exception as e:
            self.log(f"Error connecting to camera {index}: {e}")

    def start_preview(self):
        """Start camera preview"""
        if self.camera and self.camera.isOpened():
            self.preview_running = True
            self.update_preview()

    def update_preview(self):
        """Update camera preview"""
        if self.camera and self.camera.isOpened() and self.preview_running:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()

                # Resize for display
                height, width = frame.shape[:2]
                max_width, max_height = 700, 500

                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)

                frame_resized = cv2.resize(frame, (new_width, new_height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

                # Convert to PhotoImage
                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(img)

                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo  # Keep reference

            # Schedule next update
            self.root.after(50, self.update_preview)

    def disconnect_camera(self):
        """Disconnect camera"""
        if self.camera:
            self.preview_running = False
            self.camera.release()
            self.camera = None
            self.camera_index = None
            self.status_label.config(text="Status: No camera connected", fg="red")
            self.preview_label.config(image="", text="No camera connected")
            self.update_camera_info()
            self.log("Camera disconnected")

    # Test Execution Methods
    def run_selected_tests(self):
        """Run selected tests"""
        if not self.camera or not self.camera.isOpened():
            messagebox.showerror("Error", "Please connect a camera first")
            return

        selected_tests = [name for name, var in self.test_vars.items() if var.get()]
        if not selected_tests:
            messagebox.showwarning("Warning", "No tests selected")
            return

        self.run_tests(selected_tests)

    def run_all_tests(self):
        """Run all tests"""
        if not self.camera or not self.camera.isOpened():
            messagebox.showerror("Error", "Please connect a camera first")
            return

        all_tests = list(self.test_vars.keys())
        self.run_tests(all_tests)

    def run_tests(self, test_names):
        """Run specified tests"""
        self.is_testing = True
        self.progress_var.set(0)

        # Map test names to functions
        test_functions = {
            "Basic Connection": self._test_basic_connection,
            "Resolution Test": self._test_resolution,
            "Frame Rate Test": self._test_framerate,
            "Autofocus Test": self._test_autofocus_comprehensive,
            "Exposure Control": self._test_exposure_control,
            "White Balance": self._test_white_balance,
            "S5KGM1ST Sensor": self._test_s5kgm1st_sensor_specific,
            "Image Quality": self._test_image_quality,
            "USB Performance": self._test_usb_performance
        }

        def run_tests_thread():
            try:
                for i, test_name in enumerate(test_names):
                    if not self.is_testing:
                        break

                    self.log(f"\n=== Running {test_name} ===")
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    if test_name in test_functions:
                        result = test_functions[test_name](timestamp)
                        self.test_results.append(result)
                        self.log(f"{test_name}: {result.status} - {result.message}")

                    progress = ((i + 1) / len(test_names)) * 100
                    self.progress_var.set(progress)

                    time.sleep(0.5)  # Brief pause between tests

                self.log(f"\n=== Testing Complete ===")
                self.log(f"Results: {len(self.test_results)} tests completed")

            except Exception as e:
                self.log(f"Test execution error: {e}")
            finally:
                self.is_testing = False

        threading.Thread(target=run_tests_thread, daemon=True).start()

    def stop_tests(self):
        """Stop running tests"""
        self.is_testing = False
        self.log("Tests stopped by user")

    # Individual Test Functions
    def _test_basic_connection(self, timestamp):
        """Test basic camera connection"""
        try:
            ret, frame = self.camera.read()
            if ret:
                height, width = frame.shape[:2]
                return TestResult("Basic Connection", "PASS",
                                f"Camera connected successfully - Frame: {width}x{height}",
                                timestamp)
            else:
                return TestResult("Basic Connection", "FAIL",
                                "Cannot read frame from camera",
                                timestamp)
        except Exception as e:
            return TestResult("Basic Connection", "FAIL",
                            f"Connection test error: {str(e)}",
                            timestamp)

    def _test_resolution(self, timestamp):
        """Test camera resolution capabilities"""
        try:
            # Test different resolutions
            resolutions = [(640, 480), (1280, 720), (1920, 1080), (3840, 2160), (4000, 3000)]
            supported = []

            for width, height in resolutions:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                time.sleep(0.1)

                actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if actual_width == width and actual_height == height:
                    supported.append(f"{width}x{height}")

            message = f"Supported resolutions: {', '.join(supported)}"
            status = "PASS" if len(supported) > 0 else "FAIL"

            return TestResult("Resolution Test", status, message, timestamp,
                            {"supported_resolutions": supported})

        except Exception as e:
            return TestResult("Resolution Test", "FAIL",
                            f"Resolution test error: {str(e)}",
                            timestamp)

    def _test_framerate(self, timestamp):
        """Test camera frame rate"""
        try:
            # Capture frames for 3 seconds
            start_time = time.time()
            frame_count = 0

            while time.time() - start_time < 3.0:
                ret, frame = self.camera.read()
                if ret:
                    frame_count += 1

            elapsed = time.time() - start_time
            fps = frame_count / elapsed

            message = f"Measured FPS: {fps:.1f} ({frame_count} frames in {elapsed:.1f}s)"
            status = "PASS" if fps > 5 else "FAIL"  # Expect at least 5 FPS

            return TestResult("Frame Rate Test", status, message, timestamp,
                            {"measured_fps": fps, "frame_count": frame_count})

        except Exception as e:
            return TestResult("Frame Rate Test", "FAIL",
                            f"Frame rate test error: {str(e)}",
                            timestamp)

    def _test_exposure_control(self, timestamp):
        """Test exposure control"""
        try:
            # Test exposure settings
            exposure_values = [-3, -1, 0, 1, 3]
            exposures_tested = []

            for exp_val in exposure_values:
                try:
                    self.camera.set(cv2.CAP_PROP_EXPOSURE, exp_val)
                    time.sleep(0.5)
                    actual_exp = self.camera.get(cv2.CAP_PROP_EXPOSURE)
                    exposures_tested.append((exp_val, actual_exp))
                except:
                    pass

            message = f"Exposure control test: {len(exposures_tested)} settings tested"
            status = "PASS" if len(exposures_tested) > 0 else "FAIL"

            return TestResult("Exposure Control", status, message, timestamp,
                            {"exposures_tested": exposures_tested})

        except Exception as e:
            return TestResult("Exposure Control", "FAIL",
                            f"Exposure test error: {str(e)}",
                            timestamp)

    def _test_white_balance(self, timestamp):
        """Test white balance control"""
        try:
            # Test auto white balance
            auto_wb = self.camera.get(cv2.CAP_PROP_AUTO_WB)

            # Test manual white balance if possible
            wb_temp = self.camera.get(cv2.CAP_PROP_WB_TEMPERATURE)

            message = f"White balance - Auto: {auto_wb}, Temperature: {wb_temp}"
            status = "PASS"  # Basic availability test

            return TestResult("White Balance", status, message, timestamp,
                            {"auto_wb": auto_wb, "wb_temperature": wb_temp})

        except Exception as e:
            return TestResult("White Balance", "FAIL",
                            f"White balance test error: {str(e)}",
                            timestamp)

    def _test_image_quality(self, timestamp):
        """Test image quality metrics"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                return TestResult("Image Quality", "FAIL",
                                "Cannot capture frame for quality test",
                                timestamp)

            # Calculate sharpness (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Calculate brightness
            brightness = np.mean(gray)

            # Calculate contrast (standard deviation)
            contrast = np.std(gray)

            message = f"Sharpness: {sharpness:.1f}, Brightness: {brightness:.1f}, Contrast: {contrast:.1f}"
            status = "PASS" if sharpness > 100 else "WARN"  # Basic quality threshold

            return TestResult("Image Quality", status, message, timestamp,
                            {"sharpness": sharpness, "brightness": brightness, "contrast": contrast})

        except Exception as e:
            return TestResult("Image Quality", "FAIL",
                            f"Image quality test error: {str(e)}",
                            timestamp)

    def _test_autofocus_comprehensive(self, timestamp):
        """Test autofocus functionality"""
        try:
            # Test autofocus capability
            af_available = self.camera.get(cv2.CAP_PROP_AUTOFOCUS)
            focus_pos = self.camera.get(cv2.CAP_PROP_FOCUS)

            # Test focus range
            focus_positions = [0, 64, 128, 192, 255]
            focus_results = []

            for pos in focus_positions:
                try:
                    self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable auto
                    time.sleep(0.2)
                    self.camera.set(cv2.CAP_PROP_FOCUS, pos)
                    time.sleep(0.5)

                    ret, frame = self.camera.read()
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                        focus_results.append((pos, sharpness))
                except:
                    pass

            message = f"Autofocus available: {af_available}, Focus positions tested: {len(focus_results)}"
            status = "PASS" if len(focus_results) > 0 else "FAIL"

            return TestResult("Autofocus Test", status, message, timestamp,
                            {"af_available": af_available, "focus_results": focus_results})

        except Exception as e:
            return TestResult("Autofocus Test", "FAIL",
                            f"Autofocus test error: {str(e)}",
                            timestamp)

    def _test_s5kgm1st_sensor_specific(self, timestamp):
        """Test S5KGM1ST sensor specific features"""
        try:
            # Test gain control (important for ISOCELL sensors)
            gain_levels = [0, 4, 8, 12, 16]
            gain_results = []

            for gain in gain_levels:
                try:
                    self.camera.set(cv2.CAP_PROP_GAIN, gain)
                    time.sleep(0.3)
                    actual_gain = self.camera.get(cv2.CAP_PROP_GAIN)
                    gain_results.append((gain, actual_gain))
                except:
                    pass

            # Test saturation (color reproduction)
            saturation = self.camera.get(cv2.CAP_PROP_SATURATION)

            message = f"S5KGM1ST sensor test - Gain levels: {len(gain_results)}, Saturation: {saturation}"
            status = "PASS" if len(gain_results) > 0 else "WARN"

            return TestResult("S5KGM1ST Sensor", status, message, timestamp,
                            {"gain_results": gain_results, "saturation": saturation})

        except Exception as e:
            return TestResult("S5KGM1ST Sensor", "FAIL",
                            f"Sensor test error: {str(e)}",
                            timestamp)

    def _test_usb_performance(self, timestamp):
        """Test USB interface performance"""
        try:
            # Test sustained capture rate
            start_time = time.time()
            frame_sizes = []

            for _ in range(30):  # Capture 30 frames
                ret, frame = self.camera.read()
                if ret:
                    frame_sizes.append(frame.size)
                else:
                    break

            elapsed = time.time() - start_time
            avg_fps = len(frame_sizes) / elapsed if elapsed > 0 else 0

            message = f"USB performance - Frames: {len(frame_sizes)}, Avg FPS: {avg_fps:.1f}"
            status = "PASS" if avg_fps > 10 else "WARN"

            return TestResult("USB Performance", status, message, timestamp,
                            {"frames_captured": len(frame_sizes), "avg_fps": avg_fps})

        except Exception as e:
            return TestResult("USB Performance", "FAIL",
                            f"USB test error: {str(e)}",
                            timestamp)

    # Results and Export Methods
    def export_results(self):
        """Export test results to JSON file"""
        if not self.test_results:
            messagebox.showwarning("Warning", "No test results to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Test Results"
        )

        if filename:
            try:
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "camera_model": "WN-L2307k368 48MP BM",
                    "summary": {
                        "total": len(self.test_results),
                        "passed": sum(1 for r in self.test_results if r.status == "PASS"),
                        "failed": sum(1 for r in self.test_results if r.status == "FAIL"),
                        "warnings": sum(1 for r in self.test_results if r.status == "WARN")
                    },
                    "results": [asdict(result) for result in self.test_results]
                }

                with open(filename, 'w') as f:
                    json.dump(report_data, f, indent=2)

                self.log(f"Results exported to {filename}")
                messagebox.showinfo("Success", f"Results exported to {filename}")

            except Exception as e:
                self.log(f"Export error: {e}")
                messagebox.showerror("Error", f"Failed to export results: {e}")

    def clear_results(self):
        """Clear test results"""
        self.test_results.clear()
        self.progress_var.set(0)
        self.log("Test results cleared")

    def run(self):
        """Start the application"""
        print("Starting USB Camera Hardware Tester...")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        print("Application ended")

    def on_closing(self):
        """Handle window closing"""
        self.disconnect_camera()
        self.root.destroy()

def main():
    """Main entry point"""
    app = CameraHardwareTester()
    app.run()

if __name__ == "__main__":
    main()