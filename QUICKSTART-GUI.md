# Vortex GUI Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install base requirements
sudo apt install -y python3-pip python3-dev aircrack-ng

# Install PyQt5
sudo apt install -y python3-pyqt5
```

### Step 2: Clone and Setup Vortex

```bash
# Clone repository
git clone https://github.com/CKCDHX/vortex.git
cd vortex

# Checkout GUI branch
git checkout gui-window-mode

# Install Python packages
sudo pip3 install -r requirements.txt
sudo pip3 install -r requirements-gui.txt
```

### Step 3: Run Vortex GUI

```bash
# Simple way (with mode selection)
sudo python3 vortex.py

# Or direct GUI launch
sudo python3 vortex-gui.py
```

## What Happens Next

One of these will appear:

### Option A: Mode Selection Dialog

```
┌───────────────────────────┐
│         Vortex                     │
│   WiFi Security Auditor           │
│ ─────────────────────────── │
│ Select your preferred mode:      │
│                                  │
│  [CLI Mode]      [GUI Mode]      │
│                                  │
│ CLI Mode: Traditional CLI         │
│ GUI Mode: Modern graphical UI    │
└───────────────────────────┘
```

**Click**: "GUI Mode" (green button)

### Option B: Main GUI Window

The GUI window will open with 5 tabs:

```
┌Network Scanner╮🛰️Attack Config╮Handshake📊Cracking🔐Console💻┐
├─────────────────────────────────────┤
│                              │
│  [Start Scan] [Stop] [Refresh]  │
│                              │
│  Network Table...             │
│                              │
└─────────────────────────────────────┘
```

## First Attack: 10-Minute WPA2 Crack

### Step 1: Scan Networks (1 min)

1. Click on **Network Scanner** tab
2. Click **[Start Scan]** button
3. Wait 30-60 seconds for networks to appear

### Step 2: Select Target (1 min)

1. Look at the network table
2. Click on your target network
3. Note the BSSID (MAC address)

### Step 3: Configure Attack (2 min)

1. Click **Attack Configuration** tab
2. Attack Method: Select "WPA2 Handshake + Dictionary"
3. Deauth Frames: Keep at 10
4. Wordlist: Click **Browse** → Select `/usr/share/wordlists/rockyou.txt`
5. Ensure "Use GPU Acceleration" is checked if you have NVIDIA GPU

### Step 4: Capture Handshake (3 min)

1. Click **Handshake Capture** tab
2. Click **[Send Deauth]** → Sends disconnection frames
3. Click **[Start Capture]** → Listen for 30 seconds
4. Watch EAPOL frames count go from 0/4 → 4/4

### Step 5: Crack Password (3 min)

1. Click **Cracking** tab
2. Click **[Start Cracking]**
3. Watch the progress bar fill
4. When found, password appears in green text

## Example Scenario

```
Time  Action                        Output
──── ─────────────────────── ────────────────────
0:00  Click [Start Scan]            [+] Enabling monitor mode
0:15  Networks appearing           [+] Found 5 networks
0:45  Click on "MyNetwork"         [+] Target selected: MyNetwork
1:00  Go to Attack Config          [+] Configuration loaded
1:30  Select rockyou.txt           [+] Wordlist: 14,344,391 passwords
2:00  Go to Handshake              [*] Ready to capture
2:05  Click [Send Deauth]          [+] Sent 10 deauth frames
2:10  Click [Start Capture]        [*] Listening for EAPOL...
2:45  EAPOL 4/4 Complete           [+] Handshake captured!
3:00  Go to Cracking               [*] Ready to crack
3:05  Click [Start Cracking]       [*] Dictionary attack started
3:30  Testing 100,000 keys         [+] Speed: 500,000 keys/sec
5:15  Password found!              [+] Password: MyPassword123
```

## Common Commands

### Start GUI with Mode Selection
```bash
sudo python3 vortex.py
```

### Start GUI Directly
```bash
sudo python3 vortex-gui.py
```

### Use Force GUI Mode
```bash
sudo python3 vortex.py --gui
```

### Use CLI Mode Instead
```bash
sudo python3 vortex.py --cli
```

## Troubleshooting

### GUI Won't Start

**Error**: `ModuleNotFoundError: No module named 'PyQt5'`

**Fix**:
```bash
sudo apt install python3-pyqt5
# or
sudo pip3 install PyQt5
```

### No Networks Appear

**Causes**:
1. Wireless adapter not in monitor mode
2. No networks broadcasting in your area
3. Adapter not capable of monitor mode

**Fix**:
```bash
# Check if adapter supports monitor mode
sudo airmon-ng

# Manually enable monitor mode
sudo airmon-ng start wlan0
```

### Handshake Won't Capture

**Causes**:
1. Deauth frames not reaching clients
2. No clients connected to target
3. Insufficient timeout duration

**Fix**:
1. Increase deauth frames to 20
2. Move closer to AP
3. Increase timeout to 60 seconds

### Cracking Very Slow

**Fix**:
1. Use smaller wordlist (top100, top500)
2. Enable GPU: Check "Use GPU Acceleration"
3. Close other applications

## Next Steps

- Read **GUI-SETUP.md** for detailed features
- Check **GUI-IMPLEMENTATION.md** for technical details
- See **README.md** for original Vortex documentation
- File issues on GitHub if you find bugs

## Quick Reference

| Tab | Purpose | Main Action |
|-----|---------|-------------|
| Network Scanner | Find WiFi networks | Start Scan, Select Target |
| Attack Config | Configure attack | Choose method, Select wordlist |
| Handshake | Capture WPA2 frames | Send Deauth, Start Capture |
| Cracking | Crack password | Start Cracking, Wait |
| Console | View tool output | Monitor progress, Clear log |

## Safety Checklist

- [ ] Only testing networks you own
- [ ] Have written permission from network owner
- [ ] Know local laws regarding penetration testing
- [ ] Have backup access methods
- [ ] Testing in secure environment
- [ ] Not using for illegal access

## Getting Help

- **Documentation**: See [GUI-SETUP.md](GUI-SETUP.md)
- **Issues**: https://github.com/CKCDHX/vortex/issues
- **Main Repo**: https://github.com/CKCDHX/vortex

---

**Ready to crack?** Start with `sudo python3 vortex.py` and click **[GUI Mode]**!
