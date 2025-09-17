#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - CLI Installer
Command-line version for maximum compatibility
"""

import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil
from pathlib import Path
import tempfile
import time

class CLIUSBCameraTesterInstaller:
    def __init__(self):
        self.installation_path = "/Applications"
        self.app_name = "USB Camera Tester"
        self.temp_dir = None

    def log_message(self, message):
        """Print message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

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

        for package in packages:
            self.log_message(f"Installing {package}...")
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

    def run_installation(self):
        """Run the complete installation process"""
        print("🚀 USB Camera Hardware Test Suite - Command Line Installer")
        print("=========================================================")
        print()

        # Ask for confirmation
        response = input("Install USB Camera Tester to Applications folder? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return

        try:
            self.temp_dir = tempfile.mkdtemp(prefix="usb_camera_installer_")
            self.log_message(f"Created temporary directory: {self.temp_dir}")

            # Step 1: Check system requirements
            self.log_message("Checking system requirements...")
            self.check_system_requirements()

            # Step 2: Download application
            self.log_message("Downloading USB Camera Tester...")
            self.download_application()

            # Step 3: Install Python dependencies
            self.log_message("Installing Python dependencies...")
            self.install_dependencies()

            # Step 4: Create application bundle
            self.log_message("Creating application bundle...")
            self.create_app_bundle()

            # Step 5: Install to Applications
            self.log_message("Installing to Applications folder...")
            self.install_to_applications()

            # Step 6: Complete
            self.log_message("Installation completed successfully!")
            print()
            print("🎉 Installation Complete!")
            print(f"USB Camera Tester has been installed to: {self.final_app_path}")
            print()
            print("The application is now available in:")
            print("• Applications folder")
            print("• Launchpad")
            print("• Spotlight search")
            print()

            # Ask to launch
            launch = input("Would you like to launch the application now? (y/N): ")
            if launch.lower() == 'y':
                subprocess.run(["open", self.final_app_path])

        except Exception as e:
            self.log_message(f"Installation failed: {str(e)}")
            print(f"\n❌ Installation failed: {str(e)}")
            print("Please check the error message above and try again.")
        finally:
            self.cleanup_temp_files()

if __name__ == "__main__":
    installer = CLIUSBCameraTesterInstaller()
    installer.run_installation()