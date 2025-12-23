#!/usr/bin/env python3
"""Vortex GUI Launcher

Convenience script to directly launch Vortex GUI.
Usage: sudo python3 vortex-gui.py
"""

import sys
import os

# Ensure we're running as root
if os.geteuid() != 0:
    print('[!] This script must be run as root')
    print('[*] Try: sudo python3 vortex-gui.py')
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifite.gui.main_window import run_gui

if __name__ == '__main__':
    print('[+] Launching Vortex GUI...')
    success = run_gui()
    if not success:
        print('[!] Failed to launch GUI')
        sys.exit(1)
