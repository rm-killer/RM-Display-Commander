#!/usr/bin/env python3
"""
RM Display Commander — Main Desktop Launcher
Hardware control hub for Xiaomi Mi Curved 34" and standard DDC/CI displays.
"""
import sys
import os

# Ensure src/ is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from gui import main

if __name__ == "__main__":
    main()
