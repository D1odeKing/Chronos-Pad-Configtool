# Chronos Pad Layer-Switching RGB System

## Overview
This document explains the architecture, configuration, and runtime behavior of the per-layer RGB lighting system for the Chronos Pad, as implemented in the Configtool and generated firmware. It covers how per-layer color maps are stored, how the physical LED order is handled, and how the firmware updates the LEDs in real time as layers change.

---

## 1. Data Model: Per-Layer RGB Storage

- **Global Palette:**
  - `key_colors`: A dictionary mapping key indices (0–19) to hex color strings (e.g., `"#FFAABB"`). This is the default color for each key if no layer override is set.
- **Per-Layer Overrides:**
  - `layer_key_colors`: A dictionary mapping layer indices (as strings) to their own `{key_index: color}` dicts. If a key has a color in this dict for the current layer, it overrides the global palette.
- **Persistence:**
  - Both are saved in `kmk_Config_Save/rgb_matrix.json` and loaded at startup. The schema is backward compatible with older configs.

---

## 2. Physical LED Mapping

- **KEY_PIXEL_ORDER:**
  - The Chronos Pad's physical NeoPixel order is defined by a list:
    ```python
  KEY_PIXEL_ORDER = [
    0, 1, 2, 3,
    7, 6, 5, 4,
    8, 9, 10, 11,
    15, 14, 13, 12,
    16, 17, 18, 19,
  ]
  ```
    This means key index 0 (top-left in the logical matrix) is NeoPixel 0, and key index 19 (bottom-right) is NeoPixel 19. Rows two and four are mirrored to follow the pad's wiring harness.
  - The per-key color editor mirrors the matrix across both axes so the preview matches this physical layout.
- **led_key_pos:**
  - The generated `code.py` sets `keyboard.led_key_pos` to this mapping, so the firmware knows which pixel to update for each key.

---

## 3. Code Generation Pipeline

- **_generate_rgb_matrix_code():**
  - For each layer, builds a list of RGB values for all 20 keys:
    - If a color is set in `layer_key_colors` for that layer, use it.
    - Else, fall back to `key_colors`.
    - If the key is `KC.NO`, set to `[0,0,0]` (off).
    - If the key is `KC.TRNS` (transparent), inherit the color from the previous layer (if any).
    - Otherwise, use the default color.
  - Also builds a list for underglow LEDs if configured.
  - All per-layer maps are combined into a `layer_rgb_maps` Python list, which is emitted as a literal in `code.py`.
- **led_key_pos and total_pixels:**
  - `keyboard.led_key_pos` is set to the physical mapping for the 20 keys, followed by indices for any underglow LEDs.
  - `keyboard.num_pixels` is set to the total number of NeoPixels (keys + underglow).

---

## 4. Runtime Layer Sync Module

- **LayerRgbSync Class:**
  - This class is emitted into `code.py` and appended to `keyboard.modules`.
  - It receives the `rgb` extension and the `layer_rgb_maps` data.
- **Hooks Implemented:**
  - `during_bootup`, `after_matrix_scan`, `after_hid_send`, and `before_hid_send` (all called by KMK at various points in the scan/send cycle).
  - Each hook calls `_check`, which:
    - Reads the current active layer from `keyboard.active_layers`.
    - If the layer has changed (or on first run), updates the `rgb_ext.ledDisplay` with the RGB map for that layer.
    - Calls `rgb_ext.setBasedOffDisplay()` to copy the color data to the NeoPixel buffer.
    - If `disable_auto_write` is set, calls `neopixel.show()` to push the update to the LEDs.
- **Layer Change Detection:**
  - The module tracks the last applied layer and only updates the LEDs if the layer changes or if it hasn’t applied any map yet.

---

## 5. User Workflow

- **Editing:**
  - In the GUI, you can open the Per-key Colors dialog for any layer and set colors for each key.
  - These are saved as per-layer overrides.
  - When you generate `code.py`, the full per-layer RGB data and the sync module are included.
- **On Device:**
  - When you switch layers (via encoder, key, or macro), the firmware automatically updates the RGB LEDs to match the new layer’s color map, with the correct physical mapping.

---

## 6. Fallbacks and Compatibility

- If a layer has no override for a key, the global color is used.
- If a key is set to `KC.TRNS`, the color from the previous (lower-priority) layer is used.
- If a key is `KC.NO`, the LED is turned off.
- If you have no per-layer colors, the behavior is identical to the old single-palette system.

---

## 7. Extensibility

- The system is designed to support any number of layers and any number of underglow LEDs.
- The physical mapping can be changed by editing `KEY_PIXEL_ORDER` in the generator.

---

## 8. Example: How It All Connects

1. **User sets per-key colors for Layer 0 and Layer 1 in the GUI.**
2. **Configtool saves these in `layer_key_colors` and emits a `layer_rgb_maps` list in `code.py`.**
3. **`LayerRgbSync` watches for layer changes at runtime:**
   - When the layer changes, it updates the `ledDisplay` buffer with the correct RGB values for that layer.
   - The physical mapping ensures the right LED lights up, regardless of wiring order.
4. **Result:**
   - Each layer switch instantly updates the pad’s lighting to the user’s chosen palette.

---

## 9. Troubleshooting

- If colors do not match the expected keys, check that `KEY_PIXEL_ORDER` matches your wiring.
- If per-layer colors do not appear, ensure you have set them in the GUI and regenerated `code.py`.
- If you see errors about missing hooks, update the Configtool to the latest version.

---

## 10. References
- See `main.py` for the generator logic.
- See the generated `code.py` for the runtime module and data.
- See `kmk/extensions/peg_rgb_matrix.py` for the Peg RGB Matrix extension internals.

---

For further questions or to request a diagram, contact the project maintainer.
