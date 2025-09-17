#!/usr/bin/env python3
"""
USB Camera Hardware Test Application - MINIMAL VERSION
Extremely simplified to eliminate any grey screen issues
"""

import os
import sys
import platform

# Basic GUI environment check
if os.environ.get('CLAUDECODE') or os.environ.get('SSH_CLIENT'):
    print("Headless environment detected - GUI not available")
    sys.exit(1)

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class CameraHardwareTester:
    def __init__(self):
        print("Creating minimal camera tester...")

        # Create window - absolutely minimal approach
        self.root = tk.Tk()
        self.root.title("USB Camera Tester - Minimal")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        # Minimal UI
        self.create_minimal_ui()

        print("Minimal setup complete")

    def create_minimal_ui(self):
        """Create the most basic UI possible"""
        # Title
        title = tk.Label(self.root, text="USB Camera Hardware Tester",
                        font=("Arial", 18, "bold"), bg='white')
        title.pack(pady=20)

        # Status
        self.status = tk.Label(self.root, text="Ready to test cameras",
                              font=("Arial", 12), bg='white')
        self.status.pack(pady=10)

        # Simple buttons
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Connect Camera",
                 command=self.connect_camera, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Run Tests",
                 command=self.run_tests, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Exit",
                 command=self.root.quit, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        # Simple text area
        text_frame = tk.Frame(self.root, bg='white')
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.text_area = tk.Text(text_frame, height=15, font=("Courier", 10))
        self.text_area.pack(fill="both", expand=True)

        # Initial message
        self.log("USB Camera Tester initialized")
        self.log("Click 'Connect Camera' to begin")

    def log(self, message):
        """Simple logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        print(log_line.strip())
        self.text_area.insert(tk.END, log_line)
        self.text_area.see(tk.END)

    def connect_camera(self):
        """Connect to camera"""
        self.log("Attempting to connect to camera...")
        self.status.config(text="Connecting to camera...")
        # Placeholder
        self.log("Camera connection not implemented yet")

    def run_tests(self):
        """Run tests"""
        self.log("Running camera tests...")
        self.status.config(text="Running tests...")
        # Placeholder
        self.log("Tests not implemented yet")

    def run(self):
        """Start the application"""
        print("Starting minimal camera tester...")
        self.root.mainloop()
        print("Application ended")

def main():
    """Main entry point"""
    app = CameraHardwareTester()
    app.run()

if __name__ == "__main__":
    main()