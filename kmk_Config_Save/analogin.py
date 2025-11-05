from analogio import AnalogIn as AnalogInPin
import time

# LED brightness control via 10k sliding potentiometer on GP28
class BrightnessSlider:
    def __init__(self, keyboard, pin, poll_interval=0.05):
        self.keyboard = keyboard
        self.analog_pin = AnalogInPin(pin)
        self.poll_interval = poll_interval
        self.last_poll = time.monotonic()
        self.threshold = 2000  # Minimum change to trigger brightness adjustment (out of 65535)
        
    def read_value(self):
        """Read analog value (0-65535)"""
        return self.analog_pin.value
    
    def during_bootup(self, keyboard):
        """Initialize at boot"""
        return
    
    def before_matrix_scan(self, keyboard):
        """Check slider position before each matrix scan"""
        return
    
    def after_matrix_scan(self, keyboard):
        """Check slider position after each matrix scan"""
        current_time = time.monotonic()
        
        # Only poll at specified interval to avoid excessive checking
        if current_time - self.last_poll < self.poll_interval:
            return
        
        self.last_poll = current_time
        current_value = self.read_value()
        
        # Convert 16-bit ADC value (0-65535) to brightness (0.0-1.0)
        # Using 0.3 as max to reduce current consumption
        target_brightness = (current_value / 65535.0) * 0.3
        
        # Check if keyboard has RGB extension
        if hasattr(keyboard, 'extensions'):
            for ext in keyboard.extensions:
                if hasattr(ext, 'set_brightness'):
                    ext.set_brightness(target_brightness)
                elif hasattr(ext, 'brightness'):
                    ext.brightness = target_brightness
                    if hasattr(ext, 'neopixel') and ext.neopixel:
                        ext.neopixel.brightness = target_brightness
        
        return
    
    def before_hid_send(self, keyboard):
        """Called before HID report is sent"""
        return
    
    def after_hid_send(self, keyboard):
        """Called after HID report is sent"""
        return
    
    def on_powersave_enable(self, keyboard):
        """Called when powersave is enabled"""
        return
    
    def on_powersave_disable(self, keyboard):
        """Called when powersave is disabled"""
        return

# Create and register brightness slider extension
brightness_slider = BrightnessSlider(keyboard, board.GP28, poll_interval=0.05)
keyboard.extensions.append(brightness_slider)
