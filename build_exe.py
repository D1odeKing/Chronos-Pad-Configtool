"""
Build script for creating Chronos Pad Configurator executable
Run this script to build the .exe: python build_exe.py
"""
import subprocess
import sys
import os
import shutil

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
    shutil.rmtree('dist', ignore_errors=True)

# PyInstaller command - using Python module syntax
command = [
    sys.executable,  # Python interpreter
    '-m',
    'PyInstaller',
    '--clean',
    'ChronosPadConfigurator.spec'
]

print("Building Chronos Pad Configurator executable...")
print(f"Command: {' '.join(command)}")
print()

try:
    result = subprocess.run(command, check=True)
    print("\n✅ Build successful!")
    print(f"Executable location: dist\\ChronosPadConfigurator.exe")
    print("\nThe exe will auto-download KMK firmware and libraries on first run.")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Build failed with error code {e.returncode}")
    sys.exit(1)
except FileNotFoundError:
    print("\n❌ PyInstaller not found. Install it with:")
    print("   pip install pyinstaller")
    sys.exit(1)
