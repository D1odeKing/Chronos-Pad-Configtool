# Simple RGB test - copy this to your CircuitPython device as code.py to test RGB hardware
import board
import neopixel
import time

# Initialize RGB on GP9
pixels = neopixel.NeoPixel(board.GP9, 20, brightness=0.5, auto_write=False, pixel_order=(1, 0, 2))

# Set all LEDs to RED
for i in range(20):
    pixels[i] = (255, 0, 0)
pixels.show()
print("All LEDs should be RED")

time.sleep(2)

# Set all LEDs to BLUE  
for i in range(20):
    pixels[i] = (0, 0, 255)
pixels.show()
print("All LEDs should be BLUE")

time.sleep(2)

# Set all LEDs to GREEN
for i in range(20):
    pixels[i] = (0, 255, 0)
pixels.show()
print("All LEDs should be GREEN")

print("RGB hardware test complete!")
while True:
    time.sleep(1)
