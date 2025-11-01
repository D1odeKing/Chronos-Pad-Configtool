# Encoder Auto-Setup with Layer Cycling and Display Updates

## Overview
The encoder configuration has been redesigned to provide automatic layer cycling with integrated display updates. This replaces the old manual configuration system with a streamlined interface.

## Features

### 1. **Fixed Hardware Configuration**
- Pin A: GP10
- Pin B: GP11
- Button: GP14
- These pins are fixed for the Chronos Pad and cannot be changed

### 2. **Rotation Behavior Options**
- **Cycle Layers (Recommended)**: Automatically cycles through keyboard layers
  - Counter-clockwise: Previous layer
  - Clockwise: Next layer
  - Wraps around (e.g., from layer 2 back to layer 0)
- **Volume Control**: Vol Down / Vol Up
- **Brightness**: Down / Up
- **Media**: Previous Track / Next Track
- **Custom Actions**: Define your own keycodes

### 3. **Center Button Actions**
- **Reset to Layer 0 (Recommended)**: Instantly returns to base layer
- **Toggle Layer 1**: Switches between layer 0 and layer 1
- **Mute**: Audio mute toggle
- **Play/Pause**: Media playback control
- **Custom Action**: Any custom keycode

### 4. **Display Integration**
- **Auto-update on layer change**: Checkbox to enable/disable
- **Show current layer number**: Displays "Layer X" at top of OLED
- **Full keymap display**: Shows all 20 keys with abbreviated labels for current layer
- Updates happen automatically when encoder rotates

### 5. **Direction Control**
- **Invert rotation direction**: Checkbox to swap CW/CCW actions
- Useful if encoder feels backwards for your preference

## Generated Code Structure

When you configure the encoder with layer cycling enabled, the tool generates:

### 1. LayerCycler Class
```python
class LayerCycler:
    def __init__(self, keyboard, num_layers):
        # Manages layer state and display updates
        
    def next_layer(self):
        # Increment layer, wrap around, update display
        
    def prev_layer(self):
        # Decrement layer, wrap around, update display
        
    def reset_layer(self):
        # Return to layer 0, update display
        
    def update_display(self):
        # Calls global update_display_for_layer() function
```

### 2. Custom Keycodes
```python
KC.LAYER_NEXT = KC.make_key(on_press=lambda k, *args: layer_cycler.next_layer() if layer_cycler else None)
KC.LAYER_PREV = KC.make_key(on_press=lambda k, *args: layer_cycler.prev_layer() if layer_cycler else None)
KC.LAYER_RESET = KC.make_key(on_press=lambda k, *args: layer_cycler.reset_layer() if layer_cycler else None)
```

### 3. Encoder Handler
```python
encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14, False),)
encoder_handler.map = [((KC.LAYER_PREV, KC.LAYER_NEXT, KC.LAYER_RESET),)]
keyboard.modules.append(encoder_handler)
```

### 4. Display Update Function (if display enabled)
```python
all_layer_labels = [
    # Layer 0
    [["Key1", "Key2", ...], ...],
    # Layer 1
    [["Key1", "Key2", ...], ...],
    ...
]

def update_display_for_layer(layer_index):
    # Clears display
    # Shows "Layer X" header
    # Renders 5x4 grid of key labels for current layer
```

### 5. Layer Cycler Initialization
```python
# After keyboard.keymap is defined:
layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))
```

## How It Works Together

1. **User rotates encoder**
   - KMK encoder module detects rotation
   - Calls appropriate action (KC.LAYER_NEXT or KC.LAYER_PREV)

2. **Custom keycode triggered**
   - Calls layer_cycler.next_layer() or prev_layer()
   - Updates keyboard.active_layers[0] to new layer index

3. **Display update (if enabled)**
   - LayerCycler.update_display() called
   - Calls global update_display_for_layer() function
   - OLED refreshes to show new layer's keymap

4. **RGB update (automatic)**
   - RgbLayerColors extension monitors keyboard.active_layers
   - Detects layer change in after_hid_send()
   - Updates LED colors to match new layer
   - Also monitors numlock state for keypad color alternates

5. **Button press**
   - If configured as "Reset to Layer 0"
   - Calls layer_cycler.reset_layer()
   - Returns to base layer with full display update

## Usage in Config Tool

1. Open the encoder configuration dialog (Extensions → Configure Encoder)
2. Select rotation behavior (recommend "Cycle Layers")
3. Optionally invert direction if it feels backwards
4. Select center button action (recommend "Reset to Layer 0")
5. Enable display updates (checkbox)
6. Enable layer number display (checkbox)
7. Click OK
8. Generate code (File → Generate Code)
9. Flash to CircuitPython device

## Display Layout

The OLED shows:
```
Layer X         <- Layer indicator at top (y=4)
Key1 Key2 ... <- Row 0 starting at y=14
Key5 Key6 ... <- Row 1 at y=24
... (5 rows, 4 columns, 10px row spacing, 32px column spacing)
```

Each key label is abbreviated to max 6 characters for readability.

## Integration with Other Features

### Per-Layer RGB
- RGB colors automatically update when encoder changes layers
- Uses RgbLayerColors extension
- No additional code needed - works automatically

### Numlock Support
- Keypad key colors change based on numlock state
- Works on all layers
- Independent of layer switching

### Macros
- Macros can be assigned to any key on any layer
- Display shows macro name (abbreviated)
- Works seamlessly with layer cycling

## Troubleshooting

### Encoder direction feels backwards
- Re-open encoder config
- Check "Invert rotation direction"
- Regenerate code

### Display doesn't update
- Ensure "Update display on layer change" is checked
- Verify I2C connections (GP20=SDA, GP21=SCL)
- Check that display is working (should show Layer 0 on boot)

### Layer doesn't change
- Verify encoder pins are correct (GP10, GP11, GP14)
- Check encoder is working (test with volume control action first)
- Ensure encoder module is in generated code

### Can't get back to Layer 0
- Use center button press action "Reset to Layer 0"
- Or cycle through all layers to wrap back around

## Next Steps

After setting up the encoder:
1. Test layer cycling by rotating encoder
2. Verify display updates correctly
3. Check RGB colors change with layers
4. Test button press functionality
5. Customize layer keymaps as needed

The encoder, display, and RGB now work together as an integrated system for a seamless layer switching experience!
