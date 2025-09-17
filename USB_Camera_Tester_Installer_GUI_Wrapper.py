#!/usr/bin/env python3
"""
USB Camera Hardware Test Suite - GUI Wrapper for CLI Installer
Provides a simple GUI that launches the CLI installer in a visible way
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import sys
import os
import threading
import tempfile

class InstallerGUIWrapper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("USB Camera Tester - Installer")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.create_interface()

    def create_interface(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame,
                              text="USB Camera Hardware Test Suite",
                              font=('Helvetica', 18, 'bold'),
                              bg='white', fg='#333')
        title_label.pack(pady=(0, 5))

        # Subtitle
        subtitle_label = tk.Label(main_frame,
                                 text="Professional Installer for macOS",
                                 font=('Helvetica', 12),
                                 bg='white', fg='#666')
        subtitle_label.pack(pady=(0, 20))

        # Description
        desc_text = """This installer will:
• Download the latest USB Camera Tester from GitHub
• Install all required Python dependencies (OpenCV, NumPy, etc.)
• Create a professional macOS application bundle
• Install to your Applications folder
• Set up desktop integration (Launchpad, Spotlight)

The installation process will be shown in the terminal window below."""

        desc_label = tk.Label(main_frame, text=desc_text,
                             font=('Helvetica', 10), bg='white',
                             justify=tk.LEFT, anchor='w')
        desc_label.pack(fill=tk.X, pady=(0, 20))

        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(0, 20))

        # Install button
        self.install_button = tk.Button(button_frame,
                                       text="Install USB Camera Tester",
                                       command=self.start_installation,
                                       font=('Helvetica', 12, 'bold'),
                                       bg='#007AFF', fg='white',
                                       padx=30, pady=12)
        self.install_button.pack(side=tk.LEFT, padx=(0, 10))

        # Cancel button
        cancel_button = tk.Button(button_frame,
                                 text="Cancel",
                                 command=self.root.quit,
                                 font=('Helvetica', 10),
                                 padx=20, pady=10)
        cancel_button.pack(side=tk.LEFT)

        # Terminal output area
        terminal_frame = tk.LabelFrame(main_frame, text="Installation Progress",
                                      font=('Helvetica', 10, 'bold'), bg='white')
        terminal_frame.pack(fill=tk.BOTH, expand=True)

        self.terminal_output = scrolledtext.ScrolledText(terminal_frame,
                                                        height=15,
                                                        font=('Monaco', 10),
                                                        bg='black', fg='green',
                                                        state=tk.DISABLED)
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log_to_terminal(self, message):
        """Add message to terminal output"""
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, message + '\n')
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_installation(self):
        """Start the installation process"""
        # Confirm installation
        result = messagebox.askyesno(
            "Confirm Installation",
            "Install USB Camera Tester to Applications folder?\n\n"
            "This will:\n"
            "• Download the latest version from GitHub\n"
            "• Install Python dependencies\n"
            "• Create application bundle\n"
            "• Add to Applications folder\n\n"
            "Continue?"
        )

        if not result:
            return

        # Disable install button
        self.install_button.config(state='disabled', text='Installing...')

        # Clear terminal
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.config(state=tk.DISABLED)

        # Start installation in background thread
        install_thread = threading.Thread(target=self.run_installation, daemon=True)
        install_thread.start()

    def run_installation(self):
        """Run the CLI installer and capture output"""
        try:
            # Find the CLI installer script
            cli_installer = os.path.join(self.script_dir, "USB_Camera_Tester_Installer.py")

            if not os.path.exists(cli_installer):
                # Try in Resources directory (if running from app bundle)
                cli_installer = os.path.join(self.script_dir, "..", "Resources", "USB_Camera_Tester_Installer.py")

            if not os.path.exists(cli_installer):
                self.log_to_terminal("ERROR: CLI installer script not found!")
                self.installation_failed("CLI installer script not found")
                return

            self.log_to_terminal("🚀 Starting USB Camera Tester installation...")
            self.log_to_terminal(f"Using installer: {cli_installer}")
            self.log_to_terminal("")

            # Create a process with environment to auto-answer 'y'
            process = subprocess.Popen([sys.executable, cli_installer],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True)

            # Send 'y' to confirm installation
            process.stdin.write('y\n')
            process.stdin.flush()

            # Read output line by line
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_to_terminal(output.strip())

            # Wait for process to complete
            return_code = process.poll()

            if return_code == 0:
                self.log_to_terminal("")
                self.log_to_terminal("🎉 Installation completed successfully!")
                self.installation_complete()
            else:
                self.log_to_terminal(f"Installation failed with return code: {return_code}")
                self.installation_failed("Installation process failed")

        except Exception as e:
            self.log_to_terminal(f"ERROR: {str(e)}")
            self.installation_failed(str(e))

    def installation_complete(self):
        """Handle successful installation"""
        self.install_button.config(state='normal', text='Installation Complete ✓')
        self.install_button.config(state='disabled')

        # Show success dialog
        result = messagebox.askyesno(
            "Installation Complete!",
            "USB Camera Tester has been successfully installed!\n\n"
            "The application is now available in:\n"
            "• Applications folder\n"
            "• Launchpad\n"
            "• Spotlight search\n\n"
            "Would you like to launch the application now?"
        )

        if result:
            try:
                subprocess.run(["open", "/Applications/USB Camera Tester.app"])
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Launch Error",
                                   f"Could not launch application: {str(e)}")

    def installation_failed(self, error_message):
        """Handle installation failure"""
        self.install_button.config(state='normal', text='Install USB Camera Tester')

        messagebox.showerror(
            "Installation Failed",
            f"The installation encountered an error:\n\n{error_message}\n\n"
            "Please check the terminal output above for more details."
        )

    def run(self):
        """Run the GUI"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = InstallerGUIWrapper()
        app.run()
    except Exception as e:
        # Fallback error handling
        import tkinter.messagebox as mb
        mb.showerror("Error", f"Failed to start installer GUI: {str(e)}")
        sys.exit(1)