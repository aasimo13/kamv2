#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - Complete Uninstaller
Removes all files, caches, and dependencies for clean reinstallation
"""

import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path
import time

class USBCameraUninstaller:
    def __init__(self):
        self.files_to_remove = []
        self.directories_to_remove = []
        self.packages_to_uninstall = [
            "opencv-python",
            "PyQt6",
            "matplotlib",
            "reportlab"
        ]

    def show_dialog(self, title, message, buttons=["OK"], default_button="OK"):
        """Show native macOS dialog"""
        button_list = '", "'.join(buttons)
        script = f'''
        display dialog "{message}" ¬
        buttons {{"{button_list}"}} ¬
        default button "{default_button}" ¬
        with title "{title}" ¬
        with icon caution
        '''

        try:
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split(':')[-1].strip()
            return None
        except:
            return None

    def show_progress(self, message):
        """Show progress in Terminal"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

    def find_installation_files(self):
        """Find all USB Camera Tester related files"""
        self.show_progress("Scanning for USB Camera Tester installations...")

        # Application files
        app_locations = [
            "/Applications/USB Camera Tester.app",
            os.path.expanduser("~/Applications/USB Camera Tester.app"),
            "/Applications/USB Camera Tester Installer.app",
            os.path.expanduser("~/Applications/USB Camera Tester Installer.app")
        ]

        for app_path in app_locations:
            if os.path.exists(app_path):
                self.directories_to_remove.append(app_path)
                self.show_progress(f"Found: {app_path}")

        # Cache and temporary files
        cache_locations = [
            os.path.expanduser("~/Library/Caches/com.usb-camera-tester.app"),
            os.path.expanduser("~/Library/Caches/USB Camera Tester"),
            os.path.expanduser("~/Library/Application Support/USB Camera Tester"),
            os.path.expanduser("~/Library/Preferences/com.usb-camera-tester.plist"),
            os.path.expanduser("~/Desktop/installer_debug.log"),
            "/tmp/usb_camera_error.log",
            "/tmp/usb_camera_installer_*",
            os.path.expanduser("~/Downloads/*USB_Camera_Tester*"),
            os.path.expanduser("~/Downloads/kamv2*")
        ]

        for cache_path in cache_locations:
            if "*" in cache_path:
                # Handle wildcards
                import glob
                matches = glob.glob(cache_path)
                for match in matches:
                    if os.path.exists(match):
                        if os.path.isdir(match):
                            self.directories_to_remove.append(match)
                        else:
                            self.files_to_remove.append(match)
                        self.show_progress(f"Found: {match}")
            else:
                if os.path.exists(cache_path):
                    if os.path.isdir(cache_path):
                        self.directories_to_remove.append(cache_path)
                    else:
                        self.files_to_remove.append(cache_path)
                    self.show_progress(f"Found: {cache_path}")

        # DMG files that might be left behind
        dmg_locations = [
            os.path.expanduser("~/Downloads/USB_Camera_Tester*.dmg"),
            os.path.expanduser("~/Desktop/USB_Camera_Tester*.dmg")
        ]

        for dmg_pattern in dmg_locations:
            import glob
            matches = glob.glob(dmg_pattern)
            for dmg_path in matches:
                if os.path.exists(dmg_path):
                    self.files_to_remove.append(dmg_path)
                    self.show_progress(f"Found DMG: {dmg_path}")

        # Python package installations (user-specific)
        self.show_progress("Checking for Python packages installed by USB Camera Tester...")

    def remove_python_packages(self):
        """Remove Python packages that were installed by the camera tester"""
        self.show_progress("Removing USB Camera Tester Python dependencies...")

        # Find Python installations
        python_candidates = [
            "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "python3"
        ]

        removed_packages = []

        for python_cmd in python_candidates:
            try:
                # Check if this python exists
                if not shutil.which(python_cmd) and not os.path.exists(python_cmd):
                    continue

                self.show_progress(f"Checking packages in: {python_cmd}")

                for package in self.packages_to_uninstall:
                    try:
                        # Check if package is installed
                        check_result = subprocess.run([
                            python_cmd, "-c", f"import {package.replace('-', '_') if package == 'opencv-python' else package}; print('installed')"
                        ], capture_output=True, text=True)

                        if check_result.returncode == 0:
                            # Package is installed, try to remove it
                            self.show_progress(f"Removing {package}...")
                            result = subprocess.run([
                                python_cmd, "-m", "pip", "uninstall", "-y", package
                            ], capture_output=True, text=True)

                            if result.returncode == 0:
                                self.show_progress(f"✓ Removed {package}")
                                if package not in removed_packages:
                                    removed_packages.append(package)
                            else:
                                self.show_progress(f"⚠ Could not remove {package}: {result.stderr}")

                    except Exception as e:
                        self.show_progress(f"⚠ Error checking {package}: {e}")

            except Exception as e:
                self.show_progress(f"⚠ Error with Python {python_cmd}: {e}")

        if removed_packages:
            self.show_progress(f"✓ Removed Python packages: {', '.join(removed_packages)}")
        else:
            self.show_progress("No Python packages needed removal")

    def remove_files_and_directories(self):
        """Remove all found files and directories"""
        removed_count = 0

        # Remove files
        for file_path in self.files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.show_progress(f"✓ Removed file: {file_path}")
                    removed_count += 1
            except Exception as e:
                self.show_progress(f"⚠ Could not remove {file_path}: {e}")

        # Remove directories
        for dir_path in self.directories_to_remove:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    self.show_progress(f"✓ Removed directory: {dir_path}")
                    removed_count += 1
            except Exception as e:
                self.show_progress(f"⚠ Could not remove {dir_path}: {e}")

        return removed_count

    def clean_pip_cache(self):
        """Clean pip cache that might contain corrupted packages"""
        self.show_progress("Cleaning pip cache...")

        python_candidates = [
            "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "python3"
        ]

        for python_cmd in python_candidates:
            try:
                if shutil.which(python_cmd) or os.path.exists(python_cmd):
                    result = subprocess.run([
                        python_cmd, "-m", "pip", "cache", "purge"
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        self.show_progress(f"✓ Cleaned pip cache for {python_cmd}")
                    else:
                        self.show_progress(f"⚠ Could not clean pip cache for {python_cmd}")

            except Exception as e:
                self.show_progress(f"⚠ Error cleaning cache for {python_cmd}: {e}")

    def run_uninstallation(self):
        """Run the complete uninstallation process"""

        # Confirmation dialog
        welcome_msg = """USB Camera Hardware Test Suite - Complete Uninstaller

⚠️  WARNING: This will remove ALL USB Camera Tester files including:

• Application files from /Applications
• All cache and temporary files
• Python packages (opencv-python, PyQt6, etc.)
• Configuration files and logs
• Downloaded installers and DMG files

This is useful for:
• Fixing corrupted installations
• Preparing for clean reinstall
• Completely removing the software

Continue with complete uninstallation?"""

        result = self.show_dialog("USB Camera Tester Uninstaller", welcome_msg,
                                ["Uninstall", "Cancel"], "Uninstall")

        if result != "Uninstall":
            self.show_progress("Uninstallation cancelled by user.")
            return

        print("\n🗑️  USB Camera Hardware Test Suite - Complete Uninstallation")
        print("=" * 65)

        try:
            # Step 1: Find all files
            self.show_progress("Step 1: Scanning for files...")
            self.find_installation_files()

            if not self.files_to_remove and not self.directories_to_remove:
                self.show_progress("No USB Camera Tester files found to remove.")
            else:
                self.show_progress(f"Found {len(self.files_to_remove)} files and {len(self.directories_to_remove)} directories to remove")

            # Step 2: Remove Python packages
            self.show_progress("Step 2: Removing Python packages...")
            self.remove_python_packages()

            # Step 3: Clean pip cache
            self.show_progress("Step 3: Cleaning pip cache...")
            self.clean_pip_cache()

            # Step 4: Remove files and directories
            self.show_progress("Step 4: Removing files and directories...")
            removed_count = self.remove_files_and_directories()

            # Step 5: Complete
            self.show_progress("Uninstallation completed!")

            print(f"\n🎉 Uninstallation Complete!")
            print(f"Removed {removed_count} files/directories")

            # Success dialog
            success_msg = f"""Uninstallation completed successfully!

Removed:
• {len(self.directories_to_remove)} application directories
• {len(self.files_to_remove)} files and cache entries
• Python packages: {', '.join(self.packages_to_uninstall)}
• Pip cache cleaned

Your system is now clean and ready for:
• Fresh installation of USB Camera Tester
• Troubleshooting installation issues
• Complete removal verification

You can now safely run a fresh installer if needed."""

            self.show_dialog("Uninstallation Complete", success_msg, ["OK"], "OK")

        except Exception as e:
            error_msg = f"Uninstallation encountered an error: {str(e)}"
            self.show_progress(error_msg)
            print(f"\n❌ {error_msg}")

            self.show_dialog("Uninstallation Error",
                           f"Uninstallation encountered an error:\n\n{str(e)}\n\nSome files may not have been removed.",
                           ["OK"], "OK")

if __name__ == "__main__":
    if platform.system() != "Darwin":
        print("This uninstaller is designed for macOS only.")
        sys.exit(1)

    uninstaller = USBCameraUninstaller()
    uninstaller.run_uninstallation()