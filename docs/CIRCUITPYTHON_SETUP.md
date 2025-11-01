# CircuitPython Setup Guide

## ⚠️ Important Version Requirement

This tool **requires CircuitPython 9.x** to be installed on your Raspberry Pi Pico.

- ✅ **CircuitPython 9.x** - Fully supported
- ❌ **CircuitPython 10.x** - NOT supported (may break functionality)

---

## Download CircuitPython 9.x

### Option 1: Direct Download (Recommended)

**[CircuitPython 9.2.9 UF2 for Raspberry Pi Pico](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2)**

### Option 2: Browse All 9.x Versions

Visit: [CircuitPython Downloads - Raspberry Pi Pico](https://circuitpython.org/board/raspberry_pi_pico/)

1. Scroll to find your Pico board
2. Select **version 9.x** (e.g., 9.2.9, 9.3.0, etc.)
3. Click the `.uf2` file to download

---

## Installation Steps

### Step 1: Enter Bootloader Mode

1. **Hold down** the **BOOTSEL** button on your Pico
2. **While holding BOOTSEL**, connect the Pico to your computer via USB
3. **Release** the BOOTSEL button
4. Your Pico will appear as a USB drive named `RPI-RP2`

**Visual Guide:**
```
BOOTSEL button (on top of Pico)
    ↓
┌─────────────────────┐
│  ◯ ◯ ◯  BOOTSEL    │
│ (GPIO pads)         │
│  ◯ ◯ ◯              │
└─────────────────────┘
```

### Step 2: Drag and Drop CircuitPython

1. Download the `.uf2` file (see above)
2. Locate the `RPI-RP2` drive on your computer
3. **Drag and drop** the UF2 file onto the `RPI-RP2` drive
4. The Pico will automatically reboot

**What you should see:**
```
Computer > This PC > RPI-RP2 (USB Drive)
    └── adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2
```

### Step 3: Verify Installation

After reboot, your Pico should appear as a new drive called `CIRCUITPY`:

```
Computer > This PC > CIRCUITPY (USB Drive)
    ├── boot.py
    ├── code.py
    ├── boot_out.txt
    ├── lib/
    └── ...
```

### Step 4: Check CircuitPython Version

1. Open the `CIRCUITPY` drive
2. Open `boot_out.txt` with a text editor
3. Look for the version line:

```
Adafruit CircuitPython 9.2.9 on 2024-10-18; Raspberry Pi Pico with RP2040
```

✅ If you see **9.x.x**, you're all set!

❌ If you see **10.x** or higher, please reinstall using version 9.x

---

## Using the Chronos Pad Configurator

### Step 1: Run the Configurator

- **Windows exe**: Double-click `ChronosPadConfigurator.exe`
- **From source**: Run `python main.py`

### Step 2: Create Your Configuration

1. Design your keymap in the configurator
2. Configure extensions (encoder, display, RGB, etc.)
3. Create any macros you need

### Step 3: Deploy to Your Pico

1. Click **"Save code.py"**
2. The configurator will auto-detect your `CIRCUITPY` drive
3. Select the `CIRCUITPY` folder
4. The tool will:
   - Generate complete KMK code
   - Copy KMK firmware (if needed)
   - Install required libraries
   - Save `code.py` to your Pico

### Step 4: Test Your Configuration

1. Your Pico will automatically reboot
2. Try pressing keys - they should work!
3. If using an OLED display, you should see the keymap
4. If using an encoder, turn it to cycle layers

---

## Troubleshooting

### Pico Won't Enter Bootloader Mode

**Issue**: The `RPI-RP2` drive doesn't appear

**Solutions**:
1. Try a different USB cable (some cables are power-only)
2. Press and hold BOOTSEL **before** plugging in
3. Try a different USB port
4. Update your Pico's bootloader if it has one

### CircuitPython Won't Install

**Issue**: UF2 file won't copy to RPI-RP2 drive

**Solutions**:
1. Erase the Pico first:
   - Download [flash_nuke.uf2](https://adafruit-circuit-python.s3.amazonaws.com/bin/rp2040/flash_nuke.uf2)
   - Copy it to RPI-RP2 (same as CircuitPython)
   - Wait 30 seconds
   - Pico will reboot and be erased
2. Then copy the CircuitPython UF2 file again

### CIRCUITPY Drive Won't Appear

**Issue**: After rebooting, you don't see the CIRCUITPY drive

**Solutions**:
1. Wait 10-15 seconds (it takes time to initialize)
2. Try unplugging and replugging the USB cable
3. Check Device Manager (Windows) or Finder (macOS) for an unknown device
4. If all else fails, re-run the bootloader and try flashing CircuitPython again

### Wrong CircuitPython Version

**Issue**: `boot_out.txt` shows version 10.x instead of 9.x

**Solutions**:
1. Download the correct 9.x UF2 file (not 10.x)
2. Re-enter bootloader mode
3. Copy the 9.x UF2 file to RPI-RP2
4. Verify version in `boot_out.txt` shows 9.x

### Configurator Can't Find CIRCUITPY

**Issue**: "No CIRCUITPY drive detected" message

**Solutions**:
1. Make sure CircuitPython is installed on your Pico
2. Ensure the Pico is connected via USB
3. Check Device Manager to see if Pico is visible
4. Try a different USB port
5. Manually browse to your CIRCUITPY drive when prompted

---

## Next Steps

Once CircuitPython 9.x is installed on your Pico:

1. ➡️ Open the **Chronos Pad Configurator**
2. ➡️ Design your keymap
3. ➡️ Click **"Save code.py"**
4. ➡️ Select your `CIRCUITPY` drive
5. ➡️ Enjoy your configured keyboard!

---

## Resources

- [CircuitPython Official Documentation](https://docs.circuitpython.org/)
- [Adafruit Learning Guides](https://learn.adafruit.com/)
- [KMK Firmware Documentation](https://docs.keymak.info/)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/products/raspberry-pi-pico/)

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 Read the main [README.md](../README.md)
- 🔧 See [INSTALLATION.md](INSTALLATION.md) for configurator setup
