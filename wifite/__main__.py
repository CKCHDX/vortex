#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wifite.gui.launcher import get_launch_mode, PYQT5_AVAILABLE
from wifite.gui.main_window import run_gui
import sys
import os


def main():
    """Main entry point for Vortex.
    
    Determines whether to launch CLI or GUI mode based on user selection.
    """
    # Check for command line arguments
    if '--gui' in sys.argv:
        mode = 'gui'
    elif '--cli' in sys.argv:
        mode = 'cli'
    else:
        # Show launcher if PyQt5 is available
        if PYQT5_AVAILABLE:
            print('[*] Launching Vortex launcher...')
            mode = get_launch_mode()
        else:
            print('[!] PyQt5 not available. Using CLI mode.')
            print('[*] To use GUI, install PyQt5: pip3 install PyQt5')
            mode = 'cli'

    print(f'[+] Starting Vortex in {mode.upper()} mode')

    if mode == 'gui':
        try:
            from wifite.gui.main_window import run_gui
            run_gui()
        except Exception as e:
            print(f'[!] Error launching GUI: {e}')
            print('[!] Falling back to CLI mode')
            cli_main()
    else:
        cli_main()


def cli_main():
    """Run CLI mode (original wifite2 interface)."""
    from wifite.args import Arguments
    from wifite.model.target import Target
    from wifite.util.color import Color
    from wifite.config import Configuration
    import wifite.tools.airmon
    
    try:
        args = Arguments(sys.argv[1:])
        config = Configuration()
        Color.pl('{+} Starting Vortex WiFi Auditor (CLI Mode)')
        Color.pl('{+} For GUI mode, run: sudo python3 vortex.py --gui')
        
        # Original wifite2 CLI logic would go here
        # This is a placeholder for the existing implementation
        Color.pl('{!} CLI mode requires the full wifite2 implementation')
        Color.pl('{*} Please ensure all dependencies are installed')
        
    except KeyboardInterrupt:
        Color.pl('{!} Interrupted')
        sys.exit(1)
    except Exception as e:
        Color.pl(f'{{!}} Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
