#!/usr/bin/env python3
"""
V4L2 Camera Settings Module for USB Camera Tester
Implements optimal settings for WN-L2307k368 48MP Camera
"""

import subprocess
import platform
import os
import json
from typing import Dict, Any, Optional, Tuple

class V4L2CameraSettings:
    """Manages v4l2 settings for the USB camera"""

    # Optimal settings for WN-L2307k368 camera
    OPTIMAL_SETTINGS = {
        'brightness': 15,
        'contrast': 34,
        'saturation': 32,
        'hue': 32,
        'gamma': 32,
        'gain': 1,
        'white_balance_temperature_auto': 1,
        'sharpness': 32,
        'exposure_auto': 3,  # Auto exposure
        'focus_auto': 1,     # Auto focus
    }

    # Power line frequency settings
    POWER_LINE_FREQ = {
        'US': 2,  # 60 Hz
        'EU': 1,  # 50 Hz
        'AUTO': 0  # Auto detect
    }

    # Photo capture settings
    PHOTO_RESOLUTION = {
        'width': 4000,
        'height': 3000
    }

    # Preview settings (lower res for performance)
    PREVIEW_RESOLUTION = {
        'width': 640,
        'height': 480
    }

    def __init__(self, device: str = "/dev/video0"):
        """Initialize with camera device"""
        self.device = device
        self.is_linux = platform.system() == 'Linux'
        self.region = self.detect_region()

    def detect_region(self) -> str:
        """Detect region for power line frequency"""
        # Try to detect based on timezone or locale
        try:
            import locale
            country = locale.getlocale()[0]
            if country:
                # US, Canada, Mexico, parts of South America use 60Hz
                if any(x in country.upper() for x in ['US', 'CA', 'MX', 'BR']):
                    return 'US'
                else:
                    return 'EU'
        except:
            pass
        return 'AUTO'

    def check_v4l2_available(self) -> bool:
        """Check if v4l2-ctl is available"""
        if not self.is_linux:
            return False
        try:
            result = subprocess.run(['which', 'v4l2-ctl'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def get_current_settings(self) -> Dict[str, Any]:
        """Get current camera settings"""
        if not self.check_v4l2_available():
            return {"error": "v4l2-ctl not available"}

        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', self.device, '--all'],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                return {"error": f"Failed to get settings: {result.stderr}"}

            # Parse the output
            settings = {}
            for line in result.stdout.split('\n'):
                if ':' in line and '0x' in line:
                    # Parse control lines
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        value_part = parts[1].strip()
                        # Extract value
                        if 'value=' in value_part:
                            value = value_part.split('value=')[1].split()[0]
                            settings[name] = value

            return settings

        except subprocess.TimeoutExpired:
            return {"error": "Timeout getting camera settings"}
        except Exception as e:
            return {"error": f"Error getting settings: {str(e)}"}

    def apply_optimal_settings(self) -> Tuple[bool, str]:
        """Apply optimal settings to camera"""
        if not self.check_v4l2_available():
            return False, "v4l2-ctl not available (Linux only)"

        # Build settings with region-specific power line frequency
        settings = self.OPTIMAL_SETTINGS.copy()
        settings['power_line_frequency'] = self.POWER_LINE_FREQ.get(self.region, 0)

        # Build v4l2-ctl command
        ctrl_string = ','.join([f"{k}={v}" for k, v in settings.items()])
        cmd = ['v4l2-ctl', '-d', self.device, f'--set-ctrl={ctrl_string}']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, f"Applied optimal settings (Region: {self.region})"
            else:
                return False, f"Failed to apply settings: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout applying settings"
        except Exception as e:
            return False, f"Error applying settings: {str(e)}"

    def verify_camera_model(self) -> Tuple[bool, str]:
        """Verify this is the correct camera model"""
        if not self.is_linux:
            # On macOS/Windows, we can't use lsusb easily
            return True, "Cannot verify model on non-Linux systems"

        try:
            # Check with lsusb
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            output = result.stdout.lower()

            # Known identifiers for this camera
            known_names = [
                '48m usb camera',
                'wn camera',
                'k368',
                '48mp usb camera',
                'kruu vision'
            ]

            for name in known_names:
                if name in output:
                    return True, f"Found camera: {name}"

            return False, "Camera model not recognized as WN-L2307k368"

        except Exception as e:
            return False, f"Error checking camera: {str(e)}"

    def capture_photo(self, filename: str) -> Tuple[bool, str]:
        """Capture a photo at optimal resolution"""
        if not self.check_v4l2_available():
            return False, "v4l2-ctl not available"

        try:
            # Capture using v4l2-ctl
            cmd = [
                'v4l2-ctl',
                '--device', self.device,
                '--stream-mmap',
                '--stream-count=1',
                '--stream-to=-',
                f'--set-fmt-video=width={self.PHOTO_RESOLUTION["width"]},height={self.PHOTO_RESOLUTION["height"]}'
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode != 0:
                return False, f"Capture failed: {result.stderr.decode()}"

            # Save the raw image
            with open(filename, 'wb') as f:
                f.write(result.stdout)

            # Try to process with ImageMagick if available
            try:
                # Crop to 3:2 aspect ratio
                subprocess.run([
                    'convert', filename,
                    '-gravity', 'center',
                    '-crop', '3:2',
                    filename
                ], timeout=5)
            except:
                pass  # ImageMagick not available, use raw image

            return True, f"Photo saved to {filename}"

        except subprocess.TimeoutExpired:
            return False, "Timeout capturing photo"
        except Exception as e:
            return False, f"Error capturing photo: {str(e)}"

    def test_settings(self) -> Dict[str, Any]:
        """Run comprehensive settings test"""
        results = {
            'v4l2_available': self.check_v4l2_available(),
            'region_detected': self.region,
            'power_line_freq': self.POWER_LINE_FREQ.get(self.region, 0),
            'tests': []
        }

        if not self.check_v4l2_available():
            results['tests'].append({
                'name': 'V4L2 Availability',
                'passed': False,
                'message': 'v4l2-ctl not available (Linux only feature)'
            })
            return results

        # Test 1: Verify camera model
        passed, message = self.verify_camera_model()
        results['tests'].append({
            'name': 'Camera Model Verification',
            'passed': passed,
            'message': message
        })

        # Test 2: Get current settings
        current = self.get_current_settings()
        if 'error' not in current:
            results['tests'].append({
                'name': 'Read Current Settings',
                'passed': True,
                'message': f"Read {len(current)} settings",
                'settings': current
            })
        else:
            results['tests'].append({
                'name': 'Read Current Settings',
                'passed': False,
                'message': current['error']
            })

        # Test 3: Apply optimal settings
        passed, message = self.apply_optimal_settings()
        results['tests'].append({
            'name': 'Apply Optimal Settings',
            'passed': passed,
            'message': message,
            'settings_applied': self.OPTIMAL_SETTINGS if passed else None
        })

        # Test 4: Verify settings were applied
        if passed:
            new_settings = self.get_current_settings()
            if 'error' not in new_settings:
                # Check if key settings match
                matches = 0
                total = 0
                for key, value in self.OPTIMAL_SETTINGS.items():
                    if key in new_settings:
                        total += 1
                        if str(new_settings[key]) == str(value):
                            matches += 1

                results['tests'].append({
                    'name': 'Verify Settings Applied',
                    'passed': matches == total,
                    'message': f"{matches}/{total} settings verified",
                    'verified_settings': new_settings
                })

        return results


def format_test_results(results: Dict[str, Any]) -> str:
    """Format test results for display"""
    output = []
    output.append("=" * 50)
    output.append("V4L2 CAMERA SETTINGS TEST RESULTS")
    output.append("=" * 50)
    output.append(f"V4L2 Available: {'Yes' if results['v4l2_available'] else 'No (Linux only)'}")
    output.append(f"Region Detected: {results['region_detected']}")
    output.append(f"Power Line Frequency: {results['power_line_freq']} Hz")
    output.append("")

    for test in results['tests']:
        status = "✅ PASS" if test['passed'] else "❌ FAIL"
        output.append(f"{status}: {test['name']}")
        output.append(f"  Message: {test['message']}")

        if 'settings' in test and test['settings']:
            output.append(f"  Settings Count: {len(test['settings'])}")

        if 'settings_applied' in test and test['settings_applied']:
            output.append("  Applied Settings:")
            for k, v in test['settings_applied'].items():
                output.append(f"    - {k}: {v}")

        output.append("")

    return '\n'.join(output)


# Test function for standalone execution
if __name__ == "__main__":
    print("Testing V4L2 Camera Settings...")

    # Create settings manager
    v4l2 = V4L2CameraSettings()

    # Run tests
    results = v4l2.test_settings()

    # Print results
    print(format_test_results(results))

    # Try to capture a test photo
    if v4l2.check_v4l2_available():
        print("\nAttempting to capture test photo...")
        success, message = v4l2.capture_photo("/tmp/test_photo.jpg")
        print(f"Photo Capture: {'✅' if success else '❌'} {message}")