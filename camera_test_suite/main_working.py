#!/usr/bin/env python3
"""
USB Camera Hardware Test Application - WORKING VERSION
Functional but keeps UI simple to avoid grey screen
"""

import os
import sys
import platform

# Basic GUI environment check
if os.environ.get('CLAUDECODE') or os.environ.get('SSH_CLIENT'):
    print("Headless environment detected - GUI not available")
    sys.exit(1)

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading

class CameraHardwareTester:
    def __init__(self):
        print("Creating USB Camera Tester...")

        # Create window
        self.root = tk.Tk()
        self.root.title("USB Camera Hardware Test Suite - WN-L2307k368 48MP")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')

        # Camera properties
        self.camera = None
        self.camera_index = None
        self.preview_running = False

        # Create UI
        self.create_ui()

        print("Setup complete")

    def create_ui(self):
        """Create functional but simple UI"""
        # Title
        title = tk.Label(self.root, text="USB Camera Hardware Test Suite",
                        font=("Arial", 20, "bold"), bg='white')
        title.pack(pady=10)

        # Main container
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side - Controls
        left_frame = tk.Frame(main_frame, bg='white', width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        # Camera controls
        cam_frame = tk.LabelFrame(left_frame, text="Camera Control", font=("Arial", 12, "bold"))
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

        # Test controls
        test_frame = tk.LabelFrame(left_frame, text="Hardware Tests", font=("Arial", 12, "bold"))
        test_frame.pack(fill="x", pady=(0, 10))

        tk.Button(test_frame, text="Basic Connection Test", command=self.test_connection,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)
        tk.Button(test_frame, text="Resolution Test", command=self.test_resolution,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)
        tk.Button(test_frame, text="Frame Rate Test", command=self.test_framerate,
                 font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

        # Right side - Preview and Output
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side="right", fill="both", expand=True)

        # Preview area
        preview_frame = tk.LabelFrame(right_frame, text="Camera Preview", font=("Arial", 12, "bold"))
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.preview_label = tk.Label(preview_frame, text="No camera connected",
                                    bg='lightgray', font=("Arial", 14))
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)

        # Output area
        output_frame = tk.LabelFrame(right_frame, text="Test Output", font=("Arial", 12, "bold"))
        output_frame.pack(fill="x", pady=0)

        self.output_text = tk.Text(output_frame, height=8, font=("Courier", 9))
        scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.output_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Initial log
        self.log("USB Camera Tester initialized")
        self.log("Click 'Auto-Detect Cameras' to begin")

    def log(self, message):
        """Log message to output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        print(log_line.strip())

        self.output_text.insert(tk.END, log_line)
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def auto_detect_cameras(self):
        """Auto-detect available cameras"""
        self.log("Scanning for cameras...")

        cameras_found = []
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cameras_found.append((i, width, height))
                    self.log(f"Found camera {i}: {width}x{height}")
                cap.release()
            except Exception as e:
                self.log(f"Error checking camera {i}: {e}")

        if cameras_found:
            self.log(f"Found {len(cameras_found)} camera(s)")
            # Connect to first camera
            self.connect_camera(cameras_found[0][0])
        else:
            self.log("No cameras detected")

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
                # Resize for display
                height, width = frame.shape[:2]
                max_width, max_height = 600, 400

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
            self.log("Camera disconnected")

    def test_connection(self):
        """Test camera connection"""
        if not self.camera or not self.camera.isOpened():
            self.log("ERROR: No camera connected")
            messagebox.showerror("Error", "Please connect a camera first")
            return

        self.log("Testing camera connection...")
        ret, frame = self.camera.read()
        if ret:
            height, width = frame.shape[:2]
            self.log(f"✓ Connection test PASSED - Frame: {width}x{height}")
        else:
            self.log("✗ Connection test FAILED - Cannot read frame")

    def test_resolution(self):
        """Test camera resolution"""
        if not self.camera or not self.camera.isOpened():
            self.log("ERROR: No camera connected")
            messagebox.showerror("Error", "Please connect a camera first")
            return

        self.log("Testing camera resolution...")

        # Test different resolutions
        resolutions = [(640, 480), (1280, 720), (1920, 1080), (3840, 2160)]

        for width, height in resolutions:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if actual_width == width and actual_height == height:
                self.log(f"✓ Resolution {width}x{height} - SUPPORTED")
            else:
                self.log(f"✗ Resolution {width}x{height} - Not supported (got {actual_width}x{actual_height})")

    def test_framerate(self):
        """Test camera frame rate"""
        if not self.camera or not self.camera.isOpened():
            self.log("ERROR: No camera connected")
            messagebox.showerror("Error", "Please connect a camera first")
            return

        self.log("Testing frame rate...")

        # Capture frames for 2 seconds
        import time
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < 2.0:
            ret, frame = self.camera.read()
            if ret:
                frame_count += 1

        elapsed = time.time() - start_time
        fps = frame_count / elapsed

        self.log(f"✓ Frame rate test: {fps:.1f} FPS ({frame_count} frames in {elapsed:.1f}s)")

    def run(self):
        """Start the application"""
        print("Starting USB Camera Tester...")
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