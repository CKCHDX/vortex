#!/usr/bin/env python3
"""Vortex GUI Test Launcher for Windows (with import error handling)

Run this file to test the GUI without needing Linux dependencies.

Usage: python test_gui_windows.py
"""

import sys
import os

# Check if PyQt5 is installed first
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, 
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QCheckBox, QFileDialog,
        QProgressBar, QMessageBox, QStatusBar
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QColor
    print('[+] PyQt5 imported successfully')
except ImportError as e:
    print(f'[!] ERROR: PyQt5 is not installed')
    print(f'[!] Error details: {e}')
    print()
    print('[*] Install PyQt5 with:')
    print('    pip install PyQt5')
    print()
    print('[*] Or for a fresh install:')
    print('    pip install --upgrade PyQt5')
    sys.exit(1)


class NetworkScanThread(QThread):
    """Background thread for scanning WiFi networks (Demo mode on Windows)."""
    
    scan_result = pyqtSignal(dict)
    scan_progress = pyqtSignal(str)
    scan_complete = pyqtSignal()

    def __init__(self, interface=None):
        super().__init__()
        self.interface = interface
        self.is_running = True

    def run(self):
        """Execute network scan (simulated for Windows)."""
        try:
            self.scan_progress.emit('[*] Starting network scan...')
            
            # Simulate some networks
            networks = [
                {
                    'ssid': 'Sample-Network-1',
                    'bssid': '00:11:22:33:44:55',
                    'channel': 6,
                    'signal': -45,
                    'encryption': 'WPA2',
                    'clients': 2
                },
                {
                    'ssid': 'Guest-WiFi',
                    'bssid': 'AA:BB:CC:DD:EE:FF',
                    'channel': 11,
                    'signal': -60,
                    'encryption': 'WPA2',
                    'clients': 5
                },
                {
                    'ssid': 'Old-Network',
                    'bssid': '12:34:56:78:90:AB',
                    'channel': 1,
                    'signal': -75,
                    'encryption': 'WEP',
                    'clients': 1
                },
            ]
            
            for network in networks:
                if not self.is_running:
                    break
                self.scan_progress.emit(f'[*] Found: {network["ssid"]}')
                self.scan_result.emit(network)
            
            self.scan_progress.emit('[+] Scan complete')
            self.scan_complete.emit()
        except Exception as e:
            self.scan_progress.emit(f'[!] Error: {str(e)}')


class VortexMainWindow(QMainWindow):
    """Main Vortex GUI window."""

    def __init__(self):
        super().__init__()
        self.scan_thread = None
        self.target_ap = None
        self.wordlist_path = None
        self.setup_ui()
        self.apply_dark_theme()

    def setup_ui(self):
        """Initialize main window UI."""
        self.setWindowTitle('Vortex - WiFi Security Auditor [DEMO MODE - Windows]')
        self.setGeometry(50, 50, 1400, 900)
        self.setMinimumSize(1200, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Network Scanner
        tabs.addTab(self.create_scanner_tab(), 'Network Scanner')
        
        # Tab 2: Attack Configuration
        tabs.addTab(self.create_attack_tab(), 'Attack Configuration')
        
        # Tab 3: Handshake Capture
        tabs.addTab(self.create_handshake_tab(), 'Handshake Capture')
        
        # Tab 4: Cracking
        tabs.addTab(self.create_cracking_tab(), 'Cracking')
        
        # Tab 5: Console
        tabs.addTab(self.create_console_tab(), 'Console')

        main_layout.addWidget(tabs)

        # Status bar
        self.statusBar().showMessage('Ready (Demo Mode - Windows)')

    def create_scanner_tab(self):
        """Create network scanner tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel('Discovered Networks')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel('Click "Start Scan" to discover WiFi networks (Demo mode simulates networks)')
        layout.addWidget(desc)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton('Start Scan')
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setStyleSheet(self.get_button_style('green'))
        button_layout.addWidget(self.scan_btn)

        stop_btn = QPushButton('Stop Scan')
        stop_btn.setMinimumHeight(40)
        stop_btn.clicked.connect(self.stop_scan)
        stop_btn.setStyleSheet(self.get_button_style('red'))
        button_layout.addWidget(stop_btn)

        refresh_btn = QPushButton('Refresh')
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.refresh_networks)
        refresh_btn.setStyleSheet(self.get_button_style('blue'))
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Network table
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(6)
        self.network_table.setHorizontalHeaderLabels(['SSID', 'BSSID', 'Channel', 'Signal', 'Encryption', 'Clients'])
        self.network_table.setSelectionBehavior(self.network_table.SelectRows)
        self.network_table.setSelectionMode(self.network_table.SingleSelection)
        self.network_table.itemSelectionChanged.connect(self.on_network_selected)
        layout.addWidget(self.network_table)

        # Selected AP info
        info_layout = QHBoxLayout()
        
        info_left = QVBoxLayout()
        info_left.addWidget(QLabel('<b>Selected AP</b>'))
        self.selected_ap_label = QLabel('None')
        self.selected_ap_label.setStyleSheet('color: #888;')
        info_left.addWidget(self.selected_ap_label)
        info_layout.addLayout(info_left)

        info_right = QVBoxLayout()
        info_right.addWidget(QLabel('<b>Status</b>'))
        self.status_label = QLabel('Ready')
        self.status_label.setStyleSheet('color: #2ECC71;')
        info_right.addWidget(self.status_label)
        info_layout.addLayout(info_right)

        layout.addLayout(info_layout)

        return widget

    def create_attack_tab(self):
        """Create attack configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel('Attack Configuration')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Attack type
        attack_layout = QHBoxLayout()
        attack_layout.addWidget(QLabel('Attack Method:'))
        self.attack_combo = QComboBox()
        self.attack_combo.addItems([
            'WPA2 Handshake + Dictionary',
            'WPA2 PMKID (Hashcat)',
            'WPS Pixie Dust',
            'WPS Brute Force',
            'WEP Fragmentation',
            'WEP ChopChop'
        ])
        attack_layout.addWidget(self.attack_combo)
        layout.addLayout(attack_layout)

        # Deauth settings
        deauth_layout = QHBoxLayout()
        deauth_layout.addWidget(QLabel('Deauth Frames:'))
        self.deauth_spin = QSpinBox()
        self.deauth_spin.setValue(10)
        self.deauth_spin.setMinimum(1)
        self.deauth_spin.setMaximum(100)
        deauth_layout.addWidget(self.deauth_spin)
        layout.addLayout(deauth_layout)

        # Timeout settings
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel('Handshake Timeout (seconds):'))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setValue(30)
        self.timeout_spin.setMinimum(5)
        self.timeout_spin.setMaximum(300)
        timeout_layout.addWidget(self.timeout_spin)
        layout.addLayout(timeout_layout)

        # Wordlist selection
        wordlist_layout = QHBoxLayout()
        wordlist_layout.addWidget(QLabel('Wordlist:'))
        self.wordlist_input = QLineEdit()
        self.wordlist_input.setPlaceholderText('C:/path/to/wordlist.txt')
        wordlist_layout.addWidget(self.wordlist_input)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_wordlist)
        browse_btn.setStyleSheet(self.get_button_style('blue'))
        wordlist_layout.addWidget(browse_btn)
        layout.addLayout(wordlist_layout)

        # Advanced options
        self.gpu_check = QCheckBox('Use GPU Acceleration (Hashcat)')
        layout.addWidget(self.gpu_check)

        self.verbose_check = QCheckBox('Verbose Output')
        layout.addWidget(self.verbose_check)

        layout.addStretch()

        return widget

    def create_handshake_tab(self):
        """Create handshake capture tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel('WPA2 4-Way Handshake Capture')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        desc = QLabel('Capture EAPOL key frames between AP and client for offline cracking.')
        layout.addWidget(desc)

        # Control buttons
        control_layout = QHBoxLayout()
        
        self.deauth_btn = QPushButton('Send Deauth')
        self.deauth_btn.setMinimumHeight(40)
        self.deauth_btn.clicked.connect(self.send_deauth)
        self.deauth_btn.setStyleSheet(self.get_button_style('orange'))
        control_layout.addWidget(self.deauth_btn)

        self.capture_btn = QPushButton('Start Capture')
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.clicked.connect(self.start_capture)
        self.capture_btn.setStyleSheet(self.get_button_style('green'))
        control_layout.addWidget(self.capture_btn)

        layout.addLayout(control_layout)

        # Capture status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('<b>EAPOL Frames:</b>'))
        self.eapol_label = QLabel('0/4')
        self.eapol_label.setStyleSheet('color: #E74C3C;')
        status_layout.addWidget(self.eapol_label)
        status_layout.addWidget(QLabel('<b>Captured At:</b>'))
        self.capture_time_label = QLabel('-')
        status_layout.addWidget(self.capture_time_label)
        layout.addLayout(status_layout)

        # PMKID status
        pmkid_layout = QHBoxLayout()
        pmkid_layout.addWidget(QLabel('<b>PMKID Found:</b>'))
        self.pmkid_label = QLabel('No')
        self.pmkid_label.setStyleSheet('color: #E74C3C;')
        pmkid_layout.addWidget(self.pmkid_label)
        layout.addLayout(pmkid_layout)

        # Capture log
        self.capture_log = QTextEdit()
        self.capture_log.setReadOnly(True)
        self.capture_log.setPlaceholderText('[DEMO MODE] This is where handshake capture logs would appear. On Linux with proper hardware, this would show real EAPOL frame captures.')
        layout.addWidget(self.capture_log)

        return widget

    def create_cracking_tab(self):
        """Create password cracking tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel('Password Cracking')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Stats
        stats_layout = QHBoxLayout()
        
        keys_layout = QVBoxLayout()
        keys_layout.addWidget(QLabel('<b>Keys Tested</b>'))
        self.keys_label = QLabel('0')
        self.keys_label.setStyleSheet('color: #3498DB; font-size: 14px; font-weight: bold;')
        keys_layout.addWidget(self.keys_label)
        stats_layout.addLayout(keys_layout)

        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel('<b>Speed (keys/s)</b>'))
        self.speed_label = QLabel('0')
        self.speed_label.setStyleSheet('color: #3498DB; font-size: 14px; font-weight: bold;')
        speed_layout.addWidget(self.speed_label)
        stats_layout.addLayout(speed_layout)

        layout.addLayout(stats_layout)

        # Progress
        self.crack_progress = QProgressBar()
        self.crack_progress.setValue(0)
        layout.addWidget(self.crack_progress)

        # Result
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel('<b>Password Found:</b>'))
        self.password_label = QLabel('-')
        self.password_label.setStyleSheet('color: #2ECC71; font-weight: bold;')
        result_layout.addWidget(self.password_label)
        layout.addLayout(result_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        
        self.crack_btn = QPushButton('Start Cracking')
        self.crack_btn.setMinimumHeight(40)
        self.crack_btn.clicked.connect(self.start_cracking)
        self.crack_btn.setStyleSheet(self.get_button_style('green'))
        button_layout.addWidget(self.crack_btn)

        stop_crack_btn = QPushButton('Stop')
        stop_crack_btn.setMinimumHeight(40)
        stop_crack_btn.clicked.connect(self.stop_cracking)
        stop_crack_btn.setStyleSheet(self.get_button_style('red'))
        button_layout.addWidget(stop_crack_btn)

        layout.addLayout(button_layout)

        # Cracking log
        self.crack_log = QTextEdit()
        self.crack_log.setReadOnly(True)
        self.crack_log.setPlaceholderText('[DEMO MODE] This is where cracking progress would appear. On Linux, actual password cracking would happen here.')
        layout.addWidget(self.crack_log)

        return widget

    def create_console_tab(self):
        """Create console output tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel('Live Console Output')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont('Courier', 10))
        self.console_output.setStyleSheet('background-color: #0D0D0D; color: #00FF00;')
        self.console_output.append('[+] Vortex GUI loaded in demo mode (Windows)')
        self.console_output.append('[*] This is a UI preview - actual attacks require Linux with monitor-capable wireless hardware')
        layout.addWidget(self.console_output)

        # Clear button
        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_console)
        clear_btn.setStyleSheet(self.get_button_style('red'))
        layout.addWidget(clear_btn)

        return widget

    def start_scan(self):
        """Start network scanning."""
        self.scan_btn.setEnabled(False)
        self.statusBar().showMessage('Scanning networks...')
        self.scan_thread = NetworkScanThread()
        self.scan_thread.scan_result.connect(self.add_network)
        self.scan_thread.scan_progress.connect(self.update_console)
        self.scan_thread.scan_complete.connect(self.scan_complete)
        self.scan_thread.start()

    def stop_scan(self):
        """Stop network scanning."""
        if self.scan_thread:
            self.scan_thread.is_running = False
            self.scan_thread.wait()
        self.scan_btn.setEnabled(True)
        self.statusBar().showMessage('Scan stopped')

    def refresh_networks(self):
        """Refresh network list."""
        self.network_table.setRowCount(0)
        self.update_console('[*] Refreshing network list...')
        self.start_scan()

    def add_network(self, network_info):
        """Add network to table."""
        row = self.network_table.rowCount()
        self.network_table.insertRow(row)
        
        self.network_table.setItem(row, 0, QTableWidgetItem(network_info.get('ssid', '')))
        self.network_table.setItem(row, 1, QTableWidgetItem(network_info.get('bssid', '')))
        self.network_table.setItem(row, 2, QTableWidgetItem(str(network_info.get('channel', ''))))
        self.network_table.setItem(row, 3, QTableWidgetItem(str(network_info.get('signal', ''))))
        self.network_table.setItem(row, 4, QTableWidgetItem(network_info.get('encryption', '')))
        self.network_table.setItem(row, 5, QTableWidgetItem(str(network_info.get('clients', ''))))

    def on_network_selected(self):
        """Handle network selection."""
        rows = self.network_table.selectedIndexes()
        if rows:
            row = rows[0].row()
            ssid = self.network_table.item(row, 0).text()
            bssid = self.network_table.item(row, 1).text()
            self.target_ap = {'ssid': ssid, 'bssid': bssid}
            self.selected_ap_label.setText(f'{ssid} ({bssid})')
            self.status_label.setText('Target Selected')
            self.status_label.setStyleSheet('color: #F39C12;')
            self.update_console(f'[+] Target selected: {ssid}')

    def scan_complete(self):
        """Handle scan completion."""
        self.scan_btn.setEnabled(True)
        self.statusBar().showMessage('Scan complete')

    def send_deauth(self):
        """Send deauthentication frames."""
        if not self.target_ap:
            QMessageBox.warning(self, 'No Target', 'Please select a target AP first')
            return
        msg = f'[*] Sending {self.deauth_spin.value()} deauth frames to {self.target_ap["bssid"]}'
        self.capture_log.append(msg)
        self.update_console(msg)

    def start_capture(self):
        """Start handshake capture."""
        if not self.target_ap:
            QMessageBox.warning(self, 'No Target', 'Please select a target AP first')
            return
        msg = f'[*] Capturing handshake for {self.target_ap["ssid"]}'
        self.capture_log.append(msg)
        self.eapol_label.setText('0/4')
        self.eapol_label.setStyleSheet('color: #E74C3C;')
        self.update_console(msg)

    def start_cracking(self):
        """Start password cracking."""
        if not self.wordlist_input.text():
            QMessageBox.warning(self, 'No Wordlist', 'Please select a wordlist')
            return
        msg = '[*] Starting dictionary attack...'
        self.crack_log.append(msg)
        self.crack_progress.setValue(0)
        self.update_console(msg)

    def stop_cracking(self):
        """Stop password cracking."""
        msg = '[!] Cracking stopped'
        self.crack_log.append(msg)
        self.update_console(msg)

    def browse_wordlist(self):
        """Browse for wordlist file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Wordlist',
            os.path.expanduser('~'),
            'Text Files (*.txt);;All Files (*)'
        )
        if file_path:
            self.wordlist_input.setText(file_path)
            self.wordlist_path = file_path
            self.update_console(f'[+] Wordlist selected: {file_path}')

    def clear_console(self):
        """Clear console output."""
        self.console_output.clear()

    def update_console(self, message):
        """Update console with message."""
        self.console_output.append(message)

    def apply_dark_theme(self):
        """Apply dark theme to entire window."""
        self.setStyleSheet(self.get_dark_theme_stylesheet())

    def get_dark_theme_stylesheet(self):
        """Return dark theme stylesheet."""
        return """
        QMainWindow, QWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QTabWidget::pane {
            border: 1px solid #333;
        }
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #FFFFFF;
            padding: 8px 20px;
            border: 1px solid #333;
        }
        QTabBar::tab:selected {
            background-color: #3D3D3D;
            border-bottom: 2px solid #2ECC71;
        }
        QTableWidget {
            background-color: #252525;
            alternate-background-color: #2D2D2D;
            color: #FFFFFF;
            gridline-color: #333;
        }
        QHeaderView::section {
            background-color: #2D2D2D;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #333;
        }
        QTextEdit {
            background-color: #0D0D0D;
            color: #FFFFFF;
            border: 1px solid #333;
        }
        QLineEdit, QComboBox, QSpinBox {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #444;
            padding: 5px;
            border-radius: 3px;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1px solid #2ECC71;
        }
        QCheckBox {
            color: #FFFFFF;
        }
        QProgressBar {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #0D0D0D;
        }
        QProgressBar::chunk {
            background-color: #2ECC71;
        }
        QStatusBar {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border-top: 1px solid #333;
        }
        """

    def get_button_style(self, color='blue'):
        """Get button style for given color."""
        colors = {
            'green': ('#27AE60', '#2ECC71'),
            'red': ('#C0392B', '#E74C3C'),
            'blue': ('#2C3E50', '#3498DB'),
            'orange': ('#D68910', '#F39C12')
        }
        bg, border = colors.get(color, colors['blue'])
        return f"""
        QPushButton {{
            background-color: {bg};
            color: white;
            border: 2px solid {border};
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {border};
            border: 2px solid #FFF;
        }}
        QPushButton:pressed {{
            background-color: {bg};
        }}
        QPushButton:disabled {{
            background-color: #555;
            border: 2px solid #666;
            color: #888;
        }}
        """


if __name__ == '__main__':
    print('[*] Starting Vortex GUI in demo mode for Windows...')
    app = QApplication(sys.argv)
    window = VortexMainWindow()
    window.show()
    sys.exit(app.exec_())
