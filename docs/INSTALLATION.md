# Installation Guide

## Quick Start

Choose your preferred installation method:

| Method | Best For | Setup Time |
|--------|----------|-----------|
| **[Executable (.exe)](#option-1-pre-built-executable-windows)** | End users (Windows) | 5 minutes |
| **[Run from Source](#option-2-run-from-source-all-platforms)** | Developers / Linux / macOS | 10 minutes |
| **[Build Your Own Exe](#building-your-own-executable)** | Contributors / Distribution | 15 minutes |

---

## Prerequisites

### System Requirements
- Windows 10+, macOS 10.12+, or any Linux distribution
- Internet connection (for first-time library downloads)

### For CircuitPython Device
- Raspberry Pi Pico 2 with **CircuitPython 10.0.3** installed
- See [CIRCUITPYTHON_SETUP.md](CIRCUITPYTHON_SETUP.md) for installation instructions

---

## Option 1: Pre-built Executable (Windows)

**This is the easiest option for most users!**

### Step 1: Download
1. Go to [Releases](https://github.com/D1odeKing/Chronos-Pad-Configtool/releases)
2. Download `ChronosPadConfigurator.exe` (~38 MB)

### Step 2: Run
1. Double-click `ChronosPadConfigurator.exe`
2. If Windows shows a security warning:
   - Click "More info"
   - Click "Run anyway"

### Step 3: First Launch Setup
The tool will automatically:
- Download KMK firmware (GPL-3.0)
- Download CircuitPython libraries (MIT)
- Create a `libraries/` folder next to the exe
- **This takes about 30 seconds**

### Step 4: Start Configuring
Your settings are saved in the same folder as the exe. Everything is portable!

### Troubleshooting

**"Windows Defender SmartScreen prevented an unrecognized app from starting"**
- Click "More info" and then "Run anyway"
- This happens because the exe isn't code-signed (typical for open-source projects)

**"VCRUNTIME140.dll not found"**
- Install Microsoft Visual C++ Redistributable: https://support.microsoft.com/en-us/help/2977003
- Download the x64 version and run the installer

**Slow first launch**
- The tool is downloading libraries (30-60 seconds)
- Subsequent launches will be instant

---

## Option 2: Run from Source (All Platforms)

**Perfect for developers and contributors!**

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, but recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/D1odeKing/Chronos-Pad-Configtool.git
cd Chronos-Pad-Configtool
```

Or download as ZIP:
1. Click the green "Code" button on GitHub
2. Select "Download ZIP"
3. Extract the folder

### Step 2: Install Dependencies

**Basic installation:**
```bash
pip install PyQt6
```

**Using a virtual environment (recommended):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install PyQt6
```

### Step 3: Run the Application

```bash
python main.py
```

### Step 4: First Run
The tool will automatically:
- Download KMK firmware
- Download CircuitPython libraries
- Store them in `libraries/` folder
- **Takes about 30 seconds on first run**

### Troubleshooting

**"ModuleNotFoundError: No module named 'PyQt6'"**
```bash
pip install PyQt6
```

**"Python: command not found" (macOS/Linux)**
```bash
python3 main.py
```

**"Permission denied" (Linux)**
```bash
chmod +x main.py
./main.py
```

---

## Building Your Own Executable

**For developers who want to create a custom exe!**

### Prerequisites
- Python 3.8 or higher
- PyInstaller: `pip install pyinstaller`

### Method 1: Using the Build Script (Recommended)

```bash
# Install PyInstaller first
pip install pyinstaller

# Build the exe
python build_exe.py
```

The exe will be created in `dist/ChronosPadConfigurator.exe`

### Method 2: Manual PyInstaller Command

```bash
pyinstaller --onefile \
    --windowed \
    --name ChronosPadConfigurator \
    --icon=NONE \
    main.py \
    --add-data "profiles.json;."
```

On Windows (one line):
```bash
pyinstaller --onefile --windowed --name ChronosPadConfigurator --icon=NONE main.py --add-data "profiles.json;."
```

### Build Output

- **Location**: `dist/ChronosPadConfigurator.exe`
- **Size**: ~38 MB
- **Portable**: Yes, can be run from any folder
- **Dependencies**: All bundled inside

### Distribution

Your exe is ready to distribute! To share it:

1. Copy `ChronosPadConfigurator.exe` from the `dist/` folder
2. Users can run it without installing Python
3. Create a GitHub Release and upload the exe

See [BUILD_EXE.md](BUILD_EXE.md) for detailed build configuration.

---

## Post-Installation

### First Time Setup

1. **Configure CircuitPython**: See [CIRCUITPYTHON_SETUP.md](CIRCUITPYTHON_SETUP.md)
2. **Connect Your Device**: Plug in your Pico with CircuitPython
3. **Generate Code**: Use the configurator to generate and deploy `code.py`

### File Locations

**Saved Configurations**
- Exe mode: Same folder as `ChronosPadConfigurator.exe`
- Source mode: `kmk_Config_Save/` subfolder

**Downloaded Libraries**
- Exe mode: `libraries/` folder next to exe
- Source mode: `libraries/` folder in project

### Next Steps

- Read [USAGE.md](USAGE.md) for the complete usage guide
- Check [EXTENSIONS.md](EXTENSIONS.md) for hardware configuration
- See [DISPLAY.md](DISPLAY.md) for OLED display setup

---

## System Compatibility

| Platform | Supported | Notes |
|----------|-----------|-------|
| Windows 10+ | ✅ Yes | Exe or source |
| macOS 10.12+ | ✅ Yes | Source only (no official exe) |
| Ubuntu/Debian | ✅ Yes | Source only |
| Raspberry Pi OS | ✅ Yes | Source only |
| Other Linux | ✅ Yes | Source only |

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) sections above
2. Review [CIRCUITPYTHON_SETUP.md](CIRCUITPYTHON_SETUP.md) for device setup
3. Open an issue on [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
4. Include your OS, Python version, and error message

---

## What's Next?

- ➡️ [Usage Guide](USAGE.md) - Learn how to use the configurator
- ➡️ [Extensions Guide](EXTENSIONS.md) - Configure encoder, display, RGB, etc.
- ➡️ [Display Guide](DISPLAY.md) - Set up the OLED display
