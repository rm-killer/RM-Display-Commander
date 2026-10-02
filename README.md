# RM Display Commander — Xiaomi Mi Curved 34" Control Hub

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2011%20%7C%2010-0078D6.svg)
![Monitor](https://img.shields.io/badge/monitor-Xiaomi%20Mi%20Curved%2034%22-FF6900.svg)
![Protection](https://img.shields.io/badge/safety-VCP%200xD6%20Immunity-10B981.svg)

A modern, native dark-mode Windows desktop control suite for the **Xiaomi Mi Curved Gaming Monitor 34"** (and compliant MStar DDC/CI displays). Control every physical setting of your monitor directly from Windows over **DisplayPort** or **HDMI** without ever touching the physical buttons behind the display.

---

## The Problem It Solves

Most popular monitor control utilities (e.g. *BetterDisplay*, *Twinkle Tray*, *Monitorian*, *ClickMonitorDDC*, *NirSoft ControlMyMonitor*) send the VESA power command (`VCP 0xD6`) to turn displays off. On Xiaomi monitors powered by the MStar MST9U scaler, this trips a **firmware bug that corrupts the settings EEPROM**, causing the physical OSD menu to permanently disappear and turning the screen black for 2 seconds on joystick clicks.

**RM Display Commander incorporates a hardwired hardware safety gate:**
- Permanently blocks `VCP 0xD6` in code.
- Eliminates any risk of bricking your monitor's OSD.
- Delivers 100% verified, real-time control over all active hardware registers.

---

## Features

### 1. Image & Luminance Tuning
- **Real-time Sliders:** Instant adjustments for Brightness, Contrast, Sharpness, Black Equalizer, and Color Saturation.
- **Hardware-Direct:** Bypasses software overlay filters; adjusts the monitor panel directly.

### 2. Native SmartMode Hardware Profiles
Calibrated against live hardware scans of the Xiaomi 34" scaler:
- **Standard Mode:** Factory baseline (Brightness 70, Contrast 75, Sharpness 50, Black Level 50).
- **ECO Mode:** Power-saving preset (Brightness 40, Contrast 75).
- **RTS Mode:** Real-Time Strategy preset (Brightness 85, Contrast 80).
- **Game / FPS Mode:** High-visibility competitive preset (Brightness 100, Contrast 75).
- **Movie Mode:** High-contrast multimedia preset (Brightness 100, Contrast 80).
- **Reader / Low Blue Light Mode:** Calibrated eye-care mode (Brightness 50, Contrast 70, physical Blue channel gain cut by 40% to warm the white point).

### 3. Color & Channels
- **Color Temperature Presets:** Standard (Neutral), Warm, Cool, and Custom RGB.
- **Individual RGB Gain Tuning:** Tactile Red, Green, and Blue gain sliders (0–100).

### 4. Aspect Ratio Scaling
- One-click hardware aspect ratio switching:
  - `Auto / Full Screen` (3440x1440 fullscreen)
  - `16:9 Standard` (Centered pillarboxed 2560x1440)
  - `21:9 Ultrawide` (Original panel aspect)

### 5. 1-Click Video Input Switcher
- Instantly switch display inputs from your desktop:
  - **DisplayPort 1** (`0x0F`)
  - **DisplayPort 2** (`0x10`)
  - **HDMI 1** (`0x11`)
  - **HDMI 2** (`0x12`)

---

## Download & Usage

### Option 1: Standalone Portable Binary (Recommended)
1. Download the latest **`RM-Display-Commander.exe`** from [Releases](https://github.com/rm-killer/RM-Display-Commander/releases).
2. Run the executable. No installation, no drivers, and no background terminal windows required.

### Option 2: Running from Source
Requires Python 3.8+ on Windows:
```cmd
git clone https://github.com/rm-killer/RM-Display-Commander.git
cd RM-Display-Commander
pip install customtkinter darkdetect
python main.py
```

---

## Technical Details

- **Protocol:** VESA Monitor Control Command Set (MCCS 2.1) over DisplayPort AUX / HDMI I2C via Windows `dxva2.dll`.
- **UI Framework:** CustomTkinter (modern dark-mode hardware aesthetic).
- **Zero VRAM / 0% GPU Overhead:** Pure Win32 calls and lightweight native canvas rendering that will never interfere with GPU rendering or crypto mining workloads.

---

## License

MIT License — Copyright (c) 2026 rm-killer (RM the Boss).
