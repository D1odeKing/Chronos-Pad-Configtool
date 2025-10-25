# Chronos Pad Configuration Tool

A professional GUI configurator for KMK firmware-based macropads, specifically designed for custom Raspberry Pi Pico keyboards with display and RGB support.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

### Hardware Configuration
- **Fixed 5×4 Matrix Layout**: Pre-configured for 20-key macropad
- **Raspberry Pi Pico**: Optimized pin mappings
- **Hardware Support**:
  - Rotary Encoder (GP10, GP11, GP14)
  - Analog Slider Input (GP28)
  - RGB LEDs (GP9, WS2812 compatible)
  - SH1106 OLED Display (128×64, I2C on GP20/GP21)

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

### Extensions Configuration

#### Rotary Encoder
- Single encoder configuration (GP10/GP11/GP14)
- Configure clockwise/counter-clockwise/press actions
- Customizable keycode mapping per action

#### Analog Input
- Slider/potentiometer support
- Event-based analog mapping
- Threshold configuration

#### RGB Matrix
- Per-key RGB LED control
- WS2812/NeoPixel support
- Brightness control
- Auto-configured for 20 LEDs

#### OLED Display
- **Auto-Generated Keymap Layout**: Display shows current key assignments
- Visual 5×4 grid on 128×64 display
- Abbreviated key names for readability
- Updates with keymap changes

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

**For the Macropad (Included in this repository):**
- ✅ [KMK Firmware](https://github.com/KMKfw/kmk_firmware) - Included in `kmk_firmware-main/`
- ✅ [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle) - Included in `libraries/`
- ✅ CircuitPython 9.x installed on your Raspberry Pi Pico

**Hardware:**
- Raspberry Pi Pico (RP2040) with CircuitPython
- 5×4 key matrix
- (Optional) Rotary encoder, RGB LEDs, OLED display

> **Note:** KMK firmware and CircuitPython libraries are included and will be automatically deployed to your device when you save your configuration!

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Chronos-Pad-Configtool.git
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

### Hardware Setup

#### Pin Configuration
```
Matrix:
  Rows: GP8, GP7, GP6, GP5, GP4 (5 rows)
  Cols: GP0, GP1, GP2, GP3 (4 columns)
  Diode: COL2ROW

Encoder:
  Pin A: GP10
  Pin B: GP11
  Button: GP14

Analog Input:
  Slider: GP28 (ADC2)

RGB LEDs:
  Data Pin: GP9
  Type: WS2812/NeoPixel

Display:
  Type: SH1106 OLED (128×64)
  SDA: GP20
  SCL: GP21
  I2C Address: 0x3C
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
├── kmk_firmware-main/        # KMK firmware source
│   └── kmk/                  # KMK modules
├── libraries/                # CircuitPython libraries
│   └── adafruit-circuitpython-bundle-9.x-mpy-20251024/
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

## 🔄 Version History

### v1.0.0 (2025-10-25)
- Initial release
- Fixed 5×4 matrix configuration
- OLED display keymap visualization
- Auto-deployment to CIRCUITPY
- Complete extension support (Encoder, Analog, RGB, Display)
- Profile management system
- Visual macro builder

---

**Made with ❤️ for the mechanical keyboard community**
