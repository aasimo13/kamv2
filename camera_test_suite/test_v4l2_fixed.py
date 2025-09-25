#!/usr/bin/env python3
"""
V4L2 Test Script for Linux - FIXED VERSION
Tests actual V4L2 devices, not random files
"""

import sys
import subprocess
import platform
import glob
from v4l2_settings import V4L2CameraSettings, format_test_results

def main():
    print("🎥 USB Camera Tester - V4L2 Test Suite (FIXED)")
    print("=" * 55)
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

    # Find actual video devices (FIXED: use glob to find /dev/video* only)
    video_devices = []
    try:
        # Use glob to find actual video devices
        video_devices = glob.glob('/dev/video*')
        video_devices.sort()  # Sort them numerically
    except Exception as e:
        print(f"❌ Error finding video devices: {e}")

    if not video_devices:
        print("❌ No video devices found in /dev/")
        print("   Check: ls -la /dev/video*")
        print("   Connect a USB camera and try again")
        return 1

    print(f"\n🎯 Testing {len(video_devices)} video devices")
    print("-" * 35)

    for device in video_devices:
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

        # List formats (first 10 lines to avoid spam)
        try:
            print(f"\n🎨 Supported formats for {device}")
            result = subprocess.run(['v4l2-ctl', '--device', device, '--list-formats-ext'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Show only first 15 lines to avoid clutter
                lines = result.stdout.split('\n')[:15]
                print('\n'.join(lines))
                if len(result.stdout.split('\n')) > 15:
                    print("   ... (output truncated)")
        except:
            pass

        print("\n" + "=" * 60)

    # Test photo capture with ACTUAL video device (not random files!)
    print("\n📷 Photo Capture Test")
    print("-" * 20)

    for device in video_devices:
        print(f"Testing photo capture with {device}...")
        v4l2 = V4L2CameraSettings(device)

        if v4l2.check_v4l2_available():
            # Test if device actually works
            try:
                # Quick check if device is accessible
                result = subprocess.run(['v4l2-ctl', '--device', device, '--info'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    success, message = v4l2.capture_photo(f"/tmp/test_capture_{device.replace('/', '_')}.raw")
                    print(f"{'✅' if success else '❌'} {message}")
                    if success:
                        break
                else:
                    print(f"⚠️  {device} not accessible")
            except Exception as e:
                print(f"⚠️  {device} error: {e}")

    print("\n🎉 V4L2 testing complete!")
    print("\n💡 Tips:")
    print("   • Use 'v4l2-ctl --list-devices' to see all cameras")
    print("   • Use 'v4l2-ctl -d /dev/video0 --all' to see current settings")
    print("   • Use 'guvcview' for a simple camera viewer")
    print("   • Check 'dmesg | grep -i camera' for hardware messages")
    print("   • Connect USB camera and run 'lsusb | grep -i camera'")

    return 0

if __name__ == "__main__":
    sys.exit(main())