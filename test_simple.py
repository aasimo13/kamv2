#!/usr/bin/env python3
"""Simple test version to debug grey screen"""

import tkinter as tk
from tkinter import ttk
import sys

def main():
    print("Creating root window...")
    root = tk.Tk()
    root.title("Simple Test")
    root.geometry("800x600")
    root.configure(bg='red')  # Make it obvious if it shows

    print("Adding label...")
    label = tk.Label(root, text="TEST - If you see this, it works!",
                    font=("Arial", 24), bg='yellow', fg='black')
    label.pack(expand=True)

    print("Adding button...")
    button = tk.Button(root, text="CLICK ME", font=("Arial", 16))
    button.pack(pady=20)

    print("Showing window...")
    root.deiconify()
    root.lift()
    root.update()

    print("Starting mainloop...")
    root.mainloop()
    print("Done.")

if __name__ == "__main__":
    main()