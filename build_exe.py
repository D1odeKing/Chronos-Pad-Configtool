"""
Build script for creating Chronos Pad Configurator executable
Run this script to build the .exe: python build_exe.py

Creates a clean distribution structure:
dist/
  ChronosPadConfigurator/
    ChronosPadConfigurator.exe  (single bundled exe)
    kmk_Config_Save/            (user configuration saves)
    libraries/                  (downloaded dependencies)
    profiles.json               (quick-load presets)
    settings.json               (app preferences)
    macros.json                 (global macros)
    README.txt                  (usage instructions)
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

# Check if profiles.json exists
if not os.path.exists('profiles.json'):
    print("Warning: profiles.json not found, creating empty file")
    with open('profiles.json', 'w') as f:
        f.write('{}')

# Clean old build files
if os.path.exists('build'):
    print("Cleaning old build files...")
    shutil.rmtree('build', ignore_errors=True)
if os.path.exists('dist'):
    print("Cleaning old dist folder...")
    shutil.rmtree('dist', ignore_errors=True)

# PyInstaller command - using Python module syntax
command = [
    sys.executable,  # Python interpreter
    '-m',
    'PyInstaller',
    '--clean',
    'ChronosPadConfigurator.spec'
]

print("=" * 60)
print("Building Chronos Pad Configurator executable...")
print("=" * 60)
print(f"Command: {' '.join(command)}")
print()

try:
    result = subprocess.run(command, check=True)
    print("\n✅ PyInstaller build successful!")
    
    # Create organized folder structure
    print("\n📁 Creating organized distribution structure...")
    
    dist_root = Path("dist/ChronosPadConfigurator")
    libraries_folder = dist_root / "libraries"
    config_save_folder = dist_root / "kmk_Config_Save"
    
    # Create folders at root level (no data subfolder)
    libraries_folder.mkdir(parents=True, exist_ok=True)
    config_save_folder.mkdir(parents=True, exist_ok=True)
    
    # Move the exe into the ChronosPadConfigurator folder
    exe_source = Path("dist/ChronosPadConfigurator.exe")
    exe_dest = dist_root / "ChronosPadConfigurator.exe"
    
    if exe_source.exists():
        shutil.move(str(exe_source), str(exe_dest))
        print(f"  ✓ Moved ChronosPadConfigurator.exe to ChronosPadConfigurator/")
    
    # Copy profiles.json to root folder
    if os.path.exists('profiles.json'):
        shutil.copy2('profiles.json', dist_root / 'profiles.json')
        print(f"  ✓ Copied profiles.json to root/")
    
    # Create a .gitkeep in kmk_Config_Save to preserve folder structure
    (config_save_folder / ".gitkeep").touch()
    print(f"  ✓ Created kmk_Config_Save/ folder structure")
    
    # Create README.txt with instructions
    readme_content = """
Chronos Pad Configurator - Portable Distribution
================================================

FOLDER STRUCTURE:
-----------------
ChronosPadConfigurator/
├── ChronosPadConfigurator.exe  (Main application - double-click to run)
├── kmk_Config_Save/            (Your saved configurations)
├── settings.json               (App preferences - auto-created)
├── macros.json                 (Global macros - auto-created)
├── profiles.json               (Quick-load presets)
└── libraries/                  (Auto-downloaded dependencies)
    ├── kmk_firmware-main/     (Downloaded on first run)
    └── adafruit-circuitpython-bundle-.../  (Downloaded on first run)

FIRST RUN:
----------
1. Double-click ChronosPadConfigurator.exe
2. Choose CircuitPython version (9.x or 10.x)
3. The app will automatically download required libraries (~30-60 seconds)
4. Wait for "Dependencies installed successfully!"
5. Start configuring your Chronos Pad!

HOW IT WORKS:
-------------
The executable is FULLY PORTABLE:
- All paths are relative to ChronosPadConfigurator.exe location
- Copy the entire ChronosPadConfigurator/ folder anywhere (USB drive, desktop, etc.)
- The app will always find its kmk_Config_Save/ and libraries/ folders
- Your configs stay with the app - no installation needed!

USAGE:
------
- All your saved configurations are stored in kmk_Config_Save/
- App settings (theme, version, RGB colors) are in settings.json
- Macros are shared across configs in macros.json
- The libraries/ folder contains KMK firmware (auto-managed)
- You can safely delete libraries/ to force a fresh download

SAVED CONFIGURATIONS:
---------------------
When you save a config file, it goes to: kmk_Config_Save/YourConfigName.json
This includes:
- Keymap layout for all layers
- Extension configurations (encoder, RGB, display, analog input)
- RGB matrix colors and layer-specific colors
- Boot.py settings

REQUIREMENTS:
-------------
- Windows 10/11 (64-bit)
- Raspberry Pi Pico 2 with CircuitPython 10.0.3
- USB connection to your Chronos Pad

TROUBLESHOOTING:
----------------
If the app can't find libraries:
1. Make sure kmk_Config_Save/ and libraries/ folders are in the same directory as the .exe
2. Delete libraries/ folder and restart the app to re-download
3. Check that you're not running from a compressed/zipped folder

If settings aren't saving:
1. Make sure you have write permissions in the folder
2. Try running as administrator (right-click .exe → Run as administrator)
3. Check that settings.json, macros.json, and profiles.json can be created

SUPPORT:
--------
GitHub: https://github.com/D1odeKing/Chronos-Pad-Configtool
Documentation: https://github.com/D1odeKing/Chronos-Pad-Configtool/tree/main/docs
Issues: https://github.com/D1odeKing/Chronos-Pad-Configtool/issues

Enjoy your Chronos Pad! 🎹
"""
    
    with open(dist_root / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content.strip())
    print(f"  ✓ Created README.txt with usage instructions")
    
    # Create a .gitignore for the libraries folder
    gitignore_content = """# Auto-downloaded dependencies
*
!.gitignore
"""
    with open(libraries_folder / ".gitignore", 'w') as f:
        f.write(gitignore_content.strip())
    print(f"  ✓ Created .gitignore in libraries/")
    
    print("\n" + "=" * 60)
    print("✅ Build completed successfully!")
    print("=" * 60)
    print(f"\n📦 Distribution folder: dist\\ChronosPadConfigurator\\")
    print(f"📄 Executable: dist\\ChronosPadConfigurator\\ChronosPadConfigurator.exe")
    print(f"� Config folder: dist\\ChronosPadConfigurator\\kmk_Config_Save\\")
    print(f"📚 Libraries folder: dist\\ChronosPadConfigurator\\libraries\\")
    print(f"\n💡 The exe is fully portable - copy the entire folder anywhere!")
    print(f"🚀 The app will auto-download dependencies on first run.\n")
    
except subprocess.CalledProcessError as e:
    print(f"\n❌ Build failed with error code {e.returncode}")
    sys.exit(1)
except FileNotFoundError:
    print("\n❌ PyInstaller not found. Install it with:")
    print("   pip install pyinstaller")
    sys.exit(1)

