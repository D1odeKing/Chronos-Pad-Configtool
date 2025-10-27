# Chronos Pad Configuration Tool

A professional GUI configurator for KMK firmware-based macropads, specifically designed for custom Raspberry Pi Pico keyboards with display and RGB support.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> **⚠️ Important Notice**: This configuration tool is specifically designed for the [Chronos Pad](https://github.com/D1odeKing/Chronos-Pad) hardware project. It is pre-configured with the exact pin mappings, hardware specifications, and features of the Chronos Pad macropad. For the hardware design, PCB files, and build instructions, please visit the [Chronos Pad repository](https://github.com/D1odeKing/Chronos-Pad).

## 🎯 Features

### Keymap Editor
- **Visual Grid Interface**: Intuitive button-based key assignment
- **Multi-Layer Support**: Create and manage multiple keyboard layers
- **Drag-and-Drop**: Easy keycode selection from categorized lists
- **Profile Management**: Save and load different keymap configurations

### Macro System
- **Visual Macro Builder**: Create complex macros with GUI
- **Action Types**:
  - Text insertion
  - Key taps
  - Key press/release
  - Delays
- **Macro Assignment**: Directly assign macros to any key

### Code Generation
- **One-Click Export**: Generate complete KMK firmware code
- **Auto-Deploy**:
  - Detects CIRCUITPY drive
  - Copies KMK firmware (if missing)
  - Installs required libraries automatically
  - Saves code.py to device
- **Library Management**: Includes display drivers, NeoPixel support

## 🚀 Getting Started

### Prerequisites

**For the Configurator:**
- Python 3.8 or higher
- PyQt6 (`pip install PyQt6`)

**For the Macropad (Auto-downloaded when needed):**
- ✅ [KMK Firmware](https://github.com/KMKfw/kmk_firmware) - Downloaded automatically on first run
- ✅ [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle) - Downloaded automatically on first run
- ✅ CircuitPython 9.x UF2 file - Downloaded automatically on first run

**Hardware:**

This tool is designed specifically for the **[Chronos Pad](https://github.com/D1odeKing/Chronos-Pad)** macropad. For hardware specifications, PCB files, build instructions, and case designs, visit the [Chronos Pad hardware repository](https://github.com/D1odeKing/Chronos-Pad).

> **Note:** KMK firmware and CircuitPython libraries are automatically downloaded on first run and will be deployed to your device when you save your configuration!


### Installing CircuitPython 9.x on Raspberry Pi Pico

To use this configuration tool, your Raspberry Pi Pico must have CircuitPython 9.x installed.

**Important:**
- This tool is only tested with CircuitPython 9.x. Using newer versions (such as CircuitPython 10.x) may cause unexpected errors or break functionality.

**Auto-downloaded CircuitPython 9.x .uf2 file:**
- When you first run the tool, it will automatically download the CircuitPython UF2 file to `libraries/adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2`

**Install CircuitPython:**
1. Hold down the BOOTSEL button on your Pico and plug it into your computer via USB.
2. Release the BOOTSEL button. The Pico will appear as a USB drive named `RPI-RP2`.
3. Drag and drop the downloaded `adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2` file from the `libraries` folder onto the `RPI-RP2` drive.
4. The Pico will reboot and appear as a new USB drive named `CIRCUITPY`.

Your Pico is now running CircuitPython 9.x and ready for use with this tool!

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/D1odeKing/Chronos-Pad-Configtool.git
   cd Chronos-Pad-Configtool
   ```

2. **Install dependencies**:
   ```bash
   pip install PyQt6
   ```

3. **Run the configurator**:
   ```bash
   python main.py
   ```



## 📖 Usage Guide

### Creating a Keymap

1. **Launch the application**
2. **Select keys**: Click on grid buttons to select keys
3. **Assign keycodes**: Choose from categorized keycode lists
4. **Add layers**: Use layer management to create multiple layouts
5. **Create macros**: Build custom macro sequences
6. **Configure extensions**: Set up encoder, analog input, RGB, and display

### Saving and Loading

#### Save Configuration
- **File → Save Configuration**: Saves keymap and settings to JSON
- Stored in `kmk_Config_Save/` directory
- Includes all layers and macro definitions

#### Load Configuration
- **File → Load Configuration**: Restore saved configurations
- Automatically adapts to 5×4 grid if needed
- Preserves macro assignments

### Generating Code

1. Click **"Save code.py"**
2. Select target folder (CIRCUITPY drive auto-detected)
3. Tool automatically:
   - Generates complete KMK code
   - Copies KMK firmware (if missing)
   - Installs required libraries
   - Saves code.py to device

## 🎨 Display Features

The OLED display shows a real-time visual representation of your keymap:

- **5×4 Grid Layout**: Matches physical key positions
- **Abbreviated Keys**: Short, readable key names
- **Layer 0 Display**: Shows primary layer assignments
- **Auto-Updates**: Changes when code.py is generated

### Key Abbreviations
- Standard keys: `A`, `B`, `1`, `2`, etc.
- Modifiers: `LCtl`, `LSft`, `LAlt`, `LGui`
- Special: `BkSp`, `Entr`, `Spce`, `Tab`
- Media: `Vol+`, `Vol-`, `Mute`, `Play`
- Macros: Shows macro name (up to 6 chars)

## 🔧 Extension Configuration

### Encoder Setup
```python
# Example encoder configuration
encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)
encoder_handler.map = [((KC.VOLD, KC.VOLU, KC.MUTE),)]
```

### Analog Input Setup
```python
# Example slider configuration
from analogio import AnalogIn
slider = AnalogInput(AnalogIn(board.GP28))
analog = AnalogInputs([slider], [[AnalogKey(KC.VOLU)]])
```

### RGB Configuration
- 20 LEDs for 5×4 grid
- WS2812 RGB order (GRB)
- Brightness control via keycodes
- Default: White per-key lighting

## 📁 Project Structure

```
Chronos-Pad-Configtool/
├── main.py                    # Main application
├── profiles.json              # Profile definitions
├── kmk_Config_Save/          # Saved configurations
│   ├── kmk_config.json       # Current configuration
│   ├── encoder.py            # Encoder config
│   ├── analogin.py           # Analog input config
│   ├── peg_rgb.py            # RGB config
│   └── macros.json           # Macro definitions
├── libraries/                # Auto-downloaded dependencies
│   ├── kmk_firmware-main/    # KMK firmware source
│   ├── adafruit-circuitpython-bundle-9.x-mpy/ # CircuitPython libraries
│   └── adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2
└── scripts/                  # Utility scripts
```

## 🛠️ Development

### Requirements
- Python 3.8+
- PyQt6 6.0+
- KMK firmware (included)
- CircuitPython libraries (included)

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments & Dependencies

This configurator relies on and distributes the following open-source projects:

### Core Dependencies

**[KMK Firmware](https://github.com/KMKfw/kmk_firmware)** 🎹
- License: GPL-3.0
- Purpose: Complete keyboard firmware for CircuitPython
- Used for: All keyboard functionality, key mapping, macros, and extensions
- Location: `kmk_firmware-main/`
- The heart of this project - KMK makes programmable keyboards accessible!

**[Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)** 📚
- License: MIT  
- Purpose: Hardware drivers and libraries for CircuitPython
- Used for: Display drivers (SH1106), RGB control (NeoPixel), I2C/SPI communication
- Location: `libraries/adafruit-circuitpython-bundle-9.x-mpy-20251024/`
- Key libraries: `adafruit_displayio_sh1106`, `adafruit_display_text`, `neopixel`

### UI Framework

**PyQt6**
- Python GUI framework for the configurator application

### Hardware Platform

**CircuitPython by Adafruit**
- Python for microcontrollers running on Raspberry Pi Pico (RP2040)

---

**Note:** The included libraries are redistributed in accordance with their respective open-source licenses. This configurator simply provides a graphical interface to configure and deploy these amazing tools. All credit goes to the original authors and maintainers of KMK Firmware and the Adafruit CircuitPython Bundle.

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
