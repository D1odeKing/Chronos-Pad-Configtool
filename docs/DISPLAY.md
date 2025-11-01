# OLED Display Guide

Complete guide to the OLED display feature and layer-aware visualization.

---

## Overview

The OLED display shows a real-time, layer-aware visualization of your keyboard's current keymap.

- **Hardware**: 128×64 I2C OLED display (SH1106 driver)
- **Pins**: GP20 (SDA), GP21 (SCL)
- **Features**: 
  - Shows all 5×4 keys
  - Live layer indicator
  - Auto-updates on layer changes
  - Proper 180° rotation for correct orientation
- **Status**: ✅ Fully working

---

## Display Layout

The display shows your keyboard in an easy-to-read format:

```
┌─────────────────────────────────┐
│ Layer 0                         │ ← Layer indicator
├─────────────────────────────────┤
│ A     B     C     D             │
│ E     F     G     H             │
│ I     J     K     L             │
│ M     N     O     P             │
│ Q     R     S     T             │
└─────────────────────────────────┘

Physical layout matches display layout
(no mirroring or confusion!)
```

### Key Abbreviations

Keys are shortened to fit the display:

| Full Name | Display | Full Name | Display |
|-----------|---------|-----------|---------|
| KC.A | A | KC.LCTL | LCtl |
| KC.BACKSPACE | BkSp | KC.LSFT | LSft |
| KC.SPACE | Spce | KC.LALT | LAlt |
| KC.ENTER | Entr | KC.LGUI | LGui |
| KC.TAB | Tab | KC.RCTL | RCtl |
| KC.ESC | Esc | KC.RSFT | RSft |
| KC.DELETE | Del | KC.RALT | RAlt |
| KC.HOME | Home | KC.RGUI | RGui |
| KC.END | End | KC.VOLUME_UP | Vol+ |
| KC.PAGE_UP | PgUp | KC.VOLUME_DOWN | Vol- |
| KC.PAGE_DOWN | PgDn | KC.MUTE | Mute |
| KC.UP | Up | KC.MEDIA_PLAY | Play |
| KC.DOWN | Down | KC.MEDIA_NEXT | Next |
| KC.LEFT | Left | KC.MEDIA_PREV | Prev |
| KC.RIGHT | Rght | KC.MEDIA_STOP | Stop |

### Layer Switches

Layer control keys show their target:

| Key | Display |
|-----|---------|
| KC.MO(1) | MO(1) |
| KC.TO(2) | TO(2) |
| KC.TG(3) | TG(3) |
| KC.LAYER_PREV | Prev← |
| KC.LAYER_NEXT | Next→ |

### Special Cases

```
Empty/No Key  → (blank)
Transparent   → Trans
Macros        → M: macro_name (first 6 chars)
Custom codes  → Abbreviation or ?
```

---

## Enabling the Display

### In the Configurator

1. Go to **Extensions** panel (top right)
2. Check **"Display (I2C: GP20/GP21)"**
3. Click **"Configure"** to preview generated code

### Hardware Wiring

Connect your OLED display to the Pico:

```
OLED Display    Raspberry Pi Pico
VCC      ─────→ 3V3 (pin 36)
GND      ─────→ GND (pin 38)
SDA      ─────→ GP20 (pin 26)
SCL      ─────→ GP21 (pin 27)
```

**Typical OLED pinout:**
```
┌──────────────────┐
│ VCC  GND  SDA SCL│
└──────────────────┘
 ↑    ↑    ↑    ↑
 │    │    │    └─ GP21
 │    │    └─────── GP20
 │    └──────────── GND
 └───────────────── 3V3
```

---

## How It Works

### Automatic Code Generation

When Display is enabled, the configurator generates:

1. **Display initialization code**
   - Sets up I2C communication
   - Initializes SH1106 driver
   - Applies 180° rotation

2. **Keymap data for all layers**
   - Stores abbreviated names for all keys
   - One entry per layer

3. **LayerDisplaySync module**
   - Monitors keyboard layer changes
   - Updates display when layer changes
   - Runs after matrix scan and HID send

### Layer Tracking

The display tracks your active layer automatically:

**Works with:**
- ✅ Encoder rotation (if LayerCycler configured)
- ✅ Layer toggle keys (KC.TO, KC.MO, KC.TG)
- ✅ Layer switch keys (KC.LAYER_NEXT, KC.LAYER_PREV)
- ✅ Any KMK layer switching method

**The display updates:**
- When you press a layer key
- When you rotate the encoder
- When you press KC.MO(x) (momentary)
- When you toggle with KC.TG(x)

---

## Display Code Structure

### Part 1: Display Initialization

```python
import board
import busio
import displayio
import terminalio
import adafruit_displayio_sh1106
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

# Initialize I2C
displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = I2CDisplayBus(i2c, device_address=0x3C)

# Initialize display
display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=128,
    height=64,
    rotation=180,      # Rotate to match physical layout
    colstart=2         # Column offset for SH1106
)

splash = displayio.Group()
display.root_group = splash
```

### Part 2: Layer Keymap Data

```python
all_layer_labels = [
    # Layer 0
    [
        ["A", "B", "C", "D"],
        ["E", "F", "G", "H"],
        ["I", "J", "K", "L"],
        ["M", "N", "O", "P"],
        ["Q", "R", "S", "T"],
    ],
    # Layer 1
    [
        ["1", "2", "3", "4"],
        ["5", "6", "7", "8"],
        # ... etc
    ],
]
```

### Part 3: Display Update Function

```python
def update_display_for_layer(layer_index):
    """Update display to show keymap for specified layer"""
    global splash
    
    # Clear display
    while len(splash) > 0:
        splash.pop()
    
    # Add layer indicator
    layer_label = label.Label(
        terminalio.FONT,
        text=f"Layer {layer_index}",
        color=0xFFFFFF,
        x=2, y=4
    )
    splash.append(layer_label)
    
    # Get keymap for layer
    if layer_index < len(all_layer_labels):
        key_labels = all_layer_labels[layer_index]
    else:
        key_labels = all_layer_labels[0]
    
    # Display all keys
    for row_idx, row in enumerate(key_labels):
        for col_idx, key_text in enumerate(row):
            # Calculate position (mirrored for 180° rotation)
            x_pos = (4 - 1 - col_idx) * 32 + 1
            y_pos = row_idx * 12 + 14
            
            text_area = label.Label(
                terminalio.FONT,
                text=key_text,
                color=0xFFFFFF,
                x=x_pos,
                y=y_pos
            )
            splash.append(text_area)
```

### Part 4: Layer Sync Module

```python
class LayerDisplaySync:
    """Keep OLED display in sync with keyboard state"""
    
    def __init__(self):
        self._last_layer = None
    
    def _active_layer(self, keyboard):
        """Get highest priority active layer"""
        try:
            layers = getattr(keyboard, "active_layers", None)
            if layers and len(layers) > 0:
                return layers[-1]
        except:
            pass
        return 0
    
    def _check_and_update(self, keyboard):
        """Check if layer changed and update display"""
        current = self._active_layer(keyboard)
        if current != self._last_layer:
            self._last_layer = current
            try:
                update_display_for_layer(current)
            except:
                pass
    
    def before_matrix_scan(self, keyboard):
        return
    
    def during_bootup(self, keyboard):
        self._last_layer = self._active_layer(keyboard)
        try:
            update_display_for_layer(self._last_layer)
        except:
            pass
    
    def after_matrix_scan(self, keyboard):
        """Check for layer changes after scanning"""
        self._check_and_update(keyboard)
    
    def before_hid_send(self, keyboard):
        return
    
    def after_hid_send(self, keyboard):
        """Check for layer changes after HID send"""
        self._check_and_update(keyboard)
    
    def on_powersave_enable(self, keyboard):
        return
    
    def on_powersave_disable(self, keyboard):
        return

# Initialize module
layer_display_sync = LayerDisplaySync()
keyboard.modules.append(layer_display_sync)

# Show initial layer
update_display_for_layer(0)
```

---

## Troubleshooting

### Display is Blank

**Possible causes:**
1. ❌ Display not powered
2. ❌ Wiring disconnected
3. ❌ I2C address wrong
4. ❌ Display not initialized

**Solutions:**

1. **Check power**
   - Multimeter on display VCC and GND
   - Should show 3.3V

2. **Check wiring**
   ```
   GP20 ──→ SDA
   GP21 ──→ SCL
   3V3  ──→ VCC
   GND  ──→ GND
   ```

3. **Check I2C address**
   - Some displays use 0x3D instead of 0x3C
   - Edit code: change `device_address=0x3C` to `0x3D`
   - Re-deploy code.py

4. **Test with CircuitPython REPL**
   ```python
   import board
   import busio
   i2c = busio.I2C(board.GP21, board.GP20)
   print(i2c.scan())  # Should print [60] or [61]
   ```

### Display Shows Scrambled Text

**Possible causes:**
1. ❌ Wrong rotation setting
2. ❌ Wrong column offset (colstart)
3. ❌ SH1106 vs SSD1306 driver difference
4. ❌ Font rendering issue

**Solutions:**

1. **Try different rotations**
   ```python
   # In code.py, try each:
   rotation=0    # Normal
   rotation=90   # Rotated 90°
   rotation=180  # Rotated 180° (current)
   rotation=270  # Rotated 270°
   ```

2. **Check column offset**
   ```python
   # SH1106 needs colstart
   colstart=0   # Try this
   colstart=2   # Current (try if above fails)
   colstart=4   # Or this
   ```

3. **Verify display type**
   ```python
   # Check your display docs - if it's SSD1306:
   import adafruit_displayio_ssd1306
   display = adafruit_displayio_ssd1306.SSD1306(...)
   ```

### Layer Indicator Doesn't Update

**Possible causes:**
1. ❌ LayerDisplaySync not included
2. ❌ Layer switching code not working
3. ❌ Module hook not being called

**Solutions:**

1. **Verify LayerDisplaySync is in code**
   - Open `code.py` on Pico
   - Search for "class LayerDisplaySync"
   - Should be present

2. **Test layer switching**
   - Press a layer key manually
   - Watch display for changes
   - If nothing happens, layer code might be wrong

3. **Check module is added**
   - Search for "keyboard.modules.append(layer_display_sync)"
   - Make sure it's there

4. **Try encoder if available**
   - Rotate encoder to switch layers
   - See if display updates
   - Narrows down the issue

### Display Shows Wrong Layer Number

**Possible causes:**
1. ❌ off-by-one error in layer count
2. ❌ Active layers tracking wrong value

**Solutions:**

1. **Count your layers**
   - In configurator, count Layer tabs
   - Should show 0 to N-1
   - If you have 3 layers: 0, 1, 2

2. **Check active_layers**
   - Add debug print to LayerDisplaySync:
   ```python
   def _active_layer(self, keyboard):
       layers = getattr(keyboard, "active_layers", None)
       print(f"Active layers: {layers}")  # Debug line
       if layers and len(layers) > 0:
           return layers[-1]
       return 0
   ```

### Display Performance Issues

**Slow updates or lag:**

**Solutions:**

1. **Reduce update frequency**
   - Only update in `after_hid_send` (remove `after_matrix_scan`)
   - Less frequent updates = smoother typing

2. **Optimize key label strings**
   - Keep abbreviations short
   - Avoid long names

3. **Check CircuitPython version**
   - Use 9.x (9.2.9+ recommended)
   - Newer versions are faster

---

## Advanced Customization

### Custom Display Layout

You can modify the generated code to customize the display:

```python
def update_display_for_layer(layer_index):
    """Custom display with different layout"""
    global splash
    
    # Clear
    while len(splash) > 0:
        splash.pop()
    
    # Custom header
    header = label.Label(
        terminalio.FONT,
        text=f"KEYBOARD - Layer {layer_index}",
        color=0xFFFFFF,
        x=0, y=0
    )
    splash.append(header)
    
    # Custom bottom info
    if layer_index == 0:
        info = "DEFAULT"
    elif layer_index == 1:
        info = "NUMBERS"
    else:
        info = f"LAYER {layer_index}"
    
    info_label = label.Label(
        terminalio.FONT,
        text=info,
        color=0xFFFFFF,
        x=0, y=55
    )
    splash.append(info_label)
    
    # Rest of key display...
```

### Custom Key Abbreviations

Edit the abbreviations table in the configurator (or code):

```python
abbreviations = {
    "LCTL": "CTL",      # Change
    "LSFT": "SHF",      # Abbreviations
    "LALT": "ALT",      # here
    "LGUI": "CMD",      # to suit
    "BSPC": "←",        # your
    "ENT": "↩",         # preference
    "SPC": "█",
    "TAB": "→|",
}
```

---

## Next Steps

- ➡️ See [EXTENSIONS.md](EXTENSIONS.md) for other hardware features
- ➡️ See [USAGE.md](USAGE.md) for configurator usage
- ➡️ See [INSTALLATION.md](INSTALLATION.md) for setup help

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 See [README.md](../README.md) for overview
