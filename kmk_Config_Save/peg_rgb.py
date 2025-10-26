# Peg RGB Matrix configuration (per-key only, no underglow)
# Keys with KC.NO assigned will be turned OFF
rgb = Rgb_matrix(ledDisplay=Rgb_matrix_data(keys=[Color.WHITE]*20))
keyboard.extensions.append(rgb)

# Extra user snippet:
# Peg RGB Matrix configuration (auto-generated)
rgb = Rgb_matrix(ledDisplay=Rgb_matrix_data(keys=[Color.WHITE]*20, underglow=[Color.OFF]*0))
keyboard.extensions.append(rgb)

# Extra user snippet:
# RGB configuration cleared - will use auto-generated default