"""
KMK Macropad Configurator - Raspberry Pi Pico Edition

Hardware Configuration (FIXED):
- Board: Raspberry Pi Pico 2
- Matrix: 5 rows x 4 columns (20 keys)
- Rows: GP8, GP7, GP6, GP5, GP4
- Columns: GP0, GP1, GP2, GP3
- Diode Orientation: COL2ROW
- Encoder: A=GP10, B=GP11, Button=GP14
- Slider Pot: GP28 (analog input)
- RGB LEDs: GP9 (SK6812MINI - GRB pixel order)
- Display: I2C (SDA=GP20, SCL=GP21)

This configurator allows you to customize key assignments, macros, layers,
and extensions (encoder, RGB, analog input, display) without changing the
underlying hardware pin configuration.
"""

import sys
import re
import ast
import json
import os
import time
import traceback
import urllib.request
import zipfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QGridLayout, QSpinBox, QListWidget,
    QTabWidget, QSizePolicy, QLineEdit, QFileDialog, QMessageBox,
    QComboBox, QDialog, QDialogButtonBox, QCheckBox, QInputDialog, QColorDialog,
    QFormLayout, QDoubleSpinBox, QProgressDialog
)
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from functools import partial

# --- Default Values ---
DEFAULT_KEY = "KC.NO"
CONFIG_SAVE_DIR = os.path.join(os.getcwd(), "kmk_Config_Save")
MACRO_FILE = os.path.join(CONFIG_SAVE_DIR, "macros.json")
PROFILE_FILE = "profiles.json"

# --- Dependency URLs ---
KMK_FIRMWARE_URL = "https://github.com/KMKfw/kmk_firmware/archive/refs/heads/main.zip"
CIRCUITPYTHON_BUNDLE_URL = "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest/download/adafruit-circuitpython-bundle-9.x-mpy-{date}.zip"

class DependencyDownloader(QThread):
    """Downloads KMK firmware and CircuitPython libraries automatically"""
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(bool)  # success
    
    def __init__(self):
        super().__init__()
        self.libraries_dir = os.path.join(os.getcwd(), "libraries")
        
    def run(self):
        """Download all required dependencies"""
        try:
            os.makedirs(self.libraries_dir, exist_ok=True)
            
            # Check if already downloaded
            kmk_path = os.path.join(self.libraries_dir, "kmk_firmware-main")
            bundle_path = os.path.join(self.libraries_dir, "adafruit-circuitpython-bundle-9.x-mpy")
            
            if os.path.exists(kmk_path) and os.path.exists(bundle_path):
                self.progress.emit("Dependencies already installed", 100)
                self.finished.emit(True)
                return
            
            # Download KMK Firmware
            if not os.path.exists(kmk_path):
                self.progress.emit("Downloading KMK Firmware...", 10)
                self.download_and_extract_kmk()
            
            # Download CircuitPython Bundle
            if not os.path.exists(bundle_path):
                self.progress.emit("Downloading CircuitPython Bundle...", 50)
                self.download_and_extract_bundle()
            
            self.progress.emit("Dependencies installed successfully!", 100)
            self.finished.emit(True)
            
        except Exception as e:
            self.progress.emit(f"Error downloading dependencies: {str(e)}", 0)
            self.finished.emit(False)
    
    def download_and_extract_kmk(self):
        """Download and extract KMK firmware"""
        zip_path = os.path.join(self.libraries_dir, "kmk_firmware.zip")
        
        # Download
        urllib.request.urlretrieve(KMK_FIRMWARE_URL, zip_path)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.libraries_dir)
        
        # Clean up
        os.remove(zip_path)
    
    def download_and_extract_bundle(self):
        """Download and extract CircuitPython bundle"""
        # Get latest bundle URL (try a few recent dates)
        import datetime
        today = datetime.date.today()
        
        for days_back in range(7):  # Try last 7 days
            date = (today - datetime.timedelta(days=days_back)).strftime("%Y%m%d")
            url = CIRCUITPYTHON_BUNDLE_URL.format(date=date)
            
            try:
                zip_path = os.path.join(self.libraries_dir, "circuitpython_bundle.zip")
                urllib.request.urlretrieve(url, zip_path)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.libraries_dir)
                
                # Rename to consistent name
                extracted_dirs = [d for d in os.listdir(self.libraries_dir) 
                                if d.startswith("adafruit-circuitpython-bundle-9.x-mpy-")]
                if extracted_dirs:
                    old_path = os.path.join(self.libraries_dir, extracted_dirs[0])
                    new_path = os.path.join(self.libraries_dir, "adafruit-circuitpython-bundle-9.x-mpy")
                    if os.path.exists(new_path):
                        shutil.rmtree(new_path)
                    os.rename(old_path, new_path)
                
                # Clean up
                os.remove(zip_path)
                break
                
            except Exception:
                continue
        else:
            raise Exception("Could not download CircuitPython bundle from recent dates")
# --- Hardware Configuration (Fixed) ---
# Raspberry Pi Pico 5x4 Custom Configuration
FIXED_ROWS = 5
FIXED_COLS = 4
FIXED_ROW_PINS = ["board.GP8", "board.GP7", "board.GP6", "board.GP5", "board.GP4"]
FIXED_COL_PINS = ["board.GP0", "board.GP1", "board.GP2", "board.GP3"]
FIXED_DIODE_ORIENTATION = "COL2ROW"
FIXED_ENCODER_PINS = {"a": "board.GP10", "b": "board.GP11", "button": "board.GP14"}
FIXED_ANALOG_PIN = "board.GP28"  # 10k slider pot
FIXED_RGB_PIN = "board.GP9"
FIXED_DISPLAY_PINS = {"scl": "board.GP21", "sda": "board.GP20"}


def build_default_rgb_matrix_config():
    """Create a fresh RGB matrix configuration with sane defaults."""
    return {
        "pixel_pin": FIXED_RGB_PIN,
        "brightness_limit": 0.5,
        "rgb_order": "GRB",
        "disable_auto_write": True,
        "num_underglow": 0,
        "default_key_color": "#FFFFFF",
        "default_underglow_color": "#000000",
        "key_colors": {},
        "underglow_colors": {},
    }


RGB_ORDER_TUPLES = {
    "RGB": (0, 1, 2),
    "RBG": (0, 2, 1),
    "GRB": (1, 0, 2),
    "GBR": (1, 2, 0),
    "BRG": (2, 0, 1),
    "BGR": (2, 1, 0),
}


def hex_to_rgb_list(color: str) -> list[int]:
    """Convert a hex color string (e.g. #FFAABB) into an [r, g, b] list."""
    if not isinstance(color, str):
        color = "#000000"
    clean = color.strip().lstrip('#')
    if len(clean) != 6:
        clean = "000000"
    try:
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
        return [r, g, b]
    except ValueError:
        return [0, 0, 0]


def ensure_hex_prefix(color: str, fallback: str) -> str:
    """Return a canonical '#RRGGBB' string, falling back when invalid."""
    if not isinstance(color, str):
        return fallback
    value = color.strip()
    if not value:
        return fallback
    if not value.startswith('#'):
        value = f"#{value}"
    clean = value.lstrip('#')
    if len(clean) != 6:
        return fallback
    try:
        int(clean, 16)
    except ValueError:
        return fallback
    return f"#{clean.upper()}"

# --- Default Extension Configuration Templates ---
DEFAULT_ENCODER_CONFIG = '''from kmk.modules.encoder import EncoderHandler

# Custom layer cycling for encoder
class LayerCycler:
    def __init__(self, keyboard, num_layers=6):
        self.keyboard = keyboard
        self.num_layers = num_layers
        self.current_layer = 0
    
    def next_layer(self):
        self.current_layer = (self.current_layer + 1) % self.num_layers
        self.keyboard.active_layers[0] = self.current_layer
        try:
            update_display_for_layer(self.current_layer)
        except:
            pass
        return False
    
    def prev_layer(self):
        self.current_layer = (self.current_layer - 1) % self.num_layers
        self.keyboard.active_layers[0] = self.current_layer
        try:
            update_display_for_layer(self.current_layer)
        except:
            pass
        return False
    
    def reset_layer(self):
        self.current_layer = 0
        self.keyboard.active_layers[0] = 0
        try:
            update_display_for_layer(0)
        except:
            pass
        return False

# Create layer cycler (will be bound after keyboard setup)
layer_cycler = None

# Custom key codes for layer cycling
KC.LAYER_NEXT = KC.make_key(on_press=lambda k, *args: layer_cycler.next_layer() if layer_cycler else None)
KC.LAYER_PREV = KC.make_key(on_press=lambda k, *args: layer_cycler.prev_layer() if layer_cycler else None)
KC.LAYER_RESET = KC.make_key(on_press=lambda k, *args: layer_cycler.reset_layer() if layer_cycler else None)

encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)  # (a, b, button)
encoder_handler.map = [((KC.LAYER_PREV, KC.LAYER_NEXT, KC.LAYER_RESET),)]  # CCW=prev, CW=next, Press=reset to layer 0
keyboard.modules.append(encoder_handler)

# Initialize layer cycler after keyboard is set up (do this after keymap is defined)
# Add this line after keyboard.keymap = [...] in your main code:
# layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))'''

DEFAULT_ANALOGIN_CONFIG = '''from analogio import AnalogIn as AnalogInPin
import time

# Volume control via 10k sliding potentiometer
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
        """Initialize at boot"""
        self.last_value = self.read_value()
        self.synced = False  # Require initial movement to establish baseline
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
        delta = current_value - self.last_value
        
        # Check if we've been idle too long (user may have adjusted volume elsewhere)
        time_since_movement = current_time - self.last_movement
        if time_since_movement > self.idle_timeout:
            self.synced = False  # Need to re-sync on next movement
        
        # If slider moved significantly
        if abs(delta) > self.threshold:
            # If we're not synced (first movement after idle), just update position without sending
            if not self.synced:
                self.last_value = current_value
                self.last_movement = current_time
                self.synced = True
                return
            
            # Normal operation: send volume commands based on direction
            if delta > 0:
                # Slider moved up (higher value) - increase volume
                for _ in range(self.step_size):
                    keyboard.hid_pending = True
                    keyboard._send_hid()
                    keyboard.add_key(KC.VOLU)
                    keyboard._send_hid()
                    keyboard.remove_key(KC.VOLU)
                    keyboard._send_hid()
            else:
                # Slider moved down (lower value) - decrease volume
                for _ in range(self.step_size):
                    keyboard.hid_pending = True
                    keyboard._send_hid()
                    keyboard.add_key(KC.VOLD)
                    keyboard._send_hid()
                    keyboard.remove_key(KC.VOLD)
                    keyboard._send_hid()
            
            self.last_value = current_value
            self.last_movement = current_time
        
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

# Create and register volume slider extension
volume_slider = VolumeSlider(keyboard, board.GP28, poll_interval=0.05)
keyboard.modules.append(volume_slider)'''

DEFAULT_RGB_CONFIG = '''import neopixel
from kmk.extensions.peg_rgb_matrix import Rgb_matrix, Rgb_matrix_data

# SK6812MINI RGB LEDs connected to GP9 (GRB pixel order)
rgb_ext = Rgb_matrix(
    ledData=neopixel.NeoPixel(board.GP9, 20, brightness=0.2, pixel_order=neopixel.GRB)  # 20 LEDs for 5x4 matrix
)
keyboard.extensions.append(rgb_ext)'''

DEFAULT_DISPLAY_CONFIG = '''import board
import busio
import displayio
import terminalio
import adafruit_displayio_sh1106
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

# I2C Display setup (SDA=GP20, SCL=GP21)
displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=128,
    height=64,
    rotation=0,
    colstart=2  # Column offset for proper alignment
)

# Create display group
splash = displayio.Group()
display.root_group = splash

# Add your display content here
# Example:
# text_area = label.Label(terminalio.FONT, text="Hello!", color=0xFFFFFF, x=0, y=10)
# splash.append(text_area)'''


# --- KMK Keycode Data ---
# Expanded to include more common keys like function keys and miscellaneous controls.
KEYCODES = {
    "Basic": [
        "KC.A", "KC.B", "KC.C", "KC.D", "KC.E", "KC.F", "KC.G", "KC.H", "KC.I",
        "KC.J", "KC.K", "KC.L", "KC.M", "KC.N", "KC.O", "KC.P", "KC.Q", "KC.R",
        "KC.S", "KC.T", "KC.U", "KC.V", "KC.W", "KC.X", "KC.Y", "KC.Z",
        "KC.N1", "KC.N2", "KC.N3", "KC.N4", "KC.N5", "KC.N6", "KC.N7", "KC.N8",
        "KC.N9", "KC.N0", "KC.ENT", "KC.ESC", "KC.BSPC", "KC.TAB", "KC.SPC",
        "KC.MINS", "KC.EQL", "KC.LBRC", "KC.RBRC", "KC.BSLS", "KC.SCLN",
        "KC.QUOT", "KC.GRV", "KC.COMM", "KC.DOT", "KC.SLSH"
    ],
    "Modifiers": [
        "KC.LCTL", "KC.LSFT", "KC.LALT", "KC.LGUI",
        "KC.RCTL", "KC.RSFT", "KC.RALT", "KC.RGUI"
    ],
    "Navigation": [
        "KC.UP", "KC.DOWN", "KC.LEFT", "KC.RGHT",
        "KC.HOME", "KC.END", "KC.PGUP", "KC.PGDN", "KC.DEL", "KC.INS"
    ],
    "Function": [
        "KC.F1", "KC.F2", "KC.F3", "KC.F4", "KC.F5", "KC.F6",
        "KC.F7", "KC.F8", "KC.F9", "KC.F10", "KC.F11", "KC.F12",
        "KC.F13", "KC.F14", "KC.F15", "KC.F16", "KC.F17", "KC.F18",
        "KC.F19", "KC.F20", "KC.F21", "KC.F22", "KC.F23", "KC.F24",
    ],
    "Media": [
        "KC.MUTE", "KC.VOLU", "KC.VOLD",
        "KC.BRIU", "KC.BRID",
        "KC.MNXT", "KC.MPRV", "KC.MSTP",
        "KC.MPLY", "KC.EJCT",
        "KC.MFFD", "KC.MRWD"
    ],
    "Numpad": [
        "KC.KP_0", "KC.KP_1", "KC.KP_2", "KC.KP_3", "KC.KP_4",
        "KC.KP_5", "KC.KP_6", "KC.KP_7", "KC.KP_8", "KC.KP_9",
        "KC.KP_SLASH", "KC.KP_ASTERISK", "KC.KP_MINUS", "KC.KP_PLUS",
        "KC.KP_ENTER", "KC.KP_DOT", "KC.KP_EQUAL", "KC.KP_COMMA",
        "KC.NUMLOCK"
    ],
    "Mouse": [
        "KC.MS_UP", "KC.MS_DOWN", "KC.MS_LEFT", "KC.MS_RIGHT",
        "KC.MW_UP", "KC.MW_DOWN", "KC.MB_L", "KC.MB_R", "KC.MB_M"
    ],
    "Layers": [
        "KC.MO(1)", "KC.MO(2)", "KC.MO(3)", "KC.MO(4)", "KC.MO(5)",
        "KC.TG(1)", "KC.TG(2)", "KC.TG(3)", "KC.TG(4)", "KC.TG(5)",
        "KC.DF(0)", "KC.DF(1)", "KC.DF(2)", "KC.DF(3)", "KC.DF(4)", "KC.DF(5)"
    ],
    "Misc": [
        "KC.NO", "KC.TRNS", "KC.RESET", "KC.CLCK", "KC.PSCR", "KC.SLCK",
        "KC.PAUS", "KC.NLCK", "KC.APP"
    ]
}


# A mapping from PyQt6 Qt.Key values to KMK keycode strings.
QT_TO_KMK = {
    Qt.Key.Key_Escape: "KC.ESC", Qt.Key.Key_Tab: "KC.TAB",
    Qt.Key.Key_Backspace: "KC.BSPC", Qt.Key.Key_Return: "KC.ENT",
    Qt.Key.Key_Enter: "KC.ENT", Qt.Key.Key_Insert: "KC.INS",
    Qt.Key.Key_Delete: "KC.DEL", Qt.Key.Key_Pause: "KC.PAUS",
    Qt.Key.Key_Print: "KC.PSCR", Qt.Key.Key_SysReq: "KC.SYSQ",
    Qt.Key.Key_Clear: "KC.CLR", Qt.Key.Key_Home: "KC.HOME",
    Qt.Key.Key_End: "KC.END", Qt.Key.Key_Left: "KC.LEFT",
    Qt.Key.Key_Up: "KC.UP", Qt.Key.Key_Right: "KC.RGHT",
    Qt.Key.Key_Down: "KC.DOWN", Qt.Key.Key_PageUp: "KC.PGUP",
    Qt.Key.Key_PageDown: "KC.PGDN", Qt.Key.Key_Shift: "KC.LSFT",
    Qt.Key.Key_Control: "KC.LCTL", Qt.Key.Key_Meta: "KC.LGUI",
    Qt.Key.Key_Alt: "KC.LALT", Qt.Key.Key_CapsLock: "KC.CAPS",
    Qt.Key.Key_NumLock: "KC.NUM", Qt.Key.Key_ScrollLock: "KC.SLCK",
    Qt.Key.Key_F1: "KC.F1", Qt.Key.Key_F2: "KC.F2", Qt.Key.Key_F3: "KC.F3",
    Qt.Key.Key_F4: "KC.F4", Qt.Key.Key_F5: "KC.F5", Qt.Key.Key_F6: "KC.F6",
    Qt.Key.Key_F7: "KC.F7", Qt.Key.Key_F8: "KC.F8", Qt.Key.Key_F9: "KC.F9",
    Qt.Key.Key_F10: "KC.F10", Qt.Key.Key_F11: "KC.F11", Qt.Key.Key_F12: "KC.F12",
    Qt.Key.Key_Space: "KC.SPC", Qt.Key.Key_Apostrophe: "KC.QUOT",
    Qt.Key.Key_Comma: "KC.COMM", Qt.Key.Key_Minus: "KC.MINS",
    Qt.Key.Key_Period: "KC.DOT", Qt.Key.Key_Slash: "KC.SLSH",
    Qt.Key.Key_0: "KC.N0", Qt.Key.Key_1: "KC.N1", Qt.Key.Key_2: "KC.N2",
    Qt.Key.Key_3: "KC.N3", Qt.Key.Key_4: "KC.N4", Qt.Key.Key_5: "KC.N5",
    Qt.Key.Key_6: "KC.N6", Qt.Key.Key_7: "KC.N7", Qt.Key.Key_8: "KC.N8",
    Qt.Key.Key_9: "KC.N9", Qt.Key.Key_Semicolon: "KC.SCLN",
    Qt.Key.Key_Equal: "KC.EQL",
    # Letters
    Qt.Key.Key_A: "KC.A", Qt.Key.Key_B: "KC.B",
    Qt.Key.Key_C: "KC.C", Qt.Key.Key_D: "KC.D", Qt.Key.Key_E: "KC.E",
    Qt.Key.Key_F: "KC.F", Qt.Key.Key_G: "KC.G", Qt.Key.Key_H: "KC.H",
    Qt.Key.Key_I: "KC.I", Qt.Key.Key_J: "KC.J", Qt.Key.Key_K: "KC.K",
    Qt.Key.Key_L: "KC.L", Qt.Key.Key_M: "KC.M", Qt.Key.Key_N: "KC.N",
    Qt.Key.Key_O: "KC.O", Qt.Key.Key_P: "KC.P", Qt.Key.Key_Q: "KC.Q",
    Qt.Key.Key_R: "KC.R", Qt.Key.Key_S: "KC.S", Qt.Key.Key_T: "KC.T",
    Qt.Key.Key_U: "KC.U", Qt.Key.Key_V: "KC.V", Qt.Key.Key_W: "KC.W",
    Qt.Key.Key_X: "KC.X", Qt.Key.Key_Y: "KC.Y", Qt.Key.Key_Z: "KC.Z",
    Qt.Key.Key_BracketLeft: "KC.LBRC", Qt.Key.Key_Backslash: "KC.BSLS",
    Qt.Key.Key_BracketRight: "KC.RBRC", Qt.Key.Key_QuoteLeft: "KC.GRV",
}


# --- New Dialog for Creating Key Combos (e.g., Ctrl+C) ---
class ComboCreatorDialog(QDialog):
    """A dialog to create modifier key combinations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Key Combo")
        
        layout = QVBoxLayout(self)
        
        # Modifier selection
        mods_group = QGroupBox("Modifiers")
        mods_layout = QGridLayout()
        self.mod_checkboxes = {
            "LCTL": QCheckBox("Left Control"),
            "LSFT": QCheckBox("Left Shift"),
            "LALT": QCheckBox("Left Alt"),
            "LGUI": QCheckBox("Left GUI (Win/Cmd)"),
            "RCTL": QCheckBox("Right Control"),
            "RSFT": QCheckBox("Right Shift"),
            "RALT": QCheckBox("Right Alt"),
            "RGUI": QCheckBox("Right GUI (Win/Cmd)"),
        }
        
        # Arrange checkboxes in two columns
        row, col = 0, 0
        for name, checkbox in self.mod_checkboxes.items():
            mods_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        mods_group.setLayout(mods_layout)
        layout.addWidget(mods_group)

        # Key selection
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Base Keycode (e.g., KC.C):"))
        self.key_input = QLineEdit()
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_combo_string(self):
        """Builds the KMK-formatted combo string from the UI selections."""
        base_key = self.key_input.text().strip()
        if not base_key:
            return None

        combo = base_key
        # Wrap the base key in each selected modifier
        for mod_name, checkbox in self.mod_checkboxes.items():
            if checkbox.isChecked():
                combo = f"KC.{mod_name}({combo})"
        
        return combo


# --- Macro Recorder Dialog ---
class MacroRecorderDialog(QDialog):
    """A dialog to record a sequence of key presses and releases."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Recorder")
        self.setMinimumSize(400, 300)

        self.recording = False
        self.sequence = []
        self.pressed_keys = set()
        # Map of physical key -> (press_time, sequence_index) so we can
        # detect short press+release and convert them into a single 'tap'
        # action instead of separate press/release entries.
        self.press_timestamps = {}
        self.last_event_time = 0
        # Threshold (seconds) under which a press+release is considered a tap
        self.TAP_THRESHOLD = 0.20

        layout = QVBoxLayout(self)
        
        self.instructions = QLabel("Click 'Start Recording' and then press keys to record.")
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instructions)

        self.sequence_list = QListWidget()
        layout.addWidget(self.sequence_list)

        # Legend explaining visual indicators
        self.legend = QLabel()
        self.legend.setText(
            "<b>Legend:</b> <span style='color: #00cc66'>Tap</span> = auto-collapsed quick press/release<br>"
            "<small>While recording, use 'Insert Text String' or 'Insert Delay' buttons to add special actions.</small>"
        )
        self.legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.legend)

        button_layout = QHBoxLayout()
        self.record_button = QPushButton("Start Recording")
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        
        # Add button to insert text strings during recording
        self.add_text_btn = QPushButton("Insert Text String")
        self.add_text_btn.clicked.connect(self.insert_text_string)
        self.add_text_btn.setEnabled(False)  # Only enabled during recording
        button_layout.addWidget(self.add_text_btn)
        
        # Add button to insert delay during recording
        self.add_delay_btn = QPushButton("Insert Delay")
        self.add_delay_btn.clicked.connect(self.insert_delay)
        self.add_delay_btn.setEnabled(False)  # Only enabled during recording
        button_layout.addWidget(self.add_delay_btn)

        layout.addLayout(button_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.record_button.setText("Stop Recording")
            self.instructions.setText("Recording... Press keys now. Press 'Stop' when done.")
            self.sequence = []
            self.pressed_keys.clear()
            self.press_timestamps.clear()
            self.sequence_list.clear()
            self.last_event_time = time.monotonic()
            self.add_text_btn.setEnabled(True)
            self.add_delay_btn.setEnabled(True)
            self.setFocus()
            # Install an application-wide event filter so key events are
            # swallowed while recording and do not reach other widgets.
            app = QApplication.instance()
            if app:
                app.installEventFilter(self)
        else:
            self.record_button.setText("Start Recording")
            self.instructions.setText("Click 'Start Recording' to begin.")
            self.add_text_btn.setEnabled(False)
            self.add_delay_btn.setEnabled(False)
            app = QApplication.instance()
            if app:
                try:
                    app.removeEventFilter(self)
                except Exception:
                    pass

    def keyPressEvent(self, event):
        if not self.recording or event.isAutoRepeat():
            super().keyPressEvent(event)
            return

        key = event.key()
        if key in self.pressed_keys:
            return

        self.pressed_keys.add(key)
        
        # Check if this is a numpad key
        modifiers = event.modifiers()
        is_numpad = bool(modifiers & Qt.KeyboardModifier.KeypadModifier)
        
        # Map numpad numbers to KP_ keycodes
        keycode = None
        if is_numpad:
            numpad_map = {
                Qt.Key.Key_0: "KC.KP_0", Qt.Key.Key_1: "KC.KP_1", Qt.Key.Key_2: "KC.KP_2",
                Qt.Key.Key_3: "KC.KP_3", Qt.Key.Key_4: "KC.KP_4", Qt.Key.Key_5: "KC.KP_5",
                Qt.Key.Key_6: "KC.KP_6", Qt.Key.Key_7: "KC.KP_7", Qt.Key.Key_8: "KC.KP_8",
                Qt.Key.Key_9: "KC.KP_9", Qt.Key.Key_Period: "KC.KP_DOT",
                Qt.Key.Key_Slash: "KC.KP_SLASH", Qt.Key.Key_Asterisk: "KC.KP_ASTERISK",
                Qt.Key.Key_Minus: "KC.KP_MINUS", Qt.Key.Key_Plus: "KC.KP_PLUS",
                Qt.Key.Key_Enter: "KC.KP_ENTER", Qt.Key.Key_Equal: "KC.KP_EQUAL",
                Qt.Key.Key_Comma: "KC.KP_COMMA",
            }
            keycode = numpad_map.get(key)
        
        if not keycode:
            keycode = QT_TO_KMK.get(key)
        
        if keycode:
            # Record the press and remember when/where it was added so we
            # can convert it to a 'tap' later if released quickly.
            now = time.monotonic()
            self.sequence.append(('press', keycode))
            self.sequence_list.addItem(f"Press: {keycode}")
            self.press_timestamps[key] = (now, len(self.sequence) - 1)

    def keyReleaseEvent(self, event):
        if not self.recording or event.isAutoRepeat():
            super().keyReleaseEvent(event)
            return

        key = event.key()
        if key not in self.pressed_keys:
            return
            
        self.pressed_keys.discard(key)
        
        # Check if this is a numpad key
        modifiers = event.modifiers()
        is_numpad = bool(modifiers & Qt.KeyboardModifier.KeypadModifier)
        
        # Map numpad numbers to KP_ keycodes
        keycode = None
        if is_numpad:
            numpad_map = {
                Qt.Key.Key_0: "KC.KP_0", Qt.Key.Key_1: "KC.KP_1", Qt.Key.Key_2: "KC.KP_2",
                Qt.Key.Key_3: "KC.KP_3", Qt.Key.Key_4: "KC.KP_4", Qt.Key.Key_5: "KC.KP_5",
                Qt.Key.Key_6: "KC.KP_6", Qt.Key.Key_7: "KC.KP_7", Qt.Key.Key_8: "KC.KP_8",
                Qt.Key.Key_9: "KC.KP_9", Qt.Key.Key_Period: "KC.KP_DOT",
                Qt.Key.Key_Slash: "KC.KP_SLASH", Qt.Key.Key_Asterisk: "KC.KP_ASTERISK",
                Qt.Key.Key_Minus: "KC.KP_MINUS", Qt.Key.Key_Plus: "KC.KP_PLUS",
                Qt.Key.Key_Enter: "KC.KP_ENTER", Qt.Key.Key_Equal: "KC.KP_EQUAL",
                Qt.Key.Key_Comma: "KC.KP_COMMA",
            }
            keycode = numpad_map.get(key)
        
        if not keycode:
            keycode = QT_TO_KMK.get(key)
        
        if keycode:
            now = time.monotonic()
            press_info = self.press_timestamps.pop(key, None)
            if press_info is not None:
                press_time, seq_index = press_info
                delta = now - press_time
                if delta <= self.TAP_THRESHOLD:
                    # Convert the earlier 'press' entry into a 'tap'
                    if 0 <= seq_index < len(self.sequence):
                        self.sequence[seq_index] = ('tap', keycode)
                        item = self.sequence_list.item(seq_index)
                        if item:
                            item.setText(f"Tap: {keycode}")
                            # Style the item to indicate it was auto-collapsed
                            item.setForeground(QColor('#00cc66'))
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                    else:
                        # Fallback: append a tap if index is invalid
                        self.sequence.append(('tap', keycode))
                        self.sequence_list.addItem(f"Tap: {keycode}")
                else:
                    # Not a quick tap — record release normally
                    self.sequence.append(('release', keycode))
                    self.sequence_list.addItem(f"Release: {keycode}")
            else:
                # No recorded press timestamp (edge case) — just record release
                self.sequence.append(('release', keycode))
                self.sequence_list.addItem(f"Release: {keycode}")

    def eventFilter(self, obj, event):
        # While recording, consume key press/release events so they don't
        # propagate to the rest of the application or other programs.
        # This ensures keyboard input is ONLY captured by the recorder.
        if not self.recording:
            return False

        event_type = event.type()
        
        # Block all keyboard events from propagating
        if event_type == QEvent.Type.KeyPress:
            # Forward to our handler and consume the event
            try:
                self.keyPressEvent(event)
            except Exception:
                pass
            return True  # Event consumed - won't reach other widgets or OS
            
        elif event_type == QEvent.Type.KeyRelease:
            try:
                self.keyReleaseEvent(event)
            except Exception:
                pass
            return True  # Event consumed
        
        # Block shortcut events to prevent accidental triggers
        elif event_type == QEvent.Type.Shortcut:
            return True

        # Allow all mouse events - the dialog is modal so users can only interact with it anyway
        return False

    def accept(self):
        # Ensure we stop filtering if the dialog is closed via OK
        app = QApplication.instance()
        if app:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
        super().accept()

    def reject(self):
        # Ensure we stop filtering if the dialog is closed via Cancel
        app = QApplication.instance()
        if app:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
        super().reject()

    def insert_text_string(self):
        """Allow user to insert a text string during macro recording."""
        if not self.recording:
            return
        
        # Temporarily pause event filtering so the input dialog can receive keyboard events
        was_recording = self.recording
        self.recording = False
        app = QApplication.instance()
        if app:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
        
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Insert Text String", "Enter text to type:")
        
        # Resume recording and event filtering
        if was_recording:
            self.recording = True
            if app:
                app.installEventFilter(self)
        
        if ok and text:
            self.sequence.append(('text', text))
            item_text = f"Text: {text}"
            self.sequence_list.addItem(item_text)

    def insert_delay(self):
        """Allow user to insert a delay during macro recording."""
        if not self.recording:
            return
        
        # Temporarily pause event filtering so the input dialog can receive keyboard events
        was_recording = self.recording
        self.recording = False
        app = QApplication.instance()
        if app:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
        
        from PyQt6.QtWidgets import QInputDialog
        delay_ms, ok = QInputDialog.getInt(
            self, "Insert Delay", "Enter delay in milliseconds:", 
            value=100, min=1, max=10000, step=50
        )
        
        # Resume recording and event filtering
        if was_recording:
            self.recording = True
            if app:
                app.installEventFilter(self)
        
        if ok:
            self.sequence.append(('delay', delay_ms))
            self.sequence_list.addItem(f"Delay: {delay_ms}ms")

    def get_sequence(self):
        """
        Returns the raw recorded sequence of actions.
        Each entry is a tuple of (action_type, value) where action_type
        is one of 'tap', 'press', 'release', or 'delay'.
        """
        return self.sequence


class KeyCaptureDialog(QDialog):
    """Simple dialog that captures a single key press and returns the KMK keycode."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capture Key")
        self.setModal(True)
        self.setMinimumSize(300, 100)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Press the key you want to capture (or Cancel)"))
        self.captured = None

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        modifiers = event.modifiers()
        
        # Check if this is a numpad key
        is_numpad = bool(modifiers & Qt.KeyboardModifier.KeypadModifier)
        
        # Map numpad numbers to KP_ keycodes
        if is_numpad:
            numpad_map = {
                Qt.Key.Key_0: "KC.KP_0", Qt.Key.Key_1: "KC.KP_1", Qt.Key.Key_2: "KC.KP_2",
                Qt.Key.Key_3: "KC.KP_3", Qt.Key.Key_4: "KC.KP_4", Qt.Key.Key_5: "KC.KP_5",
                Qt.Key.Key_6: "KC.KP_6", Qt.Key.Key_7: "KC.KP_7", Qt.Key.Key_8: "KC.KP_8",
                Qt.Key.Key_9: "KC.KP_9", Qt.Key.Key_Period: "KC.KP_DOT",
                Qt.Key.Key_Slash: "KC.KP_SLASH", Qt.Key.Key_Asterisk: "KC.KP_ASTERISK",
                Qt.Key.Key_Minus: "KC.KP_MINUS", Qt.Key.Key_Plus: "KC.KP_PLUS",
                Qt.Key.Key_Enter: "KC.KP_ENTER", Qt.Key.Key_Equal: "KC.KP_EQUAL",
                Qt.Key.Key_Comma: "KC.KP_COMMA",
            }
            keycode = numpad_map.get(key)
            if keycode:
                self.captured = keycode
                self.accept()
                return
        
        # Otherwise use the standard mapping
        keycode = QT_TO_KMK.get(key)
        if keycode:
            self.captured = keycode
            self.accept()
        else:
            # For printable characters not in map, try to map to KC.X style
            text = event.text().upper()
            if text and len(text) == 1 and text.isalnum():
                self.captured = f"KC.{text}"
                self.accept()
            else:
                super().keyPressEvent(event)


# --- Macro Editor Dialog ---
class MacroEditorDialog(QDialog):
    """A dialog for creating and editing macros with various action types."""
    def __init__(self, macro_name="", macro_sequence=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Editor")
        
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Macro Name:"))
        self.name_input = QLineEdit(macro_name)
        self.layout.addWidget(self.name_input)

        self.layout.addWidget(QLabel("Sequence:"))
        self.sequence_list = QListWidget()
        # Allow reordering actions via drag & drop
        from PyQt6.QtWidgets import QAbstractItemView
        self.sequence_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sequence_list.setDragEnabled(True)
        self.sequence_list.setAcceptDrops(True)
        self.sequence_list.setDropIndicatorShown(True)
        self.sequence_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        if macro_sequence:
            for action_type, value in macro_sequence:
                self.sequence_list.addItem(f"{action_type.title()}: {value}")
        self.layout.addWidget(self.sequence_list)
        # Allow double-clicking an action to edit it
        self.sequence_list.itemDoubleClicked.connect(self.edit_action_item)

        record_layout = QHBoxLayout()
        record_btn = QPushButton("Record Macro...")
        record_btn.clicked.connect(self.record_macro)
        record_layout.addWidget(record_btn)
        self.layout.addLayout(record_layout)

        action_layout = QHBoxLayout()
        add_text_btn = QPushButton("Add Text")
        add_text_btn.clicked.connect(self.add_text_action)
        action_layout.addWidget(add_text_btn)
        
        add_tap_btn = QPushButton("Add Tap")
        add_tap_btn.clicked.connect(self.add_tap_action)
        action_layout.addWidget(add_tap_btn)

        add_press_btn = QPushButton("Add Press")
        add_press_btn.clicked.connect(self.add_press_action)
        action_layout.addWidget(add_press_btn)

        add_release_btn = QPushButton("Add Release")
        add_release_btn.clicked.connect(self.add_release_action)
        action_layout.addWidget(add_release_btn)

        add_delay_btn = QPushButton("Add Delay (ms)")
        add_delay_btn.clicked.connect(self.add_delay_action)
        action_layout.addWidget(add_delay_btn)

        self.layout.addLayout(action_layout)

        manage_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Selected Action")
        remove_btn.clicked.connect(self.remove_selected_action)
        manage_layout.addWidget(remove_btn)
        self.layout.addLayout(manage_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def record_macro(self):
        dialog = MacroRecorderDialog(self)
        if dialog.exec():
            sequence = dialog.get_sequence()
            if sequence:
                self.sequence_list.clear()
                for action, value in sequence:
                    self.sequence_list.addItem(f"{action.title()}: {value}")

    def add_text_action(self):
        text, ok = QInputDialog.getText(self, "Add Text Action", "Text to type:")
        if ok and text:
            self.sequence_list.addItem(f"Text: {text}")

    def add_tap_action(self):
        key, ok = QInputDialog.getText(self, "Add Tap Action", "Enter Keycode (e.g., KC.A).\nFor combos, use separate Press/Tap/Release actions.")
        if ok and key:
            self.sequence_list.addItem(f"Tap: {key}")

    def add_press_action(self):
        key, ok = QInputDialog.getText(self, "Add Press Action", "Enter Keycode to press and hold (e.g., KC.LCTL):")
        if ok and key:
            self.sequence_list.addItem(f"Press: {key}")

    def add_release_action(self):
        key, ok = QInputDialog.getText(self, "Add Release Action", "Enter Keycode to release (e.g., KC.LCTL):")
        if ok and key:
            self.sequence_list.addItem(f"Release: {key}")
            
    def add_delay_action(self):
        delay, ok = QInputDialog.getInt(self, "Add Delay Action", "Milliseconds:", 100, 0, 10000)
        if ok:
            self.sequence_list.addItem(f"Delay: {delay}")

    def remove_selected_action(self):
        for item in self.sequence_list.selectedItems():
            self.sequence_list.takeItem(self.sequence_list.row(item))

    def edit_action_item(self, item):
        if not item:
            return
        text = item.text()
        if ':' not in text:
            return
        action_type, value = text.split(':', 1)
        action_type = action_type.strip().lower()
        value = value.strip()

        if action_type in ('tap', 'press', 'release', 'text'):
            # For key-like actions and text, open key capture for key or input for text
            if action_type == 'text':
                new_text, ok = QInputDialog.getText(self, "Edit Text Action", "Text to type:", text=value)
                if ok:
                    item.setText(f"Text: {new_text}")
            else:
                # Open capture dialog to press the desired key
                dlg = KeyCaptureDialog(self)
                if dlg.exec():
                    captured = dlg.captured
                    if captured:
                        item.setText(f"{action_type.title()}: {captured}")

        elif action_type == 'delay':
            # edit delay value
            try:
                current = int(value)
            except Exception:
                current = 100
            new_delay, ok = QInputDialog.getInt(self, "Edit Delay", "Milliseconds:", current, 0, 60000)
            if ok:
                item.setText(f"Delay: {new_delay}")
            
    def get_data(self):
        sequence = []
        for i in range(self.sequence_list.count()):
            item_text = self.sequence_list.item(i).text()
            action_type, value = item_text.split(":", 1)
            sequence.append((action_type.lower().strip(), value.strip()))
        
        macro_name = self.name_input.text().strip().upper().replace(" ", "_")
        if not macro_name or not macro_name.isidentifier():
            macro_name = None
            
        return macro_name, sequence


# --- Pin Editor Dialog ---
class PinEditorDialog(QDialog):
    """A dialog for editing the hardware row and column pin assignments."""
    def __init__(self, rows, cols, row_pins, col_pins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pin Editor")
        
        main_layout = QVBoxLayout(self)
        pin_groups_layout = QHBoxLayout()
        
        col_group = QGroupBox("Column Pins")
        col_layout = QGridLayout()
        self.col_pin_inputs = []
        for i in range(cols):
            col_layout.addWidget(QLabel(f"Col {i}:"), i, 0)
            line_edit = QLineEdit()
            if i < len(col_pins):
                line_edit.setText(col_pins[i])
            self.col_pin_inputs.append(line_edit)
            col_layout.addWidget(line_edit, i, 1)
        col_group.setLayout(col_layout)
        pin_groups_layout.addWidget(col_group)

        row_group = QGroupBox("Row Pins")
        row_layout = QGridLayout()
        self.row_pin_inputs = []
        for i in range(rows):
            row_layout.addWidget(QLabel(f"Row {i}:"), i, 0)
            line_edit = QLineEdit()
            if i < len(row_pins):
                line_edit.setText(row_pins[i])
            self.row_pin_inputs.append(line_edit)
            row_layout.addWidget(line_edit, i, 1)
        row_group.setLayout(row_layout)
        pin_groups_layout.addWidget(row_group)
        
        main_layout.addLayout(pin_groups_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_pins(self):
        col_pins = [widget.text().strip() for widget in self.col_pin_inputs]
        row_pins = [widget.text().strip() for widget in self.row_pin_inputs]
        return col_pins, row_pins


class EncoderConfigDialog(QDialog):
    """Enhanced encoder configuration dialog with automatic layer cycling and display updates."""
    def __init__(self, parent=None, initial_text="", num_layers=1):
        super().__init__(parent)
        self.setWindowTitle("Rotary Encoder Configuration")
        self.resize(600, 550)
        self.num_layers = num_layers

        main_layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel(
            "Configure your rotary encoder for layer cycling with automatic display updates.\n"
            "Hardware: Pin A=GP10, Pin B=GP11, Button=GP14"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background-color: #E3F2FD; padding: 8px; border-radius: 4px;")
        main_layout.addWidget(info)
        
        # Hardware pins (fixed for Chronos Pad)
        hw_group = QGroupBox("Hardware Configuration (Fixed)")
        hw_layout = QFormLayout()
        self.pin_a = QLineEdit("board.GP10")
        self.pin_a.setReadOnly(True)
        self.pin_b = QLineEdit("board.GP11")
        self.pin_b.setReadOnly(True)
        self.pin_button = QLineEdit("board.GP14")
        self.pin_button.setReadOnly(True)
        hw_layout.addRow("Pin A:", self.pin_a)
        hw_layout.addRow("Pin B:", self.pin_b)
        hw_layout.addRow("Button:", self.pin_button)
        hw_group.setLayout(hw_layout)
        main_layout.addWidget(hw_group)
        
        # Rotation behavior
        rotation_group = QGroupBox("Rotation Behavior")
        rotation_layout = QVBoxLayout()
        
        self.rotation_action = QComboBox()
        self.rotation_action.addItems([
            "Cycle Layers (Recommended)",
            "Volume Control (Vol Down / Vol Up)",
            "Brightness (Down / Up)",
            "Media (Prev Track / Next Track)",
            "Custom Actions"
        ])
        rotation_layout.addWidget(QLabel("Rotation Action:"))
        rotation_layout.addWidget(self.rotation_action)
        
        self.invert_direction = QCheckBox("Invert rotation direction")
        self.invert_direction.setToolTip("Swap clockwise and counter-clockwise actions")
        rotation_layout.addWidget(self.invert_direction)
        
        rotation_group.setLayout(rotation_layout)
        main_layout.addWidget(rotation_group)
        
        # Button press behavior
        button_group = QGroupBox("Center Button Press")
        button_layout = QVBoxLayout()
        
        self.button_action = QComboBox()
        self.button_action.addItems([
            "Reset to Layer 0 (Recommended)",
            "Toggle Layer 1",
            "Mute",
            "Play/Pause",
            "Custom Action"
        ])
        button_layout.addWidget(QLabel("Button Action:"))
        button_layout.addWidget(self.button_action)
        
        button_group.setLayout(button_layout)
        main_layout.addWidget(button_group)
        
        # Display updates
        display_group = QGroupBox("Display Integration")
        display_layout = QVBoxLayout()
        
        self.enable_display_updates = QCheckBox("Update display on layer change")
        self.enable_display_updates.setChecked(True)
        self.enable_display_updates.setToolTip("Automatically refresh OLED display when changing layers")
        display_layout.addWidget(self.enable_display_updates)
        
        self.show_layer_number = QCheckBox("Show current layer number on display")
        self.show_layer_number.setChecked(True)
        display_layout.addWidget(self.show_layer_number)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # Custom actions (initially hidden)
        self.custom_group = QGroupBox("Custom Actions")
        custom_layout = QFormLayout()
        self.custom_ccw = QLineEdit()
        self.custom_ccw.setPlaceholderText("e.g., KC.LEFT")
        self.custom_cw = QLineEdit()
        self.custom_cw.setPlaceholderText("e.g., KC.RGHT")
        self.custom_press = QLineEdit()
        self.custom_press.setPlaceholderText("e.g., KC.ENT")
        custom_layout.addRow("Counter-Clockwise:", self.custom_ccw)
        custom_layout.addRow("Clockwise:", self.custom_cw)
        custom_layout.addRow("Button Press:", self.custom_press)
        self.custom_group.setLayout(custom_layout)
        self.custom_group.setVisible(False)
        main_layout.addWidget(self.custom_group)
        
        # Connect signals
        self.rotation_action.currentTextChanged.connect(self._on_action_changed)
        self.button_action.currentTextChanged.connect(self._on_action_changed)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
    
    def _on_action_changed(self):
        """Show/hide custom action fields based on selection"""
        show_custom = (self.rotation_action.currentText() == "Custom Actions" or 
                      self.button_action.currentText() == "Custom Action")
        self.custom_group.setVisible(show_custom)

    def get_config(self):
        """Generate encoder configuration code"""
        lines = []
        lines.append("# --- Rotary Encoder Configuration ---")
        lines.append("from kmk.modules.encoder import EncoderHandler")
        lines.append("")
        
        # Determine rotation actions
        rotation = self.rotation_action.currentText()
        invert = self.invert_direction.isChecked()
        
        if rotation == "Cycle Layers (Recommended)":
            ccw_action = "KC.LAYER_PREV"
            cw_action = "KC.LAYER_NEXT"
        elif rotation == "Volume Control (Vol Down / Vol Up)":
            ccw_action = "KC.VOLD"
            cw_action = "KC.VOLU"
        elif rotation == "Brightness (Down / Up)":
            ccw_action = "KC.BRID"
            cw_action = "KC.BRIU"
        elif rotation == "Media (Prev Track / Next Track)":
            ccw_action = "KC.MPRV"
            cw_action = "KC.MNXT"
        else:  # Custom
            ccw_action = self.custom_ccw.text().strip() or "KC.NO"
            cw_action = self.custom_cw.text().strip() or "KC.NO"
        
        # Swap if inverted
        if invert:
            ccw_action, cw_action = cw_action, ccw_action
        
        # For layer cycling, use our custom keys instead of KC references
        if rotation == "Cycle Layers (Recommended)":
            if invert:
                ccw_action = "LAYER_NEXT_KEY"
                cw_action = "LAYER_PREV_KEY"
            else:
                ccw_action = "LAYER_PREV_KEY"
                cw_action = "LAYER_NEXT_KEY"
        
        # Determine button action
        button = self.button_action.currentText()
        if button == "Reset to Layer 0 (Recommended)":
            if rotation == "Cycle Layers (Recommended)":
                press_action = "LAYER_RESET_KEY"
            else:
                press_action = "KC.NO"  # No custom reset if not using layer cycling
        elif button == "Toggle Layer 1":
            press_action = "KC.TG(1)"
        elif button == "Mute":
            press_action = "KC.MUTE"
        elif button == "Play/Pause":
            press_action = "KC.MPLY"
        else:  # Custom
            press_action = self.custom_press.text().strip() or "KC.NO"
        
        # Generate layer cycler if needed
        if rotation == "Cycle Layers (Recommended)":
            lines.append("# Encoder configuration with layer cycling using KC.TO()")
            lines.append("encoder_handler = EncoderHandler()")
            lines.append(f"encoder_handler.pins = ((board.GP10, board.GP11, board.GP14, {invert}),)")
            lines.append("")
            lines.append("# Build encoder map for each layer")
            lines.append("# Each layer's encoder: (CCW action, CW action, Button press action)")
            lines.append("encoder_map = []")
            lines.append(f"for i in range({self.num_layers}):")
            lines.append(f"    next_layer = (i + 1) % {self.num_layers}")
            lines.append(f"    prev_layer = (i - 1) % {self.num_layers}")
            lines.append(f"    # CCW=prev layer, CW=next layer, Press=layer 0")
            lines.append(f"    encoder_map.append(((KC.TO(prev_layer), KC.TO(next_layer), KC.TO(0)),))")
            lines.append("")
            lines.append("encoder_handler.map = encoder_map")
            lines.append("keyboard.modules.append(encoder_handler)")
            lines.append("")
        else:
            # Non-layer cycling modes
            lines.append("# Configure encoder")
            lines.append("encoder_handler = EncoderHandler()")
            lines.append(f"encoder_handler.pins = ((board.GP10, board.GP11, board.GP14, {invert}),)")
            lines.append(f"encoder_handler.map = [(({ccw_action}, {cw_action}, {press_action}),)]")
            lines.append("keyboard.modules.append(encoder_handler)")
            lines.append("")
        
        if rotation == "Cycle Layers (Recommended)":
            lines.append("# Initialize layer cycler after keymap is defined")
            lines.append("# NOTE: Add this line AFTER keyboard.keymap = [...] in your code.py:")
            lines.append(f"# layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))")
        
        return "\n".join(lines)


class AnalogInConfigDialog(QDialog):
    """Configuration dialog for Chronos Pad Analog Slider.
    Hardware: 10k potentiometer on GP28
    """
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Analog Slider Configuration (GP28)")
        self.resize(550, 500)

        main_layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "<b>Chronos Pad Analog Slider</b><br>"
            "Hardware: 10k potentiometer connected to GP28<br>"
            "Choose function: Volume control or LED brightness control"
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        main_layout.addSpacing(20)
        
        # Mode selection
        mode_group = QGroupBox("Slider Function")
        mode_layout = QVBoxLayout()
        
        self.mode_volume = QCheckBox("Volume Control")
        self.mode_volume.setChecked(True)
        self.mode_volume.setToolTip("Use slider to control system volume (up/down)")
        self.mode_volume.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_volume)
        
        self.mode_brightness = QCheckBox("LED Brightness Control")
        self.mode_brightness.setToolTip("Use slider to control RGB LED brightness (0-100%)")
        self.mode_brightness.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_brightness)
        
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
        main_layout.addSpacing(10)
        
        # Configuration parameters
        form_layout = QFormLayout()
        
        # Poll interval
        self.poll_interval_spin = QDoubleSpinBox()
        self.poll_interval_spin.setRange(0.01, 1.0)
        self.poll_interval_spin.setSingleStep(0.01)
        self.poll_interval_spin.setValue(0.05)
        self.poll_interval_spin.setSuffix(" sec")
        self.poll_interval_spin.setToolTip("How often to check the slider position (seconds)")
        form_layout.addRow("Poll Interval:", self.poll_interval_spin)
        
        # Threshold
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(100, 10000)
        self.threshold_spin.setSingleStep(100)
        self.threshold_spin.setValue(2000)
        self.threshold_spin.setToolTip("Minimum slider movement to trigger change (0-65535 range)")
        form_layout.addRow("Sensitivity Threshold:", self.threshold_spin)
        
        # Step size (only for volume mode)
        self.step_size_label = QLabel("Volume Step Size:")
        self.step_size_spin = QSpinBox()
        self.step_size_spin.setRange(1, 5)
        self.step_size_spin.setValue(1)
        self.step_size_spin.setToolTip("Number of volume steps per slider movement")
        form_layout.addRow(self.step_size_label, self.step_size_spin)
        
        main_layout.addLayout(form_layout)
        
        main_layout.addSpacing(20)
        
        # Advanced: custom code editor (optional)
        main_layout.addWidget(QLabel("<b>Advanced:</b> Custom Configuration (leave empty to use defaults above)"))
        self.custom_code_editor = QTextEdit()
        self.custom_code_editor.setPlaceholderText("Optional: Paste custom slider configuration here...")
        self.custom_code_editor.setMaximumHeight(150)
        if initial_text and "slider" not in initial_text.lower():
            # Only populate if it's truly custom code
            self.custom_code_editor.setPlainText(initial_text)
        main_layout.addWidget(self.custom_code_editor)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        # Initialize UI state
        self.on_mode_changed()
    
    def on_mode_changed(self):
        """Handle mode toggle - ensure only one mode is selected"""
        sender = self.sender()
        
        if sender == self.mode_volume and self.mode_volume.isChecked():
            self.mode_brightness.setChecked(False)
            self.step_size_label.setEnabled(True)
            self.step_size_spin.setEnabled(True)
        elif sender == self.mode_brightness and self.mode_brightness.isChecked():
            self.mode_volume.setChecked(False)
            self.step_size_label.setEnabled(False)
            self.step_size_spin.setEnabled(False)
        elif sender is None:
            # Initial setup - volume is default
            if not self.mode_volume.isChecked() and not self.mode_brightness.isChecked():
                self.mode_volume.setChecked(True)

    def get_config(self):
        """Generate the slider configuration code"""
        # If custom code is provided, use it
        custom_code = self.custom_code_editor.toPlainText().strip()
        if custom_code:
            return custom_code
        
        # Check which mode is selected
        is_volume_mode = self.mode_volume.isChecked()
        
        # Get form values
        poll_interval = self.poll_interval_spin.value()
        threshold = self.threshold_spin.value()
        step_size = self.step_size_spin.value()
        
        if is_volume_mode:
            # Generate volume control code
            config = f'''from analogio import AnalogIn as AnalogInPin
from kmk.keys import KC
import time

# Volume control via 10k sliding potentiometer on GP28
class VolumeSlider:
    def __init__(self, keyboard, pin, poll_interval={poll_interval}):
        self.keyboard = keyboard
        self.analog_pin = AnalogInPin(pin)
        self.poll_interval = poll_interval
        self.last_value = self.read_value()
        self.last_poll = time.monotonic()
        self.last_movement = time.monotonic()
        self.threshold = {threshold}  # Minimum change to trigger volume adjustment (out of 65535)
        self.step_size = {step_size}  # Number of volume steps per change
        self.idle_timeout = 2.0  # Seconds of no movement before requiring re-sync
        self.synced = False  # Track if we've established direction after idle
        
    def read_value(self):
        """Read analog value (0-65535)"""
        return self.analog_pin.value
    
    def during_bootup(self, keyboard):
        """Initialize at boot"""
        self.last_value = self.read_value()
        self.synced = False  # Require initial movement to establish baseline
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
        delta = current_value - self.last_value
        
        # Check if we've been idle too long (user may have adjusted volume elsewhere)
        time_since_movement = current_time - self.last_movement
        if time_since_movement > self.idle_timeout:
            self.synced = False  # Need to re-sync on next movement
        
        # If slider moved significantly
        if abs(delta) > self.threshold:
            # If we're not synced (first movement after idle), just update position without sending
            if not self.synced:
                self.last_value = current_value
                self.last_movement = current_time
                self.synced = True
                return
            
            # Normal operation: send volume commands based on direction
            if delta > 0:
                # Slider moved up (higher value) - increase volume
                for _ in range(self.step_size):
                    # Tap volume up key
                    self.keyboard.add_key(KC.VOLU)
                    self.keyboard.remove_key(KC.VOLU)
            else:
                # Slider moved down (lower value) - decrease volume
                for _ in range(self.step_size):
                    # Tap volume down key
                    self.keyboard.add_key(KC.VOLD)
                    self.keyboard.remove_key(KC.VOLD)
            
            self.last_value = current_value
            self.last_movement = current_time
    
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
    
    def deinit(self, keyboard):
        """Clean up when keyboard is shutting down"""
        return

# Create and register volume slider extension
volume_slider = VolumeSlider(keyboard, board.GP28, poll_interval={poll_interval})
keyboard.extensions.append(volume_slider)
'''
        else:
            # Generate brightness control code
            config = f'''from analogio import AnalogIn as AnalogInPin
import time

# LED brightness control via 10k sliding potentiometer on GP28
class BrightnessSlider:
    def __init__(self, keyboard, pin, poll_interval={poll_interval}):
        self.keyboard = keyboard
        self.analog_pin = AnalogInPin(pin)
        self.poll_interval = poll_interval
        self.last_poll = time.monotonic()
        self.threshold = {threshold}  # Minimum change to trigger brightness adjustment (out of 65535)
        
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
brightness_slider = BrightnessSlider(keyboard, board.GP28, poll_interval={poll_interval})
keyboard.extensions.append(brightness_slider)
'''
        
        return config


class PegRgbConfigDialog(QDialog):
    """Dialog for configuring global RGB matrix settings."""

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("Peg RGB Matrix Configuration")
        self.resize(520, 320)

        layout = QVBoxLayout(self)
        cfg = config or build_default_rgb_matrix_config()
        self._base_config = cfg

        form = QFormLayout()

        self.pixel_pin_edit = QLineEdit(cfg.get("pixel_pin", FIXED_RGB_PIN))
        form.addRow("Pixel pin:", self.pixel_pin_edit)

        self.brightness_spin = QDoubleSpinBox()
        self.brightness_spin.setRange(0.0, 1.0)
        self.brightness_spin.setSingleStep(0.05)
        self.brightness_spin.setDecimals(2)
        self.brightness_spin.setValue(float(cfg.get("brightness_limit", 0.5)))
        form.addRow("Brightness limit:", self.brightness_spin)

        self.underglow_spin = QSpinBox()
        self.underglow_spin.setRange(0, 128)
        self.underglow_spin.setValue(int(cfg.get("num_underglow", 0)))
        form.addRow("Underglow LEDs:", self.underglow_spin)

        self.rgb_order_combo = QComboBox()
        self.rgb_order_combo.addItems(list(RGB_ORDER_TUPLES.keys()))
        order = cfg.get("rgb_order", "GRB")
        if order not in RGB_ORDER_TUPLES:
            order = "GRB"
        self.rgb_order_combo.setCurrentText(order)
        form.addRow("RGB order:", self.rgb_order_combo)

        self.disable_auto_write_checkbox = QCheckBox("Disable auto write (recommended)")
        self.disable_auto_write_checkbox.setChecked(bool(cfg.get("disable_auto_write", True)))
        form.addRow("", self.disable_auto_write_checkbox)

        self.default_key_color = ensure_hex_prefix(cfg.get("default_key_color", "#FFFFFF"), "#FFFFFF")
        self.default_underglow_color = ensure_hex_prefix(cfg.get("default_underglow_color", "#000000"), "#000000")

        self.key_color_btn = self._make_color_button(self.default_key_color, self._pick_key_color)
        form.addRow("Default key color:", self.key_color_btn)

        self.underglow_color_btn = self._make_color_button(self.default_underglow_color, self._pick_underglow_color)
        form.addRow("Default underglow color:", self.underglow_color_btn)

        layout.addLayout(form)

        info = QLabel(
            "Peg RGB Matrix sets static per-key and underglow colors. "
            "Use the per-key editor to override individual LEDs."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #777; font-size: 10px;")
        layout.addWidget(info)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _make_color_button(self, color: str, handler):
        button = QPushButton(color)
        button.setFixedWidth(120)
        button.clicked.connect(handler)
        self._update_color_button(button, color)
        return button

    def _update_color_button(self, button: QPushButton, color: str):
        rgb = hex_to_rgb_list(color)
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        text_color = "#000000" if luminance > 150 else "#FFFFFF"
        button.setText(color)
        button.setStyleSheet(f"background-color: {color}; color: {text_color};")

    def _pick_key_color(self):
        color = QColorDialog.getColor(QColor(self.default_key_color), self, "Select default key color")
        if color.isValid():
            self.default_key_color = ensure_hex_prefix(color.name(), self.default_key_color)
            self._update_color_button(self.key_color_btn, self.default_key_color)

    def _pick_underglow_color(self):
        color = QColorDialog.getColor(
            QColor(self.default_underglow_color), self, "Select default underglow color"
        )
        if color.isValid():
            self.default_underglow_color = ensure_hex_prefix(color.name(), self.default_underglow_color)
            self._update_color_button(self.underglow_color_btn, self.default_underglow_color)

    def get_config(self):
        result = build_default_rgb_matrix_config()
        base_copy = dict(self._base_config)
        result.update(base_copy)
        result["key_colors"] = dict(self._base_config.get("key_colors", {}))
        result["underglow_colors"] = dict(self._base_config.get("underglow_colors", {}))
        result["pixel_pin"] = self.pixel_pin_edit.text().strip() or FIXED_RGB_PIN
        result["brightness_limit"] = float(self.brightness_spin.value())
        result["num_underglow"] = int(self.underglow_spin.value())
        order = self.rgb_order_combo.currentText()
        if order not in RGB_ORDER_TUPLES:
            order = "GRB"
        result["rgb_order"] = order
        result["disable_auto_write"] = self.disable_auto_write_checkbox.isChecked()
        result["default_key_color"] = self.default_key_color
        result["default_underglow_color"] = self.default_underglow_color
        return result


class PerKeyColorDialog(QDialog):
    """Dialog to assign static per-key and underglow colors for Peg RGB Matrix."""

    def __init__(
        self,
        parent=None,
        rows=5,
        cols=4,
        key_colors=None,
        underglow_count=0,
        underglow_colors=None,
        default_key_color="#FFFFFF",
        default_underglow_color="#000000",
    ):
        super().__init__(parent)
        self.setWindowTitle("RGB Matrix Colors")
        self.rows = rows
        self.cols = cols
        self.underglow_count = max(0, underglow_count)
        self.parent_ref = parent

        key_default = ensure_hex_prefix(default_key_color, "#FFFFFF")
        under_default = ensure_hex_prefix(default_underglow_color, "#000000")
        self.key_colors = {
            str(k): ensure_hex_prefix(v, key_default)
            for k, v in (key_colors or {}).items()
        }
        self.underglow_colors = {
            str(k): ensure_hex_prefix(v, under_default)
            for k, v in (underglow_colors or {}).items()
        }

        self.fill_color = key_default
        self.underglow_fill_color = under_default

        self.resize(1200, 700)
        layout = QVBoxLayout(self)

        info_label = QLabel(
            "Peg RGB Matrix applies a single static color map across all layers. "
            "Use your current layer for category presets; KC.NO keys are treated as off."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "background-color: #D4EDDA; padding: 6px; border-radius: 4px; color: #155724; font-size: 10px;"
        )
        layout.addWidget(info_label)

        top = QHBoxLayout()
        clear_btn = QPushButton("Clear Keys")
        clear_btn.clicked.connect(self.clear_key_colors)
        top.addWidget(clear_btn)

        fill_btn = QPushButton("Fill Keys")
        fill_btn.clicked.connect(self.fill_key_colors)
        top.addWidget(fill_btn)

        self.fill_color_btn = QPushButton("Pick Fill Color")
        self.fill_color_btn.clicked.connect(self.pick_fill_color)
        top.addWidget(self.fill_color_btn)
        self._update_button_color(self.fill_color_btn, self.fill_color)

        top.addStretch()
        layout.addLayout(top)

        content_layout = QHBoxLayout()

        # LEFT SIDE: key grid + underglow list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("<b>Click a key to set its color:</b>"))

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        left_layout.addWidget(self.grid_widget)

        self._make_key_buttons()

        # Underglow controls
        under_group = QGroupBox(f"Underglow LEDs ({self.underglow_count})")
        under_layout = QVBoxLayout(under_group)

        under_controls = QHBoxLayout()
        under_clear = QPushButton("Clear")
        under_clear.clicked.connect(self.clear_underglow_colors)
        under_controls.addWidget(under_clear)

        under_fill = QPushButton("Fill")
        under_fill.clicked.connect(self.fill_underglow_colors)
        under_controls.addWidget(under_fill)

        self.underglow_fill_btn = QPushButton("Pick Fill Color")
        self.underglow_fill_btn.clicked.connect(self.pick_underglow_fill_color)
        under_controls.addWidget(self.underglow_fill_btn)
        self._update_button_color(self.underglow_fill_btn, self.underglow_fill_color)
        under_controls.addStretch()
        under_layout.addLayout(under_controls)

        self.underglow_buttons = []
        if self.underglow_count:
            grid = QGridLayout()
            for idx in range(self.underglow_count):
                btn = QPushButton(f"U{idx}")
                btn.setFixedSize(60, 40)
                btn.setStyleSheet("font-size: 12px;")
                btn.clicked.connect(lambda _, i=idx: self.on_underglow_clicked(i))
                self.underglow_buttons.append(btn)
                grid.addWidget(btn, idx // 8, idx % 8)
                try:
                    self._install_hover_effect(btn)
                except Exception:
                    pass
            under_layout.addLayout(grid)
        else:
            under_layout.addWidget(QLabel("No underglow LEDs configured."))

        left_layout.addWidget(under_group)
        left_layout.addStretch()
        content_layout.addWidget(left_widget, stretch=1)

        # RIGHT SIDE: presets reused from legacy dialog
        from PyQt6.QtWidgets import QScrollArea

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        presets_widget = QWidget()
        presets_layout = QVBoxLayout(presets_widget)

        self.category_colors = {
            "macro": "#FF6B6B",
            "basic": "#4ECDC4",
            "modifiers": "#A8E6CF",
            "navigation": "#FFD93D",
            "function": "#95E1D3",
            "media": "#F38181",
            "mouse": "#AA96DA",
            "layers": "#FCBAD3",
            "misc": "#B4B4B4",
        }

        category_labels = {
            "macro": "Macros",
            "basic": "Basic",
            "modifiers": "Modifiers",
            "navigation": "Navigation",
            "function": "Function",
            "media": "Media",
            "mouse": "Mouse",
            "layers": "Layers",
            "misc": "Misc",
        }

        preset_group = QGroupBox("Keycode Category Presets")
        preset_grid = QGridLayout(preset_group)
        row = 0
        for cat_key, cat_label in category_labels.items():
            preset_grid.addWidget(QLabel(f"{cat_label}:") , row, 0)

            color_btn = QPushButton()
            color_btn.setFixedSize(25, 25)
            color_btn.setStyleSheet(f"background-color: {self.category_colors[cat_key]};")
            color_btn.clicked.connect(lambda _, k=cat_key: self.pick_category_color(k))
            setattr(self, f"{cat_key}_color_btn", color_btn)
            preset_grid.addWidget(color_btn, row, 1)

            apply_btn = QPushButton("Apply")
            apply_btn.setMaximumWidth(60)
            apply_btn.clicked.connect(lambda _, k=cat_key: self.apply_category_color(k))
            preset_grid.addWidget(apply_btn, row, 2)
            row += 1

        presets_layout.addWidget(preset_group)

        self.granular_colors = {
            "numbers": "#FFA500",
            "letters": "#87CEEB",
            "space": "#90EE90",
            "enter": "#FFB6C1",
            "backspace": "#FF6347",
            "tab": "#DDA0DD",
            "shift": "#F0E68C",
            "ctrl": "#98FB98",
            "alt": "#FFDAB9",
            "keypad_nums": "#FF8C42",
            "keypad_nav": "#FFC947",
            "keypad_ops": "#C7A27C",
        }

        granular_labels = {
            "numbers": "Numbers (0-9)",
            "letters": "Letters (A-Z)",
            "space": "Space",
            "enter": "Enter",
            "backspace": "Backspace",
            "tab": "Tab",
            "shift": "Shift",
            "ctrl": "Ctrl",
            "alt": "Alt",
            "keypad_nums": "Keypad Numbers",
            "keypad_nav": "Keypad Navigation",
            "keypad_ops": "Keypad Operators",
        }

        granular_group = QGroupBox("Fine-Grained Presets")
        granular_grid = QGridLayout(granular_group)
        row = 0
        for gran_key, gran_label in granular_labels.items():
            granular_grid.addWidget(QLabel(f"{gran_label}:") , row, 0)

            color_btn = QPushButton()
            color_btn.setFixedSize(25, 25)
            color_btn.setStyleSheet(f"background-color: {self.granular_colors[gran_key]};")
            color_btn.clicked.connect(lambda _, k=gran_key: self.pick_granular_color(k))
            setattr(self, f"{gran_key}_granular_btn", color_btn)
            granular_grid.addWidget(color_btn, row, 1)

            apply_btn = QPushButton("Apply")
            apply_btn.setMaximumWidth(60)
            apply_btn.clicked.connect(lambda _, k=gran_key: self.apply_granular_color(k))
            granular_grid.addWidget(apply_btn, row, 2)
            row += 1

        presets_layout.addWidget(granular_group)
        presets_layout.addStretch()

        scroll.setWidget(presets_widget)
        content_layout.addWidget(scroll, stretch=1)

        layout.addLayout(content_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.refresh_key_buttons()
        self.refresh_underglow_buttons()

    def _make_key_buttons(self):
        self.key_buttons = []
        for r in range(self.rows):
            for c in range(self.cols):
                idx = r * self.cols + c
                btn = QPushButton(f"{r},{c}")
                btn.setFixedSize(64, 56)
                btn.setStyleSheet("font-size: 12px; padding: 4px;")
                btn.clicked.connect(self.on_key_clicked)
                self.key_buttons.append(btn)
                self.grid_layout.addWidget(btn, r, c)
                try:
                    self._install_hover_effect(btn)
                except Exception:
                    pass

    def _install_hover_effect(self, button: QPushButton):
        if hasattr(button, "_hover_filter"):
            return
        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(140)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        button._hover_anim = anim
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor("#00000033"))
        button.setGraphicsEffect(shadow)

        class _Filter(QObject):
            def __init__(self, btn, animation):
                super().__init__(btn)
                self.btn = btn
                self.anim = animation

            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.Enter:
                    g = self.btn.geometry()
                    self.anim.stop()
                    self.anim.setStartValue(g)
                    self.anim.setEndValue(g.adjusted(-4, -3, 4, 3))
                    self.anim.start()
                elif event.type() == QEvent.Type.Leave:
                    g = self.btn.geometry()
                    self.anim.stop()
                    self.anim.setStartValue(g)
                    self.anim.setEndValue(g.adjusted(4, 3, -4, -3))
                    self.anim.start()
                return False

        filt = _Filter(button, anim)
        button.installEventFilter(filt)
        button._hover_filter = filt

    def refresh_key_buttons(self):
        for idx, btn in enumerate(self.key_buttons):
            color = self.key_colors.get(str(idx))
            if color:
                rgb = hex_to_rgb_list(color)
                luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                text_color = "#000000" if luminance > 150 else "#FFFFFF"
                btn.setStyleSheet(f"background-color: {color}; color: {text_color}; font-size: 12px; padding: 4px;")
                btn.setToolTip(f"Index: {idx}\nColor: {color}")
            else:
                btn.setStyleSheet("font-size: 12px; padding: 4px;")
                btn.setToolTip(f"Index: {idx}\nColor: (default)")

    def refresh_underglow_buttons(self):
        for idx, btn in enumerate(self.underglow_buttons):
            color = self.underglow_colors.get(str(idx))
            if color:
                rgb = hex_to_rgb_list(color)
                luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                text_color = "#000000" if luminance > 150 else "#FFFFFF"
                btn.setStyleSheet(f"background-color: {color}; color: {text_color}; font-size: 12px;")
                btn.setToolTip(f"Underglow {idx}: {color}")
            else:
                btn.setStyleSheet("font-size: 12px;")
                btn.setToolTip(f"Underglow {idx}: (default)")

    def on_key_clicked(self):
        btn = self.sender()
        if btn not in self.key_buttons:
            return
        idx = self.key_buttons.index(btn)
        color = QColorDialog.getColor(QColor(self.fill_color), self, "Select key color")
        if color.isValid():
            hexc = ensure_hex_prefix(color.name(), self.fill_color)
            self.key_colors[str(idx)] = hexc
            self.refresh_key_buttons()

    def on_underglow_clicked(self, index: int):
        color = QColorDialog.getColor(QColor(self.underglow_fill_color), self, "Select underglow color")
        if color.isValid():
            hexc = ensure_hex_prefix(color.name(), self.underglow_fill_color)
            self.underglow_colors[str(index)] = hexc
            self.refresh_underglow_buttons()

    def clear_key_colors(self):
        self.key_colors.clear()
        self.refresh_key_buttons()

    def fill_key_colors(self):
        for idx in range(self.rows * self.cols):
            self.key_colors[str(idx)] = self.fill_color
        self.refresh_key_buttons()

    def pick_fill_color(self):
        color = QColorDialog.getColor(QColor(self.fill_color), self, "Pick key fill color")
        if color.isValid():
            self.fill_color = ensure_hex_prefix(color.name(), self.fill_color)
            self._update_button_color(self.fill_color_btn, self.fill_color)

    def clear_underglow_colors(self):
        self.underglow_colors.clear()
        self.refresh_underglow_buttons()

    def fill_underglow_colors(self):
        for idx in range(self.underglow_count):
            self.underglow_colors[str(idx)] = self.underglow_fill_color
        self.refresh_underglow_buttons()

    def pick_underglow_fill_color(self):
        color = QColorDialog.getColor(
            QColor(self.underglow_fill_color), self, "Pick underglow fill color"
        )
        if color.isValid():
            self.underglow_fill_color = ensure_hex_prefix(color.name(), self.underglow_fill_color)
            self._update_button_color(self.underglow_fill_btn, self.underglow_fill_color)

    def pick_category_color(self, category):
        current = self.category_colors.get(category, self.fill_color)
        color = QColorDialog.getColor(QColor(current), self, f"Pick {category} color")
        if color.isValid():
            hexc = ensure_hex_prefix(color.name(), current)
            self.category_colors[category] = hexc
            btn = getattr(self, f"{category}_color_btn", None)
            if btn:
                btn.setStyleSheet(f"background-color: {hexc};")

    def apply_category_color(self, category):
        parent = self.parent_ref
        if not parent or not hasattr(parent, "keymap_data") or not parent.keymap_data:
            QMessageBox.warning(self, "Error", "Cannot access keymap data")
            return

        layer_idx = parent.current_layer if 0 <= parent.current_layer < len(parent.keymap_data) else 0
        layer_data = parent.keymap_data[layer_idx]
        color = self.category_colors.get(category, self.fill_color)

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if r < len(layer_data) and c < len(layer_data[r]):
                    key = layer_data[r][c]
                    if self._matches_category(category, key):
                        self.key_colors[str(idx)] = color
                idx += 1
        self.refresh_key_buttons()

    def pick_granular_color(self, granular_type):
        current = self.granular_colors.get(granular_type, self.fill_color)
        color = QColorDialog.getColor(QColor(current), self, f"Pick {granular_type} color")
        if color.isValid():
            hexc = ensure_hex_prefix(color.name(), current)
            self.granular_colors[granular_type] = hexc
            btn = getattr(self, f"{granular_type}_granular_btn", None)
            if btn:
                btn.setStyleSheet(f"background-color: {hexc};")

    def apply_granular_color(self, granular_type):
        parent = self.parent_ref
        if not parent or not hasattr(parent, "keymap_data") or not parent.keymap_data:
            QMessageBox.warning(self, "Error", "Cannot access keymap data")
            return

        layer_idx = parent.current_layer if 0 <= parent.current_layer < len(parent.keymap_data) else 0
        layer_data = parent.keymap_data[layer_idx]
        color = self.granular_colors.get(granular_type, self.fill_color)

        number_keys = ['KC.N1', 'KC.N2', 'KC.N3', 'KC.N4', 'KC.N5', 'KC.N6', 'KC.N7', 'KC.N8', 'KC.N9', 'KC.N0']
        letter_keys = [
            'KC.A', 'KC.B', 'KC.C', 'KC.D', 'KC.E', 'KC.F', 'KC.G', 'KC.H', 'KC.I', 'KC.J',
            'KC.K', 'KC.L', 'KC.M', 'KC.N', 'KC.O', 'KC.P', 'KC.Q', 'KC.R', 'KC.S', 'KC.T',
            'KC.U', 'KC.V', 'KC.W', 'KC.X', 'KC.Y', 'KC.Z'
        ]
        space_keys = ['KC.SPC', 'KC.SPACE']
        enter_keys = ['KC.ENT', 'KC.ENTER', 'KC.KP_ENTER']
        backspace_keys = ['KC.BSPC', 'KC.DEL', 'KC.BACKSPACE', 'KC.DELETE']
        tab_keys = ['KC.TAB']
        shift_keys = ['KC.LSFT', 'KC.RSFT', 'KC.LSHIFT', 'KC.RSHIFT']
        ctrl_keys = ['KC.LCTL', 'KC.RCTL', 'KC.LCTRL', 'KC.RCTRL']
        alt_keys = ['KC.LALT', 'KC.RALT']
        keypad_number_keys = ['KC.KP_0', 'KC.KP_1', 'KC.KP_2', 'KC.KP_3', 'KC.KP_4', 'KC.KP_5', 'KC.KP_6', 'KC.KP_7', 'KC.KP_8', 'KC.KP_9']
        keypad_nav_keys = ['KC.KP_DOT', 'KC.KP_0', 'KC.KP_1', 'KC.KP_2', 'KC.KP_3', 'KC.KP_4', 'KC.KP_5', 'KC.KP_6', 'KC.KP_7', 'KC.KP_8', 'KC.KP_9']
        keypad_op_keys = ['KC.KP_SLASH', 'KC.KP_ASTERISK', 'KC.KP_MINUS', 'KC.KP_PLUS', 'KC.KP_ENTER', 'KC.KP_DOT', 'KC.KP_EQUAL', 'KC.KP_COMMA', 'KC.NUMLOCK']

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if r < len(layer_data) and c < len(layer_data[r]):
                    key = layer_data[r][c]
                    should_color = False

                    if granular_type == 'numbers' and key in number_keys:
                        should_color = True
                    elif granular_type == 'letters' and key in letter_keys:
                        should_color = True
                    elif granular_type == 'space' and key in space_keys:
                        should_color = True
                    elif granular_type == 'enter' and key in enter_keys:
                        should_color = True
                    elif granular_type == 'backspace' and key in backspace_keys:
                        should_color = True
                    elif granular_type == 'tab' and key in tab_keys:
                        should_color = True
                    elif granular_type == 'shift' and key in shift_keys:
                        should_color = True
                    elif granular_type == 'ctrl' and key in ctrl_keys:
                        should_color = True
                    elif granular_type == 'alt' and key in alt_keys:
                        should_color = True
                    elif granular_type == 'keypad_nums' and key in keypad_number_keys:
                        should_color = True
                    elif granular_type == 'keypad_nav' and key in keypad_nav_keys:
                        should_color = True
                    elif granular_type == 'keypad_ops' and key in keypad_op_keys:
                        should_color = True

                    if should_color:
                        self.key_colors[str(idx)] = color
                idx += 1

        self.refresh_key_buttons()

    def _matches_category(self, category: str, keycode: str) -> bool:
        if category == 'macro' and keycode.startswith('MACRO('):
            return True
        if category == 'basic':
            return keycode in KEYCODES.get('Basic', [])
        if category == 'modifiers':
            return keycode in KEYCODES.get('Modifiers', [])
        if category == 'navigation':
            return keycode in KEYCODES.get('Navigation', [])
        if category == 'function':
            return keycode in KEYCODES.get('Function', [])
        if category == 'media':
            return keycode in KEYCODES.get('Media', [])
        if category == 'mouse':
            return keycode in KEYCODES.get('Mouse', [])
        if category == 'layers':
            return (
                keycode in KEYCODES.get('Layers', [])
                or keycode.startswith('KC.MO(')
                or keycode.startswith('KC.TG(')
                or keycode.startswith('KC.DF(')
            )
        if category == 'misc':
            return keycode in KEYCODES.get('Misc', [])
        return False

    def get_maps(self):
        return self.key_colors.copy(), self.underglow_colors.copy()

    def accept(self):
        if self.parent_ref and hasattr(self.parent_ref, 'rgb_matrix_config'):
            config = self.parent_ref.rgb_matrix_config
            config['key_colors'] = self.key_colors.copy()
            config['underglow_colors'] = self.underglow_colors.copy()
            self.parent_ref.update_macropad_display()
        super().accept()

    def _update_button_color(self, button: QPushButton, color: str):
        rgb = hex_to_rgb_list(color)
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        text_color = '#000000' if luminance > 150 else '#FFFFFF'
        button.setStyleSheet(f"background-color: {color}; color: {text_color};")


# --- Main Application Window ---
class KMKConfigurator(QMainWindow):
    """The main application window for configuring KMK-based macropads."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KMK Macropad Configurator")
        self.setGeometry(100, 100, 1400, 900)

        # Check and download dependencies first
        self.check_dependencies()

        # default theme (can be changed by the user)
        self.current_theme = 'Dark'
        # Load persisted UI settings (theme) if available
        self.load_ui_settings()
        self._set_stylesheet()

        # --- Application State ---
        self.selected_key_coords = None
        self.macropad_buttons = {}
        self.current_layer = 0
        
        # Fixed hardware configuration
        self.rows = FIXED_ROWS
        self.cols = FIXED_COLS
        self.row_pins = FIXED_ROW_PINS.copy()
        self.col_pins = FIXED_COL_PINS.copy()
        self.diode_orientation = FIXED_DIODE_ORIENTATION
        
        self.macros = {}
        self.profiles = {}
        # Extensions are always enabled - user can configure them
        self.enable_encoder = True
        self.encoder_config_str = DEFAULT_ENCODER_CONFIG  # Pre-populate with default
        self.enable_analogin = True
        self.analogin_config_str = DEFAULT_ANALOGIN_CONFIG  # Pre-populate with default
        self.enable_rgb = True
        self.rgb_matrix_config = build_default_rgb_matrix_config()
        self.enable_display = True
        self.display_config_str = ""

        self.initialize_keymap_data()

        # Load persisted extension configs (if any)
        self.load_extension_configs()

        # --- UI Initialization ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)


        # --- Left Panel (Hardware, Layers, Grid) ---
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 2)

        self.setup_file_io_ui(left_layout)
        self.setup_extensions_ui(left_layout)
        self.setup_hardware_profile_ui(left_layout)
        
        # --- Center Panel (Macropad Grid) ---
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, 3)
        self.setup_layer_management_ui(center_layout)
        self.setup_macropad_grid_ui(center_layout)


        # --- Right Panel (Keycode Selection, Macros) ---
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 2)

        self.setup_keycode_selector_ui(right_layout)
        self.setup_macro_ui(right_layout)
        
        # --- Final UI Population ---
        self.recreate_macropad_grid()
        self.load_profiles()
        self.load_macros()
        self.update_layer_tabs()
        self.update_macropad_display()

        # Show startup dialog asking to load previous state
        self.show_startup_dialog()
        # Install hover/animation effects across all buttons in the UI
        try:
            self.install_global_hover_effects()
        except Exception:
            pass

    def check_dependencies(self):
        """Check if KMK firmware and CircuitPython libraries are available, download if not"""
        if os.environ.get("KMK_SKIP_DEP_CHECK"):
            return
        libraries_dir = os.path.join(os.getcwd(), "libraries")
        kmk_path = os.path.join(libraries_dir, "kmk_firmware-main")
        bundle_path = os.path.join(libraries_dir, "adafruit-circuitpython-bundle-9.x-mpy")
        
        if os.path.exists(kmk_path) and os.path.exists(bundle_path):
            return  # Dependencies already exist
        
        # Show download dialog
        reply = QMessageBox.question(
            self, 
            "Download Dependencies",
            "This tool requires KMK firmware and CircuitPython libraries.\n"
            "Would you like to download them automatically?\n\n"
            "This will download:\n"
            "• KMK Firmware (GPL-3.0 license)\n"
            "• Adafruit CircuitPython Bundle (MIT license)\n\n"
            "Files will be downloaded to the 'libraries' folder.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            QMessageBox.warning(
                self,
                "Dependencies Required",
                "This tool requires KMK firmware and CircuitPython libraries to function.\n"
                "Please download them manually or restart and choose to download automatically."
            )
            return
        
        # Show progress dialog and start download
        self.progress_dialog = QProgressDialog("Preparing download...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.show()
        
        # Start download thread
        self.downloader = DependencyDownloader()
        self.downloader.progress.connect(self.on_download_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.start()
    
    def on_download_progress(self, message, percentage):
        """Handle download progress updates"""
        self.progress_dialog.setLabelText(message)
        self.progress_dialog.setValue(percentage)
        QApplication.processEvents()
    
    def on_download_finished(self, success):
        """Handle download completion"""
        self.progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self,
                "Download Complete",
                "Dependencies downloaded successfully!\n"
                "KMK firmware and CircuitPython libraries are now available."
            )
        else:
            QMessageBox.critical(
                self,
                "Download Failed",
                "Failed to download dependencies.\n"
                "Please check your internet connection and try again,\n"
                "or download manually from:\n\n"
                "• KMK: https://github.com/KMKfw/kmk_firmware\n"
                "• CircuitPython Bundle: https://circuitpython.org/libraries"
            )

    def show_startup_dialog(self):
        """Show dialog asking user if they want to load previous state or start fresh."""
        if os.environ.get("KMK_SKIP_STARTUP_DIALOG"):
            return

        config_file = os.path.join(CONFIG_SAVE_DIR, "kmk_config.json")

        # If no previous config exists, skip dialog
        if not os.path.exists(config_file):
            return

        reply = QMessageBox.question(
            self,
            "Load Previous State?",
            "Would you like to load your previous configuration?\n\n"
            "• Yes: Load last saved keymap, macros, and RGB settings\n"
            "• No: Start fresh with all keys unassigned (gray)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.load_configuration(file_path=config_file, show_message=False)
            if success:
                return

        self.reset_to_defaults()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults - all keys KC.NO, no RGB colors"""
        # Reset keymap to all KC.NO
        self.keymap_data = [[[DEFAULT_KEY for _ in range(self.cols)] for _ in range(self.rows)]]
        self.current_layer = 0
        
        # Clear macros
        self.macros = {}
        
        # Reset RGB matrix configuration
        self.rgb_matrix_config = build_default_rgb_matrix_config()
        
        # Reset extensions to defaults
        self.enable_encoder = True
        self.enable_analogin = True
        self.enable_rgb = True
        self.enable_display = True
        self.encoder_config_str = DEFAULT_ENCODER_CONFIG
        self.analogin_config_str = DEFAULT_ANALOGIN_CONFIG
        self.display_config_str = ""
        
        # Update display
        self.update_layer_tabs()
        self.update_macropad_display()
        self.update_macro_list()
        self.sync_extension_checkboxes()
        self.update_extension_button_states()
        try:
            self.save_extension_configs()
        except Exception:
            pass

    def _set_stylesheet(self):
        """Sets the application's stylesheet based on current_theme."""
        self.setFont(QFont("Segoe UI", 9))
        # apply theme (cheerful geometry already baked into base)
        self.apply_theme(self.current_theme)

    def _apply_cheerful_stylesheet(self):
        """Apply neutral gray theme with subtle highlights."""
        base = self._base_geometry_qss()
        color_qss = '''
            QWidget { background-color: #3a3a3a; color: #e0e0e0; }
            QMainWindow { background-color: #2f2f2f; }
            QPushButton { background: #454545; border: 1px solid #555555; color: #e0e0e0; }
            QPushButton:hover { background: #505050; }
            QPushButton:pressed { background: #3f3f3f; }
            QPushButton#keymapButton:checked { background-color: #5a5a5a; border: 2px solid #707070; color: #ffffff; }
            QTabBar::tab:selected { background: #454545; }
            QListWidget::item:hover { background-color: #464646; }
            QListWidget::item:selected { background-color: #505050; color: #ffffff; font-weight: 600; }
            QLabel { color: #e5e5e5; }
            QLineEdit { background-color: #404040; border: 1px solid #606060; color: #ffffff; }
            QLineEdit:focus { border: 1px solid #808080; background-color: #484848; }
            QSpinBox { background-color: #404040; border: 1px solid #606060; color: #ffffff; }
            QSpinBox:focus { border: 1px solid #808080; background-color: #484848; }
            QComboBox { background-color: #404040; border: 1px solid #606060; color: #ffffff; }
            QComboBox:focus { border: 1px solid #808080; background-color: #484848; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #484848; color: #ffffff; selection-background-color: #585858; }
            QTextEdit { background-color: #404040; border: 1px solid #606060; color: #ffffff; }
            QTextEdit:focus { border: 1px solid #808080; background-color: #484848; }
            QGroupBox { border: 1px solid #555555; color: #e5e5e5; }
        '''
        self.setStyleSheet(base + color_qss)

    def _apply_light_stylesheet(self):
        """Apply neutral gray theme with subtle highlights (light variant)."""
        base = self._base_geometry_qss()
        color_qss = '''
            QWidget { background-color: #f5f5f5; color: #333333; }
            QMainWindow { background-color: #efefef; }
            QPushButton { background: #e8e8e8; border: 1px solid #d0d0d0; color: #333333; }
            QPushButton:hover { background: #e0e0e0; }
            QPushButton:pressed { background: #d8d8d8; }
            QPushButton#keymapButton:checked { background-color: #c0c0c0; border: 2px solid #909090; color: #000000; }
            QTabBar::tab:selected { background: #e8e8e8; }
            QListWidget::item:hover { background-color: #e0e0e0; }
            QListWidget::item:selected { background-color: #d0d0d0; color: #000000; font-weight: 600; }
            QLabel { color: #222222; }
            QLineEdit { background-color: #ffffff; border: 1px solid #c0c0c0; color: #000000; }
            QLineEdit:focus { border: 1px solid #909090; background-color: #fafafa; }
            QSpinBox { background-color: #ffffff; border: 1px solid #c0c0c0; color: #000000; }
            QSpinBox:focus { border: 1px solid #909090; background-color: #fafafa; }
            QComboBox { background-color: #ffffff; border: 1px solid #c0c0c0; color: #000000; }
            QComboBox:focus { border: 1px solid #909090; background-color: #fafafa; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #fafafa; color: #000000; selection-background-color: #e0e0e0; }
            QTextEdit { background-color: #ffffff; border: 1px solid #c0c0c0; color: #000000; }
            QTextEdit:focus { border: 1px solid #909090; background-color: #fafafa; }
            QGroupBox { border: 1px solid #d0d0d0; color: #222222; }
        '''
        self.setStyleSheet(base + color_qss)

    def _apply_dark_stylesheet(self):
        """Apply neutral gray theme with subtle highlights (dark variant)."""
        base = self._base_geometry_qss()
        color_qss = '''
            QWidget { background-color: #2a2a2a; color: #d5d5d5; }
            QMainWindow { background-color: #252525; }
            QPushButton { background: #3d3d3d; border: 1px solid #4d4d4d; color: #d5d5d5; }
            QPushButton:hover { background: #454545; }
            QPushButton:pressed { background: #353535; }
            QPushButton#keymapButton:checked { background-color: #4a4a4a; border: 2px solid #6a6a6a; color: #ffffff; }
            QTabBar::tab:selected { background: #3d3d3d; }
            QListWidget::item:hover { background-color: #3e3e3e; }
            QListWidget::item:selected { background-color: #454545; color: #ffffff; font-weight: 600; }
            QLabel { color: #e5e5e5; }
            QLineEdit { background-color: #353535; border: 1px solid #5d5d5d; color: #ffffff; }
            QLineEdit:focus { border: 1px solid #7d7d7d; background-color: #3d3d3d; }
            QSpinBox { background-color: #353535; border: 1px solid #5d5d5d; color: #ffffff; }
            QSpinBox:focus { border: 1px solid #7d7d7d; background-color: #3d3d3d; }
            QComboBox { background-color: #353535; border: 1px solid #5d5d5d; color: #ffffff; }
            QComboBox:focus { border: 1px solid #7d7d7d; background-color: #3d3d3d; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #3d3d3d; color: #ffffff; selection-background-color: #505050; }
            QTextEdit { background-color: #353535; border: 1px solid #5d5d5d; color: #ffffff; }
            QTextEdit:focus { border: 1px solid #7d7d7d; background-color: #3d3d3d; }
            QGroupBox { border: 1px solid #4d4d4d; color: #e5e5e5; }
        '''
        self.setStyleSheet(base + color_qss)

    def _base_geometry_qss(self):
        """Return QSS that defines geometry/shape/layout-only rules shared across themes."""
        return '''
            /* Base geometry and shape rules (theme-independent) */
            QGroupBox {
                border-radius: 10px;
                margin-top: 12px;
                font-weight: 700;
                padding: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 4px 8px; }
            QPushButton {
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 64px;
            }
            QTabWidget::pane { border-radius: 8px; }
            QTabBar::tab { padding: 8px 12px; border-radius: 6px; margin-right: 6px; }
            QLineEdit, QSpinBox, QComboBox { border-radius: 6px; padding: 6px; }
            QListWidget { border-radius: 8px; }
        '''

    # --- Extension config persistence ---
    def save_extension_configs(self):
        try:
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            meta = {
                "enable_encoder": self.enable_encoder,
                "enable_analogin": self.enable_analogin,
                "enable_rgb": self.enable_rgb,
                "enable_display": self.enable_display,
            }
            with open(os.path.join(CONFIG_SAVE_DIR, 'extensions.json'), 'w') as f:
                json.dump(meta, f, indent=2)

            with open(os.path.join(CONFIG_SAVE_DIR, 'encoder.py'), 'w') as f:
                f.write(self.encoder_config_str or '')
            with open(os.path.join(CONFIG_SAVE_DIR, 'analogin.py'), 'w') as f:
                f.write(self.analogin_config_str or '')
            with open(os.path.join(CONFIG_SAVE_DIR, 'display.py'), 'w') as f:
                f.write(self.display_config_str or '')

            rgb_config = build_default_rgb_matrix_config()
            current = getattr(self, 'rgb_matrix_config', None) or {}
            rgb_config.update(current)
            rgb_config['key_colors'] = dict(current.get('key_colors', {}))
            rgb_config['underglow_colors'] = dict(current.get('underglow_colors', {}))
            with open(os.path.join(CONFIG_SAVE_DIR, 'rgb_matrix.json'), 'w') as f:
                json.dump(rgb_config, f, indent=2)

            for legacy_name in ('peg_rgb.py', 'peg_rgb_colors.json', 'peg_rgb_layer.py'):
                legacy_path = os.path.join(CONFIG_SAVE_DIR, legacy_name)
                if os.path.exists(legacy_path):
                    try:
                        os.remove(legacy_path)
                    except OSError:
                        pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save extension configs:\n{e}")

    def load_extension_configs(self):
        try:
            if os.path.exists(os.path.join(CONFIG_SAVE_DIR, 'extensions.json')):
                with open(os.path.join(CONFIG_SAVE_DIR, 'extensions.json'), 'r') as f:
                    meta = json.load(f)
                # Load enable/disable states from saved config
                self.enable_encoder = meta.get('enable_encoder', True)
                self.enable_analogin = meta.get('enable_analogin', True)
                self.enable_rgb = meta.get('enable_rgb', True)
                self.enable_display = meta.get('enable_display', True)
            # Load snippet files if present
            enc_path = os.path.join(CONFIG_SAVE_DIR, 'encoder.py')
            if os.path.exists(enc_path):
                with open(enc_path, 'r') as f:
                    self.encoder_config_str = f.read()
            an_path = os.path.join(CONFIG_SAVE_DIR, 'analogin.py')
            if os.path.exists(an_path):
                with open(an_path, 'r') as f:
                    self.analogin_config_str = f.read()
            disp_path = os.path.join(CONFIG_SAVE_DIR, 'display.py')
            if os.path.exists(disp_path):
                with open(disp_path, 'r') as f:
                    self.display_config_str = f.read()
            rgb_path = os.path.join(CONFIG_SAVE_DIR, 'rgb_matrix.json')
            if os.path.exists(rgb_path):
                with open(rgb_path, 'r') as f:
                    data = json.load(f)
                merged = build_default_rgb_matrix_config()
                merged.update(data)
                merged['key_colors'] = dict(data.get('key_colors', {}))
                merged['underglow_colors'] = dict(data.get('underglow_colors', {}))
                merged['default_key_color'] = ensure_hex_prefix(
                    merged.get('default_key_color', '#FFFFFF'), '#FFFFFF'
                )
                merged['default_underglow_color'] = ensure_hex_prefix(
                    merged.get('default_underglow_color', '#000000'), '#000000'
                )
                self.rgb_matrix_config = merged
            else:
                # Legacy migration: attempt to load layer 0 colors if present
                colors_path = os.path.join(CONFIG_SAVE_DIR, 'peg_rgb_colors.json')
                legacy_colors = {}
                if os.path.exists(colors_path):
                    try:
                        with open(colors_path, 'r') as f:
                            legacy_colors = json.load(f)
                    except Exception:
                        legacy_colors = {}
                config = build_default_rgb_matrix_config()
                layer_zero = legacy_colors.get('0', {}) if isinstance(legacy_colors, dict) else {}
                config['key_colors'] = {
                    str(k): ensure_hex_prefix(v, config['default_key_color'])
                    for k, v in layer_zero.items()
                }
                self.rgb_matrix_config = config
                try:
                    self.save_extension_configs()
                except Exception:
                    pass
        except Exception:
            # don't block startup on extension load errors
            pass

    def save_ui_settings(self):
        """Save UI settings (theme) to kmk_Config_Save/ui_settings.json."""
        try:
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            settings = {
                "theme": getattr(self, 'current_theme', 'Dark')
            }
            with open(os.path.join(CONFIG_SAVE_DIR, 'ui_settings.json'), 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass

    def load_ui_settings(self):
        """Load UI settings (theme) from kmk_Config_Save/ui_settings.json."""
        try:
            settings_path = os.path.join(CONFIG_SAVE_DIR, 'ui_settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    theme = settings.get('theme', 'Dark')
                    if theme in ['Cheerful', 'Light', 'Dark']:
                        self.current_theme = theme
        except Exception:
            pass

    def setup_file_io_ui(self, parent_layout):
        group = QGroupBox("File")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Config file selector (populated from kmk_Config_Save and repo root)
        file_select_layout = QHBoxLayout()
        file_select_layout.addWidget(QLabel("Config file:"))
        self.config_file_combo = QComboBox()
        file_select_layout.addWidget(self.config_file_combo)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(70)
        refresh_btn.clicked.connect(self.populate_config_file_list)
        file_select_layout.addWidget(refresh_btn)
        layout.addLayout(file_select_layout)

        load_config_button = QPushButton("Load Configuration")
        load_config_button.clicked.connect(self.load_configuration)
        layout.addWidget(load_config_button)

        save_config_button = QPushButton("Save Config")
        save_config_button.clicked.connect(self.save_configuration_dialog)
        layout.addWidget(save_config_button)

        generate_button = QPushButton("Generate code.py")
        generate_button.clicked.connect(self.generate_code_py_dialog)
        layout.addWidget(generate_button)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Cheerful", "Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        # reflect current theme selection if available
        try:
            self.theme_combo.setCurrentText(self.current_theme)
        except Exception:
            pass
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group)

        # Fill the combo initially
        self.populate_config_file_list()

    def setup_extensions_ui(self, parent_layout):
        group = QGroupBox("Extensions")
        layout = QVBoxLayout()

        # Encoder (fixed pins: GP10, GP11, GP14)
        enc_layout = QHBoxLayout()
        self.enable_encoder_checkbox = QCheckBox("Encoder (GP10, GP11, GP14)")
        self.enable_encoder_checkbox.setChecked(self.enable_encoder)
        self.enable_encoder_checkbox.toggled.connect(self.on_encoder_toggled)
        enc_layout.addWidget(self.enable_encoder_checkbox)
        enc_cfg_btn = QPushButton("Configure")
        enc_cfg_btn.clicked.connect(self.configure_encoder)
        enc_layout.addWidget(enc_cfg_btn)
        self.encoder_cfg_btn = enc_cfg_btn
        layout.addLayout(enc_layout)

        # AnalogIn (fixed pin: GP28)
        an_layout = QHBoxLayout()
        self.enable_analogin_checkbox = QCheckBox("Analog Input (GP28 - Slider)")
        self.enable_analogin_checkbox.setChecked(self.enable_analogin)
        self.enable_analogin_checkbox.toggled.connect(self.on_analogin_toggled)
        an_layout.addWidget(self.enable_analogin_checkbox)
        an_cfg_btn = QPushButton("Configure")
        an_cfg_btn.clicked.connect(self.configure_analogin)
        an_layout.addWidget(an_cfg_btn)
        self.analogin_cfg_btn = an_cfg_btn
        layout.addLayout(an_layout)

        # Display (fixed pins: SDA=GP20, SCL=GP21)
        disp_layout = QHBoxLayout()
        self.enable_display_checkbox = QCheckBox("Display (I2C: GP20/GP21)")
        self.enable_display_checkbox.setChecked(self.enable_display)
        self.enable_display_checkbox.toggled.connect(self.on_display_toggled)
        disp_layout.addWidget(self.enable_display_checkbox)
        disp_cfg_btn = QPushButton("Configure")
        disp_cfg_btn.clicked.connect(self.configure_display)
        disp_layout.addWidget(disp_cfg_btn)
        self.display_cfg_btn = disp_cfg_btn
        layout.addLayout(disp_layout)

        # Peg RGB Matrix
        rgb_layout = QHBoxLayout()
        self.enable_rgb_checkbox = QCheckBox("RGB Matrix (GP9)")
        self.enable_rgb_checkbox.setChecked(self.enable_rgb)
        self.enable_rgb_checkbox.toggled.connect(self.on_rgb_toggled)
        rgb_layout.addWidget(self.enable_rgb_checkbox)
        rgb_cfg_btn = QPushButton("Configure")
        rgb_cfg_btn.clicked.connect(self.configure_rgb)
        rgb_layout.addWidget(rgb_cfg_btn)
        self.rgb_cfg_btn = rgb_cfg_btn
        # Quick access button for per-key color mapping
        rgb_colors_btn = QPushButton("Per-key Colors")
        def open_per_key_colors():
            cfg = self.rgb_matrix_config
            pc = PerKeyColorDialog(
                self,
                rows=self.rows,
                cols=self.cols,
                key_colors=cfg.get('key_colors', {}),
                underglow_count=cfg.get('num_underglow', 0),
                underglow_colors=cfg.get('underglow_colors', {}),
                default_key_color=cfg.get('default_key_color', '#FFFFFF'),
                default_underglow_color=cfg.get('default_underglow_color', '#000000'),
            )
            if pc.exec():
                key_map, underglow_map = pc.get_maps()
                cfg['key_colors'] = key_map
                cfg['underglow_colors'] = underglow_map
                self.save_extension_configs()
                self.update_macropad_display()
        rgb_colors_btn.clicked.connect(open_per_key_colors)
        rgb_layout.addWidget(rgb_colors_btn)
        self.rgb_colors_btn = rgb_colors_btn
        layout.addLayout(rgb_layout)

        # Update button states based on checkbox states
        self.update_extension_button_states()

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def on_theme_changed(self, name):
        self.current_theme = name
        self.apply_theme(name)
        self.save_ui_settings()

    def apply_theme(self, name):
        # Lightweight theme application: adjust stylesheet variables
        name = (name or "Cheerful").lower()
        if name == 'cheerful':
            self._apply_cheerful_stylesheet()
        elif name == 'light':
            self._apply_light_stylesheet()
        elif name == 'dark':
            self._apply_dark_stylesheet()

    # --- Extension toggle handlers ---
    def on_encoder_toggled(self, checked):
        """Handle encoder checkbox toggle."""
        self.enable_encoder = checked
        self.update_extension_button_states()
        self.save_extension_configs()

    def on_analogin_toggled(self, checked):
        """Handle analog input checkbox toggle."""
        self.enable_analogin = checked
        self.update_extension_button_states()
        self.save_extension_configs()

    def on_display_toggled(self, checked):
        """Handle display checkbox toggle."""
        self.enable_display = checked
        self.update_extension_button_states()
        self.save_extension_configs()

    def on_rgb_toggled(self, checked):
        """Handle RGB checkbox toggle."""
        self.enable_rgb = checked
        self.update_extension_button_states()
        self.save_extension_configs()

    def update_extension_button_states(self):
        """Enable or disable configuration buttons based on checkbox states."""
        if hasattr(self, 'encoder_cfg_btn'):
            self.encoder_cfg_btn.setEnabled(self.enable_encoder)
        if hasattr(self, 'analogin_cfg_btn'):
            self.analogin_cfg_btn.setEnabled(self.enable_analogin)
        if hasattr(self, 'display_cfg_btn'):
            self.display_cfg_btn.setEnabled(self.enable_display)
        if hasattr(self, 'rgb_cfg_btn'):
            self.rgb_cfg_btn.setEnabled(self.enable_rgb)
        if hasattr(self, 'rgb_colors_btn'):
            self.rgb_colors_btn.setEnabled(self.enable_rgb)

    def sync_extension_checkboxes(self):
        """Ensure extension checkboxes reflect current enabled states without triggering signals."""
        def _set_state(checkbox, value):
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(value)
                checkbox.blockSignals(False)

        _set_state(getattr(self, 'enable_encoder_checkbox', None), self.enable_encoder)
        _set_state(getattr(self, 'enable_analogin_checkbox', None), self.enable_analogin)
        _set_state(getattr(self, 'enable_display_checkbox', None), self.enable_display)
        _set_state(getattr(self, 'enable_rgb_checkbox', None), self.enable_rgb)

    def on_diode_orientation_changed(self, orientation):
        """Handle diode orientation change."""
        self.diode_orientation = orientation



    # --- Extension configuration handlers ---
    def configure_encoder(self):
        """Configure encoder with enhanced dialog for automatic layer cycling."""
        num_layers = len(self.keymap_data)
        dialog = EncoderConfigDialog(parent=self, initial_text=self.encoder_config_str or "", num_layers=num_layers)
        if dialog.exec():
            self.encoder_config_str = dialog.get_config()
            self.save_extension_configs()
            QMessageBox.information(self, "Encoder Configured", 
                                  "Encoder configuration has been updated.\n\n"
                                  "The encoder will cycle through layers and update the display automatically.")

    def configure_analogin(self):
        dlg = AnalogInConfigDialog(self, self.analogin_config_str)
        # Best-effort prefill: if string contains 'AnalogInput' place into inputs/editor
        try:
            txt = self.analogin_config_str.strip()
            if 'AnalogInput' in txt or 'AnalogIn(' in txt:
                dlg.evtmap_editor.setPlainText(txt)
        except Exception:
            pass
        if dlg.exec():
            self.analogin_config_str = dlg.get_config()
            self.save_extension_configs()

    def configure_display(self):
        """Configure display settings - shows auto-generated keymap layout."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Display Configuration")
        dlg.resize(700, 500)
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(QLabel("Display Configuration (I2C on SDA=GP20, SCL=GP21):"))
        layout.addWidget(QLabel("The display will auto-generate a visual layout of your keymap."))
        layout.addWidget(QLabel("Preview of generated code:"))
        
        editor = QTextEdit()
        # Show the auto-generated display code
        editor.setPlainText(self.generate_display_layout_code())
        editor.setFont(QFont("Courier New", 9))
        editor.setReadOnly(True)  # Make it read-only since it's auto-generated
        layout.addWidget(editor)
        
        info_label = QLabel("Note: This code is automatically generated based on your Layer 0 keymap.\nIt updates whenever you generate code.py.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)
        
        dlg.exec()

    def configure_rgb(self):
        dlg = PegRgbConfigDialog(self, self.rgb_matrix_config)

        dlg_colors_btn = QPushButton("Configure per-key colors")

        def open_colors():
            cfg = self.rgb_matrix_config
            pc = PerKeyColorDialog(
                self,
                rows=self.rows,
                cols=self.cols,
                key_colors=cfg.get('key_colors', {}),
                underglow_count=cfg.get('num_underglow', 0),
                underglow_colors=cfg.get('underglow_colors', {}),
                default_key_color=cfg.get('default_key_color', '#FFFFFF'),
                default_underglow_color=cfg.get('default_underglow_color', '#000000'),
            )
            if pc.exec():
                key_map, underglow_map = pc.get_maps()
                cfg['key_colors'] = key_map
                cfg['underglow_colors'] = underglow_map
                self.save_extension_configs()

        try:
            dlg.layout().insertWidget(0, dlg_colors_btn)
            dlg_colors_btn.clicked.connect(open_colors)
        except Exception:
            dlg_colors_btn.clicked.connect(open_colors)

        if dlg.exec():
            self.rgb_matrix_config = dlg.get_config()
            self.save_extension_configs()

        self.update_macropad_display()

    def populate_config_file_list(self):
        """Scans kmk_Config_Save and repo root for JSON files starting with 'KMK_Config' and populates the combo box."""
        paths = []
        save_dir = CONFIG_SAVE_DIR
        if os.path.isdir(save_dir):
            for f in os.listdir(save_dir):
                if f.lower().startswith('kmk_config') and f.lower().endswith('.json'):
                    full = os.path.join(save_dir, f)
                    paths.append(full)

        for f in os.listdir(os.getcwd()):
            if f.lower().startswith('kmk_config') and f.lower().endswith('.json'):
                full = os.path.join(os.getcwd(), f)
                if full not in paths:
                    paths.append(full)

        self.config_file_combo.blockSignals(True)
        self.config_file_combo.clear()
        display_names = [os.path.relpath(p, os.getcwd()) for p in paths]
        self.config_file_combo.addItems(display_names)
        self.config_file_combo.blockSignals(False)
    
    def setup_hardware_profile_ui(self, parent_layout):
        group = QGroupBox("Hardware Configuration")
        layout = QVBoxLayout()
        
        # Display fixed hardware info (read-only)
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Board:"), 0, 0)
        info_layout.addWidget(QLabel("Raspberry Pi Pico"), 0, 1)
        info_layout.addWidget(QLabel("Matrix:"), 1, 0)
        info_layout.addWidget(QLabel(f"{FIXED_ROWS}x{FIXED_COLS}"), 1, 1)
        layout.addLayout(info_layout)
        
        # Diode orientation selector
        diode_layout = QHBoxLayout()
        diode_layout.addWidget(QLabel("Diode Orientation:"))
        self.diode_combo = QComboBox()
        self.diode_combo.addItems(["COL2ROW", "ROW2COL"])
        self.diode_combo.setCurrentText(self.diode_orientation)
        self.diode_combo.currentTextChanged.connect(self.on_diode_orientation_changed)
        diode_layout.addWidget(self.diode_combo)
        layout.addLayout(diode_layout)
        
        # Profile dropdown and delete button
        profile_selection_layout = QHBoxLayout()
        profile_selection_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.load_selected_profile)
        profile_selection_layout.addWidget(self.profile_combo)
        
        delete_profile_btn = QPushButton("Del")
        delete_profile_btn.setFixedWidth(40)
        delete_profile_btn.clicked.connect(self.delete_selected_profile)
        profile_selection_layout.addWidget(delete_profile_btn)
        
        layout.addLayout(profile_selection_layout)

        save_profile_btn = QPushButton("Save Profile")
        save_profile_btn.clicked.connect(self.save_current_profile)
        layout.addWidget(save_profile_btn)

        group.setLayout(layout)
        parent_layout.addWidget(group)
        parent_layout.addStretch()


    def setup_layer_management_ui(self, parent_layout):
        layout = QHBoxLayout()
        self.layer_tabs = QTabWidget()
        self.layer_tabs.currentChanged.connect(self.on_layer_changed)
        layout.addWidget(self.layer_tabs)

        layer_button_layout = QVBoxLayout()
        add_layer_btn = QPushButton("+")
        add_layer_btn.setFixedWidth(30)
        add_layer_btn.clicked.connect(self.add_layer)
        layer_button_layout.addWidget(add_layer_btn)

        remove_layer_btn = QPushButton("-")
        remove_layer_btn.setFixedWidth(30)
        remove_layer_btn.clicked.connect(self.remove_layer)
        layer_button_layout.addWidget(remove_layer_btn)
        layer_button_layout.addStretch()
        layout.addLayout(layer_button_layout)
        
        parent_layout.addLayout(layout)


    def setup_macropad_grid_ui(self, parent_layout):
        self.macropad_group = QGroupBox(f"Keymap (Layer {self.current_layer})")
        self.macropad_layout = QGridLayout()
        self.macropad_layout.setHorizontalSpacing(10)
        self.macropad_layout.setVerticalSpacing(10)
        self.macropad_group.setLayout(self.macropad_layout)
        parent_layout.addWidget(self.macropad_group, 1)

    def setup_keycode_selector_ui(self, parent_layout):
        group = QGroupBox("Key Assignment")
        layout = QVBoxLayout()
        self.selected_key_label = QLabel("Selected Key: None")
        self.selected_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.selected_key_label)
        self.keycode_selector = self.create_keycode_selector()
        layout.addWidget(self.keycode_selector)

        # Add button for creating combo keys
        assign_combo_btn = QPushButton("Assign Combo...")
        assign_combo_btn.clicked.connect(self.assign_combo)
        layout.addWidget(assign_combo_btn)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def setup_macro_ui(self, parent_layout):
        group = QGroupBox("Macros")
        layout = QVBoxLayout()
        self.macro_list_widget = QListWidget()
        layout.addWidget(self.macro_list_widget)
        # Clicking a macro in this list assigns it to the currently-selected key
        self.macro_list_widget.itemClicked.connect(self.on_macro_selected)
        
        macro_button_layout = QHBoxLayout()
        add_macro_btn = QPushButton("Add")
        add_macro_btn.clicked.connect(self.add_macro)
        edit_macro_btn = QPushButton("Edit")
        edit_macro_btn.clicked.connect(self.edit_macro)
        remove_macro_btn = QPushButton("Remove")
        remove_macro_btn.clicked.connect(self.remove_macro)
        
        macro_button_layout.addWidget(add_macro_btn)
        macro_button_layout.addWidget(edit_macro_btn)
        macro_button_layout.addWidget(remove_macro_btn)
        
        layout.addLayout(macro_button_layout)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def closeEvent(self, event):
        """Save settings on application exit."""
        self.save_macros()
        self.save_profiles()
        event.accept()

    # --- File I/O and Profile Management ---

    def save_macros(self):
        try:
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            with open(MACRO_FILE, 'w') as f:
                json.dump(self.macros, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save macros:\n{e}")

    def load_macros(self):
        if os.path.exists(MACRO_FILE):
            try:
                with open(MACRO_FILE, 'r') as f:
                    self.macros = json.load(f)
            except Exception as e:
                # Show the user the parsing/loading error so they can fix the file
                QMessageBox.critical(self, "Error", f"Could not parse macros file ({MACRO_FILE}):\n{e}")
                self.macros = {}
        else:
            # Ensure the save directory exists for future saves
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            self.macros = {}
        self.update_macro_list()

    def save_profiles(self):
        try:
            with open(PROFILE_FILE, 'w') as f:
                json.dump(self.profiles, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save profiles:\n{e}")

    def load_profiles(self):
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, 'r') as f:
                    self.profiles = json.load(f)
            except Exception:
                self.profiles = {}
        
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItems(["Custom"] + sorted(self.profiles.keys()))
        self.profile_combo.blockSignals(False)

    def save_current_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and name:
            # Save only the keymap data - hardware is fixed
            self.profiles[name] = {
                "keymap_data": self.keymap_data
            }
            self.save_profiles()
            self.load_profiles()
            self.profile_combo.setCurrentText(name)

    def load_selected_profile(self):
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            profile = self.profiles.get(profile_name)
            if profile:
                # Load only keymap data - hardware is fixed
                self.keymap_data = profile.get("keymap_data", [])
                self.current_layer = 0
                self.update_layer_tabs()
                self.update_macropad_display()

    def delete_selected_profile(self):
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            reply = QMessageBox.question(self, "Delete Profile", f"Are you sure you want to delete the '{profile_name}' profile?")
            if reply == QMessageBox.StandardButton.Yes:
                if profile_name in self.profiles:
                    del self.profiles[profile_name]
                    self.load_profiles()


            
    # --- Key Assignment ---
    def create_keycode_selector(self):
        tab_widget = QTabWidget()
        for category, key_list in KEYCODES.items():
            list_widget = QListWidget()
            list_widget.addItems(key_list)
            list_widget.itemClicked.connect(self.on_keycode_assigned)
            tab_widget.addTab(list_widget, category)
        
        # Tab for macros
        self.macro_keycode_list = QListWidget()
        self.macro_keycode_list.itemClicked.connect(self.on_keycode_assigned)
        tab_widget.addTab(self.macro_keycode_list, "Macros")
        
        return tab_widget

    def on_keycode_assigned(self, item):
        keycode = item.text()
        if self.selected_key_coords:
            row, col = self.selected_key_coords
            self.keymap_data[self.current_layer][row][col] = keycode
            self.update_macropad_display()
        else:
            QMessageBox.warning(self, "No Key Selected", "Please select a key on the grid before assigning a keycode.")

    def assign_combo(self):
        """Open the combo creator dialog and assign the result to the selected key."""
        if not self.selected_key_coords:
            QMessageBox.warning(self, "No Key Selected", "Please select a key on the grid to assign a combo.")
            return

        dialog = ComboCreatorDialog(self)
        if dialog.exec():
            combo_string = dialog.get_combo_string()
            if combo_string:
                row, col = self.selected_key_coords
                self.keymap_data[self.current_layer][row][col] = combo_string
                self.update_macropad_display()

    # --- Macro Management ---
    def add_macro(self):
        dialog = MacroEditorDialog(parent=self)
        if dialog.exec():
            name, sequence = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Invalid Name", "Macro name must be a valid Python identifier.")
                return
            if name in self.macros:
                QMessageBox.warning(self, "Name Exists", "A macro with this name already exists.")
                return
            self.macros[name] = sequence
            self.update_macro_list()
            # Persist macros immediately
            self.save_macros()

    def edit_macro(self):
        selected_items = self.macro_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Macro Selected", "Please select a macro to edit.")
            return
        
        name = selected_items[0].text()
        sequence = self.macros.get(name, [])
        
        dialog = MacroEditorDialog(macro_name=name, macro_sequence=sequence, parent=self)
        if dialog.exec():
            new_name, new_sequence = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Macro name must be a valid Python identifier.")
                return
            
            if name != new_name and new_name in self.macros:
                QMessageBox.warning(self, "Name Exists", "A macro with that new name already exists.")
                return

            if name != new_name:
                # Update keymap if macro name changed
                for layer in self.keymap_data:
                    for r in range(len(layer)):
                        for c in range(len(layer[r])):
                            if layer[r][c] == f"MACRO({name})":
                                layer[r][c] = f"MACRO({new_name})"
                del self.macros[name]

            self.macros[new_name] = new_sequence
            self.update_macro_list()
            self.update_macropad_display()
            # Persist macros after edit
            self.save_macros()

    def remove_macro(self):
        selected_items = self.macro_list_widget.selectedItems()
        if not selected_items: return
        
        name = selected_items[0].text()
        reply = QMessageBox.question(self, "Remove Macro", f"Are you sure you want to remove the '{name}' macro?")
        
        if reply == QMessageBox.StandardButton.Yes:
            if name in self.macros:
                del self.macros[name]
            # Replace macro occurrences in the keymap with the default key
            for layer in self.keymap_data:
                for r in range(len(layer)):
                    for c in range(len(layer[r])):
                        if layer[r][c] == f"MACRO({name})":
                            layer[r][c] = DEFAULT_KEY
            self.update_macro_list()
            self.update_macropad_display()
            # Persist macros after removal
            self.save_macros()
            
    def update_macro_list(self):
        self.macro_list_widget.clear()
        self.macro_list_widget.addItems(sorted(self.macros.keys()))
        
        self.macro_keycode_list.clear()
        macro_keys = [f"MACRO({name})" for name in sorted(self.macros.keys())]
        self.macro_keycode_list.addItems(macro_keys)

        # Allow double-clicking a macro name in the left list to edit it
        self.macro_list_widget.itemDoubleClicked.connect(lambda item: self.edit_macro_by_name(item.text()))

    def edit_macro_by_name(self, name):
        # Open MacroEditorDialog for the macro with given name
        if name not in self.macros:
            QMessageBox.warning(self, "Macro Not Found", f"Macro '{name}' not found.")
            return
        sequence = self.macros.get(name, [])
        dialog = MacroEditorDialog(macro_name=name, macro_sequence=sequence, parent=self)
        if dialog.exec():
            new_name, new_sequence = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Macro name must be a valid Python identifier.")
                return
            # Check for rename collisions
            if new_name != name and new_name in self.macros:
                QMessageBox.warning(self, "Name Exists", "A macro with that new name already exists.")
                return
            # Update keymap references if name changed
            if new_name != name:
                for layer in self.keymap_data:
                    for r in range(len(layer)):
                        for c in range(len(layer[r])):
                            if layer[r][c] == f"MACRO({name})":
                                layer[r][c] = f"MACRO({new_name})"
                del self.macros[name]
            self.macros[new_name] = new_sequence
            self.update_macro_list()
            self.update_macropad_display()
            self.save_macros()

    def eventFilter(self, obj, event):
        # Handle double-clicks on macropad buttons to edit/create macros
        if event.type() == QEvent.Type.MouseButtonDblClick:
            # If one of our macropad buttons was double-clicked
            for coords, btn in self.macropad_buttons.items():
                if obj is btn:
                    r, c = coords
                    key_text = self.keymap_data[self.current_layer][r][c]
                    m = re.match(r"MACRO\((\w+)\)", key_text)
                    if m:
                        macro_name = m.group(1)
                        self.edit_macro_by_name(macro_name)
                        return True
                    # If no macro is assigned to the key, open a key-capture dialog
                    # so the user can press a key on their keyboard to assign it.
                    dlg = KeyCaptureDialog(self)
                    if dlg.exec() and dlg.captured:
                        captured = dlg.captured
                        # Assign the captured keycode directly to the key
                        self.keymap_data[self.current_layer][r][c] = captured
                        # Mark profile as custom
                        if hasattr(self, 'profile_combo'):
                            self.profile_combo.setCurrentText("Custom")
                        self.update_macropad_display()
                        return True
                    return False
        return False

    def on_macro_selected(self, item):
        """Assign the clicked macro to the currently-selected key on the grid."""
        if not item:
            return
        macro_name = item.text()
        if not self.selected_key_coords:
            QMessageBox.warning(self, "No Key Selected", "Please select a key on the grid before assigning a macro.")
            return
        row, col = self.selected_key_coords
        # Assign as MACRO(name) string used in the keymap
        self.keymap_data[self.current_layer][row][col] = f"MACRO({macro_name})"
        self.update_macropad_display()
        # Persist macros file (macros themselves not changed, but we save config-less macro references aren't stored)
        # However save keymap state via save_configuration_dialog if you want to persist the keymap to disk.

    # --- Code Generation and Saving ---
    def generate_display_layout_code(self):
        """Generates display code to show keymap layout on OLED."""
        # Get current layer (layer 0) keymap
        layer = self.keymap_data[0] if self.keymap_data else []
        rows = self.rows
        cols = self.cols
        col_spacing = max(1, 128 // max(cols, 1))
        row_spacing = max(1, 64 // max(rows, 1))
        x_offset = 1
        y_offset = 8
        
        # Helper function to abbreviate key names for display
        def abbreviate_key(key_str):
            if not key_str or key_str == "KC.NO" or key_str == "KC.TRNS":
                return "---"
            
            # Handle macros
            if key_str.startswith("MACRO("):
                macro_name = key_str[6:-1]  # Extract name from MACRO(name)
                return macro_name[:6] if len(macro_name) > 6 else macro_name
            
            # Handle layer switches
            if "MO(" in key_str or "TG(" in key_str or "TO(" in key_str:
                return key_str.replace("KC.", "")[:6]
            
            # Handle key combinations (e.g., KC.LCTL(KC.C))
            if "(" in key_str:
                # Simplify combinations like LCTL(C) -> C^C
                parts = key_str.replace("KC.", "").replace("(", "+").replace(")", "")
                return parts[:6]
            
            # Standard keys - remove KC. prefix
            key = key_str.replace("KC.", "")
            
            # Common abbreviations for display
            abbreviations = {
                "LCTL": "LCtl", "RCTL": "RCtl",
                "LSFT": "LSft", "RSFT": "RSft", 
                "LALT": "LAlt", "RALT": "RAlt",
                "LGUI": "LGui", "RGUI": "RGui",
                "BSPC": "BkSp", "ENT": "Entr",
                "SPC": "Spce", "TAB": "Tab",
                "ESC": "Esc", "DEL": "Del",
                "PGUP": "PgUp", "PGDN": "PgDn",
                "HOME": "Home", "END": "End",
                "UP": "Up", "DOWN": "Down",
                "LEFT": "Left", "RGHT": "Rght",
                "VOLU": "Vol+", "VOLD": "Vol-",
                "MUTE": "Mute", "MPLY": "Play",
                "MNXT": "Next", "MPRV": "Prev",
                "MSTP": "Stop", "EJCT": "Ejct",
                "BRIU": "Bri+", "BRID": "Bri-",
            }
            
            key = abbreviations.get(key, key)
            return key[:6] if len(key) > 6 else key
        
        # Build display code
        code = '''import board
import busio
import displayio
import terminalio
import adafruit_displayio_sh1106
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

# I2C Display setup (SDA=GP20, SCL=GP21)
displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=128,
    height=64,
    rotation=180,  # Rotated 180 degrees
    colstart=2  # Column offset for proper alignment
)

# Create display group
splash = displayio.Group()
display.root_group = splash

# Keymap layout - Generated from your configuration
'''
        
        # Generate the key labels for 5x4 grid
        code += f"# {rows}x{cols} Grid Layout (Row x Col)\n"
        code += "key_labels = [\n"
        for r in range(rows - 1, -1, -1):
            row_labels = []
            for c in range(cols):
                if r < len(layer) and c < len(layer[r]):
                    key_abbr = abbreviate_key(layer[r][c])
                    row_labels.append(f'"{key_abbr}"')
                else:
                    row_labels.append('"---"')
            code += f"    [{', '.join(row_labels)}],\n"
        code += "]\n\n"
        
        # Add display rendering code (rows reversed to match physical orientation)
        code += "# Display key layout on OLED (128x64)\n"
        code += f"# {rows} rows x {cols} cols\n"
        code += f"for row_idx in range({rows}):\n"
        code += f"    for col_idx in range({cols}):\n"
        code += "        key_text = key_labels[row_idx][col_idx]\n"
        code += f"        x_pos = ({cols} - 1 - col_idx) * {col_spacing} + {x_offset}\n"
        code += f"        y_pos = row_idx * {row_spacing} + {y_offset}\n"
        code += "\n"
        code += "        text_area = label.Label(\n"
        code += "            terminalio.FONT,\n"
        code += "            text=key_text,\n"
        code += "            color=0xFFFFFF,\n"
        code += "            x=x_pos,\n"
        code += "            y=y_pos\n"
        code += "        )\n"
        code += "        splash.append(text_area)\n"
        
        return code
    
    def generate_display_layout_code_with_layer_support(self):
        """Generates display code with support for showing different layer keymaps."""
        rows = self.rows
        cols = self.cols
        col_spacing = max(1, 128 // max(cols, 1))
        header_offset = 14
        row_spacing = max(1, (64 - header_offset) // max(rows, 1))
        x_offset = 1
        y_offset = header_offset

        # Helper function to abbreviate key names for display
        def abbreviate_key(key_str):
            if not key_str or key_str == "KC.NO" or key_str == "KC.TRNS":
                return "---"
            
            # Handle macros
            if key_str.startswith("MACRO("):
                macro_name = key_str[6:-1]  # Extract name from MACRO(name)
                return macro_name[:6] if len(macro_name) > 6 else macro_name
            
            # Handle layer switches
            if "MO(" in key_str or "TG(" in key_str or "TO(" in key_str:
                return key_str.replace("KC.", "")[:6]
            
            # Handle key combinations (e.g., KC.LCTL(KC.C))
            if "(" in key_str:
                # Simplify combinations like LCTL(C) -> C^C
                parts = key_str.replace("KC.", "").replace("(", "+").replace(")", "")
                return parts[:6]
            
            # Standard keys - remove KC. prefix
            key = key_str.replace("KC.", "")
            
            # Common abbreviations for display
            abbreviations = {
                "LCTL": "LCtl", "RCTL": "RCtl",
                "LSFT": "LSft", "RSFT": "RSft", 
                "LALT": "LAlt", "RALT": "RAlt",
                "LGUI": "LGui", "RGUI": "RGui",
                "BSPC": "BkSp", "ENT": "Entr",
                "SPC": "Spce", "TAB": "Tab",
                "ESC": "Esc", "DEL": "Del",
                "PGUP": "PgUp", "PGDN": "PgDn",
                "HOME": "Home", "END": "End",
                "UP": "Up", "DOWN": "Down",
                "LEFT": "Left", "RGHT": "Rght",
                "VOLU": "Vol+", "VOLD": "Vol-",
                "MUTE": "Mute", "MPLY": "Play",
                "MNXT": "Next", "MPRV": "Prev",
                "MSTP": "Stop", "EJCT": "Ejct",
                "BRIU": "Bri+", "BRID": "Bri-",
            }
            
            key = abbreviations.get(key, key)
            return key[:6] if len(key) > 6 else key
        
        # Build display code with all layers
        code = '''import board
import busio
import displayio
import terminalio
import adafruit_displayio_sh1106
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

# I2C Display setup (SDA=GP20, SCL=GP21)
displayio.release_displays()
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=128,
    height=64,
    rotation=180,  # Rotated 180 degrees
    colstart=2  # Column offset for proper alignment
)

# Create display group
splash = displayio.Group()
display.root_group = splash

# All layer keymaps - Generated from your configuration
'''
        
        # Generate key labels for ALL layers
        code += "all_layer_labels = [\n"
        for layer_idx, layer_data in enumerate(self.keymap_data):
            code += f"    # Layer {layer_idx}\n"
            code += "    [\n"
            for r in range(rows - 1, -1, -1):
                row_labels = []
                for c in range(cols):
                    if r < len(layer_data) and c < len(layer_data[r]):
                        key_abbr = abbreviate_key(layer_data[r][c])
                        row_labels.append(f'"{key_abbr}"')
                    else:
                        row_labels.append('"---"')
                code += f"        [{', '.join(row_labels)}],\n"
            code += "    ],\n"
        code += "]\n\n"
        
        # Add display update function
        code += '''# Helper function to update display with current layer
def update_display_for_layer(layer_index):
    """Update OLED display to show keymap for the specified layer."""
    global splash
    
    # Clear existing labels
    while len(splash) > 0:
        splash.pop()
    
    # Show layer indicator at top
    layer_label = label.Label(
        terminalio.FONT,
        text=f"Layer {{layer_index}}",
        color=0xFFFFFF,
        x=2,
        y=4
    )
    splash.append(layer_label)
    
    # Get labels for this layer
    if layer_index < len(all_layer_labels):
        key_labels = all_layer_labels[layer_index]
    else:
        key_labels = all_layer_labels[0]  # Fallback to layer 0
    
    # Display key layout (top row is physical top)
    for row_idx, row in enumerate(key_labels):
        for col_idx, key_text in enumerate(row):
            x_pos = ({cols} - 1 - col_idx) * {col_spacing} + {x_offset}
            y_pos = row_idx * {row_spacing} + {y_offset}
            text_area = label.Label(
                terminalio.FONT,
                text=key_text,
                color=0xFFFFFF,
                x=x_pos,
                y=y_pos
            )
            splash.append(text_area)

# Initial display - Show Layer 0
update_display_for_layer(0)
class LayerDisplaySync:
    """Keep the OLED layer view in sync with KMK state."""

    def __init__(self):
        self._last_layer = None

    def _active_layer(self, keyboard):
        try:
            layers = getattr(keyboard, "active_layers", None)
            if layers and len(layers) > 0:
                # Return the highest priority layer (last in the list)
                return layers[-1]
        except Exception:
            pass
        return 0

    def _check_and_update(self, keyboard):
        """Check if layer changed and update display if needed."""
        current = self._active_layer(keyboard)
        if current != self._last_layer:
            self._last_layer = current
            try:
                update_display_for_layer(current)
            except Exception:
                pass

    def before_matrix_scan(self, keyboard):
        return

    def during_bootup(self, keyboard):
        self._last_layer = self._active_layer(keyboard)
        try:
            update_display_for_layer(self._last_layer)
        except Exception:
            pass

    def after_matrix_scan(self, keyboard):
        """Check for layer changes after keys are scanned."""
        self._check_and_update(keyboard)

    def before_hid_send(self, keyboard):
        return

    def after_hid_send(self, keyboard):
        """Check for layer changes after HID report is sent."""
        self._check_and_update(keyboard)

    def on_powersave_enable(self, keyboard):
        return

    def on_powersave_disable(self, keyboard):
        return

layer_display_sync = LayerDisplaySync()
keyboard.modules.append(layer_display_sync)
'''.format(col_spacing=col_spacing, x_offset=x_offset, row_spacing=row_spacing, y_offset=y_offset, cols=cols)
        
        return code

    
    def _generate_rgb_matrix_code(self):
        """Build the Peg RGB Matrix configuration snippet for code.py."""
        if not self.enable_rgb:
            return ""

        cfg = build_default_rgb_matrix_config()
        cfg.update(self.rgb_matrix_config)
        cfg['default_key_color'] = ensure_hex_prefix(cfg.get('default_key_color', '#FFFFFF'), '#FFFFFF')
        cfg['default_underglow_color'] = ensure_hex_prefix(
            cfg.get('default_underglow_color', '#000000'), '#000000'
        )

        num_keys = self.rows * self.cols
        underglow_count = int(cfg.get('num_underglow', 0) or 0)
        total_pixels = num_keys + max(0, underglow_count)

        key_map = cfg.get('key_colors', {}) or {}
        default_key_rgb = hex_to_rgb_list(cfg['default_key_color'])

        key_entries = []
        for idx in range(num_keys):
            custom = key_map.get(str(idx))
            if custom:
                rgb = hex_to_rgb_list(custom)
            else:
                row = idx // self.cols
                col = idx % self.cols
                keycode = DEFAULT_KEY
                if self.keymap_data and self.keymap_data[0]:
                    try:
                        keycode = self.keymap_data[0][row][col]
                    except (IndexError, TypeError):
                        keycode = DEFAULT_KEY
                rgb = [0, 0, 0] if keycode == "KC.NO" else default_key_rgb
            key_entries.append(f"[{rgb[0]}, {rgb[1]}, {rgb[2]}]")

        under_map = cfg.get('underglow_colors', {}) or {}
        default_under_rgb = hex_to_rgb_list(cfg['default_underglow_color'])
        under_entries = []
        for idx in range(max(0, underglow_count)):
            custom = under_map.get(str(idx))
            rgb = hex_to_rgb_list(custom) if custom else default_under_rgb
            under_entries.append(f"[{rgb[0]}, {rgb[1]}, {rgb[2]}]")

        def format_entries(entries):
            if not entries:
                return "[]"
            chunks = []
            for start in range(0, len(entries), 8):
                chunk = ", ".join(entries[start:start+8])
                chunks.append(f"                {chunk}")
            return "[\n" + ",\n".join(chunks) + "\n            ]"

        keys_array = format_entries(key_entries)
        under_array = format_entries(under_entries)

        rgb_order = cfg.get('rgb_order', 'GRB')
        order_tuple = RGB_ORDER_TUPLES.get(rgb_order, RGB_ORDER_TUPLES['GRB'])
        disable_auto_write_value = cfg.get('disable_auto_write', True)
        if isinstance(disable_auto_write_value, str):
            disable_auto_write = disable_auto_write_value.strip().lower() not in {"false", "0", "no", "off"}
        else:
            disable_auto_write = bool(disable_auto_write_value)
        brightness = float(cfg.get('brightness_limit', 0.5) or 0.5)
        pixel_pin = cfg.get('pixel_pin', FIXED_RGB_PIN)
        if isinstance(pixel_pin, str):
            pixel_pin = pixel_pin.strip()
            if (pixel_pin.startswith("'") and pixel_pin.endswith("'")) or (
                pixel_pin.startswith('"') and pixel_pin.endswith('"')
            ):
                pixel_pin = pixel_pin[1:-1]
        if not pixel_pin:
            pixel_pin = FIXED_RGB_PIN

        code_lines = [
            "# Peg RGB Matrix configuration",
            f"keyboard.rgb_pixel_pin = {pixel_pin}",
            f"keyboard.num_pixels = {total_pixels}",
            f"keyboard.brightness_limit = {brightness}",
            f"keyboard.led_key_pos = list(range({total_pixels}))  # Keys + underglow indices",
            "rgb = Rgb_matrix(",
        ]

        if underglow_count > 0:
            code_lines.extend([
                "    ledDisplay=Rgb_matrix_data(",
                "        keys=" + keys_array + ",",
                "        underglow=" + under_array,
                "    ),",
            ])
        else:
            code_lines.append("    ledDisplay=" + keys_array + ",")

        code_lines.extend([
            f"    rgb_order={order_tuple},",
            f"    disable_auto_write={disable_auto_write},",
            ")",
            "keyboard.extensions.append(rgb)\n",
        ])

        return "\n".join(code_lines)
    
    def get_generated_python_code(self):
        """Constructs the final `code.py` file content as a string."""
        macros_exist = bool(self.macros)
        
        # --- Macro Definitions ---
        macros_def_str = ""
        if macros_exist:
            macros_def_str += "# --- Macro Definitions ---\n"
            for name, sequence in self.macros.items():
                sequence_str = []
                for action_type, value in sequence:
                    if action_type == 'text':
                        escaped_value = value.replace('"', '\\"')
                        sequence_str.append(f'"{escaped_value}"')
                    elif action_type in ('tap', 'press', 'release'):
                         sequence_str.append(f'{action_type.title()}({value})')
                    elif action_type == 'delay':
                        sequence_str.append(f"Delay({value})")
                macros_def_str += f'{name} = KC.MACRO({", ".join(sequence_str)})\n'
            macros_def_str += "\n"

        # --- Keymap Definition ---
        keymap_str = "keyboard.keymap = [\n"
        for i, layer in enumerate(self.keymap_data):
            keymap_str += f"    # Layer {i}\n    [\n"
            # Flatten the keymap - KMK expects a flat list, not nested rows
            flat_keys = []
            for row in layer:
                for key in row:
                    macro_match = re.match(r"MACRO\((\w+)\)", key)
                    if macro_match:
                        flat_keys.append(macro_match.group(1)) # Use the macro variable name
                    else:
                        flat_keys.append(key) # This is a regular keycode or combo
            # Write flat keymap with 4 keys per line for readability (matches 4 columns)
            for idx in range(0, len(flat_keys), 4):
                line_keys = flat_keys[idx:idx+4]
                keymap_str += "        " + ", ".join(line_keys) + ",\n"
            keymap_str += "    ],\n"
        keymap_str += "]\n"

        # --- Python File Template ---
        diode_orientation = self.diode_orientation
        
        imports = [
            "import board",
            "from kmk.kmk_keyboard import KMKKeyboard",
            "from kmk.keys import KC",
            "from kmk.scanners import DiodeOrientation",
            "from kmk.modules.layers import Layers",
            "from kmk.extensions.media_keys import MediaKeys",
        ]
        if macros_exist:
            imports.append("from kmk.modules.macros import Macros, Tap, Press, Release, Delay")
        # Optional extension imports
        if self.enable_encoder:
            imports.append("from kmk.modules.encoder import EncoderHandler")
        if self.enable_analogin:
            imports.append("from kmk.modules.analogin import AnalogInputs, AnalogInput")
        # RGB import will be wrapped in try-except in the code body since it requires neopixel

        # Build extension snippets provided by the user
        ext_snippets = ""
        encoder_needs_layer_cycler = False
        if self.enable_encoder and self.encoder_config_str:
            ext_snippets += "# Encoder configuration:\n"
            ext_snippets += self.encoder_config_str + "\n\n"
            # Check if layer cycler class is defined in the encoder config
            if "class LayerCycler:" in self.encoder_config_str:
                encoder_needs_layer_cycler = True
        if self.enable_analogin and self.analogin_config_str:
            ext_snippets += "# AnalogIn configuration provided by user:\n"
            ext_snippets += self.analogin_config_str + "\n\n"
        if self.enable_display:
            # Auto-generate display layout showing keymap
            # Use layer-aware version if encoder with layer cycling is enabled
            if self.enable_encoder and "LayerCycler" in self.encoder_config_str:
                ext_snippets += "# Display configuration - Layer-aware keymap layout:\n"
                ext_snippets += self.generate_display_layout_code_with_layer_support() + "\n\n"
            else:
                ext_snippets += "# Display configuration - Auto-generated keymap layout:\n"
                ext_snippets += self.generate_display_layout_code() + "\n\n"
        
        # Provide sensible default templates for enabled modules (placed before user snippets)
        # Only add defaults if user hasn't provided their own config
        default_snippets = ""
        if self.enable_encoder and not self.encoder_config_str:
            default_snippets += "# --- Encoder Handler (auto-generated) ---\n"
            default_snippets += (
                "encoder_handler = EncoderHandler()\n"
                "# Configure pins and map for your hardware. Examples:\n"
                "# encoder_handler.pins = ((board.GP17, board.GP15, board.GP14),)\n"
                "# encoder_handler.map = [ ((KC.VOLD, KC.VOLU, KC.MUTE),), ]\n"
                "keyboard.modules.append(encoder_handler)\n\n"
            )
        if self.enable_analogin and not self.analogin_config_str:
            default_snippets += "# --- Analog Inputs (auto-generated) ---\n"
            default_snippets += (
                "# Example usage (requires 'analogio' on target device):\n"
                "# from analogio import AnalogIn\n"
                "# a0 = AnalogInput(AnalogIn(board.A0))\n"
                "# analog = AnalogInputs([a0], [[AnalogKey(KC.X)]])\n"
                "# keyboard.modules.append(analog)\n\n"
            )
        # RGB will be initialized AFTER keymap definition
        rgb_init_code = ""
        if self.enable_rgb:
            imports.append("from kmk.extensions.peg_rgb_matrix import Rgb_matrix, Rgb_matrix_data")
            rgb_init_code = self._generate_rgb_matrix_code()

        # Final extension snippets: defaults first, then user-provided overrides/additions
        ext_snippets_final = default_snippets + ext_snippets
        code_template = f"""# Generated by KMK Configurator
{chr(10).join(imports)}

keyboard = KMKKeyboard()

# --- Extensions ---
keyboard.extensions.append(MediaKeys())

# --- Modules ---
keyboard.modules.append(Layers())
"""
        if macros_exist:
            code_template += "keyboard.modules.append(Macros())\n"

        code_template += f"""
# --- Hardware Settings ---
keyboard.diode_orientation = DiodeOrientation.{diode_orientation}
keyboard.col_pins = ({', '.join(self.col_pins)},)
keyboard.row_pins = ({', '.join(self.row_pins)},)

{ext_snippets_final}{macros_def_str}# --- Keymap ---
{keymap_str}
{rgb_init_code}"""
        # Add layer cycler initialization if encoder needs it
        if encoder_needs_layer_cycler:
            code_template += """# Initialize layer cycler for encoder (after keymap is defined)
layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))

"""
        
        code_template += """if __name__ == '__main__':
    keyboard.go()
"""
        return code_template.strip()

    def find_circuitpy_drive(self):
        """Attempts to find a drive named CIRCUITPY on common mount points."""
        if sys.platform == "win32":
            import string
            # Check drives D: through Z:
            for letter in string.ascii_uppercase[3:]:
                path = f"{letter}:\\"
                if os.path.exists(os.path.join(path, "boot_out.txt")):
                    return path
        elif sys.platform == "darwin": # macOS
            path = "/Volumes/CIRCUITPY"
            if os.path.exists(path):
                return path
        else:  # Linux
            username = os.getlogin()
            for base_path in [f"/media/{username}", f"/run/media/{username}"]:
                path = os.path.join(base_path, "CIRCUITPY")
                if os.path.exists(path):
                    return path
        return os.getcwd() # Fallback to current directory

    def generate_code_py_dialog(self):
        default_path = self.find_circuitpy_drive()
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Save code.py",
            default_path
        )

        if folder_path:
            file_path = os.path.join(folder_path, "code.py")
            py_code_str = self.get_generated_python_code()

            try:
                # Save code.py
                with open(file_path, 'w') as f:
                    f.write(py_code_str)
                
                # Check if kmk folder exists, if not copy it
                kmk_dest = os.path.join(folder_path, "kmk")
                if not os.path.exists(kmk_dest):
                    kmk_source = os.path.join(os.path.dirname(__file__), "libraries", "kmk_firmware-main", "kmk")
                    if os.path.exists(kmk_source):
                        import shutil
                        shutil.copytree(kmk_source, kmk_dest)
                        kmk_copied = True
                    else:
                        QMessageBox.warning(self, "Warning", 
                            f"KMK firmware source not found at:\n{kmk_source}\n\n"
                            f"Please run the application to auto-download dependencies or manually copy the kmk folder to {folder_path}")
                        kmk_copied = False
                else:
                    kmk_copied = False
                
                # Copy required libraries
                lib_source = os.path.join(os.path.dirname(__file__), "libraries", 
                                         "adafruit-circuitpython-bundle-9.x-mpy", "lib")
                lib_dest = os.path.join(folder_path, "lib")
                
                # Create lib folder if it doesn't exist
                os.makedirs(lib_dest, exist_ok=True)
                
                # Required libraries list
                required_libs = [
                    "adafruit_displayio_sh1106.mpy",
                    "adafruit_display_text",  # folder
                    "neopixel.mpy"
                ]
                
                copied_files = []
                for lib_name in required_libs:
                    src = os.path.join(lib_source, lib_name)
                    dst = os.path.join(lib_dest, lib_name)
                    
                    if os.path.exists(src):
                        if os.path.isdir(src):
                            # Copy directory
                            if os.path.exists(dst):
                                import shutil
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                            copied_files.append(f"{lib_name}/ (folder)")
                        else:
                            # Copy file
                            import shutil
                            shutil.copy2(src, dst)
                            copied_files.append(lib_name)
                
                msg = f"code.py saved successfully to:\n{file_path}\n\n"
                if kmk_copied:
                    msg += f"✓ KMK firmware copied to {kmk_dest}\n\n"
                msg += f"Libraries copied to {lib_dest}:\n" + "\n".join(f"  • {f}" for f in copied_files)
                QMessageBox.information(self, "Success", msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save code.py file:\n{e}")

    def save_configuration_dialog(self):
        save_dir = "kmk_Config_Save"
        os.makedirs(save_dir, exist_ok=True)
        
        # Set the initial directory to kmk_Config_Save
        initial_path = os.path.join(save_dir, "config.json")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration As",
            initial_path,
            "JSON Files (*.json)"
        )

        if file_path:
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            try:
                self.save_configuration_to_path(file_path)
                QMessageBox.information(self, "Success", f"Configuration saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}\n\nTraceback:\n{traceback.format_exc()}")
        else:
            # User cancelled the dialog
            print("Save cancelled by user")

    def save_configuration_to_path(self, file_path):
        """Save complete configuration including all layers, RGB colors, macros, and extension settings"""
        config_data = {
            "version": "2.0",  # New version format
            "hardware": {
                "rows": self.rows,
                "cols": self.cols,
                "col_pins": self.col_pins,
                "row_pins": self.row_pins,
                "diode_orientation": self.diode_orientation,
            },
            "keymap": {
                "layers": self.keymap_data,
                "current_layer": self.current_layer,
            },
            "macros": self.macros,
            "rgb": {
                "enabled": self.enable_rgb,
                "matrix": {
                    **build_default_rgb_matrix_config(),
                    **self.rgb_matrix_config,
                    "key_colors": dict(self.rgb_matrix_config.get("key_colors", {})),
                    "underglow_colors": dict(self.rgb_matrix_config.get("underglow_colors", {})),
                },
            },
            "extensions": {
                "encoder": {
                    "enabled": self.enable_encoder,
                    "config_str": self.encoder_config_str,
                },
                "analogin": {
                    "enabled": self.enable_analogin,
                    "config_str": self.analogin_config_str,
                },
                "display": {
                    "enabled": self.enable_display,
                    "config_str": self.display_config_str,
                },
            },
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save configuration file:\n{e}")
            raise e

    def load_configuration(self, file_path=None, show_message=True):
        """Load a saved configuration from disk."""
        selected_path = file_path

        if not selected_path:
            # If a file is selected in the config combo, use that; otherwise open a file dialog
            if hasattr(self, 'config_file_combo') and self.config_file_combo.count() > 0:
                sel = self.config_file_combo.currentText()
                if sel:
                    candidate = os.path.join(os.getcwd(), sel)
                    if os.path.exists(candidate):
                        selected_path = candidate

        if not selected_path:
            selected_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
            if not selected_path:
                return False

        try:
            with open(selected_path, 'r') as f:
                config_data = json.load(f)

            # Check version format
            version = config_data.get("version", "1.0")
            
            if version == "2.0":
                # New format with complete configuration
                
                # Load keymap
                keymap_section = config_data.get("keymap", {})
                self.keymap_data = keymap_section.get("layers", [])
                current_layer = keymap_section.get("current_layer", 0)
                
                # Load macros
                self.macros = config_data.get("macros", {})
                
                # Load RGB settings
                rgb_section = config_data.get("rgb", {})
                self.enable_rgb = rgb_section.get("enabled", True)
                matrix_cfg = rgb_section.get("matrix", {}) if isinstance(rgb_section, dict) else {}
                merged = build_default_rgb_matrix_config()
                merged.update(matrix_cfg)
                merged['key_colors'] = dict(matrix_cfg.get('key_colors', {}))
                merged['underglow_colors'] = dict(matrix_cfg.get('underglow_colors', {}))
                merged['default_key_color'] = ensure_hex_prefix(
                    merged.get('default_key_color', '#FFFFFF'), '#FFFFFF'
                )
                merged['default_underglow_color'] = ensure_hex_prefix(
                    merged.get('default_underglow_color', '#000000'), '#000000'
                )
                self.rgb_matrix_config = merged
                
                # Load extension settings
                extensions = config_data.get("extensions", {})
                
                encoder_section = extensions.get("encoder", {})
                self.enable_encoder = encoder_section.get("enabled", True)
                self.encoder_config_str = encoder_section.get("config_str", DEFAULT_ENCODER_CONFIG)
                
                analogin_section = extensions.get("analogin", {})
                self.enable_analogin = analogin_section.get("enabled", True)
                self.analogin_config_str = analogin_section.get("config_str", DEFAULT_ANALOGIN_CONFIG)
                
                display_section = extensions.get("display", {})
                self.enable_display = display_section.get("enabled", True)
                self.display_config_str = display_section.get("config_str", "")
                
            else:
                # Old format (v1.0) - backward compatibility
                self.keymap_data = config_data.get("keymap_data", [])
                # Old format doesn't have macros, RGB colors, or extension configs
            
            # Validate and adapt keymap to match fixed grid size (5x4)
            if not self.keymap_data:
                self.initialize_keymap_data()
            else:
                # Check and adapt each layer to match the fixed 5x4 grid
                adapted_layers = []
                for layer_idx, layer in enumerate(self.keymap_data):
                    # Create a new 5x4 layer
                    new_layer = []
                    for r in range(FIXED_ROWS):
                        new_row = []
                        for c in range(FIXED_COLS):
                            # Copy data if it exists in the old layer, otherwise use KC.NO
                            if r < len(layer) and c < len(layer[r]):
                                new_row.append(layer[r][c])
                            else:
                                new_row.append("KC.NO")
                        new_layer.append(new_row)
                    adapted_layers.append(new_layer)
                
                self.keymap_data = adapted_layers
            
            # Set current layer (with validation)
            if version == "2.0":
                self.current_layer = min(current_layer, len(self.keymap_data) - 1)
            else:
                self.current_layer = 0
            
            self.profile_combo.setCurrentText("Custom")

            # Refresh UI - order matters!
            self.update_layer_tabs()  # First update tabs to match layer count
            self.layer_tabs.setCurrentIndex(self.current_layer)  # Then select the correct tab
            self.recreate_macropad_grid()
            self.update_macro_list()
            self.update_macropad_display()
            self.sync_extension_checkboxes()
            self.update_extension_button_states()
            try:
                self.save_extension_configs()
            except Exception:
                pass

            if show_message:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Configuration loaded successfully.\n"
                    f"Path: {selected_path}\n"
                    f"Format: v{version}\n"
                    f"Layers: {len(self.keymap_data)}\n"
                    f"Macros: {len(self.macros)}\n"
                    f"Configured key LEDs: {len(self.rgb_matrix_config.get('key_colors', {}))}\n"
                    f"Underglow LEDs: {self.rgb_matrix_config.get('num_underglow', 0)}",
                )

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load configuration:\n{e}\n\nTraceback: {traceback.format_exc()}")
            return False
    
    # --- Grid and Layer UI Management ---
    
    def _create_new_layer(self):
        """Helper to create a blank layer with default keys."""
        return [[DEFAULT_KEY for _ in range(self.cols)] for _ in range(self.rows)]

    def initialize_keymap_data(self):
        """Initializes the keymap with a single default layer."""
        self.keymap_data = [self._create_new_layer()]

    def clear_macropad_grid(self):
        """Removes all widgets from the macropad grid layout."""
        while self.macropad_layout.count():
            item = self.macropad_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.macropad_buttons.clear()
        # Do not forcibly clear the selected_key_coords here so that
        # recreate_macropad_grid can restore the selected button if it
        # still exists in the new grid.

    def recreate_macropad_grid(self):
        """Clears and rebuilds the macropad grid buttons based on current dimensions."""
        self.clear_macropad_grid()
        # Iterate in reverse (180° rotation) to match physical board orientation
        for r in range(self.rows - 1, -1, -1):
            for c in range(self.cols - 1, -1, -1):
                button = QPushButton()
                button.setObjectName("keymapButton")
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.setCheckable(True)
                button.clicked.connect(partial(self.on_key_selected, r, c))
                # allow double-click detection via the main window's eventFilter
                button.installEventFilter(self)
                try:
                    self._install_hover_effect(button)
                except Exception:
                    pass
                # Display at inverted position while keeping actual keymap coordinates
                display_r = self.rows - 1 - r
                display_c = self.cols - 1 - c
                self.macropad_layout.addWidget(button, display_r, display_c)
                self.macropad_buttons[(r, c)] = button
        # If we have a previously-selected key and it still exists in the
        # newly-created grid, restore its checked state and label so the
        # user sees it highlighted.
        if self.selected_key_coords:
            r_sel, c_sel = self.selected_key_coords
            if (r_sel, c_sel) in self.macropad_buttons and 0 <= r_sel < self.rows and 0 <= c_sel < self.cols:
                btn = self.macropad_buttons[(r_sel, c_sel)]
                btn.setChecked(True)
                if hasattr(self, 'selected_key_label'):
                    self.selected_key_label.setText(f"Selected Key: ({r_sel}, {c_sel})")
            else:
                # Selection no longer valid for the new grid
                self.selected_key_coords = None
                if hasattr(self, 'selected_key_label'):
                    self.selected_key_label.setText("Selected Key: None")

        self.update_macropad_display()

    def update_grid_dimensions(self, force_update=False):
        """Grid dimensions are fixed - this method is kept for compatibility."""
        pass

    def add_layer(self):
        """Adds a new, blank layer to the keymap."""
        self.keymap_data.append(self._create_new_layer())
        self.update_layer_tabs()
        self.layer_tabs.setCurrentIndex(len(self.keymap_data) - 1)

    def remove_layer(self):
        """Removes the currently selected layer, if it's not the last one."""
        if len(self.keymap_data) <= 1:
            QMessageBox.warning(self, "Cannot Remove", "You must have at least one layer.")
            return

        current_index = self.layer_tabs.currentIndex()
        reply = QMessageBox.question(self, "Remove Layer", f"Are you sure you want to remove Layer {current_index}?")

        if reply == QMessageBox.StandardButton.Yes:
            del self.keymap_data[current_index]
            self.update_layer_tabs()
    
    def on_layer_changed(self, index):
        """Handles switching between layer tabs."""
        if index != -1:
            self.current_layer = index
            self.selected_key_coords = None 
            self.selected_key_label.setText("Selected Key: None")
            for button in self.macropad_buttons.values():
                button.setChecked(False)
            self.update_macropad_display()

    def update_layer_tabs(self):
        """Clears and rebuilds the layer tabs from the keymap data."""
        self.layer_tabs.blockSignals(True)
        current_index = self.layer_tabs.currentIndex()
        self.layer_tabs.clear()
        for i in range(len(self.keymap_data)):
            self.layer_tabs.addTab(QWidget(), f"Layer {i}")
        
        if current_index < self.layer_tabs.count():
             self.layer_tabs.setCurrentIndex(current_index)
        
        self.layer_tabs.blockSignals(False)
        # Add an empty widget to the last tab to ensure it's rendered correctly
        if self.layer_tabs.count() > 0:
            self.layer_tabs.widget(self.layer_tabs.count() - 1).setLayout(QVBoxLayout())

    def on_key_selected(self, row, col):
        """Handles the logic for selecting and deselecting a key on the grid."""
        clicked_coords = (row, col)
        
        # Uncheck the previously selected button if it's different
        if self.selected_key_coords and self.selected_key_coords != clicked_coords:
            prev_button = self.macropad_buttons.get(self.selected_key_coords)
            if prev_button:
                prev_button.setChecked(False)

        # If clicking the same key again, deselect it
        if self.selected_key_coords == clicked_coords:
            self.selected_key_coords = None
            self.selected_key_label.setText("Selected Key: None")
            # The button's check state is toggled automatically by PyQt
        else: # Otherwise, select the new key
            self.selected_key_coords = clicked_coords
            self.selected_key_label.setText(f"Selected Key: ({row}, {col})")
            current_button = self.macropad_buttons.get(clicked_coords)
            if current_button:
                current_button.setChecked(True)

    def update_macropad_display(self):
        """Updates the text on all grid buttons to reflect the current layer's keymap."""
        if self.current_layer >= len(self.keymap_data): return
        
        layer_data = self.keymap_data[self.current_layer]
        rgb_cfg = getattr(self, 'rgb_matrix_config', build_default_rgb_matrix_config())
        key_colors = rgb_cfg.get('key_colors', {})
        
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                button = self.macropad_buttons.get((r, c))
                if button:
                    key_text = layer_data[r][c]
                    # Format macro keys for better readability
                    macro_match = re.match(r"MACRO\((\w+)\)", key_text)
                    if macro_match:
                        display_text = f"M({macro_match.group(1)})"
                    else:
                        # Shorten standard keycodes for display
                        display_text = key_text.replace("KC.", "")
                    button.setText(display_text)
                    
                    # Apply RGB color if assigned to this key
                    if str(idx) in key_colors:
                        color = key_colors[str(idx)]
                        # Use white text for dark colors, black text for light colors
                        # Simple luminance check
                        try:
                            # Remove # and convert to RGB
                            rgb = color.lstrip('#')
                            r_val = int(rgb[0:2], 16)
                            g_val = int(rgb[2:4], 16)
                            b_val = int(rgb[4:6], 16)
                            # Calculate perceived luminance
                            luminance = (0.299 * r_val + 0.587 * g_val + 0.114 * b_val)
                            text_color = '#000000' if luminance > 128 else '#FFFFFF'
                        except:
                            text_color = '#FFFFFF'
                        
                        button.setStyleSheet(f'background-color: {color}; color: {text_color}; font-weight: bold;')
                    else:
                        # Clear any previous color styling but keep the default button style
                        button.setStyleSheet('')
                idx += 1
        self.macropad_group.setTitle(f"Keymap (Layer {self.current_layer})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMKConfigurator()
    window.show()
    sys.exit(app.exec())


