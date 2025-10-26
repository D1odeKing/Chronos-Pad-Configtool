# Chronos Pad Configuration Tool

A professional GUI configurator for KMK firmware-based macropads, specifically designed for custom Raspberry Pi Pico keyboards with display and RGB support.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> **⚠️ Important Notice**: This configuration tool is specifically designed for the [Chronos Pad](https://github.com/D1odeKing/Chronos-Pad) hardware project. It is pre-configured with the exact pin mappings, hardware specifications, and features of the Chronos Pad macropad. For the hardware design, PCB files, and build instructions, please visit the [Chronos Pad repository](https://github.com/D1odeKing/Chronos-Pad).

## 🎯 Features

### Hardware Configuration
- **Fixed 5×4 Matrix Layout**: Pre-configured for 20-key macropad
- **Raspberry Pi Pico**: Optimized pin mappings
- **Hardware Support**:
  - Rotary Encoder with Layer Cycling (GP10, GP11, GP14)
  - Analog Volume Slider - 10k Potentiometer (GP28)
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
- **Layer Cycling Mode**: Encoder automatically cycles through keyboard layers
  - **Counter-Clockwise**: Switch to previous layer
  - **Clockwise**: Switch to next layer
  - **Button Press**: Return to base layer (Layer 0)
- Single encoder configuration (GP10/GP11/GP14)
- Custom layer switching logic with wraparound support
- Seamless layer navigation without modifier keys

#### Analog Input (Volume Slider)
- **System Volume Control**: 10k sliding potentiometer for intuitive volume adjustment
- **Real-Time Response**: Continuously monitors slider position
- **Smooth Control**: Threshold-based detection prevents jitter
- **Hardware Pin**: GP28 with analog-to-digital conversion
- **Auto-Configuration**: Pre-configured for volume up/down based on slider movement

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
- Shows current layer layout at a glance

### Encoder Layer Navigation
- **Hardware-Based Layer Switching**: Use the rotary encoder to cycle through layers
- **Tactile Feedback**: Physical rotation provides intuitive layer navigation
- **Quick Access**: Press encoder button to instantly return to base layer
- **Automatic Wraparound**: Seamlessly cycle from last layer back to first

### Analog Volume Control
- **Hardware Volume Slider**: 10k linear potentiometer for precise volume control
- **Analog Monitoring**: Continuously tracks slider position (0-65535 ADC range)
- **Smart Threshold**: Filters minor fluctuations to prevent unwanted adjustments
- **Direct HID Control**: Sends system volume up/down commands based on slider movement
- **No Modifier Keys Needed**: Pure analog-to-digital volume control

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

## � Related Projects

### Chronos Pad Hardware
**Repository**: [github.com/D1odeKing/Chronos-Pad](https://github.com/D1odeKing/Chronos-Pad)

The Chronos Pad is a custom 5×4 macropad with integrated features:
- Raspberry Pi Pico microcontroller
- Rotary encoder with push button
- 10k linear potentiometer (volume slider)
- 20 WS2812 RGB LEDs (per-key lighting)
- SH1106 128×64 OLED display
- Hot-swap mechanical switches
- 3D-printed or CNC case designs

Visit the hardware repository for:
- PCB design files and schematics
- Bill of Materials (BOM)
- Build guide and assembly instructions
- Case design files (STL/STEP)
- Wiring diagrams

## �🔄 Version History

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
