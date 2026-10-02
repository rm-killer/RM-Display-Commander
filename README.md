# RM Display Commander

A modern, native Windows 11 hardware control suite for the **Xiaomi Mi Curved Gaming Monitor 34"** (and compliant DDC/CI monitors).

Control every physical setting of your monitor directly from your desktop over DisplayPort or HDMI without ever reaching behind the display.

---

## Features

- **Luminance & Picture Tuning:**
  - Real-time sliders for Brightness, Contrast, Sharpness, Black Equalizer, and Dynamic Luminance (DCR).
- **Gaming & Presets:**
  - One-click SmartMode selection (Standard, Movie, FPS Game, Reader).
  - FreeSync Premium toggle.
- **Color Temperature & User RGB:**
  - Presets (Standard, Warm, Cool, Custom).
  - Individual Red, Green, and Blue Gain calibration sliders (0–100).
- **1-Click Input Switching:**
  - Instant toggle between DisplayPort 1, DisplayPort 2, HDMI 1, and HDMI 2.
- **Hardware Bug Immunity:**
  - Built-in hard safety gate that permanently blocks `VCP 0xD6` (Power Mode) to prevent the notorious MStar OSD black-screen lockout bug.

---

## Requirements

- **OS:** Windows 10 / Windows 11 (64-bit)
- **Connection:** Standard DisplayPort or HDMI cable connected directly to GPU.
- **Python:** Python 3.8+ (standard library only; uses native `ctypes` Win32 `dxva2.dll` APIs).

---

## Launching

Double-click `RM Display Commander.lnk` on your Desktop, or run:
```cmd
python main.py
```

---

## License

MIT License — Copyright (c) 2026 rm-killer (RM the Boss).
