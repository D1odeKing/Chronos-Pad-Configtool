# Chronos Pad Configuration Tool

A professional GUI configurator for KMK firmware-based macropads, specifically designed for custom Raspberry Pi Pico keyboards with display and RGB support.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![CircuitPython](https://img.shields.io/badge/CircuitPython-10.0.3-blueviolet.svg)
![KMK Firmware](https://img.shields.io/badge/KMK-GPL--3.0-orange.svg)
![AI Generated](https://img.shields.io/badge/AI-Generated%20Code-blueviolet.svg)

> **🤖 AI-Generated Code Notice**: This project's codebase was primarily written by **GitHub Copilot AI** with project direction, testing, and bug detection by **D10D3K1NG**. See [Attribution](docs/ATTRIBUTION.md) for details.

> **⚠️ Hardware Notice**: This configuration tool is specifically designed for the [Chronos Pad](https://github.com/D1odeKing/Chronos-Pad) hardware project. It is pre-configured with the exact pin mappings, hardware specifications, and features of the Chronos Pad macropad. For the hardware design, PCB files, and build instructions, please visit the [Chronos Pad repository](https://github.com/D1odeKing/Chronos-Pad).

---

## 📚 Documentation

Complete documentation is organized in the [`docs/`](docs/) folder for easy navigation:

### Getting Started
| Document | Purpose |
|----------|---------|
| **[📋 Documentation Index](docs/README.md)** | Complete documentation overview |
| **[🤖 AI Attribution](docs/ATTRIBUTION.md)** | AI-generated code notice & credits |
| **[📥 Installation Guide](docs/INSTALLATION.md)** | Getting started (exe or source) |
| **[⚡ CircuitPython Setup](docs/CIRCUITPYTHON_SETUP.md)** | Installing CircuitPython 10.0.3 on Pico 2 |
| **[📖 Usage Guide](docs/USAGE.md)** | How to use the configurator |

### Advanced Topics
| Document | Purpose |
|----------|---------|
| **[🔌 Extensions Guide](docs/EXTENSIONS.md)** | Encoder, display, RGB, analog input |
| **[🖥 Display Guide](docs/DISPLAY.md)** | OLED layer-aware visualization |
| **[🎨 Layer RGB Guide](docs/LAYER_RGB_SWITCHING.md)** | Layer-aware RGB lighting |
| **[🏗 Architecture Guide](docs/ARCHITECTURE.md)** | Codebase structure & design |
| **[📦 Build Exe Guide](docs/BUILD_EXE.md)** | Creating your own executable |

---

## 🎯 Features

### Modern User Interface
- ✅ **Fullscreen Compatible**: Responsive layout that scales perfectly to any screen size
- ✅ **Tabbed Extensions Panel**: Organized interface with Extensions and Advanced tabs
- ✅ **Icon-Rich Design**: Emoji icons throughout for quick visual recognition
- ✅ **Smart Tooltips**: Comprehensive help text on every control
- ✅ **Theme Support**: Choose from Cheerful, Light, or Dark themes

### Keymap Editor
- ✅ **Visual 5×4 Grid Interface**: Intuitive button-based key assignment
- ✅ **Multi-Layer Support**: Create unlimited layers with full layer switching
- ✅ **Profile Management**: Save and load different configurations
- ✅ **Full Keycode Library**: Letters, numbers, modifiers, media keys, and more
- ✅ **Condensed Display Labels**: Optimized 3-4 character abbreviations for OLED

### Hardware Extensions
- ✅ **Encoder**: Rotary encoder with layer cycling and configurable sensitivity (GP10, GP11, GP14)
- ✅ **Analog Input**: Slider potentiometer for volume or brightness control (GP28) - FIXED!
- ✅ **OLED Display**: Live layer-aware keymap visualization with smart abbreviations (GP20, GP21)
- ✅ **RGB Lighting**: Per-key and underglow RGB support with layer colors (GP9)

### Advanced Settings
- ✅ **Encoder Sensitivity Control**: Adjust steps per pulse (1-16) for perfect responsiveness
- ✅ **Boot Configuration**: Full boot.py customization with safety warnings
- ⚠️ **Read-Only Protection**: Comprehensive warnings before enabling read-only mode
- ✅ **Drive Renaming**: Customize CIRCUITPY drive label
- ✅ **USB Configuration**: Control USB HID and storage settings

### Macro System
- ✅ **Visual Macro Builder**: Create complex sequences with GUI
- ✅ **Multiple Action Types**: Text, key presses, delays, modifiers
- ✅ **Easy Assignment**: Assign macros directly to any key

### Code Generation & Deployment
- ✅ **One-Click Export**: Generate complete KMK firmware code
- ✅ **Auto-Detection**: Finds CIRCUITPY drive automatically
- ✅ **Dependency Management**: Auto-downloads KMK firmware & libraries
- ✅ **Direct Device Deployment**: Saves code.py, boot.py, and libraries to Pico

## 🚀 Quick Start

### 1️⃣ Install Configurator

**Option A: Windows Executable (Easiest)**
```bash
# Download from Releases page
# Double-click ChronosPadConfigurator.exe
# That's it! No Python required.
```

**Option B: Run from Source**
```bash
git clone https://github.com/D1odeKing/Chronos-Pad-Configtool.git
cd Chronos-Pad-Configtool
pip install PyQt6
python main.py
```

👉 **Full details**: See [Installation Guide](docs/INSTALLATION.md)

### 2️⃣ Setup CircuitPython on Pico

1. Download [CircuitPython 10.0.3 UF2](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico2/en_US/adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2)
2. Hold BOOTSEL on Pico 2, plug into USB
3. Drag UF2 file onto RPI-RP2 drive
4. Pico 2 reboots with CIRCUITPY drive

👉 **Full details**: See [CircuitPython Setup](docs/CIRCUITPYTHON_SETUP.md)

### 3️⃣ Configure Your Keyboard

1. Launch the configurator
2. Design your keymap (5×4 grid)
3. Add layers, macros, RGB colors
4. Click "Save code.py" and select CIRCUITPY drive
5. Tool auto-deploys firmware and libraries

👉 **Full details**: See [Usage Guide](docs/USAGE.md)

### 4️⃣ Enjoy!

Your keyboard is ready to use! Keys work, layers switch, display shows your keymap, etc.

---



## 📖 Usage Guide

Learn how to use the configurator to create your custom keyboard:

- **[Complete Usage Guide](docs/USAGE.md)** - Creating keymaps, layers, macros, and more
- **[Extensions Guide](docs/EXTENSIONS.md)** - Encoder, display, RGB, analog input configuration
- **[Display Guide](docs/DISPLAY.md)** - OLED display setup and troubleshooting

---

## 📁 Project Structure

```
Chronos-Pad-Configtool/
├── docs/                          # 📚 Complete documentation
│   ├── INSTALLATION.md           # Installation & setup
│   ├── CIRCUITPYTHON_SETUP.md    # CircuitPython 10.0.3 installation for Pico 2
│   ├── USAGE.md                  # Usage guide
│   ├── EXTENSIONS.md             # Hardware configuration
│   ├── DISPLAY.md                # OLED display guide
│   └── BUILD_EXE.md              # Building from source
├── main.py                        # Main application
├── build_exe.py                  # Build script for executable
├── profiles.json                 # Default profiles
├── kmk_Config_Save/              # Auto-created: saved configs
├── libraries/                    # Auto-created: downloaded deps
└── dist/                         # Auto-created: built executable
```

---

## 🛠️ Development

### Building the Executable

```bash
pip install pyinstaller
python build_exe.py
```

See [BUILD_EXE.md](docs/BUILD_EXE.md) for detailed instructions.

### Requirements
- Python 3.8+
- PyQt6 6.0+
- PyInstaller (for exe builds)

### Contributing
Contributions welcome! Please submit Pull Requests.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments & Dependencies

This configurator automatically downloads and uses the following open-source projects:

### Runtime Dependencies (Auto-Downloaded)

**[KMK Firmware](https://github.com/KMKfw/kmk_firmware)** 🎹
- License: GPL-3.0
- Purpose: Complete keyboard firmware for CircuitPython
- Used for: All keyboard functionality, key mapping, macros, and extensions
- Auto-downloaded to: `libraries/kmk_firmware-main/`
- Status: ✅ **Automatically downloaded on first run**
- The heart of this project - KMK makes programmable keyboards accessible!

**[Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)** 📚
- License: MIT  
- Purpose: Hardware drivers and libraries for CircuitPython
- Used for: Display drivers (SH1106), RGB control (NeoPixel), I2C/SPI communication
- Auto-downloaded to: `libraries/adafruit-circuitpython-bundle-9.x-mpy/` (or latest version)
- Status: ✅ **Automatically downloaded on first run**
- Key libraries used: `adafruit_displayio_sh1106`, `adafruit_display_text`, `neopixel`

> **Note:** These dependencies are automatically downloaded from their official sources on first run. The configurator acts as a convenience wrapper to help you configure and deploy these amazing open-source tools. This repository does not include the actual library files to comply with license requirements and ensure you always get the latest versions.

### Development Dependencies

**PyQt6**
- Python GUI framework for the configurator application
- Install via: `pip install PyQt6`

### Hardware Platform

**CircuitPython 10.0.3 by Adafruit**
- Python for microcontrollers running on Raspberry Pi Pico 2 (RP2350)
- **Version requirement:** CircuitPython 10.0.3 (latest)
- **Must be manually installed** on your Raspberry Pi Pico 2
- Download from: https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico2/en_US/adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2

---

**Attribution:** All credit goes to the original authors and maintainers of KMK Firmware and the Adafruit CircuitPython Bundle. This configurator simply provides a graphical interface to make their excellent work more accessible.

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the README for configuration examples
- Refer to [KMK Documentation](https://github.com/KMKfw/kmk_firmware/tree/main/docs/en) for firmware details


## 🔗 Related Projects

### Chronos Pad Hardware
For all hardware details, PCB files, build instructions, and case designs, please visit the official hardware repository:

**Repository:** [github.com/D1odeKing/Chronos-Pad](https://github.com/D1odeKing/Chronos-Pad)

This configuration tool is designed specifically for the Chronos Pad. All hardware-specific documentation and setup are maintained in the hardware repo.

## 🔄 Version History

### v1.1.0 (2025-11-01) - Current
- ✅ **OLED Display Enhancements**:
  - Layer-aware display updates in real-time
  - Correct left/right orientation (column mirroring)
  - Fixed top-to-bottom row ordering
  - `LayerDisplaySync` module for automatic layer tracking
  - Updates on encoder rotation, layer keys, or any switching method
- ✅ **Encoder Improvements**:
  - Layer cycling with display integration
  - Custom keycodes for layer navigation
- ✅ **RGB Matrix Refactor**:
  - Migrated to `rgb_matrix.json` storage format
  - Per-key and underglow color mapping
  - Automatic legacy file migration
- ⚠️ **Known Issues**:
  - Analog input functionality under active development

### v1.0.0 (2025-10-25)
- Initial release
- Fixed 5×4 matrix configuration
- OLED display keymap visualization
- Auto-deployment to CIRCUITPY
- Complete extension support (Encoder, Analog, RGB, Display)
- Profile management system
- Visual macro builder

## 👏 Credits

**Development**: The majority of the code for this configuration tool was written by **Claude Sonnet 4.5** (Anthropic's AI assistant), working collaboratively with the project maintainer to implement features, debug issues, and create comprehensive documentation.

**Hardware Design**: Chronos Pad macropad by D1odeKing

**Special Thanks**:
- [KMK Firmware](https://github.com/KMKfw/kmk_firmware) - Keyboard firmware framework (GPL-3.0)
- [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle) - Essential libraries (MIT)
- PyQt6 - GUI framework
- The mechanical keyboard community

---

**Made with ❤️ for the mechanical keyboard community**
