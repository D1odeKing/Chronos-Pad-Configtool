# Extensions & Hardware Configuration

This guide covers configuring all hardware extensions: Encoder, Analog Input, Display, and RGB Lighting.

---

## Quick Reference

| Extension | Hardware | Status | Guide |
|-----------|----------|--------|-------|
| **Encoder** | GP10, GP11, GP14 | ✅ Fully working | [Link](#encoder) |
| **Analog Input** | GP28 | ⚠️ Under development | [Link](#analog-input) |
| **Display** | GP20, GP21 (I2C) | ✅ Fully working | [Link](#display) |
| **RGB Matrix** | GP9 | ✅ Fully working | [Link](#rgb-matrix) |

---

## Encoder

### Overview

The rotary encoder lets you control your keyboard by turning and clicking.

- **Pins**: GP10 (A), GP11 (B), GP14 (Button)
- **Features**: Layer cycling, volume control, brightness control, etc.
- **Status**: ✅ Fully implemented

### Enabling Encoder

1. Go to **Extensions** panel
2. Check **"Encoder (GP10, GP11, GP14)"**
3. Click **"Configure"** button

### Configuration

#### Basic Setup

In the **Encoder Configuration** dialog:

1. **Encoder Map**: Define what happens when you turn or press
2. **Default**: Layer cycling (turn to change layers, press to toggle)

#### Code Snippet: Layer Cycling

```python
from kmk.modules.encoder import EncoderHandler
import board
from kmk.keys import KC

# Create encoder handler
encoder_handler = EncoderHandler()

# Define the pins (GP10=A, GP11=B, GP14=Button)
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)

# Define the keymap (CCW, CW, Button)
encoder_handler.map = [
    ((KC.LAYER_PREV, KC.LAYER_NEXT, KC.LAYER_TOGGLE),)
]

# Add to keyboard
keyboard.modules.append(encoder_handler)
```

#### Code Snippet: Volume Control

```python
encoder_handler.map = [
    ((KC.VOLD, KC.VOLU, KC.MUTE),)
]
```

#### Code Snippet: Media Control

```python
encoder_handler.map = [
    ((KC.MPRV, KC.MNXT, KC.MPLY),)
]
```

#### Code Snippet: Layer Cycling with Display Update

```python
class LayerCycler:
    """Advanced layer cycling with OLED display updates"""
    
    def __init__(self, keyboard, num_layers=6):
        self.keyboard = keyboard
        self.num_layers = num_layers
        self.current_layer = 0

    def next_layer(self):
        """Move to next layer and update display"""
        self.current_layer = (self.current_layer + 1) % self.num_layers
        self.keyboard.active_layers[0] = self.current_layer
        try:
            # This function is auto-generated if Display is enabled
            update_display_for_layer(self.current_layer)
        except:
            pass
        return False

    def prev_layer(self):
        """Move to previous layer and update display"""
        self.current_layer = (self.current_layer - 1) % self.num_layers
        self.keyboard.active_layers[0] = self.current_layer
        try:
            update_display_for_layer(self.current_layer)
        except:
            pass
        return False

    def toggle_layer(self):
        """Toggle back to layer 0"""
        self.current_layer = 0
        self.keyboard.active_layers[0] = 0
        try:
            update_display_for_layer(0)
        except:
            pass
        return False

# Initialize
encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)
layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))

# Map encoder to layer control methods
encoder_handler.map = [
    ((layer_cycler.prev_layer, layer_cycler.next_layer, layer_cycler.toggle_layer),)
]

keyboard.modules.append(encoder_handler)
```

### Troubleshooting

**Encoder doesn't respond**
- Check pin mappings (should be GP10, GP11, GP14)
- Verify CircuitPython version is 10.0.3
- Check wiring on your PCB

**Layers won't cycle**
- Verify LayerCycler code is included
- Check number of layers matches configuration
- Test with simpler keymap first

**Wrong direction**
- Swap `LAYER_PREV` and `LAYER_NEXT` in code

---

## Analog Input

### Overview

The analog input lets you use a slider or potentiometer to control your keyboard.

- **Pin**: GP28 (Analog)
- **Hardware**: 10k slider potentiometer (Chronos Pad)
- **Features**: Volume control, brightness, custom ranges
- **Status**: ⚠️ **Under active development** - May not work perfectly yet

### Enabling Analog Input

1. Go to **Extensions** panel
2. Check **"Analog Input (GP28 - Slider)"**
3. Click **"Configure"** button

### Configuration

#### Basic Setup

In the **Analog Input Configuration** dialog:

1. **Slider Range**: Map the slider to specific values
2. **Output Action**: What happens when you move the slider

#### Code Snippet: Volume Control

```python
from kmk.modules.analogin import AnalogInputs, AnalogInput
from analogio import AnalogIn
import board
from kmk.keys import KC

# Create analog input from slider on GP28
slider = AnalogInput(AnalogIn(board.GP28))

# Map the slider to volume control
# Range: 0-65535 → KC.VOLD (quiet) to KC.VOLU (loud)
analog = AnalogInputs(
    [slider],
    [[AnalogKey(KC.VOLU, min=32768, max=65535)]]  # Upper half = volume up
)

keyboard.modules.append(analog)
```

#### Code Snippet: Custom Range Mapping

```python
# Map slider to brightness control
slider = AnalogInput(AnalogIn(board.GP28))

# Value ranges:
# 0-21845       = Brightness down
# 21845-43690   = Nothing
# 43690-65535   = Brightness up

analog = AnalogInputs(
    [slider],
    [[
        AnalogKey(KC.BRID, min=0, max=21845),      # Lower third: brightness down
        AnalogKey(KC.BRIU, min=43690, max=65535),  # Upper third: brightness up
    ]]
)

keyboard.modules.append(analog)
```

### Known Issues

⚠️ **Analog input is under development:**

- Slider sensitivity may need tuning
- Rapid updates can cause lag
- Some key mappings not fully tested
- Check GitHub issues for latest status

### Workaround

For now, if analog input isn't reliable:

1. Disable Analog Input extension
2. Use encoder rotation for volume/brightness instead
3. Consider using it as a macro trigger in future updates

---

## Display

### Overview

The OLED display shows your current keymap layer in real-time.

- **Hardware**: I2C OLED (128x64, SH1106 driver)
- **Pins**: GP20 (SDA), GP21 (SCL)
- **Features**: Layer-aware, real-time updates, proper orientation
- **Status**: ✅ Fully working

### Enabling Display

1. Go to **Extensions** panel
2. Check **"Display (I2C: GP20/GP21)"**
3. Click **"Configure"** button to preview

### Configuration

#### Auto-Generated Features

When Display is enabled, the configurator automatically:

1. ✅ Sets rotation to 180° (matches physical layout)
2. ✅ Generates keymap visualization code
3. ✅ Creates `LayerDisplaySync` module (auto-updates on layer change)
4. ✅ Shows layer indicator at top
5. ✅ Displays abbreviated key names

#### Key Abbreviations

The display shows shortened names to fit the 128x64 screen:

```
Standard keys: A, B, 1, 2, etc.
Modifiers: LCtl, LSft, LAlt, LGui, RCtl, RSft, RAlt, RGui
Special: BkSp, Entr, Spce, Tab, Esc, Del
Navigation: Up, Down, Left, Rght, Home, End, PgUp, PgDn
Media: Vol+, Vol-, Mute, Play, Next, Prev, Stop
Macros: M: macro_name (up to 6 chars)
Layers: MO(1), TO(2), TG(3)
Empty: (blank)
```

#### Code Snippet: Display with Layer Sync

The configurator auto-generates this code:

```python
import board
import busio
import displayio
import terminalio
import adafruit_displayio_sh1106
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

# I2C Display setup
displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=128,
    height=64,
    rotation=180,  # 180 degree rotation
    colstart=2     # Column alignment
)

splash = displayio.Group()
display.root_group = splash

# Layer labels for all layers
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
    ]
]

def update_display_for_layer(layer_index):
    """Update display to show keymap for specified layer"""
    global splash
    
    # Clear previous display
    while len(splash) > 0:
        splash.pop()
    
    # Show layer indicator
    layer_label = label.Label(
        terminalio.FONT,
        text=f"Layer {layer_index}",
        color=0xFFFFFF,
        x=2,
        y=4
    )
    splash.append(layer_label)
    
    # Display key layout
    key_labels = all_layer_labels[layer_index] if layer_index < len(all_layer_labels) else all_layer_labels[0]
    
    for row_idx, row in enumerate(key_labels):
        for col_idx, key_text in enumerate(row):
            x_pos = (4 - col_idx) * 32 + 1  # Right-aligned for 4 columns
            y_pos = row_idx * 12 + 14
            
            text_area = label.Label(
                terminalio.FONT,
                text=key_text,
                color=0xFFFFFF,
                x=x_pos,
                y=y_pos
            )
            splash.append(text_area)

# Layer sync module
class LayerDisplaySync:
    """Keep OLED display in sync with keyboard layer changes"""
    
    def __init__(self):
        self._last_layer = None
    
    def _active_layer(self, keyboard):
        """Get the highest priority active layer"""
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
    
    def after_matrix_scan(self, keyboard):
        """Called after keys are scanned"""
        self._check_and_update(keyboard)
    
    def after_hid_send(self, keyboard):
        """Called after HID report is sent"""
        self._check_and_update(keyboard)

# Initialize
layer_display_sync = LayerDisplaySync()
keyboard.modules.append(layer_display_sync)

# Show initial layer
update_display_for_layer(0)
```

### Troubleshooting

**Display is blank**
- Check I2C wiring (GP20=SDA, GP21=SCL)
- Verify CircuitPython version is 10.0.3
- Check if OLED display is powered
- Try: Press a key - if display updates briefly, wiring is OK

**Display shows scrambled text**
- Rotation might be wrong (try rotation=0 or 90)
- I2C address might be 0x3D instead of 0x3C (check display docs)
- Try reducing brightness

**Layer indicator shows wrong number**
- Check LayerDisplaySync is enabled
- Verify layer switching code (KMK.TO, KMK.MO, etc.)
- Test with encoder rotation

**Display doesn't update on layer change**
- Enable LayerDisplaySync in the configurator
- Re-deploy code.py
- Check that Layers module is included

---

## RGB Matrix

### Overview

RGB lighting adds per-key and underglow LED support to your keyboard.

- **Hardware**: SK6812MINI LEDs on GP9
- **Count**: 20 LEDs (5×4 grid for keys + optional underglow)
- **Pixel Order**: GRB (Green, Red, Blue)
- **Status**: ✅ Fully working

### Enabling RGB

1. Go to **Extensions** panel
2. Check **"RGB Matrix (GP9)"**
3. Click **"Configure"** or **"Per-key Colors"** button

### Configuration Options

#### RGB Configuration Dialog

Set defaults:
- **Brightness**: 0.0 - 1.0 (default: 0.5)
- **Default Key Color**: Hex code (e.g., #FFFFFF for white)
- **Default Underglow Color**: Hex code (e.g., #000000 for off)
- **Number of Underglow LEDs**: 0-20 (default: 0)

#### Per-Key Colors

1. Click **"Per-key Colors"** button
2. Click on any key in the grid
3. Choose a color with the color picker
4. Color is saved per-key

#### Code Snippet: Default RGB Setup

```python
from kmk.extensions.peg_rgb_matrix import Rgb_matrix, Rgb_matrix_data

# Basic RGB setup (all white)
rgb = Rgb_matrix(
    ledDisplay=[
        [255, 255, 255],  # Key 0: White
        [255, 255, 255],  # Key 1: White
        # ... 20 keys total
    ],
    rgb_order=(1, 0, 2),  # GRB format
    disable_auto_write=True,
)

keyboard.extensions.append(rgb)
```

#### Code Snippet: Custom Per-Key Colors

```python
# Different colors per key
rgb = Rgb_matrix(
    ledDisplay=[
        [255, 0, 0],      # Key 0: Red
        [0, 255, 0],      # Key 1: Green
        [0, 0, 255],      # Key 2: Blue
        [255, 255, 0],    # Key 3: Yellow
        # ... etc
    ],
    rgb_order=(1, 0, 2),  # GRB
)

keyboard.extensions.append(rgb)
```

#### Code Snippet: With Underglow

```python
# Keys + underglow (8 LEDs)
rgb = Rgb_matrix(
    ledDisplay=Rgb_matrix_data(
        keys=[
            [255, 255, 255],  # Key 0-19 (all white)
            # ... 20 keys
        ],
        underglow=[
            [255, 0, 0],      # Underglow 0: Red
            [0, 255, 0],      # Underglow 1: Green
            # ... 8 underglow LEDs
        ]
    ),
    rgb_order=(1, 0, 2),  # GRB
)

keyboard.extensions.append(rgb)
```

### RGB Settings

**RGB Order**
- `GRB` (default): Green, Red, Blue
- `RGB`: Red, Green, Blue
- `GBRW`: Includes white channel
- Check LED datasheet for correct order

**Disable Auto Write**
- `True`: Update LEDs only when changed
- `False`: Update every frame (more power usage)

**Brightness Limit**
- 0.0 - 1.0 range
- Default 0.5 (50% brightness)
- Lower values reduce power consumption

### Color Reference

Common colors (RGB format):

```python
White       = [255, 255, 255]
Red         = [255, 0, 0]
Green       = [0, 255, 0]
Blue        = [0, 0, 255]
Yellow      = [255, 255, 0]
Magenta     = [255, 0, 255]
Cyan        = [0, 255, 255]
Black/Off   = [0, 0, 0]
Orange      = [255, 165, 0]
Purple      = [128, 0, 128]
```

**Converting Hex to RGB:**
- `#FFFFFF` → `[255, 255, 255]`
- `#FF0000` → `[255, 0, 0]`
- `#00FF00` → `[0, 255, 0]`

### Troubleshooting

**LEDs don't light up**
- Check GP9 wiring
- Verify LED polarity (DIN is data input)
- Test with simple code: RGB all white
- Check power supply

**Wrong colors**
- Check RGB order setting (should be GRB for SK6812MINI)
- Try adjusting RGB order: RGB, GRB, GBRW
- Ensure brightness > 0.0

**Some LEDs don't work**
- One LED failure can break the chain
- Check for loose connections
- Try replacing the bad LED

**Too much power draw**
- Reduce brightness setting (use 0.3-0.5)
- Reduce number of LEDs
- Use underglow sparingly

---

## Extension Priority

If multiple extensions are enabled, they work together:

1. **Encoder** → Controls layer switching
2. **Display** → Shows current layer keymap
3. **RGB** → Per-key lighting for visual feedback
4. **Analog Input** → Alternative layer/macro control

---

## Disabling Extensions

To save code space or reduce power:

1. Uncheck extension in Extensions panel
2. That code won't be included in `code.py`
3. Re-deploy: Click "Save code.py"

---

## Next Steps

- ➡️ See [USAGE.md](USAGE.md) for complete usage guide
- ➡️ See [DISPLAY.md](DISPLAY.md) for detailed display info
- ➡️ See [INSTALLATION.md](INSTALLATION.md) for setup help

---

## Questions?

- 💬 Check [GitHub Issues](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- 📖 See [README.md](../README.md) for overview
