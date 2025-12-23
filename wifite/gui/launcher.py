#!/usr/bin/env python3
"""Vortex Launcher - CLI/GUI Mode Selection

Provides initial prompt asking user to choose between CLI and GUI mode.
"""

import sys
import os
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFrame
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPalette
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


class VortexLauncher(QMainWindow if PYQT5_AVAILABLE else object):
    """Launcher window for selecting CLI or GUI mode."""

    def __init__(self):
        if PYQT5_AVAILABLE:
            super().__init__()
        self.mode_selected = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize launcher UI."""
        self.setWindowTitle('Vortex - WiFi Auditor')
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet(self.get_stylesheet())

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel('Vortex')
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel('WiFi Security Auditor')
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #888;')
        layout.addWidget(subtitle)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Description
        desc = QLabel('Select your preferred mode:')
        desc_font = QFont()
        desc_font.setPointSize(11)
        desc.setFont(desc_font)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # CLI Button
        cli_btn = QPushButton('CLI Mode')
        cli_btn.setMinimumSize(QSize(150, 60))
        cli_font = QFont()
        cli_font.setPointSize(11)
        cli_font.setBold(True)
        cli_btn.setFont(cli_font)
        cli_btn.setStyleSheet(
            'QPushButton {'
            '  background-color: #2C3E50;'
            '  color: white;'
            '  border: 2px solid #3498DB;'
            '  border-radius: 5px;'
            '  padding: 10px;'
            '}'
            'QPushButton:hover {'
            '  background-color: #34495E;'
            '  border: 2px solid #5DADE2;'
            '}'
            'QPushButton:pressed {'
            '  background-color: #1C2833;'
            '}'
        )
        cli_btn.clicked.connect(self.select_cli)
        button_layout.addWidget(cli_btn)

        # GUI Button
        gui_btn = QPushButton('GUI Mode')
        gui_btn.setMinimumSize(QSize(150, 60))
        gui_btn.setFont(cli_font)
        gui_btn.setStyleSheet(
            'QPushButton {'
            '  background-color: #27AE60;'
            '  color: white;'
            '  border: 2px solid #2ECC71;'
            '  border-radius: 5px;'
            '  padding: 10px;'
            '}'
            'QPushButton:hover {'
            '  background-color: #229954;'
            '  border: 2px solid #58D68D;'
            '}'
            'QPushButton:pressed {'
            '  background-color: #1E8449;'
            '}'
        )
        gui_btn.clicked.connect(self.select_gui)
        button_layout.addWidget(gui_btn)

        layout.addLayout(button_layout)

        # Info text
        info = QLabel(
            '<b>CLI Mode:</b> Traditional command-line interface<br>'
            '<b>GUI Mode:</b> Modern graphical interface with real-time updates'
        )
        info_font = QFont()
        info_font.setPointSize(9)
        info.setFont(info_font)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet('color: #AAA; margin-top: 20px;')
        layout.addWidget(info)

        layout.addStretch()

    def get_stylesheet(self):
        """Return dark theme stylesheet."""
        return """
        QMainWindow {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
        }
        QFrame {
            color: #444;
        }
        """

    def select_cli(self):
        """User selected CLI mode."""
        self.mode_selected = 'cli'
        self.close()

    def select_gui(self):
        """User selected GUI mode."""
        self.mode_selected = 'gui'
        self.close()


def get_launch_mode():
    """Show launcher and return selected mode.
    
    Returns:
        str: 'cli' or 'gui'
    """
    if not PYQT5_AVAILABLE:
        print('[!] PyQt5 not available. Falling back to CLI mode.')
        print('[*] Install PyQt5: pip3 install PyQt5')
        return 'cli'

    app = QApplication(sys.argv)
    launcher = VortexLauncher()
    launcher.show()
    app.exec_()

    return launcher.mode_selected or 'cli'


if __name__ == '__main__':
    mode = get_launch_mode()
    print(f'Selected mode: {mode}')
