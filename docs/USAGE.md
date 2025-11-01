# Usage Guide

Learn how to use the Chronos Pad Configurator to create your custom keyboard configuration.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating a Keymap](#creating-a-keymap)
3. [Working with Layers](#working-with-layers)
4. [Creating Macros](#creating-macros)
5. [Configuring Extensions](#configuring-extensions)
6. [Saving & Loading](#saving--loading)
7. [Deploying to Your Device](#deploying-to-your-device)

---

## Getting Started

### Launch the Configurator

**Windows (Exe):**
- Double-click `ChronosPadConfigurator.exe`

**From Source (Any Platform):**
```bash
python main.py
```

### First Time?

1. The tool detects your configuration
2. Initializes a blank 5×4 keymap
3. Loads previous profiles if available

---

## Creating a Keymap

### Step 1: Configure Hardware

1. Look at the **"Hardware Configuration"** panel (left side)
2. Set **Diode Orientation**:
   - `COL2ROW`: Most common for custom keyboards
   - `ROW2COL`: Check your PCB documentation
3. Leave other settings as-is (fixed pins for Chronos Pad)

```
Hardware Configuration:
┌─────────────────────────┐
│ Board: Raspberry Pi Pico│
│ Matrix: 5x4             │
│ Diode: [COL2ROW  ▼]     │
│ Profile: [Custom    ▼] │
└─────────────────────────┘
```

### Step 2: Select a Key

1. Click any button in the **5×4 grid** (center panel)
2. The button will highlight in blue
3. Look at the **"Selected Key"** label to confirm

```
Keymap (Layer 0):
┌─────────────────────────────┐
│ [A]  [B]  [C]  [D]          │
│ [E]  [F]  [G]  [H]          │
│ [I]  [J]  [K]  [L]          │
│ [M]  [N]  [O]  [P]          │
│ [Q]  [R]  [S]  [T]          │
└─────────────────────────────┘
Selected Key: (0, 0)  ← Shows row, col
```

### Step 3: Assign a Keycode

1. With a key selected, browse the **"Key Assignment"** tabs (right side)
2. Choose a category (Letters, Numbers, Modifiers, Media, etc.)
3. Click a keycode to assign it
4. The grid button updates with the new key

**Common Keycode Categories:**
- **Letters**: A-Z, quick access
- **Numbers**: 0-9, @#$% symbols
- **Modifiers**: Shift, Ctrl, Alt, GUI
- **Navigation**: Arrow keys, Home, End, Page Up/Down
- **Media**: Volume, mute, play, next
- **Functions**: F1-F24 keys
- **Special**: Enter, Space, Tab, Backspace
- **Macros**: Your custom macros (created in Macros section)

**Example Workflow:**
```
1. Click key at position (0, 2)
2. Go to "Letters" tab
3. Click "C"
4. Key (0, 2) now shows "C"
```

### Step 4: Deselect a Key

- Click the same button again, OR
- Click a different button to select a new one

---

## Working with Layers

Layers let you create multiple keyboard layouts and switch between them.

### Understanding Layers

- **Layer 0**: Default layout (always active)
- **Layers 1+**: Alternate layouts (activated by layer keys or encoder)
- **Max layers**: Unlimited, but performance degrades beyond 10

### Creating Layers

1. Look at the **Layer tabs** (above the grid)
2. Click the **"+"** button (right of the tabs)
3. A new blank layer is created
4. Click the new tab to edit it

```
Layer 0  Layer 1  Layer 2  [+] [-]
  ↓                               ↑
  Current layer            Add/Remove buttons
```

### Deleting Layers

1. Click the layer you want to delete
2. Click the **"-"** button
3. Confirm the deletion
4. Minimum 1 layer must always exist

### Editing Layers

Each layer is completely independent:

1. Click the tab for the layer you want to edit
2. Assign keys as normal (see [Creating a Keymap](#creating-a-keymap))
3. Click another tab to switch layers
4. Your changes are saved automatically

### Layer Switching Keys

Use these keys to switch between layers in your keymap:

**Momentary (hold to activate):**
- `KC.MO(1)` - Activate Layer 1 while held

**Toggle (press to switch on/off):**
- `KC.TG(2)` - Toggle Layer 2 on/off

**One-shot (switch and stay):**
- `KC.TO(3)` - Switch permanently to Layer 3

**Layer navigation:**
- `KC.LAYER_PREV` - Go to previous layer
- `KC.LAYER_NEXT` - Go to next layer

**Example Setup:**
```
Layer 0:  A  B  C  D
          └─ MO(1) on one key
          
Layer 1:  1  2  3  4
          └─ MO(0) to go back
```

---

## Creating Macros

Macros let you automate key sequences, text, and more.

### Step 1: Open Macro Editor

1. Click **"Add"** in the **"Macros"** panel (bottom right)
2. Enter a macro name (e.g., "greet", "email_prefix")
3. Click **"New action"** to add actions

### Step 2: Add Actions

Click **"New action"** and choose:

**Text (Type Text)**
- Adds text literally
- Example: Type "Hello, World!"

**Key Tap (Tap a Key)**
- Presses and releases a key instantly
- Example: Press Enter

**Key Press (Hold Down)**
- Holds a key down (wait for release action)
- Example: Hold Shift, then tap other keys

**Key Release (Release Key)**
- Releases a held key
- Example: Release Shift

**Delay**
- Wait for milliseconds
- Example: Delay 500ms (for slow typing effect)

### Step 3: Example Macros

**Email Macro:**
```
1. Text: "john@example.com"
2. Key Tap: KC.ENTER
```

**Copy Command (Ctrl+C):**
```
1. Key Press: KC.LCTL (hold Ctrl)
2. Key Tap: KC.C (tap C)
3. Key Release: KC.LCTL (release Ctrl)
```

**Slow Text Entry:**
```
1. Text: "H"
2. Delay: 100ms
3. Text: "i"
4. Delay: 100ms
5. Text: "!"
```

### Step 4: Assign Macro to Key

1. Select a key in the grid (see [Creating a Keymap](#creating-a-keymap))
2. Go to the **"Macros"** tab in Key Assignment
3. Click your macro name
4. The key now displays `M: <macro_name>`

### Step 5: Edit or Delete Macro

1. Select macro in the **Macros** list
2. Click **"Edit"** to modify
3. Click **"Remove"** to delete

**Note:** Macros assigned to keys are preserved even if you delete the macro, but they won't do anything.

---

## Configuring Extensions

Extensions are optional hardware features. Enable only what you need.

### Available Extensions

All extensions are in the **Extensions panel** (top right):

- ✅ **Encoder** (GP10, GP11, GP14) - Rotary encoder with button
- ⚠️ **Analog Input** (GP28) - Slider potentiometer (under development)
- ✅ **Display** (GP20, GP21) - OLED screen with keymap view
- ✅ **RGB Matrix** (GP9) - Per-key LED lighting

### Enabling/Disabling Extensions

1. Check/uncheck the checkbox next to an extension
2. When unchecked, the code isn't included in `code.py`
3. When checked, the "Configure" button becomes active

```
Extensions:
☑ Encoder (GP10, GP11, GP14)        [Configure]
☑ Analog Input (GP28 - Slider)      [Configure]
☑ Display (I2C: GP20/GP21)          [Configure]
☑ RGB Matrix (GP9)                  [Configure]
    └─ [Per-key Colors]
```

### Configuring Each Extension

Click **"Configure"** for each enabled extension:

**Encoder Configuration**
- Assign keys to rotation/button
- See [EXTENSIONS.md](EXTENSIONS.md) for details

**Display Configuration**
- Preview auto-generated display code
- Shows all layers
- See [DISPLAY.md](DISPLAY.md) for details

**RGB Configuration**
- Set default colors
- Map colors per-key
- See [EXTENSIONS.md](EXTENSIONS.md) for details

**Analog Input Configuration**
- Assign slider range
- Map to keys/macros
- See [EXTENSIONS.md](EXTENSIONS.md) for details

---

## Saving & Loading

### Save Configuration

Save your work to JSON file:

1. Click **File → Save Configuration**
2. Choose a filename and location
3. Click **Save**

**Default location:** `kmk_Config_Save/` folder

**What's saved:**
- ✅ All layers and keymaps
- ✅ Macro definitions
- ✅ RGB color settings
- ✅ Extension configurations
- ✅ Profiles

**File format:** JSON (human-readable)

### Load Configuration

1. Click **File → Load Configuration**
2. Select a JSON file
3. Click **Open**
4. Configuration loads into the editor

**Features:**
- Auto-detects 5×4 grid and adapts if needed
- Preserves macro assignments
- Loads all layer data

### Profiles

Save multiple named configurations:

1. Configure your keyboard (keys, macros, extensions)
2. Click **"Save Profile"** in Hardware Configuration
3. Enter a name (e.g., "Gaming", "Work", "Default")
4. Click **OK**

**Using Profiles:**
1. Open the **Profile** dropdown
2. Select a saved profile name
3. Configuration auto-loads

**Managing Profiles:**
- View all profiles in the dropdown
- Click **"Del"** to remove current profile
- Switch quickly between setups

---

## Deploying to Your Device

### Prerequisites

- CircuitPython 9.x or later installed on Pico (see [CIRCUITPYTHON_SETUP.md](../docs/CIRCUITPYTHON_SETUP.md))
- Pico connected via USB
- `CIRCUITPY` drive visible on your computer

### Step 1: Generate Code

1. Configure your keymap, layers, macros, and extensions
2. Click **"Save code.py"** (bottom of window)

### Step 2: Select Destination

1. File browser opens
2. Tool auto-detects `CIRCUITPY` drive
3. If not detected, browse to your CIRCUITPY folder manually
4. Click **Select Folder**

### Step 3: Automatic Deployment

The tool automatically:
1. ✅ Generates complete KMK firmware code
2. ✅ Creates necessary folders (`lib/`, `kmk/`)
3. ✅ Copies KMK firmware (if not present)
4. ✅ Downloads and installs required libraries
5. ✅ Saves `code.py` to the Pico
6. ✅ Shows success message

**This process takes 30 seconds - 2 minutes depending on internet speed**

### Step 4: Test Your Configuration

1. Your Pico reboots automatically
2. Try pressing keys - they should work!
3. If using display, you should see the keymap
4. If using encoder, rotate to switch layers
5. Check RGB lighting if enabled

### Troubleshooting Deployment

**"CIRCUITPY drive not found"**
- Make sure Pico is connected
- Check Device Manager for the Pico
- Reconnect the USB cable

**"Failed to copy code.py"**
- The Pico might be busy
- Safely eject it from Windows/macOS
- Reconnect and try again

**Code runs but keys don't work**
- Check matrix pins in Hardware Configuration
- Verify diode orientation setting
- Check CircuitPython version (must be 9.x or later)

**Display shows scrambled text**
- Enable Display extension in Extensions panel
- Click Configure to preview
- Re-deploy code.py

---

## Keyboard in Action

Once deployed:

1. **Press keys** - They send the assigned keycodes
2. **Rotate encoder** - Cycles through layers (if enabled)
3. **Watch display** - Shows current keymap and layer (if enabled)
4. **Press macros** - Execute the sequences

---

## Tips & Tricks

### Organization Tips

- ✅ Use logical layer names (Gaming, Typing, Media)
- ✅ Group similar keys together
- ✅ Use layer 0 for most-used keys
- ✅ Save profiles for different setups

### Performance Tips

- ✅ Limit macros to 20+ actions
- ✅ Use delays sparingly (slows typing)
- ✅ Avoid too many layers (>10)
- ✅ Test on device frequently

### Backup Tips

- ✅ Save configuration before major changes
- ✅ Use profiles as backups
- ✅ Keep copies of JSON files
- ✅ Push configs to GitHub for version control

---

## Next Steps

- ➡️ See [EXTENSIONS.md](EXTENSIONS.md) for detailed hardware configuration
- ➡️ See [DISPLAY.md](DISPLAY.md) for OLED setup
- ➡️ Check [INSTALLATION.md](INSTALLATION.md) for setup help
- ➡️ Read [BUILD_EXE.md](BUILD_EXE.md) if building from source

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 See [README.md](../README.md) for project overview
