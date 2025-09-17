#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - Simple macOS Installer
Simplified version for maximum compatibility
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import urllib.request
import zipfile
import shutil
from pathlib import Path
import tempfile
import time

class SimpleUSBCameraTesterInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("USB Camera Tester Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Installation state
        self.installation_path = "/Applications"
        self.app_name = "USB Camera Tester"
        self.temp_dir = None
        self.is_installing = False

        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to install")

        self.create_interface()

    def create_interface(self):
        """Create simple, reliable interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="USB Camera Hardware Test Suite",
                              font=('Helvetica', 18, 'bold'), bg='white')
        title_label.pack(pady=(0, 10))

        # Subtitle
        subtitle_label = tk.Label(main_frame,
                                 text="Professional camera testing for WN-L2307k368 48MP modules",
                                 font=('Helvetica', 10), bg='white', fg='gray')
        subtitle_label.pack(pady=(0, 20))

        # Features
        features_frame = tk.LabelFrame(main_frame, text="What will be installed:",
                                      font=('Helvetica', 12, 'bold'), bg='white')
        features_frame.pack(fill=tk.X, pady=(0, 20))

        features = [
            "✓ Complete camera testing application",
            "✓ All required Python dependencies",
            "✓ Professional app bundle for Applications folder",
            "✓ Desktop and Launchpad integration"
        ]

        for feature in features:
            feature_label = tk.Label(features_frame, text=feature,
                                   font=('Helvetica', 10), bg='white', anchor='w')
            feature_label.pack(fill=tk.X, padx=10, pady=2)

        # Installation path
        path_frame = tk.Frame(main_frame, bg='white')
        path_frame.pack(fill=tk.X, pady=(0, 20))

        path_label = tk.Label(path_frame, text="Install Location:",
                             font=('Helvetica', 10, 'bold'), bg='white')
        path_label.pack(anchor=tk.W)

        path_display = tk.Label(path_frame, text=f"{self.installation_path}/{self.app_name}.app",
                               font=('Helvetica', 10), bg='white', fg='blue')
        path_display.pack(anchor=tk.W, pady=(2, 0))

        # Progress section
        progress_frame = tk.Frame(main_frame, bg='white')
        progress_frame.pack(fill=tk.X, pady=(0, 20))

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=(0, 10))

        self.status_label = tk.Label(progress_frame, textvariable=self.status_var,
                                    font=('Helvetica', 9), bg='white')
        self.status_label.pack()

        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(20, 0))

        self.install_button = tk.Button(button_frame, text="Install USB Camera Tester",
                                       command=self.start_installation,
                                       font=('Helvetica', 12, 'bold'),
                                       bg='#007AFF', fg='white',
                                       padx=20, pady=10)
        self.install_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = tk.Button(button_frame, text="Cancel",
                                      command=self.cancel_installation,
                                      font=('Helvetica', 10),
                                      padx=20, pady=10)
        self.cancel_button.pack(side=tk.LEFT)

    def log_message(self, message):
        """Add message to log (simplified)"""
        print(f"[INSTALLER] {message}")

    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.progress_var.set(value)
        self.status_var.set(status)
        self.log_message(status)
        self.root.update_idletasks()

    def start_installation(self):
        """Start the installation process"""
        if self.is_installing:
            return

        # Confirm installation
        result = messagebox.askyesno(
            "Confirm Installation",
            f"Install USB Camera Tester to Applications folder?\n\n"
            "This will:\n"
            "• Download the latest version\n"
            "• Install Python dependencies\n"
            "• Create application bundle\n"
            "• Add to Applications folder\n\n"
            "Continue?"
        )

        if not result:
            return

        self.is_installing = True
        self.install_button.config(state='disabled', text="Installing...")

        # Start installation in background thread
        install_thread = threading.Thread(target=self.run_installation, daemon=True)
        install_thread.start()

    def run_installation(self):
        """Run the complete installation process"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="usb_camera_installer_")
            self.log_message(f"Created temporary directory: {self.temp_dir}")

            # Step 1: Check system requirements
            self.update_progress(10, "Checking system requirements...")
            self.check_system_requirements()

            # Step 2: Download application
            self.update_progress(20, "Downloading USB Camera Tester...")
            self.download_application()

            # Step 3: Install Python dependencies
            self.update_progress(40, "Installing Python dependencies...")
            self.install_dependencies()

            # Step 4: Create application bundle
            self.update_progress(70, "Creating application bundle...")
            self.create_app_bundle()

            # Step 5: Install to Applications
            self.update_progress(90, "Installing to Applications folder...")
            self.install_to_applications()

            # Step 6: Complete
            self.update_progress(100, "Installation completed successfully!")
            self.installation_complete()

        except Exception as e:
            self.log_message(f"Installation failed: {str(e)}")
            self.update_progress(0, f"Installation failed: {str(e)}")
            self.installation_failed(str(e))
        finally:
            self.cleanup_temp_files()

    def check_system_requirements(self):
        """Check if system meets requirements"""
        self.log_message("Checking Python installation...")
        result = subprocess.run([sys.executable, '--version'],
                               capture_output=True, text=True)
        if result.returncode == 0:
            python_version = result.stdout.strip()
            self.log_message(f"Python version: {python_version}")
        else:
            raise Exception("Python installation not found")

    def download_application(self):
        """Download the latest version from GitHub"""
        github_url = "https://github.com/aasimo13/Kam/archive/refs/heads/main.zip"
        download_path = os.path.join(self.temp_dir, "usb_camera_tester.zip")

        self.log_message(f"Downloading from: {github_url}")
        urllib.request.urlretrieve(github_url, download_path)

        # Extract the downloaded file
        self.log_message("Extracting downloaded files...")
        extract_path = os.path.join(self.temp_dir, "extracted")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        self.source_path = os.path.join(extract_path, "Kam-main", "Kam")

    def install_dependencies(self):
        """Install required Python dependencies"""
        self.log_message("Installing Python packages...")

        packages = [
            "opencv-python",
            "numpy",
            "Pillow",
            "matplotlib",
            "psutil",
            "reportlab"
        ]

        for i, package in enumerate(packages):
            progress = 40 + (i / len(packages)) * 30
            self.update_progress(progress, f"Installing {package}...")

            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)

            if result.returncode == 0:
                self.log_message(f"✓ Installed {package}")
            else:
                self.log_message(f"✗ Failed to install {package}: {result.stderr}")

    def create_app_bundle(self):
        """Create proper macOS application bundle"""
        app_bundle_path = os.path.join(self.temp_dir, f"{self.app_name}.app")

        # Create app bundle structure
        contents_dir = os.path.join(app_bundle_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")

        os.makedirs(macos_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)

        self.log_message("Creating application bundle structure...")

        # Copy application files
        app_source = os.path.join(self.source_path, "camera_test_suite")
        app_dest = os.path.join(resources_dir, "camera_test_suite")

        if not os.path.exists(app_source):
            raise Exception(f"Source application files not found at: {app_source}")

        self.log_message(f"Copying application files...")
        shutil.copytree(app_source, app_dest)

        # Create launcher script
        launcher_script = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"
cd "$RESOURCES_DIR"

# Find Python executable
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    osascript -e 'display dialog "Python is required. Please install Python from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Launch the application
exec "$PYTHON_CMD" camera_test_suite/main.py "$@"
'''

        launcher_path = os.path.join(macos_dir, "USBCameraTester")
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        os.chmod(launcher_path, 0o755)

        # Create Info.plist
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>USBCameraTester</string>
    <key>CFBundleIdentifier</key>
    <string>com.usb-camera-tester.app</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>2.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSCameraUsageDescription</key>
    <string>This app needs camera access to test USB camera hardware functionality.</string>
</dict>
</plist>'''

        plist_path = os.path.join(contents_dir, "Info.plist")
        with open(plist_path, 'w') as f:
            f.write(info_plist)

        self.app_bundle_path = app_bundle_path
        self.log_message("Application bundle created successfully")

    def install_to_applications(self):
        """Install the app bundle to Applications folder"""
        final_app_path = os.path.join(self.installation_path, f"{self.app_name}.app")

        # Remove existing installation if present
        if os.path.exists(final_app_path):
            self.log_message("Removing existing installation...")
            shutil.rmtree(final_app_path)

        # Copy app bundle to Applications
        self.log_message(f"Installing to {final_app_path}...")
        shutil.copytree(self.app_bundle_path, final_app_path)

        # Verify installation
        if os.path.exists(final_app_path):
            self.log_message(f"✓ Successfully installed to {final_app_path}")
        else:
            raise Exception("Installation verification failed")

        self.final_app_path = final_app_path

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            self.log_message("Cleaning up temporary files...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def installation_complete(self):
        """Handle successful installation completion"""
        self.is_installing = False
        self.install_button.config(state='normal', text="Installation Complete ✓")
        self.install_button.config(state='disabled')

        # Show success dialog
        result = messagebox.askyesno(
            "Installation Complete!",
            f"USB Camera Tester has been successfully installed!\n\n"
            f"The application is now available in:\n"
            "• Applications folder\n"
            "• Launchpad\n"
            "• Spotlight search\n\n"
            "Would you like to launch the application now?"
        )

        if result:
            self.launch_application()

    def installation_failed(self, error_message):
        """Handle installation failure"""
        self.is_installing = False
        self.install_button.config(state='normal', text="Install USB Camera Tester")

        messagebox.showerror(
            "Installation Failed",
            f"The installation encountered an error:\n\n{error_message}\n\n"
            "Please try again or check the terminal for more details."
        )

    def launch_application(self):
        """Launch the installed application"""
        try:
            subprocess.run(["open", self.final_app_path])
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch application: {str(e)}")

    def cancel_installation(self):
        """Cancel the installation"""
        if self.is_installing:
            result = messagebox.askyesno(
                "Cancel Installation",
                "Are you sure you want to cancel the installation?"
            )
            if result:
                self.is_installing = False
                self.cleanup_temp_files()
                self.root.quit()
        else:
            self.root.quit()

    def run(self):
        """Run the installer"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

        self.root.mainloop()

if __name__ == "__main__":
    installer = SimpleUSBCameraTesterInstaller()
    installer.run()