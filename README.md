# Chronos Pad Configuration Tool

A professional GUI configurator for KMK firmware-based macropads, specifically designed for custom Raspberry Pi Pico keyboards with display and RGB support.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![CircuitPython](https://img.shields.io/badge/CircuitPython-9.x-blueviolet.svg)
![KMK Firmware](https://img.shields.io/badge/KMK-GPL--3.0-orange.svg)

> **⚠️ Important Notice**: This configuration tool is specifically designed for the [Chronos Pad](https://github.com/D1odeKing/Chronos-Pad) hardware project. It is pre-configured with the exact pin mappings, hardware specifications, and features of the Chronos Pad macropad. For the hardware design, PCB files, and build instructions, please visit the [Chronos Pad repository](https://github.com/D1odeKing/Chronos-Pad).

## 🎯 Features

### Keymap Editor
- **Visual Grid Interface**: Intuitive button-based key assignment
- **Multi-Layer Support**: Create and manage multiple keyboard layers
- **Drag-and-Drop**: Easy keycode selection from categorized lists
- **Profile Management**: Save and load different keymap configurations

### Hardware Extensions
- **Modular Design**: Enable or disable extensions as needed
- **Encoder Support**: ✅ Rotary encoder with button for layer cycling (GP10, GP11, GP14)
- **Analog Input**: ⚠️ 10k slider potentiometer (GP28) - *Under development*
- **OLED Display**: ✅ I2C display with live layer-aware keymap visualization (GP20, GP21)
- **RGB Lighting**: ✅ SK6812MINI per-key RGB with color mapping (GP9, GRB pixel order)
- **Configuration Persistence**: Extension states saved between sessions

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

**For the Macropad (Auto-downloaded by the tool):**
- ✅ [KMK Firmware](https://github.com/KMKfw/kmk_firmware) (GPL-3.0 License) - Downloaded automatically on first run
- ✅ [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle) (MIT License) - Downloaded automatically on first run

**Hardware:**

This tool is designed specifically for the **[Chronos Pad](https://github.com/D1odeKing/Chronos-Pad)** macropad. For hardware specifications, PCB files, build instructions, and case designs, visit the [Chronos Pad hardware repository](https://github.com/D1odeKing/Chronos-Pad).

> **Note:** KMK firmware and CircuitPython libraries are automatically downloaded on first run and will be deployed to your device when you save your configuration!


### Installing CircuitPython 9.x on Raspberry Pi Pico

**⚠️ IMPORTANT: CircuitPython Version Requirement**

This tool requires **CircuitPython 9.x** to be installed on your Raspberry Pi Pico. 
- ✅ **CircuitPython 9.x is supported**
- ❌ **CircuitPython 10.x is NOT currently supported** and may cause errors or break functionality

**Download CircuitPython 9.2.9 (Recommended):**

**Direct Download:** [CircuitPython 9.2.9 UF2 for Raspberry Pi Pico](https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2)

Or browse all versions at: [CircuitPython Downloads for Raspberry Pi Pico](https://circuitpython.org/board/raspberry_pi_pico/)
- **Select version 9.x** (e.g., 9.2.9 or any 9.x release)
- Do NOT download version 10.x or higher

**Installation Steps:**

1. **Download the UF2 file**: 
   - Click the direct download link above, or
   - Visit https://circuitpython.org/board/raspberry_pi_pico/
   - Find and download **CircuitPython 9.2.9** or the latest **9.x version** (NOT 10.x)

2. **Enter bootloader mode**:
   - Hold down the **BOOTSEL** button on your Raspberry Pi Pico
   - While holding BOOTSEL, plug the Pico into your computer via USB
   - Release the BOOTSEL button
   - The Pico will appear as a USB drive named `RPI-RP2`

3. **Install CircuitPython**:
   - Drag and drop the downloaded `adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.9.uf2` file onto the `RPI-RP2` drive
   - The Pico will automatically reboot
   - After rebooting, it will appear as a new USB drive named `CIRCUITPY`

4. **Verify installation**:
   - You should see a `CIRCUITPY` drive with a `boot_out.txt` file
   - Open `boot_out.txt` to confirm the version is **9.2.9** (or your installed 9.x version)

Your Pico is now ready for use with this configuration tool!

### Installation

You have two options for running the Chronos Pad Configurator:

---

#### Option 1: Use Pre-built Executable (Windows - Recommended for Most Users)

**Perfect for users who just want to configure their keyboard without installing Python.**

1. **Download the latest release**:
   - Go to the [Releases](https://github.com/D1odeKing/Chronos-Pad-Configtool/releases) page
   - Download `ChronosPadConfigurator.exe` (approximately 38 MB)

2. **Run the application**:
   - Double-click `ChronosPadConfigurator.exe` to launch
   - No installation or Python required!
   - The exe is fully portable and can be run from any folder

3. **First run setup**:
   - On first launch, the tool will automatically:
     - Download KMK firmware (GPL-3.0)
     - Download Adafruit CircuitPython libraries (MIT)
     - Create a `libraries/` folder next to the exe
     - This process takes about 30 seconds

4. **Start configuring**:
   - Your settings and configurations are saved in the same folder as the exe
   - All profiles and macros persist between sessions

**Note**: Windows may show a security warning on first run since the exe is not signed. Click "More info" → "Run anyway" to proceed.

---

#### Option 2: Run from Source (All Platforms - For Developers)

**Perfect for developers, contributors, or users on Linux/macOS who want to run from Python.**

**System Requirements:**
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for first-time dependency downloads)

**Installation Steps:**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/D1odeKing/Chronos-Pad-Configtool.git
   cd Chronos-Pad-Configtool
   ```

2. **Install Python dependencies**:
   ```bash
   pip install PyQt6
   ```
   
   Or if you prefer using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install PyQt6
   ```

3. **Run the configurator**:
   ```bash
   python main.py
   ```

4. **First run**:
   - The tool will automatically download KMK firmware and CircuitPython libraries
   - Files are stored in `libraries/` folder in the project directory
   - Subsequent runs will use the cached libraries

**Building Your Own Executable (Windows):**

If you want to create your own standalone executable:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   python build_exe.py
   ```
   
   Or manually:
   ```bash
   pyinstaller --onefile --windowed --name ChronosPadConfigurator main.py --add-data "profiles.json;."
   ```

3. **Find your exe**:
   - Built executable will be in `dist/ChronosPadConfigurator.exe`
   - Size will be approximately 38 MB
   - Fully portable and ready to distribute

---



## 📖 Usage Guide

### Creating a Keymap

1. **Launch the application**
2. **Configure hardware**: Select diode orientation (COL2ROW or ROW2COL) in Hardware Configuration panel
3. **Select keys**: Click on grid buttons to select keys
4. **Assign keycodes**: Choose from categorized keycode lists
5. **Add layers**: Use layer management to create multiple layouts
6. **Create macros**: Build custom macro sequences
7. **Configure extensions**: Set up encoder, analog input, RGB, and display

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

The OLED display shows a **live, layer-aware** visual representation of your keymap:

- **5×4 Grid Layout**: Matches physical key positions with correct orientation
- **Layer Indicator**: Shows current active layer at the top
- **Real-time Updates**: Display changes automatically when you switch layers
- **Multiple Switching Methods**: Works with encoder rotation, layer keys (KC.TO, KC.MO, KC.TG), and custom layer cycling
- **Abbreviated Keys**: Short, readable key names
- **Proper Mirroring**: Display matches physical layout (corrected left/right orientation)

### Key Abbreviations
- Standard keys: `A`, `B`, `1`, `2`, etc.
- Modifiers: `LCtl`, `LSft`, `LAlt`, `LGui`
- Special: `BkSp`, `Entr`, `Spce`, `Tab`
- Media: `Vol+`, `Vol-`, `Mute`, `Play`
- Macros: Shows macro name (up to 6 chars)
- Layer switches: `MO(1)`, `TO(2)`, `TG(3)`

## 🔧 Extension Configuration

All hardware extensions can be **enabled or disabled** via checkboxes in the Extensions panel. When disabled, the corresponding code will not be included in the generated `code.py` file.

### Encoder Setup
- **Hardware**: GP10 (A), GP11 (B), GP14 (Button)
- **Enable/Disable**: Use checkbox in Extensions panel
- **Configuration**: Click "Configure" button to edit encoder map
- **Layer Cycling**: Default configuration cycles through layers and updates display in real-time

```python
# Example encoder configuration with layer cycling
class LayerCycler:
    def __init__(self, keyboard, num_layers=6):
        self.keyboard = keyboard
        self.num_layers = num_layers
        self.current_layer = 0
    
    def next_layer(self):
        self.current_layer = (self.current_layer + 1) % self.num_layers
        self.keyboard.active_layers[0] = self.current_layer
        try:
            update_display_for_layer(self.current_layer)  # Updates OLED
        except:
            pass
        return False

encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)
encoder_handler.map = [((KC.LAYER_PREV, KC.LAYER_NEXT, KC.LAYER_RESET),)]
```

### Analog Input Setup
- **Hardware**: GP28 (10k slider potentiometer)
- **Enable/Disable**: Use checkbox in Extensions panel
- **Configuration**: Click "Configure" button to edit analog settings
- **Status**: ⚠️ **Under active development** - Currently being debugged and improved

```python
# Example slider configuration (under development)
from analogio import AnalogIn
slider = AnalogInput(AnalogIn(board.GP28))
analog = AnalogInputs([slider], [[AnalogKey(KC.VOLU)]])
```

### Display Configuration
- **Hardware**: I2C OLED (SDA=GP20, SCL=GP21)
- **Enable/Disable**: Use checkbox in Extensions panel
- **Auto-generates**: Layer-aware keymap visualization code
- **Configuration**: Click "Configure" button to preview generated display code
- **Features**: 
  - Live layer tracking via `LayerDisplaySync` module
  - Updates on layer change (encoder, keys, or any switching method)
  - Proper orientation with 180° rotation and column mirroring
  - Layer indicator at top of display

### RGB Configuration
- **Hardware**: SK6812MINI LEDs on GP9
- **Enable/Disable**: Use checkbox in Extensions panel
- **LEDs**: 20 LEDs for 5×4 grid
- **Pixel Order**: GRB (Green, Red, Blue)
- **Features**: Per-key color mapping, brightness control
- **Default**: White per-key lighting
- **Persistence**: Stored in `kmk_Config_Save/rgb_matrix.json` (legacy `peg_rgb*` files migrate automatically)

## 📁 Project Structure

```
Chronos-Pad-Configtool/
├── main.py                    # Main application
├── profiles.json              # Profile definitions
├── kmk_Config_Save/          # Saved configurations
│   ├── kmk_config.json       # Current configuration
│   ├── encoder.py            # Encoder config
│   ├── analogin.py           # Analog input config
│   ├── rgb_matrix.json       # Peg RGB matrix settings (per-key + underglow)
│   └── macros.json           # Macro definitions
├── libraries/                # Auto-downloaded dependencies (not in repo)
│   ├── kmk_firmware-main/    # KMK firmware (auto-downloaded)
│   └── adafruit-circuitpython-bundle-9.x-mpy/ # CP libraries (auto-downloaded)
└── scripts/                  # Utility scripts
```

> **Note:** The `libraries/` folder is automatically created and populated when you first run the tool. These files are not included in the repository to comply with licensing requirements.

## 🛠️ Development

### Building the Executable

To create a standalone Windows executable:

```bash
python build_exe.py
```

The `.exe` will be created in the `dist/` folder. See [BUILD_EXE.md](BUILD_EXE.md) for detailed instructions.

### Requirements
- Python 3.8+
- PyQt6 6.0+
- PyInstaller (for building exe): `pip install pyinstaller`
- KMK firmware (auto-downloaded on first run)
- CircuitPython libraries (auto-downloaded on first run)

**Headless/CI usage**
- Set `KMK_SKIP_DEP_CHECK=1` to bypass dependency download prompts.
- Set `KMK_SKIP_STARTUP_DIALOG=1` to bypass the startup restore dialog.

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

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
- Auto-downloaded to: `libraries/adafruit-circuitpython-bundle-9.x-mpy/`
- Status: ✅ **Automatically downloaded on first run**
- Key libraries used: `adafruit_displayio_sh1106`, `adafruit_display_text`, `neopixel`

> **Note:** These dependencies are automatically downloaded from their official sources on first run. The configurator acts as a convenience wrapper to help you configure and deploy these amazing open-source tools. This repository does not include the actual library files to comply with license requirements and ensure you always get the latest versions.

### Development Dependencies

**PyQt6**
- Python GUI framework for the configurator application
- Install via: `pip install PyQt6`

### Hardware Platform

**CircuitPython 9.x by Adafruit** ⚠️
- Python for microcontrollers running on Raspberry Pi Pico (RP2040)
- **Version requirement:** CircuitPython 9.x (NOT 10.x)
- **Must be manually installed** on your Raspberry Pi Pico
- Download from: https://circuitpython.org/board/raspberry_pi_pico/

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
