# Vortex GUI Setup & Usage Guide

This guide explains how to install and use Vortex with the new graphical interface.

## Installation

### Prerequisites

Before installing the GUI, ensure you have the base Vortex requirements installed:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip aircrack-ng iwconfig
```

### Install Vortex with GUI Support

```bash
# Clone the repository
git clone https://github.com/CKCHDX/vortex.git
cd vortex

# Checkout GUI branch
git checkout gui-window-mode

# Install base requirements
pip3 install -r requirements.txt

# Install GUI requirements
sudo pip3 install -r requirements-gui.txt
```

### Install PyQt5 System-wide (Recommended)

For better integration with your system:

```bash
# On Kali/Debian/Ubuntu
sudo apt install -y python3-pyqt5

# Or via pip
sudo pip3 install PyQt5
```

## Running Vortex

### Automatic Mode Selection

By default, Vortex will show a launcher dialog allowing you to choose between CLI and GUI:

```bash
sudo python3 vortex.py
```

A window will appear with two options:
- **CLI Mode**: Traditional command-line interface
- **GUI Mode**: Modern graphical interface

### Force GUI Mode

To directly launch the GUI without the launcher dialog:

```bash
sudo python3 vortex.py --gui
```

### Force CLI Mode

To use the traditional CLI mode:

```bash
sudo python3 vortex.py --cli
```

## GUI Interface Overview

### Main Tabs

The GUI is organized into 5 main tabs:

#### 1. 🛰️ Network Scanner

**Purpose**: Scan and discover nearby WiFi networks

**Features**:
- **Start Scan**: Begin scanning for WiFi networks in your area
- **Stop Scan**: Halt the current scanning operation
- **Refresh**: Clear and restart the network list
- **Network Table**: Displays all discovered networks with:
  - SSID (Network Name)
  - BSSID (MAC Address)
  - Channel Number
  - Signal Strength (dBm)
  - Encryption Type (WPA2, WEP, etc.)
  - Connected Clients Count

**Workflow**:
1. Click "Start Scan"
2. Wait for networks to appear in the table
3. Click on a network to select it as your target
4. Selected AP info will be displayed below

#### 2. ⚙️ Attack Configuration

**Purpose**: Configure attack parameters before launching

**Options**:

- **Attack Method**:
  - WPA2 Handshake + Dictionary
  - WPA2 PMKID (Hashcat)
  - WPS Pixie Dust
  - WPS Brute Force
  - WEP Fragmentation
  - WEP ChopChop

- **Deauth Frames**: Number of deauthentication frames to send (default: 10)
- **Handshake Timeout**: Maximum seconds to wait for handshake capture (default: 30)
- **Wordlist**: Path to password dictionary file
  - Click "Browse" to select a file
  - Common locations:
    - `/usr/share/wordlists/rockyou.txt`
    - `/usr/share/wordlists/fasttrack.txt`

- **Advanced Options**:
  - [ ] Use GPU Acceleration (Hashcat) - For PMKID cracking on GPU
  - [ ] Verbose Output - Show detailed logging

#### 3. 📊 Handshake Capture

**Purpose**: Capture WPA2 4-way handshake for offline cracking

**Features**:

- **Send Deauth**: Send deauthentication frames to force clients to reconnect
- **Start Capture**: Begin listening for EAPOL frames
- **Status Display**:
  - EAPOL Frames: Shows progress (0/4, 1/4, 2/4, 3/4, 4/4)
  - Captured At: Timestamp of successful capture
  - PMKID Found: Whether PMKID was extracted

**Workflow**:
1. Select target AP from Network Scanner tab
2. Click "Send Deauth" to disconnect clients
3. Click "Start Capture" to begin listening
4. Wait for EAPOL frames to be captured
5. When all 4 frames are captured (4/4), proceed to Cracking tab

#### 4. 🔐 Password Cracking

**Purpose**: Crack captured handshakes or PMKID hashes

**Statistics Display**:
- **Keys Tested**: Number of passwords attempted
- **Speed (keys/s)**: Cracking speed in keys per second
- **Progress Bar**: Visual representation of cracking progress
- **Password Found**: Displays password when successfully cracked

**Controls**:
- **Start Cracking**: Begin dictionary attack
- **Stop**: Halt the cracking process

**Methods**:
- **Dictionary Attack**: Linear password matching from wordlist
- **GPU Cracking** (PMKID): Accelerated using Hashcat on GPU

#### 5. 💻 Console Output

**Purpose**: View real-time tool output and debugging information

**Features**:
- Live output from tools (airmon-ng, airodump-ng, aircrack-ng, etc.)
- Color-coded terminal-style interface
- **Clear** button to reset console

## Common Workflows

### Workflow 1: WPA2 Handshake + Dictionary Crack

1. Open Vortex with `sudo python3 vortex.py --gui`
2. Go to **Network Scanner** tab
3. Click **Start Scan**
4. Select your target network
5. Go to **Handshake Capture** tab
6. Click **Send Deauth** (sends 10 deauth frames)
7. Click **Start Capture** (listen for 30 seconds)
8. Go to **Attack Configuration** tab
9. Select "WPA2 Handshake + Dictionary"
10. Click Browse and select `/usr/share/wordlists/rockyou.txt`
11. Go to **Cracking** tab
12. Click **Start Cracking**
13. Wait for password to be found

### Workflow 2: WPS Pixie Dust Attack

1. Scan networks and select a WPS-enabled AP
2. Go to **Attack Configuration**
3. Select "WPS Pixie Dust" as attack method
4. Click the attack button (if direct attack available)
5. Wait for PIN to be cracked
6. Use PIN to connect or crack PSK

### Workflow 3: PMKID + GPU Cracking

1. Scan and select target
2. Go to **Handshake Capture**
3. Click **Start Capture** (PMKID is passive, no deauth needed)
4. Wait for PMKID to be extracted
5. Go to **Attack Configuration**
6. Select "WPA2 PMKID (Hashcat)"
7. Check "Use GPU Acceleration"
8. Select wordlist
9. Go to **Cracking**
10. Click **Start Cracking**
11. GPU will accelerate the hash comparison

## Troubleshooting

### GUI Won't Start

**Error**: `ModuleNotFoundError: No module named 'PyQt5'`

**Solution**:
```bash
sudo pip3 install PyQt5
# or
sudo apt install python3-pyqt5
```

### Monitor Mode Won't Enable

**Error**: Monitor mode failed to activate

**Solution**:
```bash
# Kill interfering processes
sudo airmon-ng check kill

# Manually enable monitor mode
sudo airmon-ng start wlan0

# Check interface
iwconfig
```

### No Networks Found

**Cause**: Wireless adapter not in monitor mode or not compatible

**Solution**:
1. Check wireless adapter: `iwconfig`
2. Verify monitor mode: `iwconfig | grep Monitor`
3. Check compatibility: See aircrack-ng compatible hardware list
4. Try scanning again with "Refresh" button

### Handshake Won't Capture

**Cause**: Deauth frames not reaching clients or clients not reconnecting

**Solution**:
1. Increase deauth frames to 20-30
2. Move closer to target AP
3. Use 2.4GHz networks (better penetration)
4. Extend timeout to 60+ seconds
5. Ensure clients are connected (visible in Client count)

### Cracking Very Slow

**Cause**: CPU bottleneck or inefficient wordlist

**Solution**:
1. Use GPU acceleration for PMKID: Check "Use GPU Acceleration"
2. Use smaller, targeted wordlists
3. Increase system RAM if available
4. Check system load: `htop`

## Advanced Features

### Custom Wordlists

To use your own wordlist:

1. Go to **Attack Configuration**
2. Click **Browse** next to Wordlist
3. Select your custom `.txt` file
4. Proceed with cracking

### GPU Acceleration Setup

For PMKID cracking with GPU:

```bash
# Install Hashcat
sudo apt install -y hashcat

# Install NVIDIA drivers (if using NVIDIA GPU)
sudo apt install -y nvidia-driver-latest

# In GUI: Check "Use GPU Acceleration" in Attack Configuration
```

### Multiple Interfaces

If you have multiple wireless adapters:

1. Go to **Attack Configuration**
2. Specify the interface (wlan0, wlan1, etc.)
3. Run scanning and attacks on specific adapters

## Keyboard Shortcuts

- `Ctrl+Q`: Quit Vortex
- `Ctrl+S`: Start Scan
- `Ctrl+E`: Send Deauth
- `Ctrl+C`: Capture Handshake
- `Ctrl+K`: Start Cracking

## Performance Tips

1. **Use 2.4GHz networks**: Better signal penetration than 5GHz
2. **Position antenna properly**: Experiment with antenna angle
3. **Close unnecessary applications**: Frees up system resources
4. **Use SSD for wordlists**: Faster file I/O
5. **Enable GPU acceleration**: 100-1000x faster for PMKID cracking

## Security & Ethics

**IMPORTANT**: 
- Only test networks you own or have explicit written permission to test
- Unauthorized access is illegal
- The authors assume no liability for misuse
- Keep audit logs for compliance

## Getting Help

- **Documentation**: See README.md
- **Issues**: GitHub Issues at https://github.com/CKCHDX/vortex/issues
- **Discussion**: GitHub Discussions

## Switching Back to CLI

If you prefer the command-line interface:

```bash
sudo python3 vortex.py --cli
```

Or run specific tools directly:

```bash
airmon-ng start wlan0
airodump-ng wlan0mon
aircrack-ng capture.cap -w wordlist.txt
```

---

**Vortex GUI v1.0** | [GitHub](https://github.com/CKCHDX/vortex) | [Report Issues](https://github.com/CKCHDX/vortex/issues)
