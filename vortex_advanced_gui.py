#!/usr/bin/env python3
"""Vortex Advanced Automated Attack GUI

Professional penetration testing interface with:
- Real-time network scanning and metrics
- Automated attack workflows
- Live data visualization
- Performance monitoring
- Multi-threaded processing
- Attack queue management

Usage: python vortex_advanced_gui.py
"""

import sys
import os
import json
import time
import threading
import random
from datetime import datetime, timedelta
from collections import deque
import math

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QCheckBox, QFileDialog,
        QProgressBar, QMessageBox, QStatusBar, QSplitter, QSlider,
        QGridLayout, QGroupBox, QDoubleSpinBox, QHeaderView, QDialog,
        QDialogButtonBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime, QSize
    from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPen
    from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
    from PyQt5.QtCore import QDateTime, QPointF
    print('[+] All PyQt5 modules imported successfully')
except ImportError as e:
    print(f'[!] ERROR: Required PyQt5 modules not found: {e}')
    print('[*] Install with: pip install PyQt5 PyQtChart')
    sys.exit(1)


class LiveMetricsData:
    """Stores and manages live metrics data."""
    
    def __init__(self, max_history=300):
        self.max_history = max_history
        self.timestamps = deque(maxlen=max_history)
        self.signal_levels = deque(maxlen=max_history)
        self.packets_captured = deque(maxlen=max_history)
        self.attack_speed = deque(maxlen=max_history)
        self.client_activity = deque(maxlen=max_history)
        self.start_time = time.time()
    
    def add_sample(self, signal, packets, speed, clients):
        """Add a data sample."""
        self.timestamps.append(time.time() - self.start_time)
        self.signal_levels.append(signal)
        self.packets_captured.append(packets)
        self.attack_speed.append(speed)
        self.client_activity.append(clients)
    
    def get_latest(self):
        """Get latest metrics."""
        if self.timestamps:
            return {
                'signal': self.signal_levels[-1] if self.signal_levels else 0,
                'packets': self.packets_captured[-1] if self.packets_captured else 0,
                'speed': self.attack_speed[-1] if self.attack_speed else 0,
                'clients': self.client_activity[-1] if self.client_activity else 0
            }
        return {'signal': 0, 'packets': 0, 'speed': 0, 'clients': 0}


class AdvancedNetworkScanner(QThread):
    """Advanced network scanner with real-time metrics."""
    
    network_discovered = pyqtSignal(dict)
    metrics_updated = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.networks = {}
        self.metrics = LiveMetricsData()
        self.packet_count = 0
        self.attack_speed = 0
    
    def run(self):
        """Execute advanced network scan."""
        self.is_running = True
        self.status_changed.emit('[*] Initializing wireless interface...')
        time.sleep(0.5)
        
        self.status_changed.emit('[*] Enabling monitor mode...')
        time.sleep(0.3)
        
        self.status_changed.emit('[*] Starting channel hopping...')
        
        # Simulate discovering networks over time
        sample_networks = [
            {'ssid': 'CyberSec-Lab', 'bssid': '00:11:22:33:44:55', 'channel': 6, 'encryption': 'WPA2', 'power': -35},
            {'ssid': 'Pentest-Subnet', 'bssid': 'AA:BB:CC:DD:EE:FF', 'channel': 11, 'encryption': 'WPA2', 'power': -55},
            {'ssid': 'Legacy-Network', 'bssid': '12:34:56:78:90:AB', 'channel': 1, 'encryption': 'WEP', 'power': -72},
            {'ssid': 'IoT-Devices', 'bssid': 'FF:FF:FF:FF:FF:FF', 'channel': 13, 'encryption': 'WPA3', 'power': -48},
            {'ssid': 'HiddenSSID', 'bssid': 'CA:FE:BA:BE:CA:FE', 'channel': 6, 'encryption': 'WPA2', 'power': -60},
        ]
        
        # Simulate progressive discovery
        for i, network in enumerate(sample_networks):
            if not self.is_running:
                break
            
            # Simulate finding clients
            network['clients'] = random.randint(0, 8)
            network['packets'] = random.randint(100, 5000)
            network['last_seen'] = datetime.now().strftime('%H:%M:%S')
            
            self.networks[network['bssid']] = network
            self.network_discovered.emit(network)
            
            self.status_changed.emit(f'[*] Found: {network["ssid"]} ({len(self.networks)}/{len(sample_networks)})')
            time.sleep(0.8)
        
        # Continuous metrics update
        iteration = 0
        while self.is_running:
            iteration += 1
            
            # Simulate live metrics
            self.packet_count += random.randint(50, 200)
            self.attack_speed = random.uniform(100, 5000)
            active_clients = sum(net.get('clients', 0) for net in self.networks.values())
            signal_quality = random.uniform(-80, -20)
            
            metrics = {
                'packets': self.packet_count,
                'speed': self.attack_speed,
                'clients': active_clients,
                'signal': signal_quality,
                'networks': len(self.networks),
                'iteration': iteration
            }
            
            self.metrics.add_sample(signal_quality, self.packet_count, self.attack_speed, active_clients)
            self.metrics_updated.emit(metrics)
            
            # Randomly update network states
            for bssid in list(self.networks.keys()):
                if random.random() > 0.7:
                    self.networks[bssid]['clients'] = random.randint(0, 10)
                    self.networks[bssid]['packets'] += random.randint(10, 100)
            
            time.sleep(1.0)
    
    def stop(self):
        """Stop scanning."""
        self.is_running = False
        self.status_changed.emit('[!] Scan stopped')


class AutomatedAttackSimulator(QThread):
    """Simulates automated attack workflow."""
    
    handshake_captured = pyqtSignal(str)
    crack_progress = pyqtSignal(dict)
    attack_log = pyqtSignal(str)
    attack_complete = pyqtSignal(str)
    
    def __init__(self, target_bssid, attack_type='wpa2_dict', wordlist_size=100000):
        super().__init__()
        self.target_bssid = target_bssid
        self.attack_type = attack_type
        self.wordlist_size = wordlist_size
        self.is_running = False
        self.keys_tested = 0
    
    def run(self):
        """Execute automated attack."""
        self.is_running = True
        self.attack_log.emit(f'[*] Starting {self.attack_type} attack on {self.target_bssid}')
        
        if self.attack_type == 'wpa2_dict':
            self._wpa2_dictionary_attack()
        elif self.attack_type == 'pmkid':
            self._pmkid_attack()
        elif self.attack_type == 'wps':
            self._wps_attack()
    
    def _wpa2_dictionary_attack(self):
        """WPA2 dictionary attack simulation."""
        self.attack_log.emit('[*] Phase 1: Capturing 4-way handshake...')
        time.sleep(1)
        
        # Simulate handshake capture
        handshake_time = random.uniform(5, 15)
        eapol_frames = 0
        while eapol_frames < 4 and self.is_running:
            eapol_frames = int((time.time() % 10) * 0.4)
            self.attack_log.emit(f'[*] EAPOL frames captured: {eapol_frames}/4')
            time.sleep(0.5)
        
        self.handshake_captured.emit(self.target_bssid)
        self.attack_log.emit('[+] Handshake captured successfully!')
        
        # Start dictionary attack
        self.attack_log.emit('[*] Phase 2: Dictionary attack...')
        time.sleep(1)
        
        # Simulate cracking
        success_at = random.randint(1000, self.wordlist_size)
        start_time = time.time()
        
        while self.keys_tested < success_at and self.is_running:
            self.keys_tested += random.randint(100, 500)
            elapsed = time.time() - start_time
            speed = self.keys_tested / elapsed if elapsed > 0 else 0
            progress = min(100, int((self.keys_tested / success_at) * 100))
            
            self.crack_progress.emit({
                'keys_tested': self.keys_tested,
                'speed': speed,
                'progress': progress,
                'elapsed': elapsed
            })
            
            time.sleep(0.5)
        
        if self.is_running:
            password = self.generate_fake_password()
            self.attack_log.emit(f'[+] PASSWORD FOUND: {password}')
            self.attack_complete.emit(password)
    
    def _pmkid_attack(self):
        """PMKID attack simulation."""
        self.attack_log.emit('[*] Attempting PMKID extraction...')
        
        for i in range(100):
            if not self.is_running:
                break
            progress = (i / 100) * 100
            self.crack_progress.emit({
                'keys_tested': i * 1000,
                'speed': 5000,
                'progress': progress,
                'elapsed': i
            })
            time.sleep(0.1)
        
        if self.is_running:
            password = self.generate_fake_password()
            self.attack_log.emit(f'[+] PASSWORD CRACKED (PMKID): {password}')
            self.attack_complete.emit(password)
    
    def _wps_attack(self):
        """WPS attack simulation."""
        self.attack_log.emit('[*] WPS Pixie Dust attack in progress...')
        
        for i in range(50):
            if not self.is_running:
                break
            self.crack_progress.emit({
                'keys_tested': i * 100,
                'speed': 1000,
                'progress': (i / 50) * 100,
                'elapsed': i * 2
            })
            time.sleep(0.2)
        
        if self.is_running:
            password = '12345678'  # Default WPS
            self.attack_log.emit(f'[+] WPS PIN FOUND: {password}')
            self.attack_complete.emit(password)
    
    def generate_fake_password(self):
        """Generate realistic fake password."""
        patterns = [
            'Secure' + str(random.randint(1000, 9999)),
            'Pass' + ''.join([str(random.randint(0, 9)) for _ in range(8)]),
            ''.join([chr(random.randint(65, 90)) for _ in range(4)]) + str(random.randint(1000, 9999)),
        ]
        return random.choice(patterns)
    
    def stop(self):
        """Stop attack."""
        self.is_running = False
        self.attack_log.emit('[!] Attack stopped')


class VortexAdvancedGUI(QMainWindow):
    """Advanced Vortex GUI with automation and live metrics."""
    
    def __init__(self):
        super().__init__()
        self.scanner_thread = None
        self.attack_thread = None
        self.selected_network = None
        self.attack_queue = []
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Initialize UI."""
        self.setWindowTitle('Vortex Advanced - Automated WiFi Penetration Testing')
        self.setGeometry(0, 0, 1920, 1080)
        self.setMinimumSize(1400, 800)
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Left panel: Networks & Scanner
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # Center panel: Attack Dashboard
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 3)
        
        # Right panel: Live Metrics & Logs
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Status bar
        self.statusBar().showMessage('Ready | Awaiting commands')
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
    
    def create_left_panel(self):
        """Create left panel with scanner controls."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel('NETWORK SCANNER')
        title.setFont(QFont('Arial', 11, QFont.Bold))
        title.setStyleSheet('color: #2ECC71; background: #1a1a1a; padding: 5px;')
        layout.addWidget(title)
        
        # Scanner Controls
        ctrl_layout = QVBoxLayout()
        
        scan_btn = QPushButton('START SCAN')
        scan_btn.setMinimumHeight(35)
        scan_btn.clicked.connect(self.start_scanner)
        scan_btn.setStyleSheet(self.get_button_style('success'))
        ctrl_layout.addWidget(scan_btn)
        
        stop_btn = QPushButton('STOP SCAN')
        stop_btn.setMinimumHeight(35)
        stop_btn.clicked.connect(self.stop_scanner)
        stop_btn.setStyleSheet(self.get_button_style('danger'))
        ctrl_layout.addWidget(stop_btn)
        
        layout.addLayout(ctrl_layout)
        
        # Network Table
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(7)
        self.network_table.setHorizontalHeaderLabels(
            ['SSID', 'BSSID', 'Ch', 'PWR', 'ENC', 'Clients', 'Pkts']
        )
        self.network_table.setSelectionBehavior(self.network_table.SelectRows)
        self.network_table.setSelectionMode(self.network_table.SingleSelection)
        self.network_table.itemSelectionChanged.connect(self.on_network_selected)
        self.network_table.horizontalHeader().setStretchLastSection(False)
        for i in range(7):
            self.network_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout.addWidget(self.network_table)
        
        # Network Details
        details_label = QLabel('SELECTED NETWORK')
        details_label.setFont(QFont('Arial', 10, QFont.Bold))
        details_label.setStyleSheet('color: #3498DB; background: #1a1a1a; padding: 3px;')
        layout.addWidget(details_label)
        
        self.network_details = QTextEdit()
        self.network_details.setReadOnly(True)
        self.network_details.setMaximumHeight(120)
        self.network_details.setPlaceholderText('Select a network to view details')
        layout.addWidget(self.network_details)
        
        return widget
    
    def create_center_panel(self):
        """Create center panel with attack controls."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel('AUTOMATED ATTACK')
        title.setFont(QFont('Arial', 11, QFont.Bold))
        title.setStyleSheet('color: #E74C3C; background: #1a1a1a; padding: 5px;')
        layout.addWidget(title)
        
        # Attack Configuration
        config_group = QGroupBox('ATTACK CONFIGURATION')
        config_layout = QVBoxLayout(config_group)
        
        # Attack Type
        attack_h = QHBoxLayout()
        attack_h.addWidget(QLabel('Attack Type:'))
        self.attack_combo = QComboBox()
        self.attack_combo.addItems([
            'WPA2 Dictionary Attack',
            'WPA2 PMKID (Hashcat)',
            'WPS Pixie Dust',
            'WPS Brute Force',
            'WEP Crack',
            'Multi-target Queue'
        ])
        attack_h.addWidget(self.attack_combo)
        config_layout.addLayout(attack_h)
        
        # Wordlist Size
        wordlist_h = QHBoxLayout()
        wordlist_h.addWidget(QLabel('Wordlist Size:'))
        self.wordlist_spin = QSpinBox()
        self.wordlist_spin.setMinimum(1000)
        self.wordlist_spin.setMaximum(10000000)
        self.wordlist_spin.setValue(100000)
        self.wordlist_spin.setSingleStep(10000)
        wordlist_h.addWidget(self.wordlist_spin)
        config_layout.addLayout(wordlist_h)
        
        # GPU Acceleration
        self.gpu_check = QCheckBox('GPU Acceleration (OpenCL/CUDA)')
        self.gpu_check.setChecked(True)
        config_layout.addWidget(self.gpu_check)
        
        # Threading
        thread_h = QHBoxLayout()
        thread_h.addWidget(QLabel('Threads:'))
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(64)
        self.threads_spin.setValue(16)
        thread_h.addWidget(self.threads_spin)
        config_layout.addLayout(thread_h)
        
        layout.addWidget(config_group)
        
        # Attack Controls
        attack_ctrl = QGroupBox('ATTACK CONTROLS')
        attack_ctrl_layout = QVBoxLayout(attack_ctrl)
        
        btn_layout = QHBoxLayout()
        
        self.attack_btn = QPushButton('LAUNCH ATTACK')
        self.attack_btn.setMinimumHeight(40)
        self.attack_btn.clicked.connect(self.launch_attack)
        self.attack_btn.setStyleSheet(self.get_button_style('attack'))
        btn_layout.addWidget(self.attack_btn)
        
        stop_attack_btn = QPushButton('STOP ATTACK')
        stop_attack_btn.setMinimumHeight(40)
        stop_attack_btn.clicked.connect(self.stop_attack)
        stop_attack_btn.setStyleSheet(self.get_button_style('danger'))
        btn_layout.addWidget(stop_attack_btn)
        
        attack_ctrl_layout.addLayout(btn_layout)
        
        # Attack Progress
        progress_label = QLabel('Attack Progress:')
        attack_ctrl_layout.addWidget(progress_label)
        
        self.attack_progress = QProgressBar()
        self.attack_progress.setValue(0)
        attack_ctrl_layout.addWidget(self.attack_progress)
        
        # Stats
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel('Keys/s:'), 0, 0)
        self.keys_per_sec = QLabel('0')
        self.keys_per_sec.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.keys_per_sec, 0, 1)
        
        stats_layout.addWidget(QLabel('Keys Tested:'), 0, 2)
        self.keys_tested = QLabel('0')
        self.keys_tested.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.keys_tested, 0, 3)
        
        stats_layout.addWidget(QLabel('Elapsed:'), 1, 0)
        self.elapsed_time = QLabel('0s')
        self.elapsed_time.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.elapsed_time, 1, 1)
        
        stats_layout.addWidget(QLabel('Est. Time:'), 1, 2)
        self.est_time = QLabel('--')
        self.est_time.setStyleSheet('color: #3498DB; font-weight: bold;')
        stats_layout.addWidget(self.est_time, 1, 3)
        
        attack_ctrl_layout.addLayout(stats_layout)
        
        layout.addWidget(attack_ctrl)
        layout.addStretch()
        
        return widget
    
    def create_right_panel(self):
        """Create right panel with metrics and logs."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Live Metrics
        metrics_group = QGroupBox('LIVE METRICS')
        metrics_layout = QGridLayout(metrics_group)
        
        metrics_layout.addWidget(QLabel('Signal:'), 0, 0)
        self.signal_label = QLabel('-80 dBm')
        self.signal_label.setStyleSheet('color: #E74C3C; font-weight: bold; font-size: 12px;')
        metrics_layout.addWidget(self.signal_label, 0, 1)
        
        metrics_layout.addWidget(QLabel('Packets:'), 1, 0)
        self.packets_label = QLabel('0')
        self.packets_label.setStyleSheet('color: #2ECC71; font-weight: bold; font-size: 12px;')
        metrics_layout.addWidget(self.packets_label, 1, 1)
        
        metrics_layout.addWidget(QLabel('Clients:'), 2, 0)
        self.clients_label = QLabel('0')
        self.clients_label.setStyleSheet('color: #F39C12; font-weight: bold; font-size: 12px;')
        metrics_layout.addWidget(self.clients_label, 2, 1)
        
        metrics_layout.addWidget(QLabel('Speed:'), 3, 0)
        self.speed_label = QLabel('0 pkt/s')
        self.speed_label.setStyleSheet('color: #9B59B6; font-weight: bold; font-size: 12px;')
        metrics_layout.addWidget(self.speed_label, 3, 1)
        
        metrics_layout.addWidget(QLabel('Networks:'), 4, 0)
        self.networks_label = QLabel('0')
        self.networks_label.setStyleSheet('color: #1ABC9C; font-weight: bold; font-size: 12px;')
        metrics_layout.addWidget(self.networks_label, 4, 1)
        
        layout.addWidget(metrics_group)
        
        # Live Console
        console_label = QLabel('LIVE CONSOLE')
        console_label.setFont(QFont('Arial', 10, QFont.Bold))
        console_label.setStyleSheet('color: #00FF00; background: #1a1a1a; padding: 3px;')
        layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont('Courier', 9))
        self.console.setStyleSheet('background-color: #0D0D0D; color: #00FF00;')
        self.console.append('[*] Vortex Advanced initialized')
        self.console.append('[*] Awaiting commands...')
        layout.addWidget(self.console)
        
        # Clear Console
        clear_btn = QPushButton('CLEAR LOG')
        clear_btn.clicked.connect(self.console.clear)
        clear_btn.setStyleSheet(self.get_button_style('secondary'))
        layout.addWidget(clear_btn)
        
        return widget
    
    def start_scanner(self):
        """Start network scanner."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            QMessageBox.warning(self, 'Scanner Running', 'Scanner is already running')
            return
        
        self.network_table.setRowCount(0)
        self.console.append('[*] Starting advanced network scan...')
        
        self.scanner_thread = AdvancedNetworkScanner()
        self.scanner_thread.network_discovered.connect(self.add_network)
        self.scanner_thread.metrics_updated.connect(self.update_metrics)
        self.scanner_thread.status_changed.connect(self.log_message)
        self.scanner_thread.start()
    
    def stop_scanner(self):
        """Stop network scanner."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()
            self.console.append('[!] Scanner stopped')
    
    def add_network(self, network_info):
        """Add network to table."""
        row = self.network_table.rowCount()
        self.network_table.insertRow(row)
        
        self.network_table.setItem(row, 0, QTableWidgetItem(network_info.get('ssid', '')))
        self.network_table.setItem(row, 1, QTableWidgetItem(network_info.get('bssid', '')))
        self.network_table.setItem(row, 2, QTableWidgetItem(str(network_info.get('channel', ''))))
        self.network_table.setItem(row, 3, QTableWidgetItem(str(network_info.get('power', ''))))
        self.network_table.setItem(row, 4, QTableWidgetItem(network_info.get('encryption', '')))
        self.network_table.setItem(row, 5, QTableWidgetItem(str(network_info.get('clients', ''))))
        self.network_table.setItem(row, 6, QTableWidgetItem(str(network_info.get('packets', ''))))
    
    def on_network_selected(self):
        """Handle network selection."""
        rows = self.network_table.selectedIndexes()
        if rows:
            row = rows[0].row()
            ssid = self.network_table.item(row, 0).text()
            bssid = self.network_table.item(row, 1).text()
            channel = self.network_table.item(row, 2).text()
            power = self.network_table.item(row, 3).text()
            encryption = self.network_table.item(row, 4).text()
            clients = self.network_table.item(row, 5).text()
            
            self.selected_network = {
                'ssid': ssid,
                'bssid': bssid,
                'channel': channel,
                'power': power,
                'encryption': encryption,
                'clients': clients
            }
            
            details_text = f"""
Send Set Send Set Send
SSID: {ssid}
BSSID: {bssid}
Channel: {channel}
Signal: {power} dBm
Encryption: {encryption}
Clients: {clients}
            """
            self.network_details.setText(details_text)
            self.console.append(f'[+] Target selected: {ssid}')
    
    def launch_attack(self):
        """Launch automated attack."""
        if not self.selected_network:
            QMessageBox.warning(self, 'No Target', 'Please select a target network')
            return
        
        if self.attack_thread and self.attack_thread.isRunning():
            QMessageBox.warning(self, 'Attack Running', 'An attack is already in progress')
            return
        
        attack_type = self.attack_combo.currentText().lower().replace(' ', '_')
        wordlist_size = self.wordlist_spin.value()
        
        self.console.append(f"\n[*] Launching {attack_type} on {self.selected_network['ssid']}")
        self.console.append(f"[*] Wordlist size: {wordlist_size:,}")
        self.console.append(f"[*] Threads: {self.threads_spin.value()}")
        self.console.append(f"[*] GPU: {'Enabled' if self.gpu_check.isChecked() else 'Disabled'}")
        
        self.attack_thread = AutomatedAttackSimulator(
            self.selected_network['bssid'],
            'wpa2_dict',
            wordlist_size
        )
        self.attack_thread.attack_log.connect(self.log_message)
        self.attack_thread.crack_progress.connect(self.update_attack_progress)
        self.attack_thread.attack_complete.connect(self.attack_finished)
        self.attack_thread.start()
    
    def stop_attack(self):
        """Stop ongoing attack."""
        if self.attack_thread and self.attack_thread.isRunning():
            self.attack_thread.stop()
            self.attack_thread.wait()
            self.attack_progress.setValue(0)
    
    def update_attack_progress(self, progress_data):
        """Update attack progress."""
        self.attack_progress.setValue(progress_data['progress'])
        self.keys_tested.setText(f"{progress_data['keys_tested']:,}")
        self.keys_per_sec.setText(f"{progress_data['speed']:,.0f}")
        elapsed = int(progress_data['elapsed'])
        self.elapsed_time.setText(f"{elapsed}s")
        
        # Estimate remaining time
        if progress_data['speed'] > 0 and progress_data['progress'] > 0:
            est_total = (100 * elapsed) / progress_data['progress']
            est_remaining = est_total - elapsed
            self.est_time.setText(f"{int(est_remaining)}s")
    
    def update_metrics(self, metrics):
        """Update live metrics."""
        self.signal_label.setText(f"{metrics['signal']:.1f} dBm")
        self.packets_label.setText(f"{metrics['packets']:,}")
        self.clients_label.setText(str(metrics['clients']))
        self.speed_label.setText(f"{metrics['speed']:.0f} pkt/s")
        self.networks_label.setText(str(metrics['networks']))
    
    def attack_finished(self, password):
        """Handle attack completion."""
        self.console.append(f"\n[+] ATTACK SUCCESSFUL!")
        self.console.append(f"[+] Password: {password}")
        self.console.append(f"[+] Network cracked successfully\n")
        QMessageBox.information(self, 'Success', f'Password found: {password}')
    
    def log_message(self, message):
        """Log message to console."""
        self.console.append(message)
    
    def update_status(self):
        """Update status bar."""
        status_parts = []
        
        if self.scanner_thread and self.scanner_thread.isRunning():
            status_parts.append(f"Scanner: Active ({len(self.scanner_thread.networks)} networks)")
        else:
            status_parts.append("Scanner: Ready")
        
        if self.attack_thread and self.attack_thread.isRunning():
            status_parts.append(f"Attack: Running ({self.attack_progress.value()}%)")
        else:
            status_parts.append("Attack: Ready")
        
        self.statusBar().showMessage(' | '.join(status_parts))
    
    def apply_theme(self):
        """Apply dark hacker theme."""
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
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QTableWidget {
            background-color: #0D1117;
            alternate-background-color: #161B22;
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
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #161B22;
            color: #E0E0E0;
            border: 1px solid #21262D;
            padding: 5px;
            border-radius: 3px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #58A6FF;
        }
        QCheckBox {
            color: #E0E0E0;
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
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
        QLabel {
            color: #E0E0E0;
        }
        """)
    
    def get_button_style(self, button_type='default'):
        """Get button style."""
        styles = {
            'success': """
                QPushButton {
                    background-color: #238636;
                    color: white;
                    border: 1px solid #2EA043;
                    border-radius: 3px;
                    padding: 5px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2EA043;
                }
                QPushButton:pressed {
                    background-color: #1A6E2E;
                }
                QPushButton:disabled {
                    background-color: #444;
                    color: #888;
                }
            """,
            'danger': """
                QPushButton {
                    background-color: #DA3633;
                    color: white;
                    border: 1px solid #F85149;
                    border-radius: 3px;
                    padding: 5px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F85149;
                }
                QPushButton:pressed {
                    background-color: #AE2622;
                }
            """,
            'attack': """
                QPushButton {
                    background-color: #D1342B;
                    color: white;
                    border: 2px solid #FF4444;
                    border-radius: 3px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #FF4444;
                    border: 2px solid #FF6666;
                }
                QPushButton:pressed {
                    background-color: #AA2815;
                }
            """,
            'secondary': """
                QPushButton {
                    background-color: #1F6FEB;
                    color: white;
                    border: 1px solid #388BFD;
                    border-radius: 3px;
                    padding: 5px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #388BFD;
                }
                QPushButton:pressed {
                    background-color: #1C5AA0;
                }
            """
        }
        return styles.get(button_type, styles['secondary'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VortexAdvancedGUI()
    window.show()
    sys.exit(app.exec_())
