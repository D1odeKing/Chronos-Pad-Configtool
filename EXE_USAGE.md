# Quick Start Guide - Executable Version

## Running the Executable

1. **Download**: Get `ChronosPadConfigurator.exe` from the [Releases](https://github.com/D1odeKing/Chronos-Pad-Configtool/releases) page
2. **Run**: Double-click `ChronosPadConfigurator.exe`
3. **First Launch**: The tool will prompt to download KMK firmware and libraries (one-time, ~5 MB)
4. **Start Configuring**: The GUI will open automatically

## What Gets Created

When you run the exe, these folders are created in the same directory:

```
ChronosPadConfigurator.exe     ← Your executable
libraries/                     ← Auto-downloaded (KMK + CircuitPython libs)
kmk_Config_Save/              ← Your saved configurations
  ├── kmk_config.json         ← Current keymap
  ├── macros.json             ← Macro definitions
  ├── encoder.py              ← Encoder settings
  ├── analogin.py             ← Analog input settings
  └── rgb_matrix.json         ← RGB colors
```

## Requirements

- **Windows**: 10 or 11 (64-bit)
- **No Python Installation Needed**: Everything is bundled in the exe
- **Internet Connection**: Required only for first-run download
- **Disk Space**: ~200 MB total (exe + libraries)

## Portable Usage

The executable is **fully portable**:
- No installation required
- No registry changes
- Can run from USB drive
- All settings stored in local folders

Just copy these items together:
```
ChronosPadConfigurator.exe
libraries/              (after first download)
kmk_Config_Save/       (your settings)
profiles.json          (if you have custom profiles)
```

## Troubleshooting

### "Windows protected your PC"
This is normal for unsigned executables:
1. Click "More info"
2. Click "Run anyway"

### Exe won't start
- Try running as Administrator (right-click → Run as administrator)
- Check Windows Defender hasn't quarantined it
- Make sure exe isn't on a network drive with restricted permissions

### Download fails on first run
- Check your internet connection
- Disable antivirus temporarily
- Manually download dependencies (see main README)

### GUI doesn't appear
The exe runs in windowed mode (no console). If nothing appears:
- Check Task Manager for running process
- Look for error in Event Viewer
- Report issue on GitHub with your Windows version

## Features

All features from the Python version work identically:
- ✅ Visual keymap editor
- ✅ Multi-layer support
- ✅ Macro recorder
- ✅ RGB configuration
- ✅ OLED display setup
- ✅ Encoder configuration
- ✅ One-click deployment to CIRCUITPY

## File Size

- **Executable**: ~38 MB (includes Python + PyQt6)
- **Libraries** (auto-downloaded): ~150 MB
- **Total**: ~190 MB

This is normal for Python GUI applications bundled with PyInstaller.

## Updates

To update:
1. Download new version of `ChronosPadConfigurator.exe`
2. Replace old exe
3. Keep your `libraries/` and `kmk_Config_Save/` folders

## Source Code

This exe is built from open-source code available at:
https://github.com/D1odeKing/Chronos-Pad-Configtool

To build it yourself, see [BUILD_EXE.md](BUILD_EXE.md)

## Support

Having issues? Open an issue on GitHub with:
- Your Windows version
- What you clicked/did before the error
- Any error messages you saw
