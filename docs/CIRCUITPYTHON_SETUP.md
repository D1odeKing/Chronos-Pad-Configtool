# CircuitPython Setup Guide

> **AI-Generated Documentation**: This guide was written by GitHub Copilot AI based on requirements and validation from David (D1odeKing).

---

## ⚠️ Important Version Requirement

This tool **requires CircuitPython 10.0.3** to be installed on your **Raspberry Pi Pico 2 (RP2350)**.

- ✅ **CircuitPython 10.0.3** - Fully supported and recommended
- ℹ️ **Pico 2 (RP2350)** - Required hardware (not Pico 1/RP2040)

---

## Download CircuitPython 10.0.3

### Direct Download (Recommended)

**[CircuitPython 10.0.3 for Raspberry Pi Pico 2 (RP2350)](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico2/en_US/adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2)**

### Or Browse All Versions

Visit: [CircuitPython Downloads - Raspberry Pi Pico 2](https://circuitpython.org/board/raspberry_pi_pico2/)

1. Click on **Raspberry Pi Pico 2** (not Pico)
2. Download the latest `.uf2` file
3. Use the downloaded UF2 file in the installation steps below

---

## Installation Steps

### Step 1: Enter Bootloader Mode

1. **Hold down** the **BOOTSEL** button on your Pico 2
2. **While holding BOOTSEL**, connect the Pico 2 to your computer via USB
3. **Release** the BOOTSEL button
4. Your Pico 2 will appear as a USB drive named `RPI-RP2`


### Step 2: Copy CircuitPython UF2 File

1. Download the CircuitPython 10.0.3 UF2 file:
   - **Direct Download**: [adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico2/en_US/adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2)
   - Or get it from [CircuitPython Downloads](https://circuitpython.org/board/raspberry_pi_pico2/)

2. Locate the `RPI-RP2` drive on your computer
3. **Drag and drop** the UF2 file onto the `RPI-RP2` drive
4. The Pico 2 will automatically flash and reboot

**What you should see:**
```
Computer > This PC > RPI-RP2 (USB Drive)
    └── adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2
```

### Step 3: Verify Installation

After reboot, your Pico 2 should appear as a new drive called `CIRCUITPY`:

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
Adafruit CircuitPython 10.0.3 on 2024-10-18; Raspberry Pi Pico 2 with RP2350
```

✅ If you see **CircuitPython 10.0.3**, you're all set!

❌ If you see a different version, please reinstall using the correct UF2 file above

---

## Using the Chronos Pad Configurator

### Step 1: Run the Configurator

- **Windows exe**: Double-click `ChronosPadConfigurator.exe`
- **From source**: Run `python main.py`

### Step 2: Create Your Configuration

1. Design your keymap in the configurator
2. Configure extensions (encoder, display, RGB, etc.)
3. Create any macros you need

### Step 3: Deploy to Your Pico 2

1. Click **"Save code.py"**
2. The configurator will auto-detect your `CIRCUITPY` drive
3. Select the `CIRCUITPY` folder
4. The tool will:
   - Generate complete KMK code
   - Copy KMK firmware (if needed)
   - Install required libraries
   - Save `code.py` to your Pico 2

### Step 4: Test Your Configuration

1. Your Pico 2 will automatically reboot
2. Try pressing keys - they should work!
3. If using an OLED display, you should see the keymap
4. If using an encoder, turn it to cycle layers

---

## Troubleshooting

### Pico 2 Won't Enter Bootloader Mode

**Issue**: The `RPI-RP2` drive doesn't appear

**Solutions**:
1. Try a different USB cable (some cables are power-only)
2. Press and hold BOOTSEL **before** plugging in
3. Try a different USB port
4. Update your Pico 2's bootloader if it has one

### CircuitPython Won't Install

**Issue**: UF2 file won't copy to RPI-RP2 drive

**Solutions**:
1. Erase the Pico 2 first:
   - Download [flash_nuke.uf2](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico2/flash_nuke.uf2)
   - Copy it to RPI-RP2 (same as CircuitPython)
   - Wait 30 seconds
   - Pico 2 will reboot and be erased
2. Then copy the CircuitPython UF2 file again

### CIRCUITPY Drive Won't Appear

**Issue**: After rebooting, you don't see the CIRCUITPY drive

**Solutions**:
1. Wait 10-15 seconds (it takes time to initialize)
2. Try unplugging and replugging the USB cable
3. Check Device Manager (Windows) or Finder (macOS) for an unknown device
4. If all else fails, re-run the bootloader and try flashing CircuitPython again

### Wrong CircuitPython Version

**Issue**: `boot_out.txt` shows version lower than 10.0.3

**Solutions**:
1. Download CircuitPython 10.0.3 UF2 file (see top of this guide)
2. Re-enter bootloader mode
3. Copy the UF2 file to RPI-RP2
4. Verify version in `boot_out.txt` shows 10.0.3

### Configurator Can't Find CIRCUITPY

**Issue**: "No CIRCUITPY drive detected" message

**Solutions**:
1. Make sure CircuitPython 10.0.3 is installed on your Pico 2
2. Ensure the Pico 2 is connected via USB
3. Check Device Manager to see if Pico 2 is visible
4. Try a different USB port
5. Manually browse to your CIRCUITPY drive when prompted

---

## Next Steps

Once CircuitPython 10.0.3 is installed on your Pico 2:

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
- [Raspberry Pi Pico 2 Documentation](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 Read the main [README.md](../README.md)
- 🔧 See [INSTALLATION.md](INSTALLATION.md) for configurator setup
