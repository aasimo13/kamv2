#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - Debug Version
Testing installer functionality with debug output
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

print("DEBUG: Starting installer...")
print(f"DEBUG: Python version: {sys.version}")
print(f"DEBUG: Current working directory: {os.getcwd()}")
print(f"DEBUG: Platform: {sys.platform}")

try:
    import tkinter
    print("DEBUG: Tkinter import successful")
except ImportError as e:
    print(f"DEBUG: Tkinter import failed: {e}")
    sys.exit(1)

class DebugUSBCameraTesterInstaller:
    def __init__(self):
        print("DEBUG: Initializing installer class...")
        try:
            self.root = tk.Tk()
            print("DEBUG: Tk() created successfully")

            self.root.title("USB Camera Tester Installer - Debug")
            self.root.geometry("600x500")
            self.root.resizable(False, False)
            print("DEBUG: Window configuration set")

            # Installation state
            self.installation_path = "/Applications"
            self.app_name = "USB Camera Tester"
            self.temp_dir = None
            self.is_installing = False

            print("DEBUG: Creating interface...")
            self.create_interface()
            print("DEBUG: Interface created successfully")

        except Exception as e:
            print(f"DEBUG: Error in __init__: {e}")
            import traceback
            traceback.print_exc()

    def create_interface(self):
        """Create simple, reliable interface"""
        try:
            print("DEBUG: Creating main frame...")
            # Main container
            main_frame = tk.Frame(self.root, bg='white')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            print("DEBUG: Main frame created")

            # Title
            title_label = tk.Label(main_frame, text="USB Camera Hardware Test Suite - DEBUG",
                                  font=('Helvetica', 16, 'bold'), bg='white')
            title_label.pack(pady=(0, 10))
            print("DEBUG: Title label created")

            # Status label
            self.status_label = tk.Label(main_frame, text="Debug version - Ready to test",
                                        font=('Helvetica', 12), bg='white', fg='green')
            self.status_label.pack(pady=(0, 20))
            print("DEBUG: Status label created")

            # Simple test button
            test_button = tk.Button(main_frame, text="Test GUI",
                                   command=self.test_function,
                                   font=('Helvetica', 12, 'bold'),
                                   bg='#007AFF', fg='white',
                                   padx=20, pady=10)
            test_button.pack(pady=10)
            print("DEBUG: Test button created")

            # Quit button
            quit_button = tk.Button(main_frame, text="Quit",
                                   command=self.root.quit,
                                   font=('Helvetica', 10),
                                   padx=20, pady=10)
            quit_button.pack(pady=5)
            print("DEBUG: Quit button created")

            print("DEBUG: All interface elements created successfully")

        except Exception as e:
            print(f"DEBUG: Error creating interface: {e}")
            import traceback
            traceback.print_exc()

    def test_function(self):
        print("DEBUG: Test button clicked!")
        self.status_label.config(text="Test successful! GUI is working.", fg='green')

    def run(self):
        """Run the installer"""
        try:
            print("DEBUG: Starting mainloop...")
            # Center the window
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
            self.root.geometry(f"+{x}+{y}")
            print(f"DEBUG: Window centered at {x}, {y}")

            print("DEBUG: Entering mainloop...")
            self.root.mainloop()
            print("DEBUG: Mainloop ended")

        except Exception as e:
            print(f"DEBUG: Error in run(): {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("DEBUG: Script started as main")
    try:
        installer = DebugUSBCameraTesterInstaller()
        installer.run()
        print("DEBUG: Script completed successfully")
    except Exception as e:
        print(f"DEBUG: Fatal error: {e}")
        import traceback
        traceback.print_exc()