"""
Build script for creating Chronos Pad Configurator executable
Run this script to build the .exe: python build_exe.py

Creates a clean distribution structure:
dist/
  ChronosPadConfigurator/
    ChronosPadConfigurator.exe  (single bundled exe)
    data/                       (profiles and configs)
    libraries/                  (downloaded dependencies)
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
    data_folder = dist_root / "data"
    libraries_folder = dist_root / "libraries"
    
    # Create folders
    data_folder.mkdir(parents=True, exist_ok=True)
    libraries_folder.mkdir(parents=True, exist_ok=True)
    
    # Move the exe into the ChronosPadConfigurator folder
    exe_source = Path("dist/ChronosPadConfigurator.exe")
    exe_dest = dist_root / "ChronosPadConfigurator.exe"
    
    if exe_source.exists():
        shutil.move(str(exe_source), str(exe_dest))
        print(f"  ✓ Moved ChronosPadConfigurator.exe to ChronosPadConfigurator/")
    
    # Copy profiles.json to data folder
    if os.path.exists('profiles.json'):
        shutil.copy2('profiles.json', data_folder / 'profiles.json')
        print(f"  ✓ Copied profiles.json to data/")
    
    # Create README.txt with instructions
    readme_content = """
Chronos Pad Configurator - Portable Distribution
================================================

CONTENTS:
---------
ChronosPadConfigurator.exe  - Main application (double-click to run)
data/                       - Configuration files and profiles
libraries/                  - Auto-downloaded KMK firmware and libraries
                             (will be populated on first run)

FIRST RUN:
----------
1. Double-click ChronosPadConfigurator.exe
2. The app will automatically download required libraries
3. Wait for the download to complete (~30-60 seconds)
4. Start configuring your Chronos Pad!

USAGE:
------
- All your saved configurations will be stored in the data/ folder
- Profiles are quick-load presets you can save and switch between
- The libraries/ folder contains KMK firmware (auto-managed)
- You can safely delete the libraries/ folder to force a fresh download

REQUIREMENTS:
-------------
- Windows 10/11 (64-bit)
- Raspberry Pi Pico 2 with CircuitPython 10.0.3
- USB connection to your Chronos Pad

SUPPORT:
--------
GitHub: https://github.com/D1odeKing/Chronos-Pad-Configtool
Documentation: See docs/ folder in the repository

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
    print(f"📁 Data folder: dist\\ChronosPadConfigurator\\data\\")
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

