#!/usr/bin/env python3
"""
V4L2 Test Script for Linux
Tests all V4L2 functionality without GUI
Perfect for Raspberry Pi and headless testing
"""

import sys
import subprocess
import platform
from v4l2_settings import V4L2CameraSettings, format_test_results

def main():
    print("🎥 USB Camera Tester - V4L2 Test Suite")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print("")

    # Test system V4L2 capabilities
    print("🔧 System V4L2 Check")
    print("-" * 20)

    # Check v4l2-ctl availability
    try:
        result = subprocess.run(['which', 'v4l2-ctl'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ v4l2-ctl found: {result.stdout.strip()}")
        else:
            print("❌ v4l2-ctl not found")
            print("   Install: sudo apt install v4l-utils")
            return 1
    except Exception as e:
        print(f"❌ Error checking v4l2-ctl: {e}")
        return 1

    # List V4L2 devices
    print("\n📹 V4L2 Devices")
    print("-" * 15)
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ No V4L2 devices found")
    except Exception as e:
        print(f"❌ Error listing devices: {e}")

    # Test each video device
    video_devices = []
    try:
        result = subprocess.run(['ls', '/dev/video*'],
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            video_devices = result.stdout.strip().split('\n')
    except:
        pass

    if not video_devices:
        print("❌ No video devices found in /dev/")
        return 1

    print(f"\n🎯 Testing {len(video_devices)} video devices")
    print("-" * 30)

    for device in video_devices:
        device = device.strip()
        if not device:
            continue

        print(f"\n📸 Testing {device}")
        print("-" * (len(device) + 10))

        # Create V4L2 settings instance for this device
        v4l2 = V4L2CameraSettings(device)

        # Run comprehensive test
        results = v4l2.test_settings()

        # Display formatted results
        print(format_test_results(results))

        # Additional device info
        try:
            print(f"\n📋 Device Info for {device}")
            result = subprocess.run(['v4l2-ctl', '--device', device, '--info'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
        except:
            pass

        # List formats
        try:
            print(f"\n🎨 Supported formats for {device}")
            result = subprocess.run(['v4l2-ctl', '--device', device, '--list-formats-ext'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Show only first 20 lines to avoid clutter
                lines = result.stdout.split('\n')[:20]
                print('\n'.join(lines))
                if len(result.stdout.split('\n')) > 20:
                    print("   ... (output truncated)")
        except:
            pass

        print("\n" + "=" * 60)

    # Test photo capture with first working camera
    print("\n📷 Photo Capture Test")
    print("-" * 20)

    for device in video_devices:
        device = device.strip()
        if not device:
            continue

        v4l2 = V4L2CameraSettings(device)
        if v4l2.check_v4l2_available():
            print(f"Testing photo capture with {device}...")
            success, message = v4l2.capture_photo("/tmp/test_capture.raw")
            print(f"{'✅' if success else '❌'} {message}")
            if success:
                break

    print("\n🎉 V4L2 testing complete!")
    print("\n💡 Tips:")
    print("   • Use 'v4l2-ctl --list-devices' to see all cameras")
    print("   • Use 'v4l2-ctl -d /dev/video0 --all' to see current settings")
    print("   • Use 'guvcview' for a simple camera viewer")
    print("   • Check 'dmesg | grep -i camera' for hardware messages")

    return 0

if __name__ == "__main__":
    sys.exit(main())