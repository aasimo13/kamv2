#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - Simple Native Installer
Uses native macOS dialogs instead of Tkinter for maximum compatibility
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
import ssl

class SimpleNativeInstaller:
    def __init__(self):
        self.installation_path = "/Applications"
        self.app_name = "USB Camera Tester"
        self.temp_dir = None

    def show_dialog(self, title, message, buttons=["OK"], default_button="OK"):
        """Show native macOS dialog"""
        button_list = '", "'.join(buttons)
        script = f'''
        display dialog "{message}" ¬
        buttons {{"{button_list}"}} ¬
        default button "{default_button}" ¬
        with title "{title}" ¬
        with icon note
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
        """Show progress in Terminal and log file"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        # Also log to file for debugging when run as app bundle
        try:
            log_file = os.path.expanduser("~/Desktop/installer_debug.log")
            with open(log_file, "a") as f:
                f.write(log_message + "\n")
        except:
            pass

    def run_installation(self):
        """Run the complete installation with native dialogs"""

        # Welcome dialog
        welcome_msg = """Welcome to USB Camera Hardware Test Suite v4.0 Installer!

🚀 NEW: Professional PyQt6 Native GUI Interface
🍎 ARM64: Optimized for Apple Silicon (M1/M2/M3/M4 Macs)

This installer will automatically:
• Detect your Mac architecture (Apple Silicon vs Intel)
• Install Python 3.13.7 optimized for your system
• Download the latest PyQt6 version from GitHub
• Install all required dependencies (including PyQt6)
• Create a professional native macOS application
• Install to your Applications folder

Click 'Install' to begin or 'Cancel' to exit."""

        result = self.show_dialog("USB Camera Tester Installer", welcome_msg,
                                ["Install", "Cancel"], "Install")

        # Debug what we actually got
        self.show_progress(f"Dialog result: {repr(result)}")

        if result != "Install":
            self.show_progress("Installation cancelled by user.")
            return

        print("\n🚀 USB Camera Hardware Test Suite - Installation Starting")
        print("=" * 60)

        try:
            self.temp_dir = tempfile.mkdtemp(prefix="usb_camera_installer_")
            self.show_progress(f"Created temporary directory: {self.temp_dir}")

            # Step 1: Check system requirements
            self.show_progress("Checking system requirements...")
            self.check_system_requirements()

            # Step 2: Download application
            self.show_progress("Downloading USB Camera Tester...")
            self.download_application()

            # Step 3: Install Python dependencies
            self.show_progress("Installing Python dependencies...")
            self.install_dependencies()

            # Step 4: Create application bundle
            self.show_progress("Creating application bundle...")
            self.create_app_bundle()

            # Step 5: Install to Applications
            self.show_progress("Installing to Applications folder...")
            self.install_to_applications()

            # Step 6: Complete
            self.show_progress("Installation completed successfully!")

            print("\n🎉 Installation Complete!")
            print(f"USB Camera Tester installed to: {self.final_app_path}")

            # Success dialog
            success_msg = """Installation completed successfully!

USB Camera Tester is now available in:
• Applications folder
• Launchpad
• Spotlight search

Would you like to launch the application now?"""

            result = self.show_dialog("Installation Complete", success_msg,
                                    ["Launch", "Don't Launch"], "Launch")

            if result == "Launch":
                try:
                    self.show_progress("Launching USB Camera Tester...")
                    # Give the installer dialog time to close
                    time.sleep(0.5)

                    # Try to launch the application
                    launch_result = subprocess.run(["open", self.final_app_path],
                                                 capture_output=True, text=True, timeout=15)
                    if launch_result.returncode == 0:
                        self.show_progress("✓ Application launched successfully")
                    else:
                        error_msg = f"Failed to launch: {launch_result.stderr}"
                        self.show_progress(f"Launch failed: {error_msg}")
                        self.show_dialog("Launch Error",
                                       f"Could not launch the application automatically.\n\n"
                                       f"Error: {error_msg}\n\n"
                                       f"You can manually launch it from:\n{self.final_app_path}",
                                       ["OK"], "OK")
                except subprocess.TimeoutExpired:
                    self.show_dialog("Launch Warning",
                                   "Application launch is taking longer than expected.\n\n"
                                   f"If it doesn't open, you can manually launch it from:\n{self.final_app_path}",
                                   ["OK"], "OK")
                except Exception as e:
                    self.show_dialog("Launch Error",
                                   f"Could not launch the application automatically.\n\n"
                                   f"Error: {str(e)}\n\n"
                                   f"You can manually launch it from:\n{self.final_app_path}",
                                   ["OK"], "OK")

        except Exception as e:
            error_msg = f"Installation failed: {str(e)}"
            self.show_progress(error_msg)
            print(f"\n❌ {error_msg}")

            self.show_dialog("Installation Failed",
                           f"Installation encountered an error:\n\n{str(e)}\n\nPlease try again.",
                           ["OK"], "OK")
        finally:
            self.cleanup_temp_files()

    def check_system_requirements(self):
        """Check if system meets requirements and install Python if needed"""
        # Check if Python 3 is available
        python_found = False
        for python_cmd in ['python3', 'python']:
            try:
                result = subprocess.run([python_cmd, '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    python_version = result.stdout.strip()
                    self.show_progress(f"Found {python_version}")
                    python_found = True
                    break
            except FileNotFoundError:
                continue

        if not python_found:
            self.show_progress("Python 3 not found. Installing Python automatically...")
            self.install_python()

        # Verify Python is now available
        result = subprocess.run([sys.executable, '--version'],
                               capture_output=True, text=True)
        if result.returncode == 0:
            python_version = result.stdout.strip()
            self.show_progress(f"Using Python: {python_version}")
        else:
            raise Exception("Python installation verification failed")

    def install_python(self):
        """Download and install Python 3.13.7 from python.org with ARM64 optimization"""

        # Detect system architecture
        arch = self._detect_system_architecture()
        self.show_progress(f"Detected system architecture: {arch}")

        # Choose appropriate Python installer based on architecture
        installation_methods = self._get_python_installers_for_architecture(arch)

        for method in installation_methods:
            try:
                self.show_progress(f"Attempting {method['name']}...")
                success = self._try_python_installation(method)
                if success:
                    return
            except Exception as e:
                self.show_progress(f"⚠ {method['name']} failed: {str(e)}")
                continue

        # All automatic methods failed - guide user to manual installation
        self._handle_python_installation_failure()

    def _try_python_installation(self, method):
        """Try a specific Python installation method"""
        pkg_path = os.path.join(self.temp_dir, f"python_{method['version']}_installer.pkg")

        self.show_progress(f"Downloading Python {method['version']} installer...")

        # Download with better error handling
        try:
            self._download_with_progress(method["url"], pkg_path)
            self.show_progress(f"✓ Python {method['version']} installer downloaded")
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

        # Try installation approaches in order of preference
        install_approaches = [
            ("user_install", self._install_python_user_mode),
            ("admin_install", self._install_python_admin_mode),
            ("manual_launch", self._install_python_manual_launch)
        ]

        for approach_name, install_func in install_approaches:
            try:
                self.show_progress(f"Trying {approach_name.replace('_', ' ')}...")
                success = install_func(pkg_path, method['version'])
                if success:
                    self.show_progress(f"✓ Python {method['version']} installed successfully using {approach_name}")
                    self._update_python_path()
                    return True
            except Exception as e:
                self.show_progress(f"⚠ {approach_name} failed: {str(e)}")
                continue

        return False

    def _download_with_progress(self, url, destination):
        """Download with better SSL handling and error reporting"""
        try:
            urllib.request.urlretrieve(url, destination)
        except (ssl.SSLError, urllib.error.URLError) as e:
            self.show_progress(f"SSL/URL error, trying alternative method: {e}")

            # Try with unverified SSL context
            try:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url, destination)
            except Exception as e2:
                # Final fallback using curl
                self.show_progress("Trying curl download...")
                result = subprocess.run([
                    "curl", "-L", "-k", "-o", destination, url
                ], capture_output=True, text=True, timeout=300)

                if result.returncode != 0:
                    raise Exception(f"Download failed: {result.stderr}")

    def _install_python_user_mode(self, pkg_path, version):
        """Try user-mode installation (no admin required)"""
        # This typically won't work for Python PKG files, but worth trying
        result = subprocess.run([
            "installer", "-pkg", pkg_path, "-target", "CurrentUserHomeDirectory"
        ], capture_output=True, text=True, timeout=300)

        return result.returncode == 0

    def _install_python_admin_mode(self, pkg_path, version):
        """Try admin installation with better error handling"""
        self.show_progress("Installing Python (requires admin password)...")

        # Show dialog asking for permission first
        choice = self.show_dialog(
            "Administrator Permission Required",
            f"Python {version} installation requires administrator privileges.\n\n"
            f"Click 'Continue' to enter your admin password, or 'Skip' to try alternative methods.",
            ["Continue", "Skip"], "Continue"
        )

        if choice != "Continue":
            raise Exception("User declined admin installation")

        result = subprocess.run([
            "sudo", "installer", "-pkg", pkg_path, "-target", "/"
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            return True
        else:
            error_details = result.stderr or result.stdout or "Unknown error"
            raise Exception(f"Admin installation failed: {error_details}")

    def _install_python_manual_launch(self, pkg_path, version):
        """Launch the installer manually for user to complete"""
        self.show_progress("Launching Python installer for manual completion...")

        choice = self.show_dialog(
            "Manual Python Installation",
            f"Automatic installation failed. Would you like to:\n\n"
            f"1. Launch the Python {version} installer manually\n"
            f"2. You'll complete the installation yourself\n"
            f"3. Then return to this installer\n\n"
            f"Continue with manual installation?",
            ["Launch Installer", "Cancel"], "Launch Installer"
        )

        if choice != "Launch Installer":
            raise Exception("User declined manual installation")

        # Launch the installer
        subprocess.run(["open", pkg_path])

        # Wait for user to complete installation
        choice = self.show_dialog(
            "Python Installation In Progress",
            f"The Python {version} installer has been launched.\n\n"
            f"Please complete the Python installation, then click 'Done' to continue.\n\n"
            f"If the installation was successful, this installer will continue automatically.",
            ["Done", "Cancel"], "Done"
        )

        if choice != "Done":
            raise Exception("User cancelled manual installation")

        # Check if Python is now available
        return self._verify_python_installation()

    def _verify_python_installation(self):
        """Verify that Python was successfully installed"""
        python_candidates = [
            "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "python3"
        ]

        for python_cmd in python_candidates:
            try:
                result = subprocess.run([python_cmd, '--version'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    version = result.stdout.strip()
                    self.show_progress(f"✓ Verified Python installation: {version}")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        return False

    def _update_python_path(self):
        """Update PATH to include new Python installation"""
        python_paths = [
            "/Library/Frameworks/Python.framework/Versions/3.13/bin",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin",
            "/opt/homebrew/bin",
            "/usr/local/bin"
        ]

        current_path = os.environ.get('PATH', '')
        for path in python_paths:
            if path not in current_path:
                os.environ["PATH"] = f"{path}:{current_path}"
                current_path = os.environ["PATH"]

    def _handle_python_installation_failure(self):
        """Handle complete Python installation failure with helpful guidance"""
        error_msg = """All automatic Python installation methods failed.

This can happen due to:
• Security settings blocking installations
• Network connectivity issues
• Insufficient disk space
• Conflicting existing Python installations

SOLUTION: Manual Python Installation Required"""

        self.show_progress(error_msg)

        choice = self.show_dialog(
            "Python Installation Required",
            f"{error_msg}\n\n"
            f"Click 'Open python.org' to download Python manually, or\n"
            f"Click 'Show Instructions' for detailed installation steps.",
            ["Open python.org", "Show Instructions", "Cancel"], "Open python.org"
        )

        if choice == "Open python.org":
            subprocess.run(["open", "https://www.python.org/downloads/macos/"])

        elif choice == "Show Instructions":
            instructions = """Manual Python Installation Instructions:

1. Go to https://www.python.org/downloads/macos/
2. Download 'macOS 64-bit universal2 installer'
3. Double-click the downloaded .pkg file
4. Follow the installation wizard
5. After installation, restart this installer

The installer will automatically detect the new Python installation."""

            self.show_dialog("Installation Instructions", instructions, ["OK"], "OK")

        raise Exception("Manual Python installation required - please install Python 3.13+ from python.org")

    def _detect_system_architecture(self):
        """Detect system architecture (ARM64 vs Intel)"""
        try:
            # Try multiple methods to detect architecture

            # Method 1: Check processor brand
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                brand = result.stdout.strip().lower()
                if 'apple' in brand or 'm1' in brand or 'm2' in brand or 'm3' in brand or 'm4' in brand:
                    return 'arm64'

            # Method 2: Check machine hardware name
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                machine = result.stdout.strip().lower()
                if machine == 'arm64':
                    return 'arm64'
                elif machine == 'x86_64':
                    return 'intel'

            # Method 3: Check architecture using platform
            import platform
            machine = platform.machine().lower()
            if machine == 'arm64':
                return 'arm64'
            elif machine in ['x86_64', 'amd64']:
                return 'intel'

            # Method 4: Check processor info (fallback)
            result = subprocess.run(['sysctl', '-n', 'hw.optional.arm64'],
                                  capture_output=True, text=True)
            if result.returncode == 0 and '1' in result.stdout:
                return 'arm64'

        except Exception as e:
            self.show_progress(f"⚠ Architecture detection error: {e}")

        # Default fallback - assume universal installer will work
        self.show_progress("⚠ Could not detect architecture, using universal installer")
        return 'universal'

    def _get_python_installers_for_architecture(self, arch):
        """Get appropriate Python installers based on system architecture"""

        if arch == 'arm64':
            # ARM64 (Apple Silicon) - prioritize ARM64 optimized versions
            return [
                {
                    "name": "Python 3.13.7 ARM64 (Apple Silicon Optimized)",
                    "url": "https://www.python.org/ftp/python/3.13.7/python-3.13.7-macos11.pkg",
                    "version": "3.13.7",
                    "arch": "arm64"
                },
                {
                    "name": "Python 3.13.6 ARM64 (Fallback)",
                    "url": "https://www.python.org/ftp/python/3.13.6/python-3.13.6-macos11.pkg",
                    "version": "3.13.6",
                    "arch": "arm64"
                },
                {
                    "name": "Python 3.13.0 Universal (Final Fallback)",
                    "url": "https://www.python.org/ftp/python/3.13.0/python-3.13.0-macos11.pkg",
                    "version": "3.13.0",
                    "arch": "universal"
                }
            ]
        elif arch == 'intel':
            # Intel x86_64 - use universal installers
            return [
                {
                    "name": "Python 3.13.7 Universal (Intel Compatible)",
                    "url": "https://www.python.org/ftp/python/3.13.7/python-3.13.7-macos11.pkg",
                    "version": "3.13.7",
                    "arch": "universal"
                },
                {
                    "name": "Python 3.13.6 Universal (Fallback)",
                    "url": "https://www.python.org/ftp/python/3.13.6/python-3.13.6-macos11.pkg",
                    "version": "3.13.6",
                    "arch": "universal"
                }
            ]
        else:
            # Universal fallback for unknown architectures
            return [
                {
                    "name": "Python 3.13.7 Universal Installer",
                    "url": "https://www.python.org/ftp/python/3.13.7/python-3.13.7-macos11.pkg",
                    "version": "3.13.7",
                    "arch": "universal"
                },
                {
                    "name": "Python 3.13.6 Universal (Fallback)",
                    "url": "https://www.python.org/ftp/python/3.13.6/python-3.13.6-macos11.pkg",
                    "version": "3.13.6",
                    "arch": "universal"
                }
            ]

    def download_application(self):
        """Download the latest version from GitHub"""
        github_url = "https://github.com/aasimo13/kamv2/archive/refs/heads/main.zip"
        download_path = os.path.join(self.temp_dir, "usb_camera_tester.zip")

        self.show_progress(f"Downloading from: {github_url}")

        # Handle SSL certificate issues on macOS
        try:
            urllib.request.urlretrieve(github_url, download_path)
        except (ssl.SSLError, urllib.error.URLError) as e:
            self.show_progress(f"Download error: {e}")
            self.show_progress("Trying alternative download method...")

            try:
                # Create unverified SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(github_url, download_path)
            except Exception as e2:
                self.show_progress("SSL fallback failed, using curl...")

                # Use curl as final fallback
                result = subprocess.run([
                    "curl", "-L", "-k", "-o", download_path, github_url
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    raise Exception(f"Download failed: {result.stderr}")

        # Extract the downloaded file
        self.show_progress("Extracting downloaded files...")
        extract_path = os.path.join(self.temp_dir, "extracted")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        self.source_path = os.path.join(extract_path, "kamv2-main")

    def install_dependencies(self):
        """Install required Python dependencies"""
        packages = [
            "opencv-python",
            "numpy",
            "Pillow",
            "matplotlib",
            "psutil",
            "reportlab",
            "PyQt6"
        ]

        # Upgrade pip first
        self.show_progress("Upgrading pip...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True, check=True)
            self.show_progress("✓ Pip upgraded")
        except subprocess.CalledProcessError as e:
            self.show_progress(f"⚠ Pip upgrade failed: {e}")

        failed_packages = []

        for package in packages:
            self.show_progress(f"Installing {package}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "--upgrade", "--user", package
                ], capture_output=True, text=True, timeout=120)

                if result.returncode == 0:
                    self.show_progress(f"✓ Installed {package}")

                    # Verify the package can be imported
                    try:
                        if package == "opencv-python":
                            subprocess.run([sys.executable, "-c", "import cv2"],
                                         check=True, capture_output=True)
                        elif package == "PyQt6":
                            subprocess.run([sys.executable, "-c", "import PyQt6"],
                                         check=True, capture_output=True)
                        else:
                            subprocess.run([sys.executable, "-c", f"import {package}"],
                                         check=True, capture_output=True)
                        self.show_progress(f"✓ Verified {package} import")
                    except subprocess.CalledProcessError:
                        self.show_progress(f"⚠ {package} installed but import failed")

                else:
                    self.show_progress(f"✗ Failed to install {package}: {result.stderr}")
                    failed_packages.append(package)

            except subprocess.TimeoutExpired:
                self.show_progress(f"✗ Installation of {package} timed out")
                failed_packages.append(package)
            except Exception as e:
                self.show_progress(f"✗ Error installing {package}: {e}")
                failed_packages.append(package)

        if failed_packages:
            self.show_progress(f"⚠ Some packages failed to install: {', '.join(failed_packages)}")

            # Show dialog about failed packages
            failed_list = '\\n'.join(failed_packages)
            choice = self.show_dialog(
                "Installation Warning",
                f"Some packages failed to install:\\n\\n{failed_list}\\n\\nThe application might not work properly. Continue anyway?",
                ["Continue", "Cancel"], "Continue"
            )

            if choice != "Continue":
                raise Exception("Installation cancelled due to failed dependencies")
        else:
            self.show_progress("✓ All dependencies installed successfully")

    def create_app_bundle(self):
        """Create proper macOS application bundle"""
        app_bundle_path = os.path.join(self.temp_dir, f"{self.app_name}.app")

        # Create app bundle structure
        contents_dir = os.path.join(app_bundle_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")

        os.makedirs(macos_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)

        # Copy application files
        app_source = os.path.join(self.source_path, "camera_test_suite")
        app_dest = os.path.join(resources_dir, "camera_test_suite")

        if not os.path.exists(app_source):
            raise Exception(f"Source application files not found at: {app_source}")

        shutil.copytree(app_source, app_dest)

        # Create launcher script
        launcher_script = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"

# Ensure we have a proper GUI environment
export DISPLAY=${DISPLAY:-:0}

# Clear Claude Code environment variables that prevent GUI
unset CLAUDECODE
unset CLAUDE_CODE
unset CLAUDE_CODE_SSE_PORT
unset CLAUDE_CODE_ENTRYPOINT

# Find Python executable - prefer user-installed versions over system
PYTHON_CMD=""
for python_path in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/*/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 /usr/bin/python3 python; do
    if command -v "$python_path" &> /dev/null; then
        # Test if this Python can import numpy (check for architecture compatibility)
        if "$python_path" -c "import numpy" 2>/dev/null; then
            PYTHON_CMD="$python_path"
            echo "Found compatible Python: $PYTHON_CMD"
            break
        else
            echo "Python $python_path has architecture issues, trying next..."
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    osascript -e 'display dialog "Python 3 is required but not found. Please install Python from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Change to the application directory
cd "$RESOURCES_DIR/camera_test_suite"

# Launch the application with proper error handling
echo "Starting USB Camera Tester with $PYTHON_CMD"
if ! "$PYTHON_CMD" main_pyqt6.py "$@" 2>/tmp/usb_camera_error.log; then
    ERROR_MSG=$(cat /tmp/usb_camera_error.log 2>/dev/null || echo "Unknown error occurred")
    echo "Error: $ERROR_MSG"
    osascript -e "display dialog \"Failed to start USB Camera Tester.\\n\\nError: $ERROR_MSG\\n\\nTry running from Terminal: cd \\\"$RESOURCES_DIR/camera_test_suite\\\" && python3 main_pyqt6.py\" buttons {\"OK\"} default button \"OK\" with icon stop"
    exit 1
fi
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
    <string>4.0</string>
    <key>CFBundleShortVersionString</key>
    <string>4.0</string>
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
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
</dict>
</plist>'''

        plist_path = os.path.join(contents_dir, "Info.plist")
        with open(plist_path, 'w') as f:
            f.write(info_plist)

        # Copy application icon if available
        icon_source = os.path.join(self.source_path, "camera_test_suite", "icons", "app_icon.icns")
        if os.path.exists(icon_source):
            icon_dest = os.path.join(resources_dir, "app_icon.icns")
            shutil.copy2(icon_source, icon_dest)
            self.show_progress("✓ Application icon added")

        self.app_bundle_path = app_bundle_path

    def install_to_applications(self):
        """Install the app bundle to Applications folder"""
        final_app_path = os.path.join(self.installation_path, f"{self.app_name}.app")

        # Remove existing installation if present
        if os.path.exists(final_app_path):
            self.show_progress("Removing existing installation...")
            shutil.rmtree(final_app_path)

        # Copy app bundle to Applications
        self.show_progress(f"Installing to {final_app_path}...")
        shutil.copytree(self.app_bundle_path, final_app_path)

        # Verify installation
        if os.path.exists(final_app_path):
            self.show_progress(f"✓ Successfully installed to {final_app_path}")
        else:
            raise Exception("Installation verification failed")

        self.final_app_path = final_app_path

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            self.show_progress("Cleaning up temporary files...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    installer = SimpleNativeInstaller()
    installer.run_installation()