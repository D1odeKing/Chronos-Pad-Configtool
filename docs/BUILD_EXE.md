# Building Your Own Executable

This guide shows you how to create a standalone Windows executable from the source code.

---

## Why Build Your Own?

- ✅ Customize the build for your needs
- ✅ Create your own distribution
- ✅ Contribute improvements back
- ✅ Build for different architectures
- ✅ Understand the packaging process

---

## Prerequisites

### System Requirements
- Windows 7 or later (for PyInstaller)
- Python 3.8 or higher
- At least 1 GB free disk space (for PyInstaller cache)

### Software Dependencies

```bash
# Install PyInstaller (required)
pip install pyinstaller>=6.0

# Install application dependencies
pip install PyQt6
```

---

## Quick Build (Recommended)

### Using the Build Script

The easiest way to build:

```bash
python build_exe.py
```

This script:
- Cleans up old builds
- Runs PyInstaller with optimal settings
- Creates `dist/ChronosPadConfigurator.exe`
- Shows you the build output

**Result**: `dist/ChronosPadConfigurator.exe` (~38 MB)

---

## Manual Build

If you want more control over the build process:

### Step 1: Prepare Your Environment

```bash
# Create a virtual environment (optional but recommended)
python -m venv build_env
build_env\Scripts\activate

# Install dependencies
pip install PyQt6 pyinstaller
```

### Step 2: Run PyInstaller

**One-line command:**

```bash
pyinstaller --onefile --windowed --name ChronosPadConfigurator main.py --add-data "profiles.json;."
```

**Breakdown of options:**
- `--onefile`: Create a single executable (instead of folder)
- `--windowed`: Don't show console window
- `--name ChronosPadConfigurator`: Name of the exe
- `main.py`: The Python script to package
- `--add-data "profiles.json;."`: Include profiles.json in the exe

### Step 3: Find Your Executable

```
dist/
└── ChronosPadConfigurator.exe   ← Your executable!
```

---

## Advanced Configuration

### Using PyInstaller Spec File

For more control, create a `.spec` file:

```bash
pyinstaller --onefile --windowed --name ChronosPadConfigurator main.py
```

This creates `ChronosPadConfigurator.spec`. Edit it:

```python
# ChronosPadConfigurator.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('profiles.json', '.')],  # Include data files
    hiddenimports=['PyQt6'],  # Ensure imports are found
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChronosPadConfigurator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX for compression (faster startup)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Don't show console
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Then build with:

```bash
pyinstaller ChronosPadConfigurator.spec
```

---

## Optimization Tips

### Reduce Exe Size

**Enable UPX compression** (if installed):

```bash
pip install upx
pyinstaller --upx-dir=C:\path\to\upx --onefile --windowed main.py
```

This can reduce exe size to ~25-30 MB.

### Improve Startup Speed

Add these options:

```bash
pyinstaller --onefile --windowed --optimize=2 main.py
```

- `-O2` optimizes Python bytecode

### Single-Thread for Stability

Some systems need single-threading:

```bash
pyinstaller --onefile --windowed --nothreaded main.py
```

---

## Distribution

### Creating a Release Package

Once you've built the exe:

1. **Test on a clean machine** (important!)
2. **Create a release on GitHub**:
   ```bash
   git tag v1.1.0
   git push --tags
   ```
3. **Upload the exe to GitHub Releases**:
   - Go to https://github.com/D1odeKing/Chronos-Pad-Configtool/releases
   - Click "Create new release"
   - Attach `ChronosPadConfigurator.exe`
   - Write release notes

### Hosting Options

- ✅ **GitHub Releases** (recommended) - Free, reliable
- ✅ **Google Drive** - Easy sharing
- ✅ **Dropbox** - Good for backups
- ✅ Your own website

---

## Troubleshooting

### "PyInstaller not found"

```bash
pip install pyinstaller
```

### "Module not found" errors during build

Add hidden imports to your build command:

```bash
pyinstaller --hidden-import=PyQt6 --onefile --windowed main.py
```

### Exe won't start / crashes immediately

1. Run from command line to see error:
   ```bash
   dist\ChronosPadConfigurator.exe
   ```

2. Check console output for errors

3. Rebuild without `--windowed` to see console:
   ```bash
   pyinstaller --onefile main.py  # No --windowed
   ```

4. Try disabling optimizations:
   ```bash
   pyinstaller --onefile --windowed --optimize=0 main.py
   ```

### Exe is too large (>50 MB)

1. Ensure UPX is enabled
2. Remove unnecessary modules with `--exclude-module`
3. Build with optimization: `-O2`

### "Missing Visual C++ Runtime"

Users need Microsoft Visual C++ Redistributable:
- https://support.microsoft.com/en-us/help/2977003
- Choose the x64 version

---

## Build Process Explained

Here's what happens when you build:

1. **PyInstaller analyzes** your code to find dependencies
2. **PyInstaller bundles** Python interpreter + all dependencies
3. **Creates bootloader** that unpacks and runs your code
4. **Compresses** with UPX (if enabled)
5. **Creates single executable** in `dist/` folder

The exe is **self-contained** and runs without Python installed!

---

## Continuous Integration (CI/CD)

You can automate builds with GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Build Exe

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install PyQt6 pyinstaller
      - run: python build_exe.py
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/ChronosPadConfigurator.exe
```

---

## Performance Comparison

| Factor | Impact |
|--------|--------|
| UPX compression | -10-15 MB size, slower startup |
| `-O2` optimization | Faster runtime, slightly larger exe |
| Single file | Larger, but portable |
| Nothreaded mode | More stable on some systems |

---

## Tips for Success

1. ✅ **Test on a clean machine** before distributing
2. ✅ **Keep build script updated** as dependencies change
3. ✅ **Version your builds** with semantic versioning (v1.0.0, v1.1.0, etc.)
4. ✅ **Include release notes** explaining what's new
5. ✅ **Support the original projects** (KMK, PyQt6, etc.)

---

## Next Steps

- ➡️ Test your exe on a different Windows machine
- ➡️ Create a GitHub Release with the exe
- ➡️ Share it with the community!

---

## Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [PyInstaller Hooks](https://pyinstaller.readthedocs.io/en/stable/hooks.html)
- [Creating Releases on GitHub](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 See [INSTALLATION.md](INSTALLATION.md) for installation instructions
