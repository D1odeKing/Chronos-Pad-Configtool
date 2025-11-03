# Usage Guide

Learn how to use the Chronos Pad Configurator to create your custom keyboard configuration.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the UI](#understanding-the-ui)
3. [Creating a Keymap](#creating-a-keymap)
4. [Working with Layers](#working-with-layers)
5. [Creating Macros](#creating-macros)
6. [Configuring Extensions](#configuring-extensions)
7. [Advanced Settings](#advanced-settings)
8. [Saving & Loading](#saving--loading)
9. [Deploying to Your Device](#deploying-to-your-device)

---

## Getting Started

### Launch the Configurator

**Windows (Exe):**
- Double-click `ChronosPadConfigurator.exe`

**From Source (Any Platform):**
```bash
python main.py
```

### Window Modes

The configurator is **fully responsive** and works in any window size:
- **Normal Mode**: Resizable window with all panels visible
- **Maximized Mode**: Expands to fill screen while maintaining proportions
- **Fullscreen Mode** (F11): Immersive full-screen experience

> 💡 **Tip**: Press F11 to toggle fullscreen mode for maximum working space!

### First Time?

1. The tool auto-detects dependencies and offers to download them
2. Initializes a blank 5×4 keymap
3. Loads previous session if available

---

## Understanding the UI

The configurator uses a **three-panel layout** that scales beautifully:

```
┌────────────────┬──────────────────────┬────────────────┐
│  LEFT PANEL    │   CENTER PANEL       │  RIGHT PANEL   │
│  (Settings)    │   (Keymap Grid)      │  (Assignment)  │
├────────────────┼──────────────────────┼────────────────┤
│ 📁 File Mgmt   │ 📑 Layer Tabs        │ 🔤 Key Types   │
│ 🔌 Extensions  │ ⌨ 5×4 Key Grid       │ ⚡ Macros       │
│ ⚙ Hardware     │                      │                │
└────────────────┴──────────────────────┴────────────────┘
```

### Left Panel

**📁 File Management**
- Load/save configurations
- Generate code.py for deployment
- Theme selection (Cheerful, Light, Dark)

**🔌 Extensions Tab**
- 🎛 Rotary Encoder configuration
- 📊 Analog Slider (volume/brightness)
- 🖥 OLED Display preview
- 💡 RGB Lighting settings

**⚙ Advanced Tab**
- Encoder sensitivity (steps per pulse)
- Boot.py configuration
- Read-only mode warnings
- USB settings

**⚙ Hardware & Profiles**
- Device information
- Diode orientation
- Save/load profiles

### Center Panel

**📑 Layer Management**
- Tab-based layer switching
- ➕ Add new layers
- ➖ Remove layers

**⌨ Keymap Grid**
- Visual 5×4 button grid
- Click to select keys
- Shows current key assignments

### Right Panel

**🔤 Key Assignment**
- Tabbed keycode categories
- Click to assign to selected key
- Search and filter options

**⚡ Macros**
- List of created macros
- ➕ Add, ✏ Edit, 🗑 Remove
- Click macro to assign to key

---

## Creating a Keymap

### Step 1: Configure Hardware

1. Look at the **"⚙ Hardware & Profiles"** panel (left side, bottom)
2. Review device information:
   - Board: Raspberry Pi Pico 2
   - Matrix: 5 rows × 4 columns (20 keys)
   - Features: Encoder • RGB • OLED • Analog
3. Set **Diode Orientation**:
   - `COL2ROW`: Standard for Chronos Pad (default)
   - `ROW2COL`: Check your PCB if using custom board

### Step 2: Select a Key

1. Click any button in the **5×4 grid** (center panel)
2. The button highlights with a colored border
3. **Selected Key** label shows coordinates

### Step 3: Assign a Keycode

1. With a key selected, browse the **"🔤 Key Assignment"** tabs (right side)
2. Choose a category (Basic, Modifiers, Navigation, Media, etc.)
3. Click a keycode to assign it
4. The grid button updates immediately with the new key

**Common Keycode Categories:**
- **Basic**: Letters A-Z, numbers 0-9
- **Modifiers**: Ctrl, Shift, Alt, GUI (Windows/Cmd)
- **Navigation**: Arrows, Home, End, Page Up/Down
- **Function**: F1-F24 function keys
- **Media**: Volume, mute, play/pause, next/prev
- **Mouse**: Mouse movement and clicks
- **Layers**: Layer switching keys (MO, TG, DF)
- **Misc**: Special keys, Reset, Transparent

**Example Workflow:**
```
1. Click key at position (0, 2)
2. Go to "Basic" tab in Key Assignment
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

Extensions add powerful hardware features to your Chronos Pad. All extensions are organized in a modern tabbed interface.

### Extensions Tab (🔌)

Navigate to the **Extensions** tab in the left panel to access all hardware features:

#### 🎛 Rotary Encoder
- **Pins**: GP10 (A), GP11 (B), GP14 (Button)
- **Features**: Layer cycling, custom rotation/button actions
- Check the box to enable
- Click **"⚙ Configure Actions"** to set up rotation and button
- See [ENCODER_SETUP.md](../ENCODER_SETUP.md) for details

#### 📊 Analog Slider
- **Pin**: GP28
- **Function**: Volume control or RGB brightness
- Check the box to enable
- Click **"⚙ Configure Function"** to choose mode:
  - **Volume Control**: Slider controls system volume (WORKING!)
  - **Brightness Control**: Slider controls RGB LED brightness
- Adjust sensitivity and polling rate

#### 🖥 OLED Display
- **Pins**: GP20 (SDA), GP21 (SCL)
- **Type**: 128×64 SH1106 OLED
- **Features**: Live keymap visualization with layer support
- Check the box to enable
- Click **"👁 Preview Layout"** to see generated display code
- Uses condensed 3-4 character abbreviations for optimal readability
- See [DISPLAY.md](DISPLAY.md) for details

#### 💡 RGB Lighting
- **Pin**: GP9
- **LEDs**: 20× SK6812MINI (per-key)
- **Features**: Per-key colors, underglow, layer-specific colors
- Check the box to enable
- Click **"⚙ Global Settings"** for brightness and defaults
- Click **"🎨 Per-Key Colors"** to customize individual keys
- Supports different colors per layer
- See [LAYER_RGB_SWITCHING.md](LAYER_RGB_SWITCHING.md) for details

> 💡 **Tip**: All extensions are optional! Disable unused features to save memory and reduce code complexity.

---

## Advanced Settings

The **Advanced** tab (⚙) provides power-user configuration options.

### Encoder Sensitivity

**Steps per action** (Encoder divisor):
- Controls how many encoder "clicks" before sending an action
- Range: 1-16 steps
- **Lower values (1-2)**: More sensitive, faster response
- **Higher values (6-8)**: Less sensitive, more deliberate control
- **Default: 4** - Works well for most standard rotary encoders

**When to adjust:**
- Encoder feels too "jumpy" → Increase steps
- Encoder feels unresponsive → Decrease steps

### Boot Configuration (⚡ boot.py)

Configure how your device boots. **Use with caution!**

#### Enable Custom boot.py
Check this box to create a custom boot.py file. Options include:

**⚠ Make storage read-only from computer** (RED WARNING!)
- CIRCUITPY drive becomes read-only when accessed from computer
- **You cannot edit files from your computer!**
- Requires editing code.py or bootloader recovery to undo
- **Warning dialog** will appear before enabling
- Only use this to protect against accidental file changes

**Disable USB keyboard/mouse (advanced)**
- Disables HID functionality
- Only use if you know what you're doing
- Device won't work as a keyboard if enabled!

**Rename drive to:**
- Change CIRCUITPY drive label
- Maximum 11 characters
- Example: "CHRONOSPAD", "MYBOARD", "MACRO20"

**Custom boot.py code:**
- Advanced: Add your own boot.py Python code
- Use for custom imports, initialization, etc.
- Runs before code.py on device boot

#### Safety Features

The configurator includes multiple safety layers:
1. **Visual Warning**: Read-only checkbox styled in bold red
2. **Confirmation Dialog**: Shows consequences before enabling
3. **Auto-uncheck**: If you click "No", checkbox reverts
4. **Documentation**: Tooltips explain every option

> ⚠️ **Important**: If you enable read-only mode by accident:
> 1. Edit code.py on the device (add a line to disable)
> 2. Or enter UF2 bootloader mode and re-flash CircuitPython
> 3. See [CIRCUITPYTHON_SETUP.md](CIRCUITPYTHON_SETUP.md) for recovery

---

## Saving & Loading

### Save Configuration

Save your work to JSON file:

1. Click **"💾 Save Configuration"** in File Management
2. Choose a filename and location
3. Click **Save**

**Default location:** `kmk_Config_Save/` folder

**What's saved:**
- ✅ All layers and keymaps
- ✅ Macro definitions
- ✅ RGB color settings (per-key and per-layer)
- ✅ Extension configurations
- ✅ Encoder divisor and settings
- ✅ Boot.py configuration
- ✅ Profiles

**File format:** JSON v2.0 (human-readable, structured)

### Load Configuration

1. Select a config from the dropdown, or click **"📂 Load Configuration"**
2. Browse to a JSON file
3. Click **Open**
4. Configuration loads immediately

**Features:**
- Auto-detects format version
- Backward compatible with v1.0 configs
- Adapts to 5×4 grid if needed
- Preserves all settings

### Profiles

Save multiple named configurations for quick switching:

1. Configure your keyboard (keys, macros, extensions, advanced settings)
2. Click **"💾 Save as Profile"** in Hardware & Profiles
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

- CircuitPython 10.0.3 installed on Pico 2 (see [CIRCUITPYTHON_SETUP.md](../docs/CIRCUITPYTHON_SETUP.md))
- Pico 2 connected via USB
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

1. Your Pico 2 reboots automatically
2. Try pressing keys - they should work!
3. If using display, you should see the keymap
4. If using encoder, rotate to switch layers
5. Check RGB lighting if enabled

### Troubleshooting Deployment

**"CIRCUITPY drive not found"**
- Make sure Pico 2 is connected
- Check Device Manager for the Pico 2
- Reconnect the USB cable

**"Failed to copy code.py"**
- The Pico 2 might be busy
- Safely eject it from Windows/macOS
- Reconnect and try again

**Code runs but keys don't work**
- Check matrix pins in Hardware Configuration
- Verify diode orientation setting
- Check CircuitPython version (must be 10.0.3)

**Display shows scrambled text**
- Enable Display extension in Extensions panel
- Click Configure to preview
- Re-deploy code.py

**Volume control slider not working**
- ✅ **Fixed in latest version!**
- Enable Analog Slider in Extensions tab
- Configure for "Volume Control" mode
- Requires MediaKeys extension (auto-imported)
- Move slider to test volume up/down

**Encoder too sensitive/unresponsive**
- Go to Advanced tab (⚙)
- Adjust "Steps per action" (1-16)
- Lower = more sensitive, Higher = less sensitive
- Default is 4 steps
- Re-save code.py after changing

**Device becomes read-only**
- Advanced tab → Boot Configuration
- Uncheck "Make storage read-only"
- Save configuration and re-deploy
- Or see [CIRCUITPYTHON_SETUP.md](CIRCUITPYTHON_SETUP.md) for recovery

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
