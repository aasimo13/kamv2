#!/usr/bin/env python3
import cv2
import sys

print("Testing camera detection...")
cameras_found = []

for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"Camera {i}: WORKING (frame size: {frame.shape})")
            cameras_found.append(i)
        else:
            print(f"Camera {i}: opened but no frame")
        cap.release()
    else:
        print(f"Camera {i}: not available")

print(f"\nFound {len(cameras_found)} working cameras: {cameras_found}")

if len(cameras_found) == 0:
    print("\nNo cameras detected. This could be due to:")
    print("1. No camera connected")
    print("2. Camera permission not granted")
    print("3. Camera in use by another application")
    print("4. Driver issues")
    sys.exit(1)
else:
    print(f"\nCamera detection successful!")
    sys.exit(0)