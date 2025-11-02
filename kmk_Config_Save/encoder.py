# --- Rotary Encoder Configuration ---
from kmk.modules.encoder import EncoderHandler

# Encoder configuration with layer cycling using KC.TO()
encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14, False),)

# Build encoder map for each layer
# Each layer's encoder: (CCW action, CW action, Button press action)
encoder_map = []
for i in range(8):
    next_layer = (i + 1) % 8
    prev_layer = (i - 1) % 8
    # CCW=prev layer, CW=next layer, Press=layer 0
    encoder_map.append(((KC.TO(prev_layer), KC.TO(next_layer), KC.TO(0)),))

encoder_handler.map = encoder_map
keyboard.modules.append(encoder_handler)

# Initialize layer cycler after keymap is defined
# NOTE: Add this line AFTER keyboard.keymap = [...] in your code.py:
# layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))