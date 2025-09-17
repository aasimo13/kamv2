#!/usr/bin/env python3
"""Debug version that progressively adds main app components"""

import tkinter as tk
from tkinter import ttk
import platform
import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DebugCameraApp:
    def __init__(self):
        print("=== Starting Debug Camera App ===")

        print("1. Creating root window...")
        self.root = tk.Tk()
        self.root.title("Debug USB Camera Test")
        self.root.geometry("1200x800")
        self.root.configure(bg='lightblue')  # Different color to see if it shows

        print("2. Basic setup...")
        self.camera = None
        self.test_results = []

        print("3. Creating notebook...")
        self.create_ui()

        print("4. Setup complete!")

    def create_ui(self):
        print("  Creating notebook widget...")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        print("  Creating tab 1...")
        self.create_simple_tab()

        print("  Creating tab 2...")
        self.create_test_tab()

        print("  UI creation complete")

    def create_simple_tab(self):
        # Simple tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Simple Test")

        label = tk.Label(frame, text="This is a simple tab",
                        font=("Arial", 16))
        label.pack(pady=20)

        button = tk.Button(frame, text="Test Button")
        button.pack(pady=10)

    def create_test_tab(self):
        # More complex tab with text widget
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tests")

        # Text output
        self.test_output = tk.Text(frame, height=15, width=80)
        self.test_output.pack(padx=10, pady=10)

        self.test_output.insert(tk.END, "Test output area\n")
        self.test_output.insert(tk.END, f"Platform: {platform.system()}\n")
        self.test_output.insert(tk.END, "If you see this, the notebook works!\n")

    def run(self):
        print("=== Starting mainloop ===")
        self.root.mainloop()
        print("=== Mainloop ended ===")

def main():
    app = DebugCameraApp()
    app.run()

if __name__ == "__main__":
    main()