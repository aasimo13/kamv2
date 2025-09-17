#!/usr/bin/env python3
"""Test which imports might be causing the grey screen"""

import tkinter as tk
from tkinter import ttk
import sys

def test_basic():
    print("=== Testing basic tkinter ===")
    root = tk.Tk()
    root.title("Basic Test")
    root.geometry("400x300")

    tk.Label(root, text="Basic tkinter works!", font=("Arial", 16)).pack(pady=50)
    tk.Button(root, text="Close", command=root.quit).pack()

    root.mainloop()
    root.destroy()

def test_with_heavy_imports():
    print("=== Testing with heavy imports ===")

    print("Importing cv2...")
    import cv2

    print("Importing numpy...")
    import numpy as np

    print("Importing PIL...")
    from PIL import Image, ImageTk

    print("Importing matplotlib...")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    print("All imports complete, creating window...")

    root = tk.Tk()
    root.title("Heavy Imports Test")
    root.geometry("600x400")

    tk.Label(root, text="Heavy imports + tkinter works!",
             font=("Arial", 16)).pack(pady=50)

    # Add a simple matplotlib plot
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_title("Test Plot")

    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().pack()

    tk.Button(root, text="Close", command=root.quit).pack(pady=10)

    print("Starting mainloop with heavy imports...")
    root.mainloop()
    root.destroy()

def main():
    try:
        test_basic()
        print("\n" + "="*50 + "\n")
        test_with_heavy_imports()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()