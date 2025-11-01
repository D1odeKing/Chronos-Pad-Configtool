# Building the Executable

This guide explains how to create a standalone `.exe` file for the Chronos Pad Configurator.

## Quick Start

### Option 1: Using the Build Script (Recommended)

```bash
python build_exe.py
```

The executable will be created at: `dist\ChronosPadConfigurator.exe`

### Option 2: Using PyInstaller Directly

```bash
pyinstaller ChronosPadConfigurator.spec
```

Or using the command line:

```bash
pyinstaller --name=ChronosPadConfigurator --onefile --windowed main.py
```

## Requirements

- Python 3.8+
- PyQt6: `pip install PyQt6`
- PyInstaller: `pip install pyinstaller`

## Output

After building, you'll find:

- `dist\ChronosPadConfigurator.exe` - Your standalone executable (distribute this)
- `build\` - Temporary build files (can be deleted)
- `ChronosPadConfigurator.spec` - Build configuration (keep for rebuilding)

## Distribution

The `.exe` file is completely standalone and includes:
- ✅ Python interpreter
- ✅ PyQt6 GUI framework
- ✅ All application code
- ✅ profiles.json

It does NOT include (auto-downloaded on first run):
- KMK Firmware (downloaded to `libraries/` folder)
- CircuitPython libraries (downloaded to `libraries/` folder)

## File Size

Expected size: ~50-70 MB (due to bundled Python + PyQt6)

## First Run

When users run the exe for the first time:
1. It will prompt to download KMK firmware and CircuitPython libraries
2. These are downloaded to a `libraries/` folder next to the exe
3. This only happens once - subsequent runs are instant

## Notes

- The exe is Windows-only (built with PyInstaller on Windows)
- For Linux/Mac, users should run the Python script directly
- The exe includes a GUI-only mode (no console window)
- Configuration files are saved to `kmk_Config_Save/` folder

## Adding an Icon (Optional)

1. Get a `.ico` file (256x256 recommended)
2. Save it as `icon.ico` in the project root
3. Update both:
   - `build_exe.py`: Change `'--icon=NONE'` to `'--icon=icon.ico'`
   - `ChronosPadConfigurator.spec`: Change `icon=None` to `icon='icon.ico'`
4. Rebuild

## Troubleshooting

### "Failed to execute script"
- Make sure all dependencies are installed: `pip install PyQt6`
- Try running in console mode first: Change `--windowed` to `--console` in build_exe.py

### Large file size
- Normal! PyInstaller bundles Python + PyQt6 (~50MB minimum)
- Use `--onefile` for single exe (slightly larger but easier to distribute)

### Missing files
- Check the `datas` section in the .spec file
- Add any missing data files: `('source_file', 'destination_folder')`

## Clean Build

To rebuild from scratch:

```bash
# Remove old build files
rmdir /s /q build dist
del ChronosPadConfigurator.spec

# Rebuild
python build_exe.py
```

## Advanced Options

Edit `ChronosPadConfigurator.spec` to customize:
- `console=True` - Show console window (useful for debugging)
- `icon='path/to/icon.ico'` - Add application icon
- `datas=[]` - Include additional data files
- `hiddenimports=[]` - Add modules not auto-detected
