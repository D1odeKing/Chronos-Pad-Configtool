import board
from analogio import AnalogIn as AnalogInPin
from kmk.keys import KC
import time

# Volume control via 10k sliding potentiometer on GP28
class VolumeSlider:
    def __init__(self, keyboard, pin, poll_interval=0.05):
        self.keyboard = keyboard
        self.analog_pin = AnalogInPin(pin)
        self.poll_interval = poll_interval
        self.last_value = self.read_value()
        self.last_poll = time.monotonic()
        self.last_movement = time.monotonic()
        self.threshold = 2000  # Minimum change to trigger volume adjustment (out of 65535)
        self.step_size = 1  # Number of volume steps per change
        self.idle_timeout = 2.0  # Seconds of no movement before requiring re-sync
        self.synced = False  # Track if we've established direction after idle

    def read_value(self):
        """Read analog value (0-65535)"""
        return self.analog_pin.value

    def during_bootup(self, keyboard):
        self.last_value = self.read_value()
        self.synced = False
        return

    def before_matrix_scan(self, keyboard):
        return

    def after_matrix_scan(self, keyboard):
        current_time = time.monotonic()

        if current_time - self.last_poll < self.poll_interval:
            return

        self.last_poll = current_time
        current_value = self.read_value()
        delta = current_value - self.last_value

        time_since_movement = current_time - self.last_movement
        if time_since_movement > self.idle_timeout:
            self.synced = False

        if abs(delta) > self.threshold:
            if not self.synced:
                self.last_value = current_value
                self.last_movement = current_time
                self.synced = True
                return

            tap_keycode = KC.VOLU if delta > 0 else KC.VOLD
            for _ in range(self.step_size):
                self.keyboard.tap_key(tap_keycode)

            self.last_value = current_value
            self.last_movement = current_time

        return

    def before_hid_send(self, keyboard):
        return

    def after_hid_send(self, keyboard):
        return

    def on_powersave_enable(self, keyboard):
        return

    def on_powersave_disable(self, keyboard):
        return


volume_slider = VolumeSlider(keyboard, board.GP28, poll_interval=0.05)
keyboard.modules.append(volume_slider)
