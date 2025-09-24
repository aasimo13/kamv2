# V4L2 Camera Settings Guide

## Overview
The USB Camera Tester now includes comprehensive V4L2 support for Linux systems, specifically optimized for the **WN-L2307k368 48MP Camera** with **Samsung S5KGM1ST sensor**.

## Optimal Camera Settings

### Core Settings (Applied Automatically)
```bash
v4l2-ctl -d /dev/video0 --set-ctrl=\
brightness=15,\
contrast=34,\
saturation=32,\
hue=32,\
gamma=32,\
gain=1,\
white_balance_temperature_auto=1,\
sharpness=32,\
exposure_auto=3,\
focus_auto=1
```

### Regional Power Line Frequency
- **US/Canada/Mexico**: `power_line_frequency=2` (60 Hz)
- **EU/Asia/Other**: `power_line_frequency=1` (50 Hz)
- **Auto-detect**: `power_line_frequency=0` (Default)

The app automatically detects your region based on system locale.

## Camera Identification

The camera is detected by `lsusb` with these identifiers:
- `48M USB Camera WN Camera K368`
- `48MP USB Camera` (various manufacturers)
- `KRUU Vision` variants

## Resolution Settings

### Photo Capture (High Quality)
- **Resolution**: 4000×3000 pixels
- **Format**: Raw capture with optional 3:2 crop
- **Command**:
```bash
v4l2-ctl --device /dev/video0 \
--stream-mmap --stream-count=1 \
--stream-to=- \
--set-fmt-video=width="4000",height="3000"
```

### Live Preview (Performance Optimized)
- **Resolution**: 640×480 pixels
- **Format**: JPEG
- **Quality**: 75%
- **Usage**: `ustreamer --device=/dev/video0 --resolution=640x480`

## Test Suite Integration

### V4L2 Optimal Settings Test
The USB Camera Tester includes a dedicated "V4L2 Optimal Settings" test that:

1. **Verifies Camera Model** - Confirms WN-L2307k368 camera
2. **Reads Current Settings** - Shows existing v4l2 controls
3. **Applies Optimal Settings** - Sets recommended values
4. **Validates Configuration** - Confirms settings were applied
5. **Regional Detection** - Auto-sets power line frequency

### Test Results Include:
- ✅ Current camera control values
- ✅ Applied optimal settings with explanations
- ✅ Regional power line frequency (50Hz/60Hz)
- ✅ Architecture compatibility (ARM64/x86_64)
- ✅ Photo capture capabilities test

## Platform Support

- **Linux**: Full V4L2 support with all features
- **macOS/Windows**: Test shows "SKIP" with explanation (V4L2 Linux-only)

## Manual Commands

### View All Current Settings
```bash
v4l2-ctl --all
```

### Apply Optimal Settings Manually
```bash
v4l2-ctl -d /dev/video0 --set-ctrl=brightness=15,contrast=34,saturation=32,hue=32,gamma=32,gain=1,power_line_frequency=2,white_balance_temperature_auto=1,sharpness=32,exposure_auto=3,focus_auto=1
```

### Capture Photo with Crop
```bash
v4l2-ctl --device /dev/video0 --stream-mmap --stream-count=1 --stream-to=- --set-fmt-video=width="4000",height="3000" | convert - -gravity center -crop 3:2 photo.jpg
```

## Integration Benefits

1. **Consistent Quality** - Optimal settings ensure consistent photo quality
2. **Regional Adaptation** - Auto-detects power line frequency for your region
3. **Professional Results** - Settings optimized for photobooth applications
4. **Easy Testing** - One-click verification of all camera parameters
5. **Documentation** - Complete parameter listing in test results

## Technical Details

- **Sensor**: Samsung S5KGM1ST ISOCELL GM1
- **Max Resolution**: 8000×6000 (48MP)
- **Binned Resolution**: 4000×3000 (12MP binned)
- **Pixel Size**: 0.8μm
- **Interface**: USB 2.0
- **Autofocus**: PDAF (Phase Detection AutoFocus)
- **Max Framerate**: 8fps @ 48MP

---

**Note**: V4L2 controls are Linux-specific. On macOS and Windows, the test will show "SKIP" status with an explanation.