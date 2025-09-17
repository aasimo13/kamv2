#!/usr/bin/env python3
"""
Minimal test app to diagnose GUI issues
"""
import tkinter as tk
from tkinter import ttk
import sys

print("Starting minimal test app...")

try:
    # Create root window
    print("Creating root window...")
    root = tk.Tk()
    root.title("Minimal Test - USB Camera Tester")
    root.geometry("600x400")

    # Make sure window is visible
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    print("Root window created")

    # Create simple content
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    label = ttk.Label(frame, text="USB Camera Tester - Minimal Test", font=("Arial", 16, "bold"))
    label.pack(pady=20)

    status_label = ttk.Label(frame, text="If you can see this, the GUI is working!", font=("Arial", 12))
    status_label.pack(pady=10)

    button = ttk.Button(frame, text="Test Button", command=lambda: print("Button clicked!"))
    button.pack(pady=10)

    quit_button = ttk.Button(frame, text="Quit", command=root.quit)
    quit_button.pack(pady=5)

    print("UI elements created, starting mainloop...")

    # Start the main loop
    root.mainloop()

    print("Mainloop ended normally")

except Exception as e:
    print(f"Error in minimal test: {e}")
    import traceback
    traceback.print_exc()