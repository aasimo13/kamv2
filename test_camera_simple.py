#!/usr/bin/env python3
"""Simplified camera app to debug grey screen issue"""

import tkinter as tk
from tkinter import ttk
import platform

class SimpleCameraTest:
    def __init__(self):
        print("Creating window...")
        self.root = tk.Tk()
        self.root.title("USB Camera Test - Simple")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        print("Creating widgets...")
        # Simple UI
        label = tk.Label(self.root, text="USB Camera Tester",
                        font=("Arial", 20), bg='white')
        label.pack(pady=20)

        button = tk.Button(self.root, text="Test Button",
                          font=("Arial", 14))
        button.pack(pady=10)

        # Text area
        text = tk.Text(self.root, height=10, width=50)
        text.pack(pady=10)
        text.insert(tk.END, "This is a test.\n")
        text.insert(tk.END, f"Platform: {platform.system()}\n")
        text.insert(tk.END, "If you see this, the basic UI works.\n")

        print("Setup complete, showing window...")

    def run(self):
        print("Starting mainloop...")
        self.root.mainloop()
        print("Mainloop ended")

def main():
    app = SimpleCameraTest()
    app.run()

if __name__ == "__main__":
    main()