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

from __future__ import annotations

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
    QFormLayout, QDoubleSpinBox, QProgressDialog, QScrollArea, QFrame, QSplitter,
    QListWidgetItem, QMenu, QStyledItemDelegate, QStyle
)
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QObject, QThread, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from functools import partial

# --- Path Resolution for PyInstaller ---
def get_application_path():
    """Get the directory where the application is running from.
    Works correctly whether running as script or frozen exe."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

# Set base directory for all file operations
BASE_DIR = get_application_path()

# Folder structure - all at root level for simplicity
LIBRARIES_DIR = os.path.join(BASE_DIR, "libraries")
CONFIG_SAVE_DIR = os.path.join(BASE_DIR, "kmk_Config_Save")

# Create folders if they don't exist
os.makedirs(LIBRARIES_DIR, exist_ok=True)
os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)

# --- Default Values ---
DEFAULT_KEY = "KC.NO"

# Configuration files - all at root level
PROFILE_FILE = os.path.join(BASE_DIR, "profiles.json")
MACRO_FILE = os.path.join(BASE_DIR, "macros.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# --- Dependency URLs ---
KMK_FIRMWARE_URL = "https://github.com/KMKfw/kmk_firmware/archive/refs/heads/main.zip"
# CircuitPython bundle URLs - version selected by user on first startup
CIRCUITPYTHON_BUNDLE_9X = "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/{date}/adafruit-circuitpython-bundle-9.x-mpy-{date}.zip"
CIRCUITPYTHON_BUNDLE_10X = "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/{date}/adafruit-circuitpython-bundle-10.x-mpy-{date}.zip"

class DependencyDownloader(QThread):
    """Downloads KMK firmware and CircuitPython libraries automatically
    
    Args:
        cp_version: CircuitPython version to download (fixed at 10.x)
    """
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(bool)  # success
    
    def __init__(self, cp_version=10):
        super().__init__()
        # Use organized libraries folder
        self.libraries_dir = LIBRARIES_DIR
        self.cp_version = cp_version  # Fixed to CircuitPython 10.x (required version)
        
    def run(self):
        """Download all required dependencies"""
        try:
            os.makedirs(self.libraries_dir, exist_ok=True)
            
            # Check if already downloaded
            kmk_path = os.path.join(self.libraries_dir, "kmk_firmware-main")
            bundle_path = os.path.join(self.libraries_dir, f"adafruit-circuitpython-bundle-{self.cp_version}.x-mpy")
            
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
        """Download and extract CircuitPython bundle for selected version"""
        # Select URL based on version
        if self.cp_version == 10:
            url_template = CIRCUITPYTHON_BUNDLE_10X
        else:
            url_template = CIRCUITPYTHON_BUNDLE_9X
        
        # Get latest bundle URL (try a few recent dates)
        import datetime
        today = datetime.date.today()
        
        for days_back in range(7):  # Try last 7 days
            date = (today - datetime.timedelta(days=days_back)).strftime("%Y%m%d")
            url = url_template.format(date=date)
            
            try:
                zip_path = os.path.join(self.libraries_dir, "circuitpython_bundle.zip")
                urllib.request.urlretrieve(url, zip_path)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.libraries_dir)
                
                # Rename to consistent name (version-specific)
                extracted_dirs = [d for d in os.listdir(self.libraries_dir) 
                                if d.startswith(f"adafruit-circuitpython-bundle-{self.cp_version}.x-mpy-")]
                if extracted_dirs:
                    old_path = os.path.join(self.libraries_dir, extracted_dirs[0])
                    new_path = os.path.join(self.libraries_dir, f"adafruit-circuitpython-bundle-{self.cp_version}.x-mpy")
                    if os.path.exists(new_path):
                        shutil.rmtree(new_path)
                    os.rename(old_path, new_path)
                
                # Clean up
                os.remove(zip_path)
                break
                
            except Exception:
                continue
        else:
            raise Exception(f"Could not download CircuitPython {self.cp_version}.x bundle from recent dates")

# --- Settings Management ---
def load_settings():
    """Load application settings from settings.json
    
    Returns:
        dict: Settings dictionary with keys like 'cp_version'
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(settings):
    """Save application settings to settings.json
    
    Args:
        settings: Dictionary of settings to save
    """
    try:
        # SETTINGS_FILE is at BASE_DIR, no subfolder needed
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save settings: {e}")

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


# Chronos Pad physical LED order (per-key indices -> NeoPixel index)
# Layout mirrored across both axes (top to bottom):
#  0  1  2  3
#  7  6  5  4
#  8  9 10 11
# 15 14 13 12
# 16 17 18 19
KEY_PIXEL_ORDER = [
    0, 1, 2, 3,
    7, 6, 5, 4,
    8, 9, 10, 11,
    15, 14, 13, 12,
    16, 17, 18, 19,
]


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
        "layer_key_colors": {},
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
DEFAULT_ENCODER_CONFIG = '''import board
from kmk.modules.encoder import EncoderHandler

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
encoder_handler.divisor = 4
encoder_handler.pins = ((board.GP10, board.GP11, board.GP14),)  # (a, b, button)
encoder_handler.map = [((KC.LAYER_PREV, KC.LAYER_NEXT, KC.LAYER_RESET),)]  # CCW=prev, CW=next, Press=reset to layer 0
keyboard.modules.append(encoder_handler)

# Initialize layer cycler after keyboard is set up (do this after keymap is defined)
# Add this line after keyboard.keymap = [...] in your main code:
# layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))'''

DEFAULT_ANALOGIN_CONFIG = '''import board
from analogio import AnalogIn as AnalogInPin
from kmk.keys import KC
from kmk.extensions.media_keys import MediaKeys
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
        return

    def after_matrix_scan(self, keyboard):
        """Check slider position after each matrix scan"""
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

            # Press and release the key with proper HID send
            tap_keycode = KC.VOLU if delta > 0 else KC.VOLD
            for _ in range(self.step_size):
                # Tap the key properly - add it, send HID, remove it, send HID again
                self.keyboard.add_key(tap_keycode)
                self.keyboard._send_hid()
                self.keyboard.remove_key(tap_keycode)
                self.keyboard._send_hid()

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


# Ensure media keys extension is loaded for volume control
if not any(isinstance(ext, MediaKeys) for ext in keyboard.extensions):
    keyboard.extensions.append(MediaKeys())

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
    "Letters": [
        "KC.A", "KC.B", "KC.C", "KC.D", "KC.E", "KC.F", "KC.G", "KC.H", "KC.I",
        "KC.J", "KC.K", "KC.L", "KC.M", "KC.N", "KC.O", "KC.P", "KC.Q", "KC.R",
        "KC.S", "KC.T", "KC.U", "KC.V", "KC.W", "KC.X", "KC.Y", "KC.Z"
    ],
    "Numbers & Symbols": [
        "KC.N1", "KC.N2", "KC.N3", "KC.N4", "KC.N5", "KC.N6", "KC.N7", "KC.N8",
        "KC.N9", "KC.N0", 
        "KC.MINS", "KC.EQL", "KC.LBRC", "KC.RBRC", "KC.BSLS", "KC.SCLN",
        "KC.QUOT", "KC.GRV", "KC.COMM", "KC.DOT", "KC.SLSH"
    ],
    "Editing": [
        "KC.ENT", "KC.ESC", "KC.BSPC", "KC.TAB", "KC.SPC", "KC.DEL", "KC.INS",
        "KC.CAPS", "KC.PSCR", "KC.SLCK", "KC.PAUS", "KC.APP"
    ],
    "Modifiers": [
        "KC.LCTL", "KC.LSFT", "KC.LALT", "KC.LGUI",
        "KC.RCTL", "KC.RSFT", "KC.RALT", "KC.RGUI"
    ],
    "Navigation": [
        "KC.UP", "KC.DOWN", "KC.LEFT", "KC.RGHT",
        "KC.HOME", "KC.END", "KC.PGUP", "KC.PGDN"
    ],
    "Function Keys": [
        "KC.F1", "KC.F2", "KC.F3", "KC.F4", "KC.F5", "KC.F6",
        "KC.F7", "KC.F8", "KC.F9", "KC.F10", "KC.F11", "KC.F12",
        "KC.F13", "KC.F14", "KC.F15", "KC.F16", "KC.F17", "KC.F18",
        "KC.F19", "KC.F20", "KC.F21", "KC.F22", "KC.F23", "KC.F24"
    ],
    "Media & Volume": [
        "KC.MUTE", "KC.VOLU", "KC.VOLD",
        "KC.MNXT", "KC.MPRV", "KC.MSTP", "KC.MPLY", 
        "KC.MFFD", "KC.MRWD", "KC.EJCT"
    ],
    "Brightness": [
        "KC.BRIU", "KC.BRID"
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
        "KC.MW_UP", "KC.MW_DOWN", 
        "KC.MB_L", "KC.MB_R", "KC.MB_M"
    ],
    "Layer Switching": [
        "KC.MO(1)", "KC.MO(2)", "KC.MO(3)", "KC.MO(4)", "KC.MO(5)",
        "KC.TO(0)", "KC.TO(1)", "KC.TO(2)", "KC.TO(3)", "KC.TO(4)", "KC.TO(5)",
        "KC.TG(1)", "KC.TG(2)", "KC.TG(3)", "KC.TG(4)", "KC.TG(5)",
        "KC.DF(0)", "KC.DF(1)", "KC.DF(2)", "KC.DF(3)", "KC.DF(4)", "KC.DF(5)"
    ],
    "Special": [
        "KC.NO", "KC.TRNS", "KC.RESET"
    ]
}

# Keycode display labels - shows actual symbol or descriptive name
# Format: "keycode": "label"
KEYCODE_LABELS = {
    # Letters - show the actual letter
    "KC.A": "A", "KC.B": "B", "KC.C": "C", "KC.D": "D", "KC.E": "E",
    "KC.F": "F", "KC.G": "G", "KC.H": "H", "KC.I": "I", "KC.J": "J",
    "KC.K": "K", "KC.L": "L", "KC.M": "M", "KC.N": "N", "KC.O": "O",
    "KC.P": "P", "KC.Q": "Q", "KC.R": "R", "KC.S": "S", "KC.T": "T",
    "KC.U": "U", "KC.V": "V", "KC.W": "W", "KC.X": "X", "KC.Y": "Y", "KC.Z": "Z",
    
    # Numbers - show the actual number
    "KC.N1": "1", "KC.N2": "2", "KC.N3": "3", "KC.N4": "4", "KC.N5": "5",
    "KC.N6": "6", "KC.N7": "7", "KC.N8": "8", "KC.N9": "9", "KC.N0": "0",
    
    # Symbols - show the actual symbol
    "KC.MINS": "-", "KC.EQL": "=", "KC.LBRC": "[", "KC.RBRC": "]",
    "KC.BSLS": "\\", "KC.SCLN": ";", "KC.QUOT": "'", "KC.GRV": "`",
    "KC.COMM": ",", "KC.DOT": ".", "KC.SLSH": "/",
    
    # Editing keys
    "KC.ENT": "↵ Enter", "KC.ESC": "Esc", "KC.BSPC": "⌫ Backspace",
    "KC.TAB": "⇥ Tab", "KC.SPC": "Space", "KC.DEL": "Del", "KC.INS": "Insert",
    "KC.CAPS": "Caps Lock", "KC.PSCR": "Print Scrn", "KC.SLCK": "Scroll Lock",
    "KC.PAUS": "Pause", "KC.APP": "Menu",
    
    # Modifiers
    "KC.LCTL": "L Ctrl", "KC.LSFT": "L Shift", "KC.LALT": "L Alt", "KC.LGUI": "L Win/Cmd",
    "KC.RCTL": "R Ctrl", "KC.RSFT": "R Shift", "KC.RALT": "R Alt", "KC.RGUI": "R Win/Cmd",
    
    # Navigation - use arrows
    "KC.UP": "↑ Up", "KC.DOWN": "↓ Down", "KC.LEFT": "← Left", "KC.RGHT": "→ Right",
    "KC.HOME": "Home", "KC.END": "End", "KC.PGUP": "PgUp", "KC.PGDN": "PgDn",
    
    # Function keys
    "KC.F1": "F1", "KC.F2": "F2", "KC.F3": "F3", "KC.F4": "F4",
    "KC.F5": "F5", "KC.F6": "F6", "KC.F7": "F7", "KC.F8": "F8",
    "KC.F9": "F9", "KC.F10": "F10", "KC.F11": "F11", "KC.F12": "F12",
    "KC.F13": "F13", "KC.F14": "F14", "KC.F15": "F15", "KC.F16": "F16",
    "KC.F17": "F17", "KC.F18": "F18", "KC.F19": "F19", "KC.F20": "F20",
    "KC.F21": "F21", "KC.F22": "F22", "KC.F23": "F23", "KC.F24": "F24",
    
    # Media & Volume
    "KC.MUTE": "🔇 Mute", "KC.VOLU": "🔊 Vol+", "KC.VOLD": "🔉 Vol-",
    "KC.MNXT": "⏭ Next", "KC.MPRV": "⏮ Prev", "KC.MSTP": "⏹ Stop",
    "KC.MPLY": "⏯ Play/Pause", "KC.MFFD": "⏩ FFwd", "KC.MRWD": "⏪ RWnd",
    "KC.EJCT": "⏏ Eject",
    
    # Brightness
    "KC.BRIU": "🔆 Bright+", "KC.BRID": "🔅 Bright-",
    
    # Numpad
    "KC.KP_0": "Num 0", "KC.KP_1": "Num 1", "KC.KP_2": "Num 2",
    "KC.KP_3": "Num 3", "KC.KP_4": "Num 4", "KC.KP_5": "Num 5",
    "KC.KP_6": "Num 6", "KC.KP_7": "Num 7", "KC.KP_8": "Num 8", "KC.KP_9": "Num 9",
    "KC.KP_SLASH": "Num /", "KC.KP_ASTERISK": "Num *", "KC.KP_MINUS": "Num -",
    "KC.KP_PLUS": "Num +", "KC.KP_ENTER": "Num ↵", "KC.KP_DOT": "Num .",
    "KC.KP_EQUAL": "Num =", "KC.KP_COMMA": "Num ,", "KC.NUMLOCK": "Num Lock",
    
    # Mouse
    "KC.MS_UP": "🖱↑ M Up", "KC.MS_DOWN": "🖱↓ M Down",
    "KC.MS_LEFT": "🖱← M Left", "KC.MS_RIGHT": "🖱→ M Right",
    "KC.MW_UP": "🖱⇡ Wheel Up", "KC.MW_DOWN": "🖱⇣ Wheel Dn",
    "KC.MB_L": "🖱L Click", "KC.MB_R": "🖱R Click", "KC.MB_M": "🖱M Click",
    
    # Layer Switching
    "KC.MO(1)": "Hold L1", "KC.MO(2)": "Hold L2", "KC.MO(3)": "Hold L3",
    "KC.MO(4)": "Hold L4", "KC.MO(5)": "Hold L5",
    "KC.TO(0)": "To L0", "KC.TO(1)": "To L1", "KC.TO(2)": "To L2",
    "KC.TO(3)": "To L3", "KC.TO(4)": "To L4", "KC.TO(5)": "To L5",
    "KC.TG(1)": "Toggle L1", "KC.TG(2)": "Toggle L2", "KC.TG(3)": "Toggle L3",
    "KC.TG(4)": "Toggle L4", "KC.TG(5)": "Toggle L5",
    "KC.DF(0)": "Default L0", "KC.DF(1)": "Default L1", "KC.DF(2)": "Default L2",
    "KC.DF(3)": "Default L3", "KC.DF(4)": "Default L4", "KC.DF(5)": "Default L5",
    
    # Special
    "KC.NO": "⊘ No Key", "KC.TRNS": "▽ Trans", "KC.RESET": "⚠ Reset",
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
        self._filter_installed = False

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

    def _install_event_filter(self):
        app = QApplication.instance()
        if app and not self._filter_installed:
            app.installEventFilter(self)
            self._filter_installed = True

    def _remove_event_filter(self):
        app = QApplication.instance()
        if app and self._filter_installed:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
            self._filter_installed = False

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
            self._install_event_filter()
        else:
            self.record_button.setText("Start Recording")
            self.instructions.setText("Click 'Start Recording' to begin.")
            self.add_text_btn.setEnabled(False)
            self.add_delay_btn.setEnabled(False)
            self._remove_event_filter()

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
        self._remove_event_filter()
        super().accept()

    def reject(self):
        # Ensure we stop filtering if the dialog is closed via Cancel
        self._remove_event_filter()
        super().reject()

    def insert_text_string(self):
        """Allow user to insert a text string during macro recording."""
        if not self.recording:
            return
        
        # Temporarily pause event filtering so the input dialog can receive keyboard events
        was_recording = self.recording
        self.recording = False
        self._remove_event_filter()
        
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Insert Text String", "Enter text to type:")
        
        # Resume recording and event filtering
        if was_recording:
            self.recording = True
            self._install_event_filter()
        
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
        self._remove_event_filter()
        
        from PyQt6.QtWidgets import QInputDialog
        delay_ms, ok = QInputDialog.getInt(
            self, "Insert Delay", "Enter delay in milliseconds:", 
            value=100, min=1, max=10000, step=50
        )
        
        # Resume recording and event filtering
        if was_recording:
            self.recording = True
            self._install_event_filter()
        
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

    def closeEvent(self, event):
        self._remove_event_filter()
        super().closeEvent(event)


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

    def _capture_keycode(self, title: str, prompt: str) -> str | None:
        """Try to capture a key press first, fall back to manual entry when requested."""
        capture_dialog = KeyCaptureDialog(self)
        capture_dialog.setWindowTitle(title)
        if capture_dialog.exec():
            return capture_dialog.captured

        key, ok = QInputDialog.getText(self, title, prompt)
        if ok and key:
            return key.strip()
        return None

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
        keycode = self._capture_keycode(
            "Add Tap Action",
            "Enter keycode manually (e.g., KC.A) if you did not press it."
        )
        if keycode:
            self.sequence_list.addItem(f"Tap: {keycode}")

    def add_press_action(self):
        keycode = self._capture_keycode(
            "Add Press Action",
            "Enter keycode manually (e.g., KC.LCTL) if you did not press it."
        )
        if keycode:
            self.sequence_list.addItem(f"Press: {keycode}")

    def add_release_action(self):
        keycode = self._capture_keycode(
            "Add Release Action",
            "Enter keycode manually (e.g., KC.LCTL) if you did not press it."
        )
        if keycode:
            self.sequence_list.addItem(f"Release: {keycode}")
            
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
    def __init__(self, parent=None, initial_text="", num_layers=1, initial_divisor=4):
        super().__init__(parent)
        self.setWindowTitle("Rotary Encoder Configuration")
        self.resize(600, 550)
        self.num_layers = num_layers
        self.initial_divisor = max(1, int(initial_divisor) if initial_divisor else 4)

        main_layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel(
            "Configure your rotary encoder for layer cycling with automatic display updates.\n"
            "Hardware: Pin A=GP10, Pin B=GP11, Button=GP14"
        )
        info.setWordWrap(True)
        info.setObjectName("infoBox")
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

        divisor_row = QHBoxLayout()
        divisor_label = QLabel("Pulses per action:")
        self.divisor_spin = QSpinBox()
        self.divisor_spin.setRange(1, 16)
        self.divisor_spin.setValue(self.initial_divisor)
        self.divisor_spin.setToolTip("Number of encoder transitions required before firing the mapped action.")
        divisor_row.addWidget(divisor_label)
        divisor_row.addWidget(self.divisor_spin)
        divisor_row.addStretch()
        rotation_layout.addLayout(divisor_row)
        
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
            lines.append(f"encoder_handler.divisor = {self.divisor_spin.value()}")
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
            lines.append(f"encoder_handler.divisor = {self.divisor_spin.value()}")
            lines.append(f"encoder_handler.pins = ((board.GP10, board.GP11, board.GP14, {invert}),)")
            lines.append(f"encoder_handler.map = [(({ccw_action}, {cw_action}, {press_action}),)]")
            lines.append("keyboard.modules.append(encoder_handler)")
            lines.append("")
        
        if rotation == "Cycle Layers (Recommended)":
            lines.append("# Initialize layer cycler after keymap is defined")
            lines.append("# NOTE: Add this line AFTER keyboard.keymap = [...] in your code.py:")
            lines.append(f"# layer_cycler = LayerCycler(keyboard, num_layers=len(keyboard.keymap))")
        
        return "\n".join(lines)

    def get_divisor(self) -> int:
        return self.divisor_spin.value()


class AnalogInConfigDialog(QDialog):
    """Configuration dialog for Chronos Pad Analog Slider.
    Hardware: 10k potentiometer on GP28
    """
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Analog Slider Configuration (GP28)")
        self.resize(550, 500)
        
        # Load saved settings from settings.json
        settings = load_settings()
        analog_settings = settings.get('analog_input', {})

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
        
        # Load saved mode (default to volume)
        saved_mode = analog_settings.get('mode', 'volume')
        
        self.mode_volume = QCheckBox("Volume Control")
        self.mode_volume.setChecked(saved_mode == 'volume')
        self.mode_volume.setToolTip("Use slider to control system volume (up/down)")
        self.mode_volume.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_volume)
        
        self.mode_brightness = QCheckBox("LED Brightness Control")
        self.mode_brightness.setChecked(saved_mode == 'brightness')
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
        self.poll_interval_spin.setValue(analog_settings.get('poll_interval', 0.05))
        self.poll_interval_spin.setSuffix(" sec")
        self.poll_interval_spin.setToolTip("How often to check the slider position (seconds)")
        form_layout.addRow("Poll Interval:", self.poll_interval_spin)
        
        # Threshold
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(100, 10000)
        self.threshold_spin.setSingleStep(100)
        self.threshold_spin.setValue(analog_settings.get('threshold', 2000))
        self.threshold_spin.setToolTip("Minimum slider movement to trigger change (0-65535 range)")
        form_layout.addRow("Sensitivity Threshold:", self.threshold_spin)
        
        # Step size (only for volume mode)
        self.step_size_label = QLabel("Volume Step Size:")
        self.step_size_spin = QSpinBox()
        self.step_size_spin.setRange(1, 5)
        self.step_size_spin.setValue(analog_settings.get('step_size', 1))
        self.step_size_spin.setToolTip("Number of volume steps per slider movement")
        form_layout.addRow(self.step_size_label, self.step_size_spin)
        
        # Load RGB max brightness from settings for consistency
        rgb_max_brightness = settings.get('rgb_max_brightness', 0.3)
        
        # Min/Max brightness (only for brightness mode)
        self.min_brightness_label = QLabel("Min Brightness:")
        self.min_brightness_spin = QDoubleSpinBox()
        self.min_brightness_spin.setRange(0.0, 1.0)
        self.min_brightness_spin.setSingleStep(0.05)
        self.min_brightness_spin.setDecimals(2)
        self.min_brightness_spin.setValue(analog_settings.get('min_brightness', 0.0))
        self.min_brightness_spin.setToolTip("Minimum brightness when slider is at bottom (0.0-1.0)")
        form_layout.addRow(self.min_brightness_label, self.min_brightness_spin)
        
        self.max_brightness_label = QLabel("Max Brightness:")
        self.max_brightness_spin = QDoubleSpinBox()
        self.max_brightness_spin.setRange(0.0, 1.0)
        self.max_brightness_spin.setSingleStep(0.05)
        self.max_brightness_spin.setDecimals(2)
        self.max_brightness_spin.setValue(min(analog_settings.get('max_brightness', 0.3), rgb_max_brightness))
        self.max_brightness_spin.setToolTip(f"Maximum brightness when slider is at top (0.0-1.0)\nEnforced max from settings: {rgb_max_brightness}")
        form_layout.addRow(self.max_brightness_label, self.max_brightness_spin)
        
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
            self.min_brightness_label.setEnabled(False)
            self.min_brightness_spin.setEnabled(False)
            self.max_brightness_label.setEnabled(False)
            self.max_brightness_spin.setEnabled(False)
        elif sender == self.mode_brightness and self.mode_brightness.isChecked():
            self.mode_volume.setChecked(False)
            self.step_size_label.setEnabled(False)
            self.step_size_spin.setEnabled(False)
            self.min_brightness_label.setEnabled(True)
            self.min_brightness_spin.setEnabled(True)
            self.max_brightness_label.setEnabled(True)
            self.max_brightness_spin.setEnabled(True)
        elif sender is None:
            # Initial setup - volume is default
            if not self.mode_volume.isChecked() and not self.mode_brightness.isChecked():
                self.mode_volume.setChecked(True)

    def get_config(self):
        """Generate the slider configuration code"""
        # Save settings to settings.json for persistence
        settings = load_settings()
        is_volume_mode = self.mode_volume.isChecked()
        
        settings['analog_input'] = {
            'mode': 'volume' if is_volume_mode else 'brightness',
            'poll_interval': self.poll_interval_spin.value(),
            'threshold': self.threshold_spin.value(),
            'step_size': self.step_size_spin.value(),
            'min_brightness': self.min_brightness_spin.value(),
            'max_brightness': self.max_brightness_spin.value(),
        }
        save_settings(settings)
        
        # If custom code is provided, use it
        custom_code = self.custom_code_editor.toPlainText().strip()
        if custom_code:
            return custom_code
        
        # Get form values
        poll_interval = self.poll_interval_spin.value()
        threshold = self.threshold_spin.value()
        step_size = self.step_size_spin.value()
        min_brightness = self.min_brightness_spin.value()
        max_brightness = self.max_brightness_spin.value()
        
        # Enforce RGB max brightness globally
        rgb_max_brightness = settings.get('rgb_max_brightness', 0.3)
        max_brightness = min(max_brightness, rgb_max_brightness)
        
        if is_volume_mode:
            # Generate volume control code
            config = f'''import board
from analogio import AnalogIn as AnalogInPin
from kmk.keys import KC
from kmk.extensions.media_keys import MediaKeys
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
            tap_keycode = KC.VOLU if delta > 0 else KC.VOLD
            for _ in range(self.step_size):
                # Properly tap the key with HID send
                self.keyboard.add_key(tap_keycode)
                self.keyboard._send_hid()
                self.keyboard.remove_key(tap_keycode)
                self.keyboard._send_hid()
            
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

# Ensure media keys extension is loaded for volume control
from kmk.extensions.media_keys import MediaKeys
if not any(isinstance(ext, MediaKeys) for ext in keyboard.extensions):
    keyboard.extensions.append(MediaKeys())

# Create and register volume slider module
volume_slider = VolumeSlider(keyboard, board.GP28, poll_interval={poll_interval})
keyboard.modules.append(volume_slider)
'''
        else:
            # Generate brightness control code
            config = f'''import board
from analogio import AnalogIn as AnalogInPin
import time

# LED brightness control via 10k sliding potentiometer on GP28
class BrightnessSlider:
    def __init__(self, keyboard, pin, poll_interval={poll_interval}, min_brightness={min_brightness}, max_brightness={max_brightness}):
        self.keyboard = keyboard
        self.analog_pin = AnalogInPin(pin)
        self.poll_interval = poll_interval
        self.last_poll = time.monotonic()
        self.threshold = {threshold}  # Minimum change to trigger brightness adjustment (out of 65535)
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        
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
        
        # Convert 16-bit ADC value (0-65535) to brightness range (min_brightness to max_brightness)
        brightness_range = self.max_brightness - self.min_brightness
        target_brightness = self.min_brightness + (current_value / 65535.0) * brightness_range
        
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

# Create and register brightness slider module
brightness_slider = BrightnessSlider(keyboard, board.GP28, poll_interval={poll_interval}, min_brightness={min_brightness}, max_brightness={max_brightness})
keyboard.modules.append(brightness_slider)
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
        
        # Load RGB max brightness from settings
        settings = load_settings()
        self.rgb_max_brightness = settings.get('rgb_max_brightness', 0.3)

        form = QFormLayout()

        self.pixel_pin_edit = QLineEdit(cfg.get("pixel_pin", FIXED_RGB_PIN))
        form.addRow("Pixel pin:", self.pixel_pin_edit)

        self.brightness_spin = QDoubleSpinBox()
        self.brightness_spin.setRange(0.0, 1.0)
        self.brightness_spin.setSingleStep(0.05)
        self.brightness_spin.setDecimals(2)
        # Enforce max brightness from settings
        current_brightness = float(cfg.get("brightness_limit", 0.5))
        self.brightness_spin.setValue(min(current_brightness, self.rgb_max_brightness))
        self.brightness_spin.setMaximum(self.rgb_max_brightness)
        self.brightness_spin.setToolTip(f"Brightness limit (0.0-1.0)\nGlobal max enforced: {self.rgb_max_brightness}")
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
        # Enforce global max brightness
        brightness_value = float(self.brightness_spin.value())
        result["brightness_limit"] = min(brightness_value, self.rgb_max_brightness)
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
        layer_index=0,
    ):
        super().__init__(parent)
        self.setWindowTitle("RGB Matrix Colors")
        self.rows = rows
        self.cols = cols
        self.underglow_count = max(0, underglow_count)
        self.parent_ref = parent
        self.layer_index = int(layer_index) if layer_index is not None else 0
        self.key_button_indices = []

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
            f"Editing colors for layer {self.layer_index}. Unset keys fall back to the global palette; "
            "KC.NO entries remain off."
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

        # Load saved category colors from settings, or use defaults
        settings = load_settings()
        saved_colors = settings.get('rgb_category_colors', {})
        
        # Default colors - vibrant and highly distinctive (no overlap with granular colors)
        default_colors = {
            "macro": "#FF0066",      # Electric Pink
            "basic": "#00FFFF",      # Aqua/Cyan
            "modifiers": "#00FF00",  # Pure Green
            "navigation": "#FFCC00", # Amber
            "function": "#9933FF",   # Vivid Purple
            "media": "#FF5500",      # Bright Orange
            "mouse": "#FF66CC",      # Bright Pink
            "layers": "#66FF00",     # Bright Lime
            "wasd": "#FF0099",       # Magenta Pink
            "arrows": "#0099FF",     # Bright Blue
        }
        
        # Merge saved colors with defaults
        self.category_colors = {**default_colors, **saved_colors}

        category_labels = {
            "macro": "Macros",
            "basic": "Basic",
            "modifiers": "Modifiers",
            "navigation": "Navigation",
            "function": "Function",
            "media": "Media",
            "mouse": "Mouse",
            "layers": "Layers",
            "wasd": "WASD Keys",
            "arrows": "Arrow Keys",
        }

        preset_group = QGroupBox("Keycode Category Presets")
        preset_grid = QGridLayout(preset_group)
        row = 0
        for cat_key, cat_label in category_labels.items():
            preset_grid.addWidget(QLabel(f"{cat_label}:"), row, 0)

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
        
        # Add Apply All and Reset buttons at the bottom
        preset_grid.addWidget(QLabel(""), row, 0)  # Spacer
        
        apply_all_btn = QPushButton("Apply All Categories")
        apply_all_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        apply_all_btn.clicked.connect(self.apply_all_categories)
        preset_grid.addWidget(apply_all_btn, row + 1, 0, 1, 3)
        
        reset_btn = QPushButton("Reset to Default Colors")
        reset_btn.clicked.connect(self.reset_category_colors)
        preset_grid.addWidget(reset_btn, row + 2, 0, 1, 3)

        presets_layout.addWidget(preset_group)

        # Fine-Grained Presets - More vibrant and distinct colors
        self.granular_colors = {
            "numbers": "#FF6B00",      # Vivid Orange
            "letters": "#00BFFF",      # Deep Sky Blue
            "space": "#00FF7F",        # Spring Green
            "enter": "#FF1493",        # Deep Pink
            "backspace": "#FF4500",    # Orange Red
            "tab": "#DA70D6",          # Orchid
            "shift": "#FFD700",        # Gold
            "ctrl": "#32CD32",         # Lime Green
            "alt": "#FF69B4",          # Hot Pink
            "keypad_nums": "#FF8C00",  # Dark Orange
            "keypad_nav": "#9370DB",   # Medium Purple
            "keypad_ops": "#20B2AA",   # Light Sea Green
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
        
        # Add Apply All button for granular presets
        granular_grid.addWidget(QLabel(""), row, 0)  # Spacer
        
        apply_all_granular_btn = QPushButton("Apply All Fine-Grained")
        apply_all_granular_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        apply_all_granular_btn.clicked.connect(self.apply_all_granular)
        granular_grid.addWidget(apply_all_granular_btn, row + 1, 0, 1, 3)

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
        self.key_button_indices = []
        for r in range(self.rows):
            for c in range(self.cols):
                key_idx = self._key_index_for_position(r, c)
                btn = QPushButton(f"{key_idx}")
                btn.setFixedSize(64, 56)
                btn.setStyleSheet("font-size: 12px; padding: 4px;")
                btn.clicked.connect(self.on_key_clicked)
                self.key_buttons.append(btn)
                self.key_button_indices.append(key_idx)
                self.grid_layout.addWidget(btn, r, c)
                try:
                    self._install_hover_effect(btn)
                except Exception:
                    pass

    def _key_index_for_position(self, display_row: int, display_col: int) -> int:
        logical_row = self.rows - 1 - display_row
        logical_col = self.cols - 1 - display_col
        return logical_row * self.cols + logical_col

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
            key_idx = self.key_button_indices[idx]
            color = self.key_colors.get(str(key_idx))
            if color:
                rgb = hex_to_rgb_list(color)
                luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                text_color = "#000000" if luminance > 150 else "#FFFFFF"
                btn.setStyleSheet(f"background-color: {color}; color: {text_color}; font-size: 12px; padding: 4px;")
                btn.setToolTip(f"Index: {key_idx}\nColor: {color}")
            else:
                btn.setStyleSheet("font-size: 12px; padding: 4px;")
                btn.setToolTip(f"Index: {key_idx}\nColor: (default)")

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
        key_idx = self.key_button_indices[idx]
        color = QColorDialog.getColor(QColor(self.fill_color), self, "Select key color")
        if color.isValid():
            hexc = ensure_hex_prefix(color.name(), self.fill_color)
            self.key_colors[str(key_idx)] = hexc
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
            # Save to settings for persistence
            self.save_category_colors()

    def apply_category_color(self, category):
        """Apply category color to all matching keys on the grid.
        
        Args:
            category: Category name (e.g., 'macro', 'basic', 'modifiers')
        """
        color = self.category_colors.get(category, self.fill_color)
        
        # Determine which keys belong to this category
        keys_to_color = self.get_keys_for_category(category)
        
        for key_idx in keys_to_color:
            self.key_colors[str(key_idx)] = color
        
        self.refresh_key_buttons()
    
    def apply_all_categories(self):
        """Apply all category colors at once to their respective keys."""
        for category in self.category_colors.keys():
            keys_to_color = self.get_keys_for_category(category)
            color = self.category_colors[category]
            for key_idx in keys_to_color:
                self.key_colors[str(key_idx)] = color
        
        self.refresh_key_buttons()
        ToastNotification.show_message(
            self, 
            "All category colors applied to keymap", 
            "SUCCESS", 
            2000
        )
    
    def reset_category_colors(self):
        """Reset all category colors to their default values."""
        # Default colors
        default_colors = {
            "macro": "#FF3366",
            "basic": "#00D9FF",
            "modifiers": "#00FF88",
            "navigation": "#FFD700",
            "function": "#9D7CFF",
            "media": "#FF6B35",
            "mouse": "#FF69B4",
            "layers": "#7FFF00",
            "wasd": "#FF1493",
            "arrows": "#1E90FF",
            "misc": "#C0C0C0",
        }
        
        self.category_colors = default_colors.copy()
        
        # Update all color buttons
        for cat_key in self.category_colors.keys():
            btn = getattr(self, f"{cat_key}_color_btn", None)
            if btn:
                btn.setStyleSheet(f"background-color: {self.category_colors[cat_key]};")
        
        # Save to settings
        self.save_category_colors()
        
        ToastNotification.show_message(
            self, 
            "Category colors reset to defaults", 
            "INFO", 
            2000
        )
    
    def save_category_colors(self):
        """Save current category colors to settings for persistence."""
        settings = load_settings()
        settings['rgb_category_colors'] = self.category_colors.copy()
        save_settings(settings)
    
    def get_keys_for_category(self, category):
        """Get list of key indices that belong to a specific category.
        
        Args:
            category: Category name
            
        Returns:
            list: List of key indices (0-19 for 5x4 grid)
        """
        if not hasattr(self, 'parent_ref') or not self.parent_ref:
            return []
        
        # Get current keymap from parent
        keymap = getattr(self.parent_ref, 'keymap_data', [])
        if not keymap:
            return []
        
        current_layer = getattr(self.parent_ref, 'current_layer', 0)
        if current_layer >= len(keymap):
            return []
        
        layer = keymap[current_layer]
        matching_keys = []
        
        # Iterate through all keys in the layer
        for row_idx, row in enumerate(layer):
            for col_idx, key_code in enumerate(row):
                key_index = row_idx * 4 + col_idx  # 5x4 grid
                
                if self.key_matches_category(key_code, category):
                    matching_keys.append(key_index)
        
        return matching_keys
    
    def key_matches_category(self, key_code, category):
        """Check if a keycode belongs to a specific category.
        
        Args:
            key_code: Key code string (e.g., 'KC.A', 'KC.LSHIFT')
            category: Category name
            
        Returns:
            bool: True if key belongs to category
        """
        if not key_code or key_code == "KC.NO" or key_code == "KC.TRNS":
            return False
        
        key = key_code.upper()
        
        if category == "macro":
            return key.startswith("MACRO(")
        elif category == "basic":
            # Letters and numbers
            return any(key.endswith(f".{c}") for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        elif category == "modifiers":
            return any(mod in key for mod in ["LSHIFT", "RSHIFT", "LCTRL", "RCTRL", "LALT", "RALT", "LGUI", "RGUI"])
        elif category == "navigation":
            return any(nav in key for nav in ["HOME", "END", "PGUP", "PGDN", "INS", "DEL"])
        elif category == "function":
            return any(f"F{i}" in key for i in range(1, 25))
        elif category == "media":
            return any(med in key for med in ["MUTE", "VOLU", "VOLD", "MPLY", "MSTP", "MNXT", "MPRV"])
        elif category == "mouse":
            return "MS_" in key or "MW_" in key or "MB_" in key
        elif category == "layers":
            return any(lyr in key for lyr in ["MO(", "TO(", "TG(", "DF(", "LT("])
        elif category == "wasd":
            return any(key.endswith(f".{c}") for c in ["W", "A", "S", "D"])
        elif category == "arrows":
            # Only match arrow keys, not page up/down or home/end
            # Note: RIGHT is abbreviated as RGHT in KMK
            return any(key.endswith(f".{arr}") for arr in ["UP", "DOWN", "LEFT", "RGHT"])
        
        return False

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
        _, layer_data = self._get_layer_data()
        if layer_data is None:
            QMessageBox.warning(self, "Error", "Cannot access keymap data")
            return
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

    def apply_all_granular(self):
        """Apply all fine-grained preset colors at once"""
        granular_types = [
            'numbers', 'letters', 'space', 'enter', 'backspace', 
            'tab', 'shift', 'ctrl', 'alt', 
            'keypad_nums', 'keypad_nav', 'keypad_ops'
        ]
        
        for gran_type in granular_types:
            self.apply_granular_color(gran_type)
        
        QMessageBox.information(
            self, 
            "Apply All Complete",
            f"Applied all {len(granular_types)} fine-grained color presets to matching keys!"
        )

    def _get_layer_data(self):
        parent = self.parent_ref
        if not parent or not hasattr(parent, "keymap_data") or not parent.keymap_data:
            return None, None
        layers = parent.keymap_data
        idx = self.layer_index if 0 <= self.layer_index < len(layers) else 0
        return idx, layers[idx]

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
        return False

    def get_maps(self):
        return self.key_colors.copy(), self.underglow_colors.copy()

    def accept(self):
        if self.parent_ref and hasattr(self.parent_ref, 'rgb_matrix_config'):
            config = self.parent_ref.rgb_matrix_config
            layer_colors = config.setdefault('layer_key_colors', {})
            layer_key = str(self.layer_index)
            if self.key_colors:
                layer_colors[layer_key] = self.key_colors.copy()
            elif layer_key in layer_colors:
                layer_colors.pop(layer_key)

            if self.layer_index == 0:
                config['key_colors'] = self.key_colors.copy()

            config['underglow_colors'] = self.underglow_colors.copy()
            self.parent_ref.update_macropad_display()
        super().accept()

    def _update_button_color(self, button: QPushButton, color: str):
        rgb = hex_to_rgb_list(color)
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        text_color = '#000000' if luminance > 150 else '#FFFFFF'
        button.setStyleSheet(f"background-color: {color}; color: {text_color};")


class TapDanceDialog(QDialog):
    """Dialog for creating TapDance configurations based on KMK documentation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TapDance Helper")
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Info
        info = QLabel(
            "<b>TapDance</b><br>"
            "Define keys that perform different actions based on the number of taps.<br>"
            "Example: Tap once for 'a', twice for 'b', tap and hold for left ctrl.<br><br>"
            "Supports all key types including HoldTap (MT, LT), TT, and Macros."
        )
        info.setWordWrap(True)
        info.setObjectName("infoBox")
        layout.addWidget(info)
        
        # TapDance entries
        self.tapdance_list = QListWidget()
        self.tapdance_list.setMinimumHeight(250)
        layout.addWidget(QLabel("<b>TapDance Definitions:</b>"))
        layout.addWidget(self.tapdance_list)
        
        # Add/Remove/Edit buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add TapDance")
        add_btn.clicked.connect(self.add_tapdance_entry)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.clicked.connect(self.edit_tapdance_entry)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("➖ Remove Selected")
        remove_btn.clicked.connect(self.remove_tapdance_entry)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Global tap time setting
        form = QFormLayout()
        self.tap_time_spin = QSpinBox()
        self.tap_time_spin.setRange(100, 3000)
        self.tap_time_spin.setValue(750)
        self.tap_time_spin.setSuffix(" ms")
        self.tap_time_spin.setToolTip(
            "Default time between taps. Can be overridden per TapDance.\n"
            "KMK default is 300ms, but 750ms is more forgiving."
        )
        form.addRow("Global Tap Time:", self.tap_time_spin)
        layout.addLayout(form)
        
        # Usage instructions
        usage = QLabel(
            "<b>Usage:</b> Use these TapDance variables in your keymap.<br>"
            "Example: If you create <code>TD_ESC_CTRL</code>, place it in your keymap grid."
        )
        usage.setWordWrap(True)
        usage.setStyleSheet("color: #666; font-size: 10pt; padding: 8px;")
        layout.addWidget(usage)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Store TapDance data
        self.tapdance_data = []  # List of dicts with {name, actions, tap_time}
    
    def add_tapdance_entry(self):
        """Add a new TapDance entry"""
        self._edit_tapdance_entry()
    
    def edit_tapdance_entry(self):
        """Edit selected TapDance entry"""
        current_row = self.tapdance_list.currentRow()
        if current_row >= 0:
            self._edit_tapdance_entry(current_row)
    
    def _edit_tapdance_entry(self, edit_index=None):
        """Internal method to add or edit a TapDance entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit TapDance" if edit_index is not None else "Add TapDance")
        dialog.resize(550, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Variable name
        form = QFormLayout()
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g., TD_ESC_CTRL")
        name_edit.setToolTip("Variable name for this TapDance (recommended to start with TD_)")
        
        # Custom tap time
        custom_tap_time_check = QCheckBox("Use custom tap time for this TapDance")
        custom_tap_time_spin = QSpinBox()
        custom_tap_time_spin.setRange(100, 5000)
        custom_tap_time_spin.setValue(750)
        custom_tap_time_spin.setSuffix(" ms")
        custom_tap_time_spin.setEnabled(False)
        custom_tap_time_check.toggled.connect(custom_tap_time_spin.setEnabled)
        
        # Load existing data if editing
        if edit_index is not None:
            existing = self.tapdance_data[edit_index]
            name_edit.setText(existing['name'])
            if existing.get('tap_time'):
                custom_tap_time_check.setChecked(True)
                custom_tap_time_spin.setValue(existing['tap_time'])
        
        form.addRow("Name:", name_edit)
        form.addRow("", custom_tap_time_check)
        form.addRow("Custom Tap Time:", custom_tap_time_spin)
        
        layout.addLayout(form)
        
        # Actions list
        layout.addWidget(QLabel("<b>Actions (in order of tap count):</b>"))
        actions_list = QListWidget()
        actions_list.setMaximumHeight(200)
        layout.addWidget(actions_list)
        
        # Load existing actions if editing
        if edit_index is not None:
            for action in existing['actions']:
                actions_list.addItem(action)
        
        # Action type selector
        action_type_group = QGroupBox("Add Action")
        action_type_layout = QVBoxLayout()
        
        action_type_combo = QComboBox()
        action_type_combo.addItems([
            "Simple Key (e.g., KC.A, KC.ESC)",
            "Mod Tap / Hold Tap (e.g., KC.HT(tap, hold))",
            "Layer Tap (e.g., KC.LT(layer, key))",
            "Toggle Layer (e.g., KC.TG(1))",
            "Tap Toggle Layer (e.g., KC.TT(1))",
            "Macro (e.g., KC.MACRO('text'))",
            "Custom / Advanced"
        ])
        action_type_layout.addWidget(action_type_combo)
        
        # Input fields for different action types
        simple_key_input = QLineEdit()
        simple_key_input.setPlaceholderText("KC.A")
        
        ht_tap_input = QLineEdit()
        ht_tap_input.setPlaceholderText("Tap key (e.g., KC.B)")
        ht_hold_input = QLineEdit()
        ht_hold_input.setPlaceholderText("Hold key (e.g., KC.LCTL)")
        ht_prefer_hold = QCheckBox("Prefer hold (default: False)")
        ht_prefer_hold.setToolTip("If True, hold action takes priority over tap")
        
        lt_layer_input = QSpinBox()
        lt_layer_input.setRange(0, 15)
        lt_key_input = QLineEdit()
        lt_key_input.setPlaceholderText("Tap key (e.g., KC.SPC)")
        
        custom_input = QTextEdit()
        custom_input.setPlaceholderText("Enter custom action (e.g., KC.MACRO('Hello'))")
        custom_input.setMaximumHeight(60)
        
        # Stack widget to show/hide inputs based on action type
        input_stack = QWidget()
        input_layout = QVBoxLayout(input_stack)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # Simple key widget
        simple_widget = QWidget()
        simple_layout = QVBoxLayout(simple_widget)
        simple_layout.addWidget(QLabel("Key:"))
        simple_layout.addWidget(simple_key_input)
        simple_layout.addStretch()
        
        # Hold Tap widget
        ht_widget = QWidget()
        ht_layout = QVBoxLayout(ht_widget)
        ht_layout.addWidget(QLabel("Tap Key:"))
        ht_layout.addWidget(ht_tap_input)
        ht_layout.addWidget(QLabel("Hold Key:"))
        ht_layout.addWidget(ht_hold_input)
        ht_layout.addWidget(ht_prefer_hold)
        ht_layout.addStretch()
        
        # Layer Tap widget
        lt_widget = QWidget()
        lt_layout = QVBoxLayout(lt_widget)
        lt_layout.addWidget(QLabel("Layer:"))
        lt_layout.addWidget(lt_layer_input)
        lt_layout.addWidget(QLabel("Tap Key:"))
        lt_layout.addWidget(lt_key_input)
        lt_layout.addStretch()
        
        # Toggle layer widget
        tg_widget = QWidget()
        tg_layout = QVBoxLayout(tg_widget)
        tg_layer_input = QSpinBox()
        tg_layer_input.setRange(0, 15)
        tg_layout.addWidget(QLabel("Layer to Toggle:"))
        tg_layout.addWidget(tg_layer_input)
        tg_layout.addStretch()
        
        # Tap Toggle layer widget
        tt_widget = QWidget()
        tt_layout = QVBoxLayout(tt_widget)
        tt_layer_input = QSpinBox()
        tt_layer_input.setRange(0, 15)
        tt_tap_time_input = QSpinBox()
        tt_tap_time_input.setRange(100, 5000)
        tt_tap_time_input.setValue(3000)
        tt_tap_time_input.setSuffix(" ms")
        tt_layout.addWidget(QLabel("Layer:"))
        tt_layout.addWidget(tt_layer_input)
        tt_layout.addWidget(QLabel("Hold Time (optional):"))
        tt_layout.addWidget(tt_tap_time_input)
        tt_layout.addStretch()
        
        # Macro widget
        macro_widget = QWidget()
        macro_layout = QVBoxLayout(macro_widget)
        macro_input = QLineEdit()
        macro_input.setPlaceholderText("Text to type")
        macro_layout.addWidget(QLabel("Macro Text:"))
        macro_layout.addWidget(macro_input)
        macro_layout.addStretch()
        
        # Custom widget
        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)
        custom_layout.addWidget(QLabel("Custom Action:"))
        custom_layout.addWidget(custom_input)
        custom_layout.addStretch()
        
        # Add all widgets to input_layout (hidden by default)
        widgets = [simple_widget, ht_widget, lt_widget, tg_widget, tt_widget, macro_widget, custom_widget]
        for w in widgets:
            w.setVisible(False)
            input_layout.addWidget(w)
        
        simple_widget.setVisible(True)  # Show first one by default
        
        def on_action_type_changed(index):
            for w in widgets:
                w.setVisible(False)
            widgets[index].setVisible(True)
        
        action_type_combo.currentIndexChanged.connect(on_action_type_changed)
        action_type_layout.addWidget(input_stack)
        
        add_action_btn = QPushButton("➕ Add This Action")
        def add_action():
            action_idx = action_type_combo.currentIndex()
            action_str = ""
            
            if action_idx == 0:  # Simple key
                action_str = simple_key_input.text().strip()
            elif action_idx == 1:  # Hold Tap
                tap = ht_tap_input.text().strip()
                hold = ht_hold_input.text().strip()
                if tap and hold:
                    prefer = ", prefer_hold=True" if ht_prefer_hold.isChecked() else ""
                    action_str = f"KC.HT({tap}, {hold}{prefer})"
            elif action_idx == 2:  # Layer Tap
                layer = lt_layer_input.value()
                key = lt_key_input.text().strip()
                if key:
                    action_str = f"KC.LT({layer}, {key})"
            elif action_idx == 3:  # Toggle Layer
                layer = tg_layer_input.value()
                action_str = f"KC.TG({layer})"
            elif action_idx == 4:  # Tap Toggle Layer
                layer = tt_layer_input.value()
                action_str = f"KC.TT({layer}, tap_time={tt_tap_time_input.value()})"
            elif action_idx == 5:  # Macro
                text = macro_input.text().strip()
                if text:
                    escaped = text.replace("'", "\\'")
                    action_str = f"KC.MACRO('{escaped}')"
            elif action_idx == 6:  # Custom
                action_str = custom_input.toPlainText().strip()
            
            if action_str:
                actions_list.addItem(action_str)
                # Clear inputs
                simple_key_input.clear()
                ht_tap_input.clear()
                ht_hold_input.clear()
                ht_prefer_hold.setChecked(False)
                lt_key_input.clear()
                macro_input.clear()
                custom_input.clear()
        
        add_action_btn.clicked.connect(add_action)
        action_type_layout.addWidget(add_action_btn)
        
        action_type_group.setLayout(action_type_layout)
        layout.addWidget(action_type_group)
        
        # Action list controls
        action_btn_layout = QHBoxLayout()
        move_up_btn = QPushButton("⬆ Move Up")
        move_up_btn.clicked.connect(lambda: self._move_action(actions_list, -1))
        action_btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("⬇ Move Down")
        move_down_btn.clicked.connect(lambda: self._move_action(actions_list, 1))
        action_btn_layout.addWidget(move_down_btn)
        
        remove_action_btn = QPushButton("➖ Remove")
        remove_action_btn.clicked.connect(lambda: actions_list.takeItem(actions_list.currentRow()))
        action_btn_layout.addWidget(remove_action_btn)
        action_btn_layout.addStretch()
        layout.addLayout(action_btn_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a variable name")
                return
            
            actions = []
            for i in range(actions_list.count()):
                actions.append(actions_list.item(i).text())
            
            if not actions:
                QMessageBox.warning(self, "No Actions", "Please add at least one action")
                return
            
            # Create or update TapDance data
            td_data = {
                'name': name,
                'actions': actions,
                'tap_time': custom_tap_time_spin.value() if custom_tap_time_check.isChecked() else None
            }
            
            if edit_index is not None:
                self.tapdance_data[edit_index] = td_data
                self.tapdance_list.item(edit_index).setText(self._format_td_display(td_data))
            else:
                self.tapdance_data.append(td_data)
                self.tapdance_list.addItem(self._format_td_display(td_data))
    
    def _move_action(self, list_widget, direction):
        """Move selected action up or down"""
        current_row = list_widget.currentRow()
        if current_row < 0:
            return
        
        new_row = current_row + direction
        if new_row < 0 or new_row >= list_widget.count():
            return
        
        item = list_widget.takeItem(current_row)
        list_widget.insertItem(new_row, item)
        list_widget.setCurrentRow(new_row)
    
    def _format_td_display(self, td_data):
        """Format TapDance data for display"""
        actions_str = ', '.join(td_data['actions'][:3])  # Show first 3 actions
        if len(td_data['actions']) > 3:
            actions_str += f", ... (+{len(td_data['actions']) - 3} more)"
        
        time_str = f" [tap_time={td_data['tap_time']}ms]" if td_data.get('tap_time') else ""
        return f"{td_data['name']}: {actions_str}{time_str}"
    
    def remove_tapdance_entry(self):
        """Remove selected TapDance entry"""
        current_row = self.tapdance_list.currentRow()
        if current_row >= 0:
            self.tapdance_list.takeItem(current_row)
            del self.tapdance_data[current_row]
    
    def get_code(self):
        """Generate TapDance code based on KMK documentation"""
        if not self.tapdance_data:
            return ""
        
        lines = []
        lines.append("# TapDance Configuration")
        lines.append("# See: https://github.com/KMKfw/kmk_firmware/blob/master/docs/en/tapdance.md")
        lines.append("from kmk.modules.tapdance import TapDance")
        lines.append("")
        lines.append("tapdance = TapDance()")
        lines.append(f"tapdance.tap_time = {self.tap_time_spin.value()}  # Default tap time in milliseconds")
        lines.append("keyboard.modules.append(tapdance)")
        lines.append("")
        lines.append("# TapDance Definitions:")
        lines.append("# Each TD can contain multiple actions triggered by successive taps")
        lines.append("# Supports: simple keys, HoldTap (MT/LT), TT, Macros, and any KC action")
        
        for td in self.tapdance_data:
            lines.append("")
            actions_str = ', '.join(td['actions'])
            
            # Add custom tap_time if specified
            if td.get('tap_time'):
                lines.append(f"{td['name']} = KC.TD({actions_str}, tap_time={td['tap_time']})")
            else:
                lines.append(f"{td['name']} = KC.TD({actions_str})")
            
            # Add comment explaining the taps
            lines.append(f"# Tap {len(td['actions'])} time(s): {' → '.join(td['actions'])}")
        
        return "\n".join(lines)


class ComboDialog(QDialog):
    """Dialog for creating Combo configurations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Combo Helper")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Info
        info = QLabel(
            "<b>Combos</b><br>"
            "Define key combinations that trigger a specific action.<br>"
            "For example: Press Q + W simultaneously to send ESC."
        )
        info.setWordWrap(True)
        info.setObjectName("infoBox")
        layout.addWidget(info)
        
        # Combo entries
        self.combo_list = QListWidget()
        self.combo_list.setMinimumHeight(250)
        layout.addWidget(QLabel("Combo Definitions:"))
        layout.addWidget(self.combo_list)
        
        # Add/Remove buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Combo")
        add_btn.clicked.connect(self.add_combo_entry)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("➖ Remove Selected")
        remove_btn.clicked.connect(self.remove_combo_entry)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def add_combo_entry(self):
        """Add a new Combo entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Combo")
        dialog.resize(450, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Keys to press
        form = QFormLayout()
        keys_edit = QLineEdit()
        keys_edit.setPlaceholderText("e.g., KC.Q, KC.W")
        keys_edit.setToolTip("Keys that must be pressed together (comma-separated)")
        form.addRow("Keys to Press:", keys_edit)
        
        # Result action
        result_edit = QLineEdit()
        result_edit.setPlaceholderText("e.g., KC.ESC")
        result_edit.setToolTip("The keycode to send when the combo is triggered")
        form.addRow("Result Action:", result_edit)
        
        layout.addLayout(form)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            keys = keys_edit.text().strip()
            result = result_edit.text().strip()
            
            if not keys or not result:
                QMessageBox.warning(self, "Invalid Input", "Please enter both keys and result")
                return
            
            # Add to list
            display_text = f"Chord(({keys}), {result})"
            self.combo_list.addItem(display_text)
    
    def remove_combo_entry(self):
        """Remove selected Combo entry"""
        current_row = self.combo_list.currentRow()
        if current_row >= 0:
            self.combo_list.takeItem(current_row)
    
    def get_code(self):
        """Generate Combo code"""
        if self.combo_list.count() == 0:
            return ""
        
        lines = []
        lines.append("# Combos Configuration")
        lines.append("from kmk.modules.combos import Combos, Chord, Sequence")
        lines.append("")
        lines.append("combos = Combos()")
        lines.append("combos.combos = [")
        
        for i in range(self.combo_list.count()):
            lines.append(f"    {self.combo_list.item(i).text()},")
        
        lines.append("]")
        lines.append("keyboard.modules.append(combos)")
        
        return "\n".join(lines)


class AdvancedSettingsDialog(QDialog):
    """Dialog for advanced settings: boot.py configuration and encoder divisor."""
    
    def __init__(self, parent=None, encoder_divisor=4, boot_config=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.resize(650, 550)
        
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different setting categories
        tabs = QTabWidget()
        
        # --- Encoder Settings Tab ---
        encoder_tab = QWidget()
        encoder_layout = QVBoxLayout(encoder_tab)
        
        encoder_group = QGroupBox("Encoder Configuration")
        encoder_form = QFormLayout()
        
        self.divisor_spin = QSpinBox()
        self.divisor_spin.setRange(1, 16)
        self.divisor_spin.setValue(encoder_divisor)
        self.divisor_spin.setToolTip(
            "Number of encoder transitions required before firing the mapped action.\n"
            "Lower = more sensitive, Higher = less sensitive.\n"
            "Recommended: 4 for standard encoders."
        )
        encoder_form.addRow("Encoder Steps per Pulse:", self.divisor_spin)
        
        info_label = QLabel(
            "<b>What is this?</b><br>"
            "The encoder divisor controls how many physical 'clicks' or steps "
            "the rotary encoder needs to turn before sending an action.<br><br>"
            "<b>Lower values (1-2):</b> More sensitive, faster response<br>"
            "<b>Higher values (4-8):</b> Less sensitive, more deliberate control<br><br>"
            "Default is 4, which works well for most standard rotary encoders."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: rgba(100, 100, 100, 0.2); border-radius: 5px;")
        encoder_layout.addWidget(info_label)
        
        encoder_group.setLayout(encoder_form)
        encoder_layout.addWidget(encoder_group)
        encoder_layout.addStretch()
        
        tabs.addTab(encoder_tab, "Encoder")
        
        # --- Boot.py Settings Tab ---
        boot_tab = QWidget()
        boot_layout = QVBoxLayout(boot_tab)
        
        boot_info = QLabel(
            "<b>Boot Configuration (boot.py)</b><br>"
            "These settings control CircuitPython's boot behavior. "
            "The boot.py file runs before your main code and can configure "
            "USB, storage, and other low-level settings."
        )
        boot_info.setWordWrap(True)
        boot_layout.addWidget(boot_info)
        
        boot_group = QGroupBox("USB and Storage Settings")
        boot_form = QVBoxLayout()
        
        self.enable_boot_py = QCheckBox("Enable custom boot.py configuration")
        self.enable_boot_py.setChecked(boot_config is not None and boot_config.strip() != "")
        self.enable_boot_py.toggled.connect(self.on_boot_toggle)
        boot_form.addWidget(self.enable_boot_py)
        
        boot_form.addSpacing(10)
        
        # Common boot.py options
        self.disable_storage_checkbox = QCheckBox("Make storage read-only (protect files from computer)")
        self.disable_storage_checkbox.setToolTip(
            "When enabled, the CIRCUITPY drive will be read-only from the computer.\n"
            "This prevents accidental file deletion but requires editing on device."
        )
        
        self.disable_usb_hid_checkbox = QCheckBox("Disable USB HID (keyboard/mouse)")
        self.disable_usb_hid_checkbox.setToolTip(
            "Disable USB keyboard/mouse functionality. Only use if you don't need HID."
        )
        
        self.rename_drive_layout = QHBoxLayout()
        self.rename_drive_checkbox = QCheckBox("Rename CIRCUITPY drive to:")
        self.drive_name_edit = QLineEdit("CHRONOSPAD")
        self.drive_name_edit.setMaxLength(11)
        self.drive_name_edit.setToolTip("Custom name for the USB drive (max 11 characters)")
        self.rename_drive_layout.addWidget(self.rename_drive_checkbox)
        self.rename_drive_layout.addWidget(self.drive_name_edit)
        
        boot_form.addWidget(self.disable_storage_checkbox)
        boot_form.addWidget(self.disable_usb_hid_checkbox)
        boot_form.addLayout(self.rename_drive_layout)
        
        boot_form.addSpacing(10)
        
        boot_form.addWidget(QLabel("<b>Custom boot.py code:</b>"))
        self.boot_code_editor = QTextEdit()
        self.boot_code_editor.setPlaceholderText(
            "# Optional: Add custom boot.py code here\n"
            "# Example:\n"
            "# import storage\n"
            "# storage.remount('/', readonly=False)\n"
        )
        self.boot_code_editor.setMaximumHeight(180)
        
        if boot_config:
            self.boot_code_editor.setPlainText(boot_config)
        
        boot_form.addWidget(self.boot_code_editor)
        
        boot_group.setLayout(boot_form)
        boot_layout.addWidget(boot_group)
        
        tabs.addTab(boot_tab, "Boot Configuration")
        
        main_layout.addWidget(tabs)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Initialize UI state
        self.on_boot_toggle()
    
    def on_boot_toggle(self):
        """Enable/disable boot.py controls based on checkbox."""
        enabled = self.enable_boot_py.isChecked()
        self.disable_storage_checkbox.setEnabled(enabled)
        self.disable_usb_hid_checkbox.setEnabled(enabled)
        self.rename_drive_checkbox.setEnabled(enabled)
        self.drive_name_edit.setEnabled(enabled)
        self.boot_code_editor.setEnabled(enabled)
    
    def get_encoder_divisor(self):
        """Return the selected encoder divisor value."""
        return self.divisor_spin.value()
    
    def get_boot_config(self):
        """Generate boot.py configuration code and save board name to settings."""
        if not self.enable_boot_py.isChecked():
            return ""
        
        # Save board name to settings if renamed
        if self.rename_drive_checkbox.isChecked():
            board_name = self.drive_name_edit.text().strip()
            if board_name:
                settings = load_settings()
                board_names = settings.get('board_names', [])
                if board_name not in board_names:
                    board_names.append(board_name)
                settings['board_names'] = board_names
                save_settings(settings)
        
        lines = []
        
        # Check if any options are enabled
        has_options = (
            self.disable_storage_checkbox.isChecked() or
            self.disable_usb_hid_checkbox.isChecked() or
            self.rename_drive_checkbox.isChecked()
        )
        
        if has_options:
            if self.disable_storage_checkbox.isChecked():
                lines.append("import storage")
                lines.append("storage.disable_usb_drive()")
                lines.append("")
            
            if self.disable_usb_hid_checkbox.isChecked():
                lines.append("import usb_hid")
                lines.append("usb_hid.disable()")
                lines.append("")
            
            if self.rename_drive_checkbox.isChecked():
                drive_name = self.drive_name_edit.text().strip()
                if drive_name:
                    lines.append("import storage")
                    lines.append(f'storage.remount("/", readonly=False)')
                    lines.append(f'storage.getmount("/").label = "{drive_name}"')
                    lines.append('storage.remount("/", readonly=True)')
                    lines.append("")
        
        # Add custom code
        custom_code = self.boot_code_editor.toPlainText().strip()
        if custom_code:
            if lines:
                lines.append("# Custom configuration:")
            lines.append(custom_code)
        
        return "\n".join(lines)


# --- Modern UI Helper Widgets ---
class ToggleSwitch(QCheckBox):
    """
    Modern toggle switch widget using QCheckBox with custom styling.
    
    Provides a visual toggle switch interface similar to iOS/Material Design
    switches instead of traditional checkboxes. The switch animates when toggled
    and uses theme-aware colors (blue when enabled, gray when disabled).
    
    Usage:
        toggle = ToggleSwitch("Enable Feature")
        toggle.setChecked(True)
        toggle.toggled.connect(on_toggle_changed)
    
    Note:
        Styling is applied via objectName="toggleSwitch" in the QSS themes.
        The switch appearance is controlled entirely by stylesheets.
    """
    
    def __init__(self, text="", parent=None):
        """
        Initialize toggle switch.
        
        Args:
            text: Label text displayed next to the switch
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setObjectName("toggleSwitch")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class CollapsibleCard(QWidget):
    """
    Collapsible card widget with header and expandable content area.
    
    Provides a modern card-based UI element with:
    - Clickable header with title and collapse/expand indicator
    - Smooth animation when expanding/collapsing
    - Card styling with rounded corners and subtle shadows
    - Badge support showing item count or status
    
    Usage:
        card = CollapsibleCard("Section Title", badge_text="3")
        content_layout = card.get_content_layout()
        content_layout.addWidget(QLabel("Content goes here"))
        
    Note:
        Content is added to the layout returned by get_content_layout().
        The card starts expanded by default but can be set to collapsed.
    """
    
    def __init__(self, title, badge_text="", parent=None, start_collapsed=False):
        """
        Initialize collapsible card.
        
        Args:
            title: Card header title text
            badge_text: Optional badge text (e.g., item count)
            parent: Parent widget
            start_collapsed: If True, card starts in collapsed state
        """
        super().__init__(parent)
        self.setObjectName("card")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header button (clickable to collapse/expand)
        self.header_btn = QPushButton()
        self.header_btn.setObjectName("cardHeader")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.clicked.connect(self.toggle_collapsed)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        # Expand/collapse indicator
        self.indicator = QLabel("▼")
        self.indicator.setObjectName("cardIndicator")
        header_layout.addWidget(self.indicator)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        header_layout.addWidget(self.title_label)
        
        # Badge (optional)
        if badge_text:
            self.badge_label = QLabel(badge_text)
            self.badge_label.setObjectName("cardBadge")
            header_layout.addWidget(self.badge_label)
        else:
            self.badge_label = None
        
        header_layout.addStretch()
        self.header_btn.setLayout(header_layout)
        main_layout.addWidget(self.header_btn)
        
        # Content container
        self.content_widget = QWidget()
        self.content_widget.setObjectName("cardContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)
        main_layout.addWidget(self.content_widget)
        
        # Start state
        self.is_collapsed = start_collapsed
        if start_collapsed:
            self.content_widget.hide()
            self.indicator.setText("▶")
    
    def toggle_collapsed(self):
        """Toggle the collapsed state of the card."""
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.content_widget.hide()
            self.indicator.setText("▶")
        else:
            self.content_widget.show()
            self.indicator.setText("▼")
    
    def set_collapsed(self, collapsed: bool):
        """Set collapsed state explicitly."""
        if self.is_collapsed != collapsed:
            self.toggle_collapsed()
    
    def get_content_layout(self) -> QVBoxLayout:
        """Get the content layout to add widgets to."""
        return self.content_layout
    
    def set_badge_text(self, text: str):
        """Update badge text."""
        if self.badge_label:
            self.badge_label.setText(text)
        elif text:
            # Create badge if it doesn't exist
            self.badge_label = QLabel(text)
            self.badge_label.setObjectName("cardBadge")
            self.header_btn.layout().insertWidget(2, self.badge_label)


class ToastNotification(QWidget):
    """
    Modern toast notification widget for brief user feedback.
    
    Features:
    - Appears bottom-right of parent window
    - Auto-dismisses after timeout (default 3 seconds)
    - Smooth fade-in/fade-out animations
    - Can be manually dismissed
    - Icon support for different message types (info, success, warning, error)
    
    Usage:
        toast = ToastNotification.show_message(
            parent_window, 
            "Configuration saved!", 
            ToastNotification.SUCCESS,
            duration=3000
        )
    
    Note:
        Uses QPropertyAnimation for smooth fade effects.
        Automatically destroys itself after animation completes.
    """
    
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    
    def __init__(self, parent, message, message_type=INFO, duration=3000):
        """
        Initialize toast notification.
        
        Args:
            parent: Parent window
            message: Message text to display
            message_type: Type of message (INFO, SUCCESS, WARNING, ERROR)
            duration: How long to show toast in milliseconds (default 3000)
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Setup UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Icon based on type
        icon_text = {
            self.INFO: "ℹ️",
            self.SUCCESS: "✅",
            self.WARNING: "⚠️",
            self.ERROR: "❌"
        }.get(message_type, "ℹ️")
        
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            color: #ffffff;
            font-size: 10pt;
            padding: 0 8px;
        """)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Background color based on type
        bg_colors = {
            self.INFO: "#4a9aff",
            self.SUCCESS: "#4ade80",
            self.WARNING: "#fb923c",
            self.ERROR: "#ef4444"
        }
        bg_color = bg_colors.get(message_type, "#4a9aff")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        
        self.adjustSize()
        self.duration = duration
        
    def show_animated(self):
        """Show toast with fade-in animation."""
        # Position at bottom-right of parent
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - 20
            y = parent_rect.height() - self.height() - 20
            self.move(x, y)
        
        # Fade in
        self.setWindowOpacity(0)
        self.show()
        
        fade_in = QPropertyAnimation(self, b"windowOpacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0)
        fade_in.setEndValue(0.95)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_in.finished.connect(self.start_timer)
        fade_in.start()
        
        self.fade_in_anim = fade_in  # Keep reference
    
    def start_timer(self):
        """Start countdown to auto-dismiss."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(self.duration, self.hide_animated)
    
    def hide_animated(self):
        """Hide toast with fade-out animation."""
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(0.95)
        fade_out.setEndValue(0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self.deleteLater)
        fade_out.start()
        
        self.fade_out_anim = fade_out  # Keep reference
    
    @staticmethod
    def show_message(parent, message, message_type=INFO, duration=3000):
        """
        Static method to show a toast notification.
        
        Args:
            parent: Parent window
            message: Message text
            message_type: Type of message (INFO, SUCCESS, WARNING, ERROR)
            duration: Display duration in milliseconds
            
        Returns:
            ToastNotification instance
            
        Example:
            ToastNotification.show_message(self, "Key assigned: KC.A", ToastNotification.SUCCESS)
        """
        toast = ToastNotification(parent, message, message_type, duration)
        toast.show_animated()
        return toast


# --- Main Application Window ---
class KMKConfigurator(QMainWindow):
    """The main application window for configuring KMK-based macropads."""

    class KeycodeListItemDelegate(QStyledItemDelegate):
        """Custom delegate to render keycode entries with right-aligned labels."""

        def __init__(self, parent_list: QListWidget):
            super().__init__(parent_list)
            base_font = parent_list.font()
            self._key_font = QFont(base_font)
            self._label_font = QFont(base_font)

        def paint(self, painter: QPainter, option, index):
            if not (index.flags() & Qt.ItemFlag.ItemIsSelectable):
                super().paint(painter, option, index)
                return

            painter.save()
            self.initStyleOption(option, index)
            text_value = option.text
            option.text = ""
            style = option.widget.style() if option.widget else QApplication.style()
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, option.widget)

            rect = option.rect.adjusted(12, 0, -12, 0)
            label = index.data(Qt.ItemDataRole.UserRole + 1) or ""

            if option.state & QStyle.StateFlag.State_Selected:
                pen_color = option.palette.highlightedText().color()
            else:
                pen_color = option.palette.text().color()

            painter.setPen(pen_color)
            painter.setFont(self._key_font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text_value)

            if label:
                painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, label)

            painter.restore()

        def sizeHint(self, option, index):
            base_hint = super().sizeHint(option, index)
            if base_hint.height() < 28:
                base_hint.setHeight(28)
            return base_hint

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KMK Macropad Configurator - Chronos Pad v1.0.0-beta")
        
        # Set minimum window size and better default size
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
        
        # Center window on screen
        self.center_on_screen()

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
        self.layer_clipboard = None  # For copy/paste layer operations
        self.key_clipboard = None  # For copy/paste individual key operations
        
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
        self.encoder_divisor = 4
        self.encoder_config_str = DEFAULT_ENCODER_CONFIG  # Pre-populate with default
        self.enable_analogin = True
        self.analogin_config_str = DEFAULT_ANALOGIN_CONFIG  # Pre-populate with default
        self.enable_rgb = True
        self.rgb_matrix_config = build_default_rgb_matrix_config()
        self.enable_display = True
        self.display_config_str = ""
        self.boot_config_str = ""  # boot.py configuration
        self.custom_ext_code = ""  # Custom extension code snippets

        self.initialize_keymap_data()

        # Load persisted extension configs (if any)
        self.load_extension_configs()

        # --- UI Initialization ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_container_layout = QVBoxLayout(central_widget)
        main_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create main horizontal splitter for resizable panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(4)
        self.main_splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing completely

        # --- Left Panel (File & Extensions) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)

        self.setup_file_io_ui(left_layout)
        self.setup_extensions_ui(left_layout)
        left_layout.addStretch()  # Push everything to the top
        
        # --- Center Panel (Macropad Grid) ---
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(5, 5, 5, 5)
        center_layout.setSpacing(10)
        
        self.setup_layer_management_ui(center_layout)
        self.setup_grid_actions_bar(center_layout)  # Add grid actions bar
        self.setup_macropad_grid_ui(center_layout)

        # --- Right Panel (Keycode Selection, Macros, TapDance) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)

        self.setup_keycode_selector_ui(right_layout)
        # Macros and TapDance are now integrated into keycode selector
        # self.setup_macro_ui(right_layout)  # REMOVED: Now part of keycode selector
        
        # Add panels to splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(center_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes: Left=250px, Center=500px, Right=550px (total ~1300)
        # These are initial suggestions; user can resize
        self.main_splitter.setSizes([250, 500, 550])
        
        # Add splitter to main container
        main_container_layout.addWidget(self.main_splitter)
        
        # --- Final UI Population ---
        self.recreate_macropad_grid()
        # self.load_profiles()  # REMOVED: Profile selector disabled
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
    
    def center_on_screen(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def check_dependencies(self):
        """Check if KMK firmware and CircuitPython libraries are available, download if not"""
        if os.environ.get("KMK_SKIP_DEP_CHECK"):
            return
        
        libraries_dir = os.path.join(BASE_DIR, "libraries")
        kmk_path = os.path.join(libraries_dir, "kmk_firmware-main")
        
        # Always use CircuitPython 10.x
        cp_version = 10
        bundle_path = os.path.join(libraries_dir, f"adafruit-circuitpython-bundle-{cp_version}.x-mpy")
        
        # Check if both dependencies exist
        if os.path.exists(kmk_path) and os.path.exists(bundle_path):
            return  # Both dependencies exist
        
        # Dependencies missing - download automatically
        self.progress_dialog = QProgressDialog(
            "Downloading required dependencies...\n\n"
            "• KMK Firmware (GPL-3.0 license)\n"
            "• Adafruit CircuitPython Bundle 10.x (MIT license)\n\n"
            "This only happens once on first run.",
            None, 0, 100, self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setCancelButton(None)  # No cancel button
        self.progress_dialog.show()
        
        # Start download thread with CircuitPython 10
        self.downloader = DependencyDownloader(cp_version=cp_version)
        self.downloader.progress.connect(self.on_download_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.start()
    
    def show_cp_version_dialog(self):
        """Show dialog to select CircuitPython bundle version
        
        Returns:
            int: Selected version (9 or 10), or None if cancelled
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Select CircuitPython Version")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Title and description
        title_label = QLabel("<h3>CircuitPython Bundle Version</h3>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Please select which CircuitPython bundle version to download.\n"
            "This should match the CircuitPython version installed on your device.\n\n"
            "• CircuitPython 9.x: For CircuitPython 9.0 and newer (up to 9.x)\n"
            "• CircuitPython 10.x: For CircuitPython 10.0 and newer\n\n"
            "If you're unsure, CircuitPython 9.x is recommended for most Pico boards."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Version selection buttons
        button_layout = QHBoxLayout()
        
        version_9_btn = QPushButton("CircuitPython 9.x")
        version_9_btn.setMinimumHeight(60)
        version_9_btn.clicked.connect(lambda: dialog.done(9))
        button_layout.addWidget(version_9_btn)
        
        version_10_btn = QPushButton("CircuitPython 10.x")
        version_10_btn.setMinimumHeight(60)
        version_10_btn.clicked.connect(lambda: dialog.done(10))
        button_layout.addWidget(version_10_btn)
        
        layout.addLayout(button_layout)
        
        # Note about changing later
        note_label = QLabel(
            "<small><i>Note: You can change this later by deleting the 'settings.json' file.</i></small>"
        )
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        result = dialog.exec()
        return result if result in (9, 10) else None
    
    def show_macro_import_dialog(self, new_macros):
        """Show dialog to import new macros from config file
        
        Args:
            new_macros: Dictionary of {macro_name: actions} for macros not in global store
            
        Returns:
            dict: Selected macros to import, or empty dict if none selected
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Macros")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Title and description
        title_label = QLabel(f"<h3>New Macros Found ({len(new_macros)})</h3>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "This configuration file contains macros that are not in your global macro store.\n"
            "Select which macros you want to import. Imported macros will be available\n"
            "across all configurations."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Scrollable list of macros with checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Store checkboxes for later retrieval
        macro_checkboxes = {}
        
        for macro_name, actions in new_macros.items():
            checkbox = QCheckBox(macro_name)
            checkbox.setChecked(True)  # Default to checked
            
            # Add description of macro actions
            action_count = len(actions)
            action_preview = f"  ({action_count} action{'s' if action_count != 1 else ''})"
            if actions:
                first_action = actions[0]
                if isinstance(first_action, (list, tuple)) and len(first_action) >= 2:
                    action_type = first_action[0]
                    action_preview += f" - starts with {action_type}"
            
            checkbox.setText(f"{macro_name}{action_preview}")
            checkbox.setToolTip(f"Macro: {macro_name}\nActions: {action_count}")
            
            scroll_layout.addWidget(checkbox)
            macro_checkboxes[macro_name] = checkbox
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Button box with Select All / Deselect All / Import / Cancel
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in macro_checkboxes.values()])
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in macro_checkboxes.values()])
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        button_layout.addWidget(buttons)
        
        layout.addLayout(button_layout)
        
        # Show dialog and collect results
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Return only checked macros
            selected_macros = {
                name: new_macros[name]
                for name, checkbox in macro_checkboxes.items()
                if checkbox.isChecked()
            }
            return selected_macros
        
        return {}
    
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
                # Restore session state after loading config
                self.restore_session_state()
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
        self.boot_config_str = ""
        
        # Update display
        self.update_layer_tabs()
        self.update_macropad_display()
        self.update_macro_list()
        self.sync_extension_checkboxes()
        self.update_extension_button_states()
        self.refresh_boot_config_ui()
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
        """
        Apply modern cheerful theme (vibrant dark variant).
        
        Features:
        - Warmer, more vibrant colors than standard dark theme
        - Same modern principles as other themes
        - Consistent hover/focus behavior
        """
        base = self._base_geometry_qss()
        cards = self._get_modern_card_stylesheet()
        color_qss = '''
            /* Base colors - warmer grays */
            QWidget { 
                background-color: #2d3748; 
                color: #e5e7eb; 
            }
            QMainWindow { 
                background-color: #1a202c; 
            }
            
            /* Buttons with smooth hover effects */
            QPushButton { 
                background: #4a5568; 
                border: 1px solid #5a6778; 
                color: #e5e7eb;
            }
            QPushButton:hover { 
                background: #5a6778; 
                border: 1px solid #6b7888;
            }
            QPushButton:pressed { 
                background: #3a4558; 
                border: 1px solid #4a5568;
            }
            QPushButton:disabled {
                background: #2d3748;
                color: #6b7280;
                border: 1px solid #4a5568;
            }
            
            /* Selected keymap button */
            QPushButton#keymapButton:checked { 
                background-color: #2a5a8a; 
                border: 3px solid #4a9aff; 
                color: #ffffff; 
                font-weight: bold;
            }
            
            /* Tab bars */
            QTabWidget::pane {
                background: #2d3748;
                border: 1px solid #4a5568;
            }
            QTabBar::tab { 
                background: #4a5568; 
                color: #9ca3af;
            }
            QTabBar::tab:hover {
                background: #5a6778;
                color: #e5e7eb;
            }
            QTabBar::tab:selected { 
                background: #4a9aff; 
                color: #ffffff;
                font-weight: 600;
            }
            
            /* List widgets */
            QListWidget {
                background: #2d3748;
                border: 1px solid #4a5568;
            }
            QListWidget::item:hover { 
                background-color: #4a5568; 
            }
            QListWidget::item:selected { 
                background-color: #4a9aff; 
                color: #ffffff; 
                font-weight: 600; 
            }
            
            /* Labels */
            QLabel { 
                color: #e5e7eb; 
            }
            QLabel#cardTitle {
                color: #f9fafb;
            }
            QLabel#infoBox { 
                background-color: #1e4d2b; 
                color: #4ade80; 
                padding: 10px; 
                border-radius: 6px;
                border: 1px solid #166534;
            }
            
            /* Input fields */
            QLineEdit, QTextEdit { 
                background-color: #4a5568; 
                border: 1px solid #5a6778; 
                color: #f9fafb; 
            }
            QLineEdit:focus, QTextEdit:focus { 
                border: 2px solid #4a9aff; 
                background-color: #2d3748; 
            }
            QSpinBox, QDoubleSpinBox { 
                background-color: #4a5568; 
                border: 1px solid #5a6778; 
                color: #f9fafb; 
            }
            QSpinBox:focus, QDoubleSpinBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #2d3748; 
            }
            QComboBox { 
                background-color: #4a5568; 
                border: 1px solid #5a6778; 
                color: #f9fafb; 
            }
            QComboBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #2d3748; 
            }
            QComboBox::drop-down { 
                border: none; 
                padding-right: 4px;
            }
            QComboBox QAbstractItemView { 
                background-color: #4a5568; 
                color: #f9fafb; 
                selection-background-color: #4a9aff;
                border: 1px solid #5a6778;
                border-radius: 4px;
            }
            
            /* Group boxes */
            QGroupBox { 
                border: 1px solid #4a5568; 
                color: #e5e7eb;
                background-color: #2d3748;
            }
            QGroupBox::title {
                color: #f9fafb;
            }
            
            /* Modern cards */
            QFrame#card {
                background-color: #374151;
                border: 1px solid #4a5568;
            }
            
            /* Collapsible card header */
            QPushButton#cardHeader {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 0;
            }
            QPushButton#cardHeader:hover {
                background-color: #4a5568;
            }
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 11pt;
                color: #f9fafb;
            }
            QLabel#cardIndicator {
                color: #9ca3af;
                font-size: 10pt;
                margin-right: 8px;
            }
            QLabel#cardBadge {
                background-color: #4a9aff;
                color: #ffffff;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 9pt;
                font-weight: 600;
                margin-left: 8px;
            }
            QWidget#cardContent {
                background-color: transparent;
            }
            
            /* Toggle Switch styling */
            QCheckBox#toggleSwitch {
                spacing: 8px;
            }
            QCheckBox#toggleSwitch::indicator {
                width: 48px;
                height: 24px;
                border-radius: 12px;
                background-color: #5a6778;
                border: 2px solid #6b7888;
            }
            QCheckBox#toggleSwitch::indicator:checked {
                background-color: #4a9aff;
                border: 2px solid #4a9aff;
            }
            QCheckBox#toggleSwitch::indicator:hover {
                border: 2px solid #9ca3af;
            }
            QCheckBox#toggleSwitch::indicator:checked:hover {
                background-color: #60a5fa;
                border: 2px solid #60a5fa;
            }
            QCheckBox#toggleSwitch:disabled {
                color: #6b7280;
            }
            QCheckBox#toggleSwitch::indicator:disabled {
                background-color: #4a5568;
                border: 2px solid #5a6778;
            }
            
            /* Checkboxes */
            QCheckBox, QRadioButton {
                color: #e5e7eb;
            }
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                background-color: #4a5568;
                border: 1px solid #5a6778;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #4a9aff;
                border: 1px solid #4a9aff;
            }
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                border: 1px solid #6b7888;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: #2d3748;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #5a6778;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6b7888;
            }
            QScrollBar:horizontal {
                background: #2d3748;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #5a6778;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6b7888;
            }
        '''
        self.setStyleSheet(base + cards + color_qss)

    def _apply_light_stylesheet(self):
        """
        Apply modern light theme with Material Design principles.
        
        Features:
        - Clean, bright surfaces with subtle shadows
        - Consistent color palette matching dark theme
        - Smooth hover/focus transitions
        - High contrast for readability
        """
        base = self._base_geometry_qss()
        cards = self._get_modern_card_stylesheet()
        color_qss = '''
            /* Base colors */
            QWidget { 
                background-color: #f9fafb; 
                color: #1f2937; 
            }
            QMainWindow { 
                background-color: #f3f4f6; 
            }
            
            /* Buttons */
            QPushButton { 
                background: #ffffff; 
                border: 1px solid #d1d5db; 
                color: #1f2937;
            }
            QPushButton:hover { 
                background: #f3f4f6; 
                border: 1px solid #9ca3af;
            }
            QPushButton:pressed { 
                background: #e5e7eb; 
                border: 1px solid #9ca3af;
            }
            QPushButton:disabled {
                background: #f3f4f6;
                color: #9ca3af;
                border: 1px solid #e5e7eb;
            }
            
            /* Selected keymap button */
            QPushButton#keymapButton:checked { 
                background-color: #5a9adf; 
                border: 3px solid #2070c0; 
                color: #ffffff; 
                font-weight: bold;
            }
            
            /* Tab bars */
            QTabWidget::pane {
                background: #ffffff;
                border: 1px solid #e5e7eb;
            }
            QTabBar::tab { 
                background: #f3f4f6; 
                color: #6b7280;
            }
            QTabBar::tab:hover {
                background: #e5e7eb;
                color: #1f2937;
            }
            QTabBar::tab:selected { 
                background: #4a9aff; 
                color: #ffffff;
                font-weight: 600;
            }
            
            /* List widgets */
            QListWidget {
                background: #ffffff;
                border: 1px solid #e5e7eb;
            }
            QListWidget::item:hover { 
                background-color: #f3f4f6; 
            }
            QListWidget::item:selected { 
                background-color: #4a9aff; 
                color: #ffffff; 
                font-weight: 600; 
            }
            
            /* Labels */
            QLabel { 
                color: #1f2937; 
            }
            QLabel#cardTitle {
                color: #111827;
            }
            QLabel#infoBox { 
                background-color: #E8F5E9; 
                color: #1b5e20; 
                padding: 10px; 
                border-radius: 6px;
                border: 1px solid #a5d6a7;
            }
            
            /* Input fields */
            QLineEdit, QTextEdit { 
                background-color: #ffffff; 
                border: 1px solid #d1d5db; 
                color: #1f2937; 
            }
            QLineEdit:focus, QTextEdit:focus { 
                border: 2px solid #4a9aff; 
                background-color: #f9fafb; 
            }
            QSpinBox, QDoubleSpinBox { 
                background-color: #ffffff; 
                border: 1px solid #d1d5db; 
                color: #1f2937; 
            }
            QSpinBox:focus, QDoubleSpinBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #f9fafb; 
            }
            QComboBox { 
                background-color: #ffffff; 
                border: 1px solid #d1d5db; 
                color: #1f2937; 
            }
            QComboBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #f9fafb; 
            }
            QComboBox::drop-down { 
                border: none; 
                padding-right: 4px;
            }
            QComboBox QAbstractItemView { 
                background-color: #ffffff; 
                color: #1f2937; 
                selection-background-color: #4a9aff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
            }
            
            /* Group boxes */
            QGroupBox { 
                border: 1px solid #e5e7eb; 
                color: #1f2937;
                background-color: #ffffff;
            }
            QGroupBox::title {
                color: #111827;
            }
            
            /* Modern cards */
            QFrame#card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
            }
            
            /* Collapsible card header */
            QPushButton#cardHeader {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 0;
            }
            QPushButton#cardHeader:hover {
                background-color: #f3f4f6;
            }
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 11pt;
                color: #111827;
            }
            QLabel#cardIndicator {
                color: #6b7280;
                font-size: 10pt;
                margin-right: 8px;
            }
            QLabel#cardBadge {
                background-color: #4a9aff;
                color: #ffffff;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 9pt;
                font-weight: 600;
                margin-left: 8px;
            }
            QWidget#cardContent {
                background-color: transparent;
            }
            
            /* Toggle Switch styling */
            QCheckBox#toggleSwitch {
                spacing: 8px;
            }
            QCheckBox#toggleSwitch::indicator {
                width: 48px;
                height: 24px;
                border-radius: 12px;
                background-color: #d1d5db;
                border: 2px solid #9ca3af;
            }
            QCheckBox#toggleSwitch::indicator:checked {
                background-color: #4a9aff;
                border: 2px solid #4a9aff;
            }
            QCheckBox#toggleSwitch::indicator:hover {
                border: 2px solid #6b7280;
            }
            QCheckBox#toggleSwitch::indicator:checked:hover {
                background-color: #60a5fa;
                border: 2px solid #60a5fa;
            }
            QCheckBox#toggleSwitch:disabled {
                color: #9ca3af;
            }
            QCheckBox#toggleSwitch::indicator:disabled {
                background-color: #f3f4f6;
                border: 2px solid #d1d5db;
            }
            
            /* Checkboxes */
            QCheckBox, QRadioButton {
                color: #1f2937;
            }
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #4a9aff;
                border: 1px solid #4a9aff;
            }
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                border: 1px solid #9ca3af;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: #f9fafb;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #d1d5db;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }
            QScrollBar:horizontal {
                background: #f9fafb;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #d1d5db;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #9ca3af;
            }
        '''
        self.setStyleSheet(base + cards + color_qss)

    def _apply_dark_stylesheet(self):
        """
        Apply modern dark theme with Material Design principles.
        
        Features:
        - Elevated surfaces with subtle shadows
        - Consistent color palette (#4a9aff blue, #4ade80 green, #fb923c orange, #ef4444 red)
        - Smooth hover/focus transitions
        - High contrast for accessibility
        """
        base = self._base_geometry_qss()
        cards = self._get_modern_card_stylesheet()
        color_qss = '''
            /* Base colors */
            QWidget { 
                background-color: #1f2937; 
                color: #e5e7eb; 
            }
            QMainWindow { 
                background-color: #111827; 
            }
            
            /* Buttons with smooth hover effects */
            QPushButton { 
                background: #374151; 
                border: 1px solid #4b5563; 
                color: #e5e7eb;
            }
            QPushButton:hover { 
                background: #4b5563; 
                border: 1px solid #6b7280;
            }
            QPushButton:pressed { 
                background: #1f2937; 
                border: 1px solid #4b5563;
            }
            QPushButton:disabled {
                background: #1f2937;
                color: #6b7280;
                border: 1px solid #374151;
            }
            
            /* Selected keymap button with glow effect */
            QPushButton#keymapButton:checked { 
                background-color: #2a5a8a; 
                border: 3px solid #4a9aff; 
                color: #ffffff; 
                font-weight: bold;
            }
            
            /* Tab bars */
            QTabWidget::pane {
                background: #1f2937;
                border: 1px solid #374151;
            }
            QTabBar::tab { 
                background: #374151; 
                color: #9ca3af;
            }
            QTabBar::tab:hover {
                background: #4b5563;
                color: #e5e7eb;
            }
            QTabBar::tab:selected { 
                background: #4a9aff; 
                color: #ffffff;
                font-weight: 600;
            }
            
            /* List widgets with hover effects */
            QListWidget {
                background: #1f2937;
                border: 1px solid #374151;
            }
            QListWidget::item:hover { 
                background-color: #374151; 
            }
            QListWidget::item:selected { 
                background-color: #4a9aff; 
                color: #ffffff; 
                font-weight: 600; 
            }
            
            /* Labels and text */
            QLabel { 
                color: #e5e7eb; 
            }
            QLabel#cardTitle {
                color: #f9fafb;
            }
            
            /* Info boxes with themed backgrounds */
            QLabel#infoBox { 
                background-color: #1e4d2b; 
                color: #4ade80; 
                padding: 10px; 
                border-radius: 6px;
                border: 1px solid #166534;
            }
            
            /* Input fields with focus effects */
            QLineEdit, QTextEdit { 
                background-color: #374151; 
                border: 1px solid #4b5563; 
                color: #f9fafb; 
            }
            QLineEdit:focus, QTextEdit:focus { 
                border: 2px solid #4a9aff; 
                background-color: #1f2937; 
            }
            
            /* Spin boxes */
            QSpinBox, QDoubleSpinBox { 
                background-color: #374151; 
                border: 1px solid #4b5563; 
                color: #f9fafb; 
            }
            QSpinBox:focus, QDoubleSpinBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #1f2937; 
            }
            
            /* Combo boxes */
            QComboBox { 
                background-color: #374151; 
                border: 1px solid #4b5563; 
                color: #f9fafb; 
            }
            QComboBox:focus { 
                border: 2px solid #4a9aff; 
                background-color: #1f2937; 
            }
            QComboBox::drop-down { 
                border: none; 
                padding-right: 4px;
            }
            QComboBox QAbstractItemView { 
                background-color: #374151; 
                color: #f9fafb; 
                selection-background-color: #4a9aff;
                border: 1px solid #4b5563;
                border-radius: 4px;
            }
            
            /* Group boxes with card styling */
            QGroupBox { 
                border: 1px solid #374151; 
                color: #e5e7eb;
                background-color: #1f2937;
            }
            QGroupBox::title {
                color: #f9fafb;
            }
            
            /* Modern cards */
            QFrame#card {
                background-color: #2d3748;
                border: 1px solid #374151;
            }
            
            /* Collapsible card header */
            QPushButton#cardHeader {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 0;
            }
            QPushButton#cardHeader:hover {
                background-color: #374151;
            }
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 11pt;
                color: #f9fafb;
            }
            QLabel#cardIndicator {
                color: #9ca3af;
                font-size: 10pt;
                margin-right: 8px;
            }
            QLabel#cardBadge {
                background-color: #4a9aff;
                color: #ffffff;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 9pt;
                font-weight: 600;
                margin-left: 8px;
            }
            QWidget#cardContent {
                background-color: transparent;
            }
            
            /* Toggle Switch styling */
            QCheckBox#toggleSwitch {
                spacing: 8px;
            }
            QCheckBox#toggleSwitch::indicator {
                width: 48px;
                height: 24px;
                border-radius: 12px;
                background-color: #4b5563;
                border: 2px solid #6b7280;
            }
            QCheckBox#toggleSwitch::indicator:checked {
                background-color: #4a9aff;
                border: 2px solid #4a9aff;
            }
            QCheckBox#toggleSwitch::indicator:hover {
                border: 2px solid #9ca3af;
            }
            QCheckBox#toggleSwitch::indicator:checked:hover {
                background-color: #60a5fa;
                border: 2px solid #60a5fa;
            }
            QCheckBox#toggleSwitch:disabled {
                color: #6b7280;
            }
            QCheckBox#toggleSwitch::indicator:disabled {
                background-color: #374151;
                border: 2px solid #4b5563;
            }
            
            /* Category Pills (horizontal keycode category buttons) */
            QPushButton#categoryPill {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 16px;
                padding: 6px 16px;
                color: #9ca3af;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton#categoryPill:hover {
                background-color: #4b5563;
                border: 1px solid #6b7280;
                color: #e5e7eb;
            }
            QPushButton#categoryPill:checked {
                background-color: #4a9aff;
                border: 2px solid #60a5fa;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton#categoryPill:checked:hover {
                background-color: #60a5fa;
                border: 2px solid #60a5fa;
            }
            QPushButton#categoryPill:pressed {
                background-color: #2563eb;
            }
            
            /* Checkboxes and radio buttons */
            QCheckBox, QRadioButton {
                color: #e5e7eb;
            }
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                background-color: #374151;
                border: 1px solid #4b5563;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #4a9aff;
                border: 1px solid #4a9aff;
            }
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                border: 1px solid #6b7280;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: #1f2937;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4b5563;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6b7280;
            }
            QScrollBar:horizontal {
                background: #1f2937;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #4b5563;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6b7280;
            }
        '''
        self.setStyleSheet(base + cards + color_qss)

    def _get_modern_card_stylesheet(self):
        """
        Generate QSS stylesheet for modern card-based layout.
        
        Cards use rounded corners (8px), subtle shadows, and consistent spacing
        following Material Design principles. Returns color-independent rules 
        that work across all themes.
        
        Returns:
            str: QSS stylesheet string for card components
            
        Note:
            Theme-specific colors are applied in theme methods (_apply_dark_stylesheet, etc.)
        """
        return '''
            /* Modern Card-Based Layout */
            QFrame#card {
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
            
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 11pt;
                margin-bottom: 8px;
            }
            
            /* Card sections with subtle elevation */
            QGroupBox#cardSection {
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
                font-weight: 600;
            }
        '''

    def _base_geometry_qss(self):
        """
        Return QSS that defines geometry/shape/layout-only rules shared across themes.
        
        Implements Material Design spacing system (4px/8px/16px/24px) and modern
        visual elements including rounded corners, smooth transitions, and proper spacing.
        
        Returns:
            str: QSS stylesheet with theme-independent geometry rules
        """
        return '''
            /* Base geometry and shape rules (theme-independent) */
            
            /* Buttons with smooth animations */
            QPushButton {
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 64px;
            }
            
            /* Group boxes with modern styling */
            QGroupBox {
                border-radius: 8px;
                margin-top: 12px;
                font-weight: 600;
                padding: 12px;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 4px 8px;
                left: 8px;
            }
            
            /* Tab widgets with rounded corners */
            QTabWidget::pane { 
                border-radius: 8px; 
                padding: 8px;
            }
            QTabBar::tab { 
                padding: 8px 12px; 
                border-radius: 6px; 
                margin-right: 4px;
                margin-bottom: 2px;
            }
            
            /* Input fields with consistent styling */
            QLineEdit, QSpinBox, QComboBox { 
                border-radius: 6px; 
                padding: 6px 10px;
                min-height: 24px;
            }
            QTextEdit {
                border-radius: 6px;
                padding: 8px;
            }
            
            /* List widgets with rounded corners */
            QListWidget { 
                border-radius: 8px; 
                padding: 4px;
            }
            QListWidget::item {
                border-radius: 4px;
                padding: 6px 8px;
                margin: 2px 4px;
            }
            
            /* Checkboxes and radio buttons */
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
            }
            QRadioButton::indicator {
                border-radius: 9px;
            }
        '''
    
    def get_info_box_style(self, variant='info'):
        """Get theme-aware style for info boxes
        
        Args:
            variant: 'info' (blue), 'success' (green), 'warning' (orange), or 'neutral' (gray)
        """
        if self.current_theme == 'Dark':
            # Dark mode - darker backgrounds with lighter text
            styles = {
                'info': "background-color: #1e3a5f; color: #b3d4ff; padding: 10px; border-radius: 4px;",
                'success': "background-color: #1e4d2b; color: #b3e6c0; padding: 10px; border-radius: 4px;",
                'warning': "background-color: #5f4a1e; color: #ffd699; padding: 10px; border-radius: 4px;",
                'neutral': "background-color: #3a3a3a; color: #d5d5d5; padding: 10px; border-radius: 4px;"
            }
        elif self.current_theme == 'Light':
            # Light mode - light backgrounds with dark text
            styles = {
                'info': "background-color: #E3F2FD; color: #0d47a1; padding: 10px; border-radius: 4px;",
                'success': "background-color: #E8F5E9; color: #1b5e20; padding: 10px; border-radius: 4px;",
                'warning': "background-color: #FFF3E0; color: #e65100; padding: 10px; border-radius: 4px;",
                'neutral': "background-color: #f5f5f5; color: #424242; padding: 10px; border-radius: 4px;"
            }
        else:  # Cheerful
            # Cheerful mode - similar to light but with more vibrant colors
            styles = {
                'info': "background-color: #E3F2FD; color: #0d47a1; padding: 10px; border-radius: 4px;",
                'success': "background-color: #E8F5E9; color: #1b5e20; padding: 10px; border-radius: 4px;",
                'warning': "background-color: #FFF3E0; color: #e65100; padding: 10px; border-radius: 4px;",
                'neutral': "background-color: #f5f5f5; color: #424242; padding: 10px; border-radius: 4px;"
            }
        
        return styles.get(variant, styles['neutral'])

    # --- Extension config persistence ---
    def save_extension_configs(self):
        try:
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            meta = {
                "enable_encoder": self.enable_encoder,
                "enable_analogin": self.enable_analogin,
                "enable_rgb": self.enable_rgb,
                "enable_display": self.enable_display,
                "encoder_divisor": self.encoder_divisor,
                "custom_ext_code": self.custom_ext_code,
            }
            with open(os.path.join(CONFIG_SAVE_DIR, 'extensions.json'), 'w') as f:
                json.dump(meta, f, indent=2)

            with open(os.path.join(CONFIG_SAVE_DIR, 'encoder.py'), 'w') as f:
                encoder_content = self.encoder_config_str or ''
                if (
                    self.encoder_divisor
                    and 'encoder_handler = EncoderHandler()' in encoder_content
                    and 'encoder_handler.divisor' not in encoder_content
                ):
                    replacement = (
                        "encoder_handler = EncoderHandler()\n"
                        f"encoder_handler.divisor = {int(self.encoder_divisor)}"
                    )
                    encoder_content = encoder_content.replace(
                        'encoder_handler = EncoderHandler()', replacement, 1
                    )
                f.write(encoder_content)
            with open(os.path.join(CONFIG_SAVE_DIR, 'analogin.py'), 'w') as f:
                f.write(self.analogin_config_str or '')
            with open(os.path.join(CONFIG_SAVE_DIR, 'display.py'), 'w') as f:
                f.write(self.display_config_str or '')
            
            # Save boot.py configuration - use the stored boot_config_str directly
            with open(os.path.join(CONFIG_SAVE_DIR, 'boot.py'), 'w') as f:
                f.write(self.boot_config_str or '')

            rgb_config = self._export_rgb_config()
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
                self.encoder_divisor = int(meta.get('encoder_divisor', self.encoder_divisor or 4))
                self.custom_ext_code = meta.get('custom_ext_code', "")
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
            boot_path = os.path.join(CONFIG_SAVE_DIR, 'boot.py')
            if os.path.exists(boot_path):
                with open(boot_path, 'r') as f:
                    self.boot_config_str = f.read()
            rgb_path = os.path.join(CONFIG_SAVE_DIR, 'rgb_matrix.json')
            if os.path.exists(rgb_path):
                with open(rgb_path, 'r') as f:
                    data = json.load(f)
                merged = build_default_rgb_matrix_config()
                merged.update(data)
                merged['key_colors'] = dict(data.get('key_colors', {}))
                layer_colors_raw = data.get('layer_key_colors', {}) or {}
                layer_colors = {}
                for layer, mapping in layer_colors_raw.items():
                    sanitized = {
                        str(k): ensure_hex_prefix(v, merged.get('default_key_color', '#FFFFFF'))
                        for k, v in (mapping or {}).items()
                    }
                    if sanitized:
                        layer_colors[str(layer)] = sanitized
                if not layer_colors and merged['key_colors']:
                    layer_colors['0'] = dict(merged['key_colors'])
                merged['layer_key_colors'] = layer_colors
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
                config['layer_key_colors'] = {'0': dict(config['key_colors'])} if config['key_colors'] else {}
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
        """Load UI settings (theme and session state) from kmk_Config_Save/ui_settings.json."""
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

    def save_session_state(self):
        """Save current UI session state (layer, selected key, active tabs, splitter sizes, category)."""
        try:
            os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
            
            # Get splitter sizes if available
            splitter_sizes = []
            if hasattr(self, 'main_splitter'):
                splitter_sizes = self.main_splitter.sizes()
            
            session_data = {
                'current_layer': self.current_layer,
                'selected_key_coords': self.selected_key_coords,
                'extension_tab_index': getattr(self.extensions_tabs, 'currentIndex', lambda: 0)(),
                'keycode_current_category': getattr(self, 'current_category', None),
                'keycode_search_query': getattr(self.keycode_search_box, 'text', lambda: '')() if hasattr(self, 'keycode_search_box') else '',
                'splitter_sizes': splitter_sizes,
            }
            session_path = os.path.join(CONFIG_SAVE_DIR, 'session.json')
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=4)
        except Exception:
            pass

    def restore_session_state(self):
        """Restore UI session state from last session."""
        try:
            session_path = os.path.join(CONFIG_SAVE_DIR, 'session.json')
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
                
                # Restore current layer
                layer = session_data.get('current_layer', 0)
                if 0 <= layer < len(self.keymap_data):
                    self.current_layer = layer
                    # Update layer tabs UI
                    if hasattr(self, 'layer_tabs'):
                        self.layer_tabs.setCurrentIndex(layer)
                
                # Restore selected key
                coords = session_data.get('selected_key_coords')
                if coords and isinstance(coords, list) and len(coords) == 2:
                    row, col = coords
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        self.selected_key_coords = coords
                        self.update_macropad_display()
                
                # Restore extension tab
                ext_tab_idx = session_data.get('extension_tab_index', 0)
                if hasattr(self, 'extensions_tabs'):
                    max_idx = self.extensions_tabs.count() - 1
                    if 0 <= ext_tab_idx <= max_idx:
                        self.extensions_tabs.setCurrentIndex(ext_tab_idx)
                
                # Restore keycode category (new sidebar approach)
                category = session_data.get('keycode_current_category')
                if category and hasattr(self, 'select_category'):
                    if category in KEYCODES:
                        self.select_category(category)
                
                # Restore search query (optional)
                search_query = session_data.get('keycode_search_query', '')
                if search_query and hasattr(self, 'keycode_search_box'):
                    self.keycode_search_box.setText(search_query)
                
                # Restore splitter sizes
                splitter_sizes = session_data.get('splitter_sizes')
                if splitter_sizes and hasattr(self, 'main_splitter'):
                    if isinstance(splitter_sizes, list) and len(splitter_sizes) == 3:
                        self.main_splitter.setSizes(splitter_sizes)
                        
        except Exception:
            pass

    def setup_file_io_ui(self, parent_layout):
        """
        Setup modern file management UI with card-based layout.
        
        Features:
        - Collapsible cards for logical grouping
        - File Management card: config selector with recent files
        - Actions card: Load/Save/Generate buttons
        - Profiles card: Quick access to saved profiles
        - Theme card: Visual theme selector
        
        Note:
            Uses CollapsibleCard widgets for modern expandable sections.
        """
        # === File Management Card ===
        file_card = CollapsibleCard("📁 File Management")
        file_layout = file_card.get_content_layout()
        
        # Config file selector with refresh button
        file_select_layout = QHBoxLayout()
        file_select_layout.addWidget(QLabel("Current Config:"))
        self.config_file_combo = QComboBox()
        self.config_file_combo.setToolTip("Select a saved configuration to load")
        self.config_file_combo.activated.connect(self.load_config_from_dropdown)
        file_select_layout.addWidget(self.config_file_combo, 1)
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(35)
        refresh_btn.clicked.connect(self.populate_config_file_list)
        refresh_btn.setToolTip("Refresh configuration list")
        file_select_layout.addWidget(refresh_btn)
        file_layout.addLayout(file_select_layout)
        
        parent_layout.addWidget(file_card)
        
        # === Actions Card ===
        actions_card = CollapsibleCard("💾 Actions")
        actions_layout = actions_card.get_content_layout()
        
        # Two-column button layout for Load/Save
        row1_layout = QHBoxLayout()
        load_config_button = QPushButton("📂 Load")
        load_config_button.clicked.connect(self.load_configuration)
        load_config_button.setToolTip("Load the selected configuration file (Ctrl+O)")
        row1_layout.addWidget(load_config_button)
        
        save_config_button = QPushButton("💾 Save")
        save_config_button.clicked.connect(self.save_configuration_dialog)
        save_config_button.setToolTip("Save current keymap and settings (Ctrl+S)")
        row1_layout.addWidget(save_config_button)
        actions_layout.addLayout(row1_layout)
        
        # Generate code.py button (full width, prominent)
        generate_button = QPushButton("⚡ Generate code.py")
        generate_button.clicked.connect(self.generate_code_py_dialog)
        generate_button.setToolTip("Export firmware to CIRCUITPY drive")
        generate_button.setStyleSheet("QPushButton { font-weight: bold; }")
        actions_layout.addWidget(generate_button)
        
        parent_layout.addWidget(actions_card)
        
        # === REMOVED: Profiles Card (redundant with config save/load) ===
        # Profile functionality commented out to simplify UI
        # Users can use config file save/load instead
        
        """
        profile_card = CollapsibleCard("⭐ Quick Profiles")
        profile_layout = profile_card.get_content_layout()
        
        # Profile dropdown with delete button
        profile_selection_layout = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.load_selected_profile)
        self.profile_combo.setToolTip("Quick-load a saved profile with keymap and settings")
        profile_selection_layout.addWidget(self.profile_combo, 1)
        
        delete_profile_btn = QPushButton("🗑")
        delete_profile_btn.setFixedWidth(35)
        delete_profile_btn.clicked.connect(self.delete_selected_profile)
        delete_profile_btn.setToolTip("Delete selected profile")
        profile_selection_layout.addWidget(delete_profile_btn)
        profile_layout.addLayout(profile_selection_layout)
        
        # Save profile button
        save_profile_btn = QPushButton("💾 Save as Profile")
        save_profile_btn.clicked.connect(self.save_current_profile)
        save_profile_btn.setToolTip("Save current configuration as a named profile")
        profile_layout.addWidget(save_profile_btn)
        
        parent_layout.addWidget(profile_card)
        """
        
        # === Theme Card ===
        theme_card = CollapsibleCard("🎨 Theme")
        theme_layout = theme_card.get_content_layout()
        
        # Theme selector (radio buttons would be nice, but combo works for now)
        theme_select_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Cheerful"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.theme_combo.setToolTip("Change the UI color theme")
        # Reflect current theme selection
        try:
            self.theme_combo.setCurrentText(self.current_theme)
        except Exception:
            pass
        theme_select_layout.addWidget(self.theme_combo, 1)
        theme_layout.addLayout(theme_select_layout)
        
        parent_layout.addWidget(theme_card)
        
        # Fill the combo initially
        self.populate_config_file_list()

    def setup_extensions_ui(self, parent_layout):
        """
        Setup extensions and advanced settings with modern toggle switches.
        
        Creates collapsible cards for each hardware extension:
        - Rotary Encoder (GP10, GP11, GP14)
        - Analog Slider (GP28)
        - OLED Display (I2C: GP20/GP21)
        - RGB Matrix (GP9)
        
        Each card includes:
        - Toggle switch for enable/disable (blue = enabled, gray = disabled)
        - Configuration button for advanced settings
        - Visual feedback via theme-aware styling
        
        Changes to extension state automatically update firmware generation
        and persist in config.json.
        """
        group = QGroupBox("Extensions & Settings")
        main_layout = QVBoxLayout()
        
        # Create tab widget for extensions and advanced settings
        self.extensions_tabs = QTabWidget()
        
        # --- Extensions Tab ---
        extensions_tab = QWidget()
        ext_scroll = QScrollArea()
        ext_scroll.setWidgetResizable(True)
        ext_scroll.setFrameShape(QFrame.Shape.NoFrame)
        ext_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        ext_content = QWidget()
        ext_layout = QVBoxLayout(ext_content)
        ext_layout.setSpacing(12)
        
        # Encoder Section with modern toggle switch
        encoder_card = CollapsibleCard("🎛 Rotary Encoder", start_collapsed=False)
        encoder_layout = encoder_card.get_content_layout()
        encoder_layout.setSpacing(8)
        
        # Toggle row: Label + Switch
        enc_toggle_layout = QHBoxLayout()
        enc_label = QLabel("Enable Encoder (GP10, GP11, GP14)")
        enc_label.setToolTip("Rotary encoder with button for layer cycling and custom actions")
        self.enable_encoder_toggle = ToggleSwitch()
        self.enable_encoder_toggle.setChecked(self.enable_encoder)
        self.enable_encoder_toggle.toggled.connect(self.on_encoder_toggled)
        self.enable_encoder_toggle.setToolTip("Toggle encoder extension on/off")
        enc_toggle_layout.addWidget(enc_label)
        enc_toggle_layout.addStretch()
        enc_toggle_layout.addWidget(self.enable_encoder_toggle)
        encoder_layout.addLayout(enc_toggle_layout)
        
        # Configure button
        enc_cfg_btn = QPushButton("⚙ Configure Actions")
        enc_cfg_btn.clicked.connect(self.configure_encoder)
        enc_cfg_btn.setToolTip("Set up encoder rotation and button press actions")
        enc_cfg_btn.setMaximumWidth(200)
        self.encoder_cfg_btn = enc_cfg_btn
        encoder_layout.addWidget(enc_cfg_btn)
        
        ext_layout.addWidget(encoder_card)

        # Analog Input Section with modern toggle switch
        analog_card = CollapsibleCard("📊 Analog Slider", start_collapsed=False)
        analog_layout = analog_card.get_content_layout()
        analog_layout.setSpacing(8)
        
        # Toggle row: Label + Switch
        an_toggle_layout = QHBoxLayout()
        an_label = QLabel("Enable Analog Input (GP28)")
        an_label.setToolTip("10k potentiometer slider for volume or brightness control")
        self.enable_analogin_toggle = ToggleSwitch()
        self.enable_analogin_toggle.setChecked(self.enable_analogin)
        self.enable_analogin_toggle.toggled.connect(self.on_analogin_toggled)
        self.enable_analogin_toggle.setToolTip("Toggle analog input extension on/off")
        an_toggle_layout.addWidget(an_label)
        an_toggle_layout.addStretch()
        an_toggle_layout.addWidget(self.enable_analogin_toggle)
        analog_layout.addLayout(an_toggle_layout)
        
        # Configure button
        an_cfg_btn = QPushButton("⚙ Configure Function")
        an_cfg_btn.clicked.connect(self.configure_analogin)
        an_cfg_btn.setToolTip("Choose between volume control or LED brightness")
        an_cfg_btn.setMaximumWidth(200)
        self.analogin_cfg_btn = an_cfg_btn
        analog_layout.addWidget(an_cfg_btn)
        
        ext_layout.addWidget(analog_card)

        # Display Section with modern toggle switch
        display_card = CollapsibleCard("🖥 OLED Display", start_collapsed=False)
        display_layout = display_card.get_content_layout()
        display_layout.setSpacing(8)
        
        # Toggle row: Label + Switch
        disp_toggle_layout = QHBoxLayout()
        disp_label = QLabel("Enable Display (I2C: GP20/GP21)")
        disp_label.setToolTip("128x64 OLED display showing current layer keymap")
        self.enable_display_toggle = ToggleSwitch()
        self.enable_display_toggle.setChecked(self.enable_display)
        self.enable_display_toggle.toggled.connect(self.on_display_toggled)
        self.enable_display_toggle.setToolTip("Toggle display extension on/off")
        disp_toggle_layout.addWidget(disp_label)
        disp_toggle_layout.addStretch()
        disp_toggle_layout.addWidget(self.enable_display_toggle)
        display_layout.addLayout(disp_toggle_layout)
        
        # Configure button
        disp_cfg_btn = QPushButton("👁 Preview Layout")
        disp_cfg_btn.clicked.connect(self.configure_display)
        disp_cfg_btn.setToolTip("Preview how keys will appear on the OLED display")
        disp_cfg_btn.setMaximumWidth(200)
        self.display_cfg_btn = disp_cfg_btn
        display_layout.addWidget(disp_cfg_btn)
        
        ext_layout.addWidget(display_card)

        # RGB Matrix Section with modern toggle switch
        rgb_card = CollapsibleCard("💡 RGB Lighting", start_collapsed=False)
        rgb_layout = rgb_card.get_content_layout()
        rgb_layout.setSpacing(8)
        
        # Toggle row: Label + Switch
        rgb_toggle_layout = QHBoxLayout()
        rgb_label = QLabel("Enable RGB Matrix (GP9)")
        rgb_label.setToolTip("SK6812MINI RGB LEDs - 20 per-key LEDs")
        self.enable_rgb_toggle = ToggleSwitch()
        self.enable_rgb_toggle.setChecked(self.enable_rgb)
        self.enable_rgb_toggle.toggled.connect(self.on_rgb_toggled)
        self.enable_rgb_toggle.setToolTip("Toggle RGB matrix extension on/off")
        rgb_toggle_layout.addWidget(rgb_label)
        rgb_toggle_layout.addStretch()
        rgb_toggle_layout.addWidget(self.enable_rgb_toggle)
        rgb_layout.addLayout(rgb_toggle_layout)
        
        # Configure buttons row
        rgb_btn_layout = QHBoxLayout()
        rgb_cfg_btn = QPushButton("⚙ Global Settings")
        rgb_cfg_btn.clicked.connect(self.configure_rgb)
        rgb_cfg_btn.setToolTip("Configure brightness, RGB order, and default colors")
        rgb_btn_layout.addWidget(rgb_cfg_btn)
        
        rgb_colors_btn = QPushButton("🎨 Per-Key Colors")
        def open_per_key_colors():
            cfg = self.rgb_matrix_config
            layer_idx = self.current_layer if 0 <= self.current_layer < len(self.keymap_data) else 0
            layer_overrides = cfg.get('layer_key_colors', {}) or {}
            key_map = layer_overrides.get(str(layer_idx), cfg.get('key_colors', {}))
            pc = PerKeyColorDialog(
                self,
                rows=self.rows,
                cols=self.cols,
                key_colors=key_map,
                underglow_count=cfg.get('num_underglow', 0),
                underglow_colors=cfg.get('underglow_colors', {}),
                default_key_color=cfg.get('default_key_color', '#FFFFFF'),
                default_underglow_color=cfg.get('default_underglow_color', '#000000'),
                layer_index=layer_idx,
            )
            if pc.exec():
                self.save_extension_configs()
        rgb_colors_btn.clicked.connect(open_per_key_colors)
        rgb_colors_btn.setToolTip("Customize individual key colors for current layer")
        rgb_btn_layout.addWidget(rgb_colors_btn)
        rgb_btn_layout.addStretch()
        self.rgb_cfg_btn = rgb_cfg_btn
        self.rgb_colors_btn = rgb_colors_btn
        rgb_layout.addLayout(rgb_btn_layout)
        
        ext_layout.addWidget(rgb_card)
        
        ext_layout.addStretch()
        
        # Set up scroll area
        ext_scroll.setWidget(ext_content)
        ext_tab_layout = QVBoxLayout(extensions_tab)
        ext_tab_layout.setContentsMargins(0, 0, 0, 0)
        ext_tab_layout.addWidget(ext_scroll)
        
        self.extensions_tabs.addTab(extensions_tab, "🔌 Extensions")
        
        # --- Custom Code Tab ---
        custom_code_tab = QWidget()
        custom_code_layout = QVBoxLayout(custom_code_tab)
        custom_code_layout.setSpacing(12)
        
        custom_code_info = QLabel(
            "<b>💻 Custom Extension Code</b><br>"
            "Add your own Python code snippets here instead of using the UI configuration.<br>"
            "This code will be inserted into the generated code.py file.<br><br>"
            "<b>Use cases:</b> Custom modules, TapDance, Combos, StringSubs, etc."
        )
        custom_code_info.setWordWrap(True)
        custom_code_info.setObjectName("infoBox")  # Tag for theme updates
        custom_code_layout.addWidget(custom_code_info)
        
        self.custom_extension_code = QTextEdit()
        self.custom_extension_code.setPlaceholderText(
            "# Example: TapDance\n"
            "# from kmk.modules.tapdance import TapDance\n"
            "# tapdance = TapDance()\n"
            "# tapdance.tap_time = 750\n"
            "# keyboard.modules.append(tapdance)\n"
            "#\n"
            "# TD_ESC_CTRL = KC.TD(KC.ESC, KC.LCTL)\n"
            "#\n"
            "# Example: Combos\n"
            "# from kmk.modules.combos import Combos, Chord\n"
            "# combos = Combos()\n"
            "# combos.combos = [\n"
            "#     Chord((KC.Q, KC.W), KC.ESC),\n"
            "# ]\n"
            "# keyboard.modules.append(combos)\n"
        )
        self.custom_extension_code.setFont(QFont("Courier New", 10))
        custom_code_layout.addWidget(self.custom_extension_code)
        
        # Initialize with empty string if not set
        if not hasattr(self, 'custom_ext_code'):
            self.custom_ext_code = ""
        self.custom_extension_code.setPlainText(self.custom_ext_code)
        self.custom_extension_code.textChanged.connect(self.on_custom_code_changed)
        
        custom_code_buttons = QHBoxLayout()
        
        tapdance_btn = QPushButton("⚡ Add TapDance")
        tapdance_btn.clicked.connect(self.add_tapdance_helper)
        tapdance_btn.setToolTip("Generate TapDance code with helper dialog")
        custom_code_buttons.addWidget(tapdance_btn)
        
        combos_btn = QPushButton("🔗 Add Combo")
        combos_btn.clicked.connect(self.add_combo_helper)
        combos_btn.setToolTip("Generate Combo code with helper dialog")
        custom_code_buttons.addWidget(combos_btn)
        
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(lambda: self.custom_extension_code.clear())
        clear_btn.setToolTip("Clear all custom code")
        custom_code_buttons.addWidget(clear_btn)
        custom_code_buttons.addStretch()
        custom_code_layout.addLayout(custom_code_buttons)
        
        self.extensions_tabs.addTab(custom_code_tab, "💻 Custom Code")
        
        # --- Advanced Settings Tab ---
        advanced_tab = QWidget()
        adv_scroll = QScrollArea()
        adv_scroll.setWidgetResizable(True)
        adv_scroll.setFrameShape(QFrame.Shape.NoFrame)
        adv_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        adv_content = QWidget()
        adv_layout = QVBoxLayout(adv_content)
        adv_layout.setSpacing(12)
        
        # Encoder Sensitivity
        encoder_adv_group = QGroupBox("🎛 Encoder Sensitivity")
        encoder_adv_layout = QFormLayout()
        
        self.divisor_spin = QSpinBox()
        self.divisor_spin.setRange(1, 16)
        self.divisor_spin.setValue(self.encoder_divisor)
        self.divisor_spin.setToolTip(
            "Number of encoder steps before sending an action.\n"
            "Lower = more sensitive (1-2), Higher = less sensitive (6-8)\n"
            "Default: 4 works well for most encoders"
        )
        self.divisor_spin.valueChanged.connect(self.on_encoder_divisor_changed)
        encoder_adv_layout.addRow("Steps per action:", self.divisor_spin)
        
        sensitivity_info = QLabel(
            "💡 <i>Adjust if encoder feels too sensitive or unresponsive</i>"
        )
        sensitivity_info.setWordWrap(True)
        sensitivity_info.setStyleSheet("color: #888; font-size: 10pt;")
        encoder_adv_layout.addRow("", sensitivity_info)
        
        encoder_adv_group.setLayout(encoder_adv_layout)
        adv_layout.addWidget(encoder_adv_group)
        
        # Boot Configuration
        boot_group = QGroupBox("⚡ Boot Configuration (boot.py)")
        boot_layout = QVBoxLayout()
        
        boot_info = QLabel(
            "Configure how the device boots. <b>Use with caution!</b>"
        )
        boot_info.setWordWrap(True)
        boot_layout.addWidget(boot_info)
        
        self.enable_boot_py = QCheckBox("Enable custom boot.py")
        self.enable_boot_py.setChecked(bool(self.boot_config_str and self.boot_config_str.strip()))
        self.enable_boot_py.toggled.connect(self.on_boot_toggle)
        boot_layout.addWidget(self.enable_boot_py)
        
        # Boot options
        self.boot_options_widget = QWidget()
        boot_options_layout = QVBoxLayout(self.boot_options_widget)
        boot_options_layout.setContentsMargins(20, 0, 0, 0)
        
        self.disable_storage_checkbox = QCheckBox("⚠ Make storage read-only from computer")
        self.disable_storage_checkbox.setStyleSheet("QCheckBox { color: #ff6b6b; font-weight: bold; }")
        self.disable_storage_checkbox.setToolTip(
            "WARNING: The CIRCUITPY drive will be read-only from your computer.\n"
            "You won't be able to edit files without special recovery steps!"
        )
        self.disable_storage_checkbox.toggled.connect(self.on_readonly_toggle)
        self.disable_storage_checkbox.toggled.connect(self.on_boot_setting_changed)
        boot_options_layout.addWidget(self.disable_storage_checkbox)
        
        self.disable_usb_hid_checkbox = QCheckBox("Disable USB keyboard/mouse (advanced)")
        self.disable_usb_hid_checkbox.setToolTip(
            "Only disable this if you know what you're doing.\n"
            "Your device won't function as a keyboard!"
        )
        self.disable_usb_hid_checkbox.toggled.connect(self.on_boot_setting_changed)
        boot_options_layout.addWidget(self.disable_usb_hid_checkbox)
        
        rename_layout = QHBoxLayout()
        self.rename_drive_checkbox = QCheckBox("Rename drive to:")
        self.drive_name_edit = QLineEdit("CHRONOSPAD")
        self.drive_name_edit.setMaxLength(11)
        self.drive_name_edit.setMaximumWidth(150)
        rename_layout.addWidget(self.rename_drive_checkbox)
        rename_layout.addWidget(self.drive_name_edit)
        rename_layout.addStretch()
        self.rename_drive_checkbox.toggled.connect(self.on_rename_drive_toggled)
        self.drive_name_edit.textChanged.connect(self.on_boot_setting_changed)
        boot_options_layout.addLayout(rename_layout)
        
        boot_options_layout.addWidget(QLabel("Custom boot.py code:"))
        self.boot_code_editor = QTextEdit()
        self.boot_code_editor.setPlaceholderText(
            "# Advanced: Add custom boot.py code here\n"
            "# Example: import storage\n"
            "# storage.remount('/', readonly=False)"
        )
        self.boot_code_editor.setMaximumHeight(120)
        self.boot_code_editor.textChanged.connect(self.on_boot_setting_changed)
        boot_options_layout.addWidget(self.boot_code_editor)
        
        boot_layout.addWidget(self.boot_options_widget)
        boot_group.setLayout(boot_layout)
        adv_layout.addWidget(boot_group)
        
        adv_layout.addStretch()
        
        # Set up scroll area
        adv_scroll.setWidget(adv_content)
        adv_tab_layout = QVBoxLayout(advanced_tab)
        adv_tab_layout.setContentsMargins(0, 0, 0, 0)
        adv_tab_layout.addWidget(adv_scroll)
        
        self.extensions_tabs.addTab(advanced_tab, "⚙ Advanced")
        
        # Connect tab change signal to save session state
        self.extensions_tabs.currentChanged.connect(lambda: self.save_session_state())
        
        # Add tabs to main layout
        main_layout.addWidget(self.extensions_tabs)
        
        # Update button states based on checkbox states
        self.update_extension_button_states()
        self.refresh_boot_config_ui()

        group.setLayout(main_layout)
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
    
    def on_boot_toggle(self):
        """Handle boot.py enable/disable toggle."""
        enabled = self.enable_boot_py.isChecked()
        if hasattr(self, 'boot_options_widget'):
            self.boot_options_widget.setEnabled(enabled)
        self.on_boot_setting_changed()
    
    def on_readonly_toggle(self, checked):
        """Show warning when user tries to enable read-only mode."""
        if checked:
            reply = QMessageBox.warning(
                self,
                "⚠ WARNING: Read-Only Storage",
                "<b>You are about to make the CIRCUITPY drive read-only from your computer!</b><br><br>"
                "This means:<br>"
                "• You won't be able to edit or delete files from your computer<br>"
                "• You'll need to modify code.py to disable this setting<br>"
                "• Or use the CircuitPython bootloader to recover<br><br>"
                "<b>Only do this if you want to prevent accidental file changes!</b><br><br>"
                "Are you sure you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                # User cancelled - uncheck the box
                self.disable_storage_checkbox.setChecked(False)

    def on_boot_setting_changed(self, *_args) -> None:
        """Regenerate boot.py configuration whenever a related option changes."""
        if not hasattr(self, 'enable_boot_py'):
            return

        if self.enable_boot_py.isChecked():
            self.boot_config_str = self.generate_boot_config()
        else:
            self.boot_config_str = ""

        try:
            self.save_extension_configs()
        except Exception:
            # Avoid blocking UI if disk write fails
            pass

    def on_rename_drive_toggled(self, checked: bool) -> None:
        """Enable or disable the drive name input and refresh config."""
        if hasattr(self, 'drive_name_edit'):
            self.drive_name_edit.setEnabled(checked)
        self.on_boot_setting_changed()

    def refresh_boot_config_ui(self) -> None:
        """Synchronize boot configuration controls with the stored script."""
        if not hasattr(self, 'enable_boot_py'):
            return

        boot_enabled = bool(self.boot_config_str and self.boot_config_str.strip())

        self.enable_boot_py.blockSignals(True)
        self.enable_boot_py.setChecked(boot_enabled)
        self.enable_boot_py.blockSignals(False)

        if hasattr(self, 'boot_options_widget'):
            self.boot_options_widget.setEnabled(boot_enabled)

        disable_storage = "storage.disable_usb_drive()" in (self.boot_config_str or "")
        self.disable_storage_checkbox.blockSignals(True)
        self.disable_storage_checkbox.setChecked(disable_storage)
        self.disable_storage_checkbox.blockSignals(False)

        disable_usb = "usb_hid.disable()" in (self.boot_config_str or "")
        self.disable_usb_hid_checkbox.blockSignals(True)
        self.disable_usb_hid_checkbox.setChecked(disable_usb)
        self.disable_usb_hid_checkbox.blockSignals(False)

        rename_match = re.search(r'storage\.getmount\("/"\)\.label\s*=\s*"([^"]+)"', self.boot_config_str or "")
        rename_enabled = bool(rename_match)
        self.rename_drive_checkbox.blockSignals(True)
        self.rename_drive_checkbox.setChecked(rename_enabled)
        self.rename_drive_checkbox.blockSignals(False)

        self.drive_name_edit.blockSignals(True)
        self.drive_name_edit.setEnabled(rename_enabled)
        if rename_match:
            self.drive_name_edit.setText(rename_match.group(1)[:11])
        self.drive_name_edit.blockSignals(False)

        custom_code = self._extract_custom_boot_code(self.boot_config_str or "")
        self.boot_code_editor.blockSignals(True)
        self.boot_code_editor.setPlainText(custom_code)
        self.boot_code_editor.blockSignals(False)

    def _extract_custom_boot_code(self, boot_config: str) -> str:
        """Extract user-provided custom code segment from a boot.py script."""
        if not boot_config:
            return ""

        marker = "# Custom configuration:"
        if marker in boot_config:
            return boot_config.split(marker, 1)[1].strip()

        toggle_tokens = (
            "storage.disable_usb_drive()",
            "usb_hid.disable()",
            'storage.getmount("/").label',
        )

        if any(token in boot_config for token in toggle_tokens):
            return ""

        return boot_config.strip()
    
    def on_encoder_divisor_changed(self, value):
        """Handle encoder divisor spinbox change."""
        self.encoder_divisor = value
        self.save_extension_configs()
    
    def on_custom_code_changed(self):
        """Handle custom extension code changes."""
        self.custom_ext_code = self.custom_extension_code.toPlainText()
        self.save_extension_configs()
        # Update TapDance list when code changes
        self.update_tapdance_list()
    
    def generate_boot_config(self):
        """Generate boot.py code from UI settings."""
        if not self.enable_boot_py.isChecked():
            return ""
        
        lines = []
        
        if self.disable_storage_checkbox.isChecked():
            lines.append("import storage")
            lines.append("storage.disable_usb_drive()")
            lines.append("")
        
        if self.disable_usb_hid_checkbox.isChecked():
            lines.append("import usb_hid")
            lines.append("usb_hid.disable()")
            lines.append("")
        
        if self.rename_drive_checkbox.isChecked():
            drive_name = self.drive_name_edit.text().strip()
            if drive_name:
                lines.append("import storage")
                lines.append('storage.remount("/", readonly=False)')
                lines.append(f'storage.getmount("/").label = "{drive_name}"')
                lines.append('storage.remount("/", readonly=True)')
                lines.append("")
        
        custom_code = self.boot_code_editor.toPlainText().strip()
        if custom_code:
            if lines:
                lines.append("# Custom configuration:")
            lines.append(custom_code)
        
        return "\n".join(lines)
        if hasattr(self, 'rgb_colors_btn'):
            self.rgb_colors_btn.setEnabled(self.enable_rgb)

    def sync_extension_checkboxes(self):
        """
        Ensure extension toggle switches reflect current enabled states without triggering signals.
        
        This method synchronizes the UI state with the internal enabled flags
        after loading a configuration or applying changes. Signal blocking prevents
        recursive toggling events during synchronization.
        
        Updates:
        - encoder toggle (enable_encoder_toggle)
        - analog input toggle (enable_analogin_toggle)
        - display toggle (enable_display_toggle)
        - RGB matrix toggle (enable_rgb_toggle)
        """
        def _set_state(toggle_switch, value):
            if toggle_switch:
                toggle_switch.blockSignals(True)
                toggle_switch.setChecked(value)
                toggle_switch.blockSignals(False)

        _set_state(getattr(self, 'enable_encoder_toggle', None), self.enable_encoder)
        _set_state(getattr(self, 'enable_analogin_toggle', None), self.enable_analogin)
        _set_state(getattr(self, 'enable_display_toggle', None), self.enable_display)
        _set_state(getattr(self, 'enable_rgb_toggle', None), self.enable_rgb)

    # --- Extension configuration handlers ---
    def open_advanced_settings(self):
        """Open the advanced settings dialog for boot.py and encoder divisor."""
        dialog = AdvancedSettingsDialog(
            parent=self,
            encoder_divisor=self.encoder_divisor,
            boot_config=self.boot_config_str
        )
        if dialog.exec():
            # Update encoder divisor
            old_divisor = self.encoder_divisor
            self.encoder_divisor = dialog.get_encoder_divisor()
            
            # Update boot.py config
            self.boot_config_str = dialog.get_boot_config()
            self.refresh_boot_config_ui()
            
            # Save settings
            self.save_extension_configs()
            
            # Notify user
            changes = []
            if old_divisor != self.encoder_divisor:
                changes.append(f"Encoder divisor changed from {old_divisor} to {self.encoder_divisor}")
            if self.boot_config_str:
                changes.append("Boot configuration updated")
            
            if changes:
                QMessageBox.information(
                    self, 
                    "Settings Updated", 
                    "Advanced settings have been saved:\n\n" + "\n".join(f"• {c}" for c in changes)
                )
    
    def configure_encoder(self):
        """Configure encoder with enhanced dialog for automatic layer cycling."""
        num_layers = len(self.keymap_data)
        dialog = EncoderConfigDialog(
            parent=self,
            initial_text=self.encoder_config_str or "",
            num_layers=num_layers,
            initial_divisor=self.encoder_divisor or 4,
        )
        if dialog.exec():
            self.encoder_config_str = dialog.get_config()
            self.encoder_divisor = dialog.get_divisor()
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
            layer_idx = self.current_layer if 0 <= self.current_layer < len(self.keymap_data) else 0
            layer_overrides = cfg.get('layer_key_colors', {}) or {}
            key_map = layer_overrides.get(str(layer_idx), cfg.get('key_colors', {}))
            pc = PerKeyColorDialog(
                self,
                rows=self.rows,
                cols=self.cols,
                key_colors=key_map,
                underglow_count=cfg.get('num_underglow', 0),
                underglow_colors=cfg.get('underglow_colors', {}),
                default_key_color=cfg.get('default_key_color', '#FFFFFF'),
                default_underglow_color=cfg.get('default_underglow_color', '#000000'),
                layer_index=layer_idx,
            )
            if pc.exec():
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
    
    def add_tapdance_helper(self):
        """Open TapDance helper dialog"""
        dialog = TapDanceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            code = dialog.get_code()
            if code:
                # Append to custom extension code
                current_code = self.custom_extension_code.toPlainText()
                if current_code.strip():
                    current_code += "\n\n"
                self.custom_extension_code.setPlainText(current_code + code)
                # Update TapDance keycode list
                self.update_tapdance_list()
    
    def update_tapdance_list(self):
        """Parse custom extension code to find TapDance definitions and update the list"""
        # Parse the custom extension code for TapDance definitions
        custom_code = self.custom_extension_code.toPlainText() if hasattr(self, 'custom_extension_code') else ""
        
        # Find lines like: TD_NAME = KC.TD(...)
        import re
        td_pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*KC\.TD\s*\('
        
        td_names = []
        for line in custom_code.split('\n'):
            match = re.match(td_pattern, line.strip())
            if match:
                td_names.append(match.group(1))
        
        # Update keycode list if TapDance category is active
        if hasattr(self, 'current_category') and self.current_category == "TapDance":
            self.keycode_list.clear()
            if td_names:
                sorted_names = sorted(td_names)
                self.keycode_list.addItems(sorted_names)
        
        # Update tapdance button count
        if hasattr(self, 'category_buttons') and "TapDance" in self.category_buttons:
            self.category_buttons["TapDance"].setText(f"🎯 TapDance\n({len(td_names)})")
        
        # Also update management list if it exists (for left panel)
        if hasattr(self, 'tapdance_management_list'):
            self.tapdance_management_list.clear()
            if td_names:
                self.tapdance_management_list.addItems(sorted(td_names))

    
    def add_combo_helper(self):
        """Open Combo helper dialog"""
        dialog = ComboDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            code = dialog.get_code()
            if code:
                # Append to custom extension code
                current_code = self.custom_extension_code.toPlainText()
                if current_code.strip():
                    current_code += "\n\n"
                self.custom_extension_code.setPlainText(current_code + code)

    def populate_config_file_list(self):
        """Populate config selector with saved JSON configs from kmk_Config_Save and project root."""

        def _collect(folder: str) -> list[str]:
            results: list[str] = []
            if not os.path.isdir(folder):
                return results
            for name in os.listdir(folder):
                lower = name.lower()
                if lower.startswith('config') and lower.endswith('.json'):
                    full_path = os.path.join(folder, name)
                    if os.path.isfile(full_path):
                        results.append(full_path)
            return results

        paths = _collect(CONFIG_SAVE_DIR)
        # Include project-root configs if present (maintains backward compatibility)
        for path in _collect(BASE_DIR):
            if path not in paths:
                paths.append(path)

        paths.sort(key=lambda p: (os.path.dirname(p).lower(), os.path.basename(p).lower()))

        self.config_file_combo.blockSignals(True)
        self.config_file_combo.clear()
        display_names = [os.path.relpath(p, BASE_DIR) for p in paths]
        self.config_file_combo.addItems(display_names)
        self.config_file_combo.setEnabled(bool(display_names))
        self.config_file_combo.blockSignals(False)
    
    def setup_layer_management_ui(self, parent_layout):
        """Setup layer management with improved visual design."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)
        
        # Header row with layer management
        header_layout = QHBoxLayout()
        
        # Layer tabs with better styling
        layer_label = QLabel("📑 <b>Layers:</b>")
        layer_label.setStyleSheet("font-size: 10pt;")
        layer_label.setFixedWidth(70)
        header_layout.addWidget(layer_label)
        
        self.layer_tabs = QTabWidget()
        self.layer_tabs.setUsesScrollButtons(True)
        self.layer_tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.layer_tabs.currentChanged.connect(self.on_layer_changed)
        self.layer_tabs.setToolTip("Switch between keyboard layers - each layer can have different key mappings")
        header_layout.addWidget(self.layer_tabs, 1)

        # Layer control buttons
        layer_button_layout = QHBoxLayout()
        layer_button_layout.setSpacing(3)
        
        add_layer_btn = QPushButton("➕")
        add_layer_btn.setFixedSize(32, 32)
        add_layer_btn.clicked.connect(self.add_layer)
        add_layer_btn.setToolTip("Add a new layer")
        layer_button_layout.addWidget(add_layer_btn)

        remove_layer_btn = QPushButton("➖")
        remove_layer_btn.setFixedSize(32, 32)
        remove_layer_btn.clicked.connect(self.remove_layer)
        remove_layer_btn.setToolTip("Remove current layer")
        layer_button_layout.addWidget(remove_layer_btn)
        
        header_layout.addLayout(layer_button_layout)
        
        container_layout.addLayout(header_layout)
        
        # Info bar showing keyboard info
        info_bar = QLabel("Chronos Pad • 5×4 Matrix • RGB • OLED Display")
        info_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_bar.setStyleSheet(
            "padding: 5px; font-size: 9pt; color: #888; "
            "background-color: rgba(100, 100, 100, 0.1); border-radius: 3px;"
        )
        container_layout.addWidget(info_bar)
        
        parent_layout.addWidget(container)

    def setup_grid_actions_bar(self, parent_layout):
        """
        Setup grid actions bar with quick action buttons and selection display.
        
        Features:
        - Clear Layer: Resets all keys in current layer to KC.NO
        - Copy Layer: Copies current layer to clipboard
        - Paste Layer: Pastes clipboard layer data to current layer
        - Selection Display: Shows currently selected key coordinates and assignment
        
        Note:
            Actions bar provides quick access to common layer operations.
        """
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(12, 8, 12, 8)
        actions_layout.setSpacing(8)
        
        # Action buttons row
        buttons_layout = QHBoxLayout()
        
        clear_layer_btn = QPushButton("🗑 Clear Layer")
        clear_layer_btn.clicked.connect(self.clear_current_layer)
        clear_layer_btn.setToolTip("Clear all keys in the current layer (set to KC.NO)")
        buttons_layout.addWidget(clear_layer_btn)
        
        copy_layer_btn = QPushButton("📋 Copy")
        copy_layer_btn.clicked.connect(self.copy_current_layer)
        copy_layer_btn.setToolTip("Copy current layer to clipboard")
        buttons_layout.addWidget(copy_layer_btn)
        
        paste_layer_btn = QPushButton("📌 Paste")
        paste_layer_btn.clicked.connect(self.paste_to_current_layer)
        paste_layer_btn.setToolTip("Paste layer from clipboard")
        buttons_layout.addWidget(paste_layer_btn)
        
        buttons_layout.addStretch()
        actions_layout.addLayout(buttons_layout)
        
        # Selection display label
        self.grid_selection_label = QLabel("Selected: None")
        self.grid_selection_label.setStyleSheet("font-size: 9pt; color: #888; padding: 4px;")
        actions_layout.addWidget(self.grid_selection_label)
        
        parent_layout.addWidget(actions_frame)



    def setup_macropad_grid_ui(self, parent_layout):
        """
        Setup macropad grid with enhanced visual styling.
        
        Features:
        - 100x100px buttons for better visibility (up from 80x80)
        - 12px spacing for cleaner modern layout
        - Coordinate labels for easy identification
        - Visual feedback on hover and selection
        
        Note:
            Grid layout is 180° rotated to match physical hardware orientation.
        """
        self.macropad_group = QGroupBox(f"⌨ Keymap Grid (Layer {self.current_layer})")
        self.macropad_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.macropad_layout = QGridLayout()
        self.macropad_layout.setHorizontalSpacing(12)  # Increased from 8px for modern spacing
        self.macropad_layout.setVerticalSpacing(12)  # Increased from 8px for modern spacing
        self.macropad_layout.setContentsMargins(10, 10, 10, 10)
        self.macropad_group.setLayout(self.macropad_layout)
        parent_layout.addWidget(self.macropad_group, 1)

    def setup_keycode_selector_ui(self, parent_layout):
        """Setup keycode selector with improved organization and visual hierarchy."""
        group = QGroupBox("🔤 Key Assignment")
        layout = QVBoxLayout()
        
        # Selected key indicator with better styling
        self.selected_key_label = QLabel("Selected Key: None")
        self.selected_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_key_label.setStyleSheet(
            "font-weight: bold; font-size: 11pt; padding: 8px; "
            "border: 2px solid #555; border-radius: 4px;"
        )
        layout.addWidget(self.selected_key_label)
        
        layout.addSpacing(5)
        
        # Keycode selector with organized tabs
        self.keycode_selector = self.create_keycode_selector()
        self.keycode_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.keycode_selector, 1)

        layout.addSpacing(5)
        
        # Quick action buttons
        quick_actions_layout = QHBoxLayout()
        
        assign_combo_btn = QPushButton("⌨ Combo")
        assign_combo_btn.clicked.connect(self.assign_combo)
        assign_combo_btn.setToolTip("Create key combinations like Ctrl+C")
        quick_actions_layout.addWidget(assign_combo_btn)
        
        clear_key_btn = QPushButton("✖ Clear")
        clear_key_btn.clicked.connect(self.clear_selected_key)
        clear_key_btn.setToolTip("Clear the selected key (set to KC.NO)")
        quick_actions_layout.addWidget(clear_key_btn)
        
        transparent_key_btn = QPushButton("🔄 Transparent")
        transparent_key_btn.clicked.connect(self.set_key_transparent)
        transparent_key_btn.setToolTip("Make key transparent (pass through to lower layer)")
        quick_actions_layout.addWidget(transparent_key_btn)
        
        layout.addLayout(quick_actions_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group, 1)

    def clear_selected_key(self):
        """Clear the selected key to KC.NO."""
        if self.selected_key_coords:
            row, col = self.selected_key_coords
            self.keymap_data[self.current_layer][row][col] = "KC.NO"
            self.update_macropad_display()
        else:
            QMessageBox.information(self, "No Key Selected", "Please select a key on the grid first.")
    
    def set_key_transparent(self):
        """Set the selected key to KC.TRNS (transparent)."""
        if self.selected_key_coords:
            row, col = self.selected_key_coords
            self.keymap_data[self.current_layer][row][col] = "KC.TRNS"
            self.update_macropad_display()
        else:
            QMessageBox.information(self, "No Key Selected", "Please select a key on the grid first.")

    def clear_current_layer(self):
        """
        Clear all keys in the current layer to KC.NO.
        
        Prompts user for confirmation before clearing. This operation can be
        undone by reloading a saved configuration.
        
        Note:
            Updates the grid display immediately after clearing.
        """
        if self.current_layer >= len(self.keymap_data):
            return
        
        reply = QMessageBox.question(
            self, 
            "Clear Layer",
            f"Clear all keys in Layer {self.current_layer}?\n\nThis will set all keys to KC.NO.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all keys in current layer
            for r in range(self.rows):
                for c in range(self.cols):
                    self.keymap_data[self.current_layer][r][c] = "KC.NO"
            self.update_macropad_display()
            QMessageBox.information(self, "Layer Cleared", f"Layer {self.current_layer} has been cleared.")

    def copy_current_layer(self):
        """
        Copy the current layer to clipboard (internal storage).
        
        Stores layer data as JSON in an internal clipboard variable.
        Can be pasted to any layer using paste_to_current_layer().
        
        Note:
            Only one layer can be in the clipboard at a time.
        """
        if self.current_layer >= len(self.keymap_data):
            return
        
        # Store layer data in clipboard
        self.layer_clipboard = [row[:] for row in self.keymap_data[self.current_layer]]
        QMessageBox.information(
            self, 
            "Layer Copied", 
            f"Layer {self.current_layer} copied to clipboard.\n\nYou can now paste it to another layer."
        )

    def paste_to_current_layer(self):
        """
        Paste clipboard layer data to the current layer.
        
        Replaces all keys in the current layer with the copied layer data.
        Prompts for confirmation before overwriting.
        
        Note:
            Requires copy_current_layer() to have been called first.
        """
        if not hasattr(self, 'layer_clipboard') or not self.layer_clipboard:
            QMessageBox.warning(
                self, 
                "No Layer Copied", 
                "No layer data in clipboard.\n\nUse 'Copy' first to copy a layer."
            )
            return
        
        if self.current_layer >= len(self.keymap_data):
            return
        
        reply = QMessageBox.question(
            self, 
            "Paste Layer",
            f"Paste clipboard to Layer {self.current_layer}?\n\nThis will overwrite all current keys.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Paste layer data
            for r in range(min(self.rows, len(self.layer_clipboard))):
                for c in range(min(self.cols, len(self.layer_clipboard[r]))):
                    self.keymap_data[self.current_layer][r][c] = self.layer_clipboard[r][c]
            self.update_macropad_display()
            QMessageBox.information(self, "Layer Pasted", f"Layer data pasted to Layer {self.current_layer}.")

    def show_key_context_menu(self, row, col, pos):
        """
        Show context menu for grid key with common operations.
        
        Menu options:
        - Copy Key: Copies key value to internal clipboard
        - Paste Key: Pastes clipboard value to this key
        - Set to Transparent: Sets key to KC.TRNS
        - Set to No Key: Sets key to KC.NO
        - Delete: Same as Set to No Key
        
        Args:
            row: Row index of the key
            col: Column index of the key
            pos: Position where context menu should appear
            
        Note:
            All operations update the grid display immediately.
        """
        if self.current_layer >= len(self.keymap_data):
            return
        
        menu = QMenu(self)
        
        # Copy key action
        copy_action = menu.addAction("📋 Copy Key")
        copy_action.triggered.connect(lambda: self.copy_key_value(row, col))
        
        # Paste key action
        paste_action = menu.addAction("📌 Paste Key")
        paste_action.triggered.connect(lambda: self.paste_key_value(row, col))
        if not hasattr(self, 'key_clipboard') or not self.key_clipboard:
            paste_action.setEnabled(False)
        
        menu.addSeparator()
        
        # Set to transparent
        transparent_action = menu.addAction("🔄 Set to Transparent")
        transparent_action.triggered.connect(lambda: self.set_key_value(row, col, "KC.TRNS"))
        
        # Set to no key
        no_key_action = menu.addAction("✖ Set to No Key")
        no_key_action.triggered.connect(lambda: self.set_key_value(row, col, "KC.NO"))
        
        menu.addSeparator()
        
        # Delete (same as no key)
        delete_action = menu.addAction("🗑 Delete")
        delete_action.triggered.connect(lambda: self.set_key_value(row, col, "KC.NO"))
        
        # Show menu at button position
        button = self.macropad_buttons.get((row, col))
        if button:
            menu.exec(button.mapToGlobal(pos))

    def copy_key_value(self, row, col):
        """Copy the value of a specific key to clipboard."""
        if self.current_layer >= len(self.keymap_data):
            return
        self.key_clipboard = self.keymap_data[self.current_layer][row][col]
        # Show toast notification
        ToastNotification.show_message(
            self, 
            f"Key copied: {self.key_clipboard}", 
            ToastNotification.INFO,
            duration=2000
        )

    def paste_key_value(self, row, col):
        """Paste clipboard value to a specific key."""
        if not hasattr(self, 'key_clipboard') or not self.key_clipboard:
            return
        if self.current_layer >= len(self.keymap_data):
            return
        self.keymap_data[self.current_layer][row][col] = self.key_clipboard
        self.update_macropad_display()
        # Show toast notification
        ToastNotification.show_message(
            self, 
            f"Key pasted: {self.key_clipboard}", 
            ToastNotification.SUCCESS,
            duration=2000
        )

    def set_key_value(self, row, col, value):
        """Set a specific key to a given value."""
        if self.current_layer >= len(self.keymap_data):
            return
        self.keymap_data[self.current_layer][row][col] = value
        self.update_macropad_display()
        # Show toast notification
        value_display = "No Key" if value == "KC.NO" else ("Transparent" if value == "KC.TRNS" else value)
        ToastNotification.show_message(
            self, 
            f"Key set to: {value_display}", 
            ToastNotification.SUCCESS,
            duration=2000
        )

    def setup_macro_ui(self, parent_layout):
        """Setup macro and TapDance management with tabbed interface."""
        # Create tab widget for Macros and TapDance
        self.advanced_keys_tabs = QTabWidget()
        
        # --- Macros Tab ---
        macros_widget = QWidget()
        macros_layout = QVBoxLayout(macros_widget)
        macros_layout.setContentsMargins(5, 5, 5, 5)
        
        # Macro list
        macros_label = QLabel("<b>Available Macros</b>")
        macros_layout.addWidget(macros_label)
        
        self.macro_list_widget = QListWidget()
        self.macro_list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.macro_list_widget.setToolTip("Click a macro to assign it to the selected key")
        macros_layout.addWidget(self.macro_list_widget, 1)
        self.macro_list_widget.itemClicked.connect(self.on_macro_selected)
        
        # Macro management buttons
        macro_button_layout = QHBoxLayout()
        add_macro_btn = QPushButton("➕ Create")
        add_macro_btn.clicked.connect(self.add_macro)
        add_macro_btn.setToolTip("Create a new macro")
        
        edit_macro_btn = QPushButton("✏ Edit")
        edit_macro_btn.clicked.connect(self.edit_macro)
        edit_macro_btn.setToolTip("Edit selected macro")
        
        remove_macro_btn = QPushButton("🗑 Delete")
        remove_macro_btn.clicked.connect(self.remove_macro)
        remove_macro_btn.setToolTip("Delete selected macro")
        
        macro_button_layout.addWidget(add_macro_btn)
        macro_button_layout.addWidget(edit_macro_btn)
        macro_button_layout.addWidget(remove_macro_btn)
        macros_layout.addLayout(macro_button_layout)
        
        self.advanced_keys_tabs.addTab(macros_widget, "⚡ Macros")
        
        # --- TapDance Tab ---
        tapdance_widget = QWidget()
        tapdance_layout = QVBoxLayout(tapdance_widget)
        tapdance_layout.setContentsMargins(5, 5, 5, 5)
        
        # Info label
        td_info = QLabel(
            "<b>TapDance Keys</b><br>"
            "<small>Keys that perform different actions based on tap count.<br>"
            "Define TapDance in Extensions → Custom Code tab.</small>"
        )
        td_info.setWordWrap(True)
        td_info.setStyleSheet("padding: 5px; background-color: rgba(100, 150, 255, 0.1); border-radius: 3px;")
        tapdance_layout.addWidget(td_info)
        
        tapdance_layout.addSpacing(5)
        
        # TapDance list (populated from custom code)
        td_list_label = QLabel("<b>Available TapDance</b>")
        tapdance_layout.addWidget(td_list_label)
        
        self.tapdance_management_list = QListWidget()
        self.tapdance_management_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tapdance_management_list.setToolTip("Click a TapDance to assign it to the selected key")
        self.tapdance_management_list.itemClicked.connect(self.on_tapdance_management_selected)
        tapdance_layout.addWidget(self.tapdance_management_list, 1)
        
        # TapDance helper buttons
        td_button_layout = QHBoxLayout()
        
        open_td_helper_btn = QPushButton("➕ Create TapDance")
        open_td_helper_btn.clicked.connect(self.open_tapdance_helper)
        open_td_helper_btn.setToolTip("Open TapDance builder in Custom Code tab")
        
        refresh_td_btn = QPushButton("🔄 Refresh")
        refresh_td_btn.clicked.connect(self.update_tapdance_list)
        refresh_td_btn.setToolTip("Refresh TapDance list from Custom Code")
        
        td_button_layout.addWidget(open_td_helper_btn)
        td_button_layout.addWidget(refresh_td_btn)
        tapdance_layout.addLayout(td_button_layout)
        
        self.advanced_keys_tabs.addTab(tapdance_widget, "🎯 TapDance")
        
        # Add tab widget to parent layout
        parent_layout.addWidget(self.advanced_keys_tabs, 1)
    
    def on_tapdance_management_selected(self, item):
        """Assign TapDance from management tab to selected key."""
        if self.selected_key_coords:
            td_name = item.text()
            row, col = self.selected_key_coords
            self.keymap_data[self.current_layer][row][col] = td_name
            self.update_macropad_display()
        else:
            QMessageBox.information(self, "No Key Selected", "Please select a key on the grid before assigning TapDance.")
    
    def open_tapdance_helper(self):
        """Open the TapDance builder in Custom Code tab."""
        # Switch to Extensions tab
        if hasattr(self, 'extensions_tabs'):
            # Find Custom Code tab (index 1)
            for i in range(self.extensions_tabs.count()):
                if "Custom Code" in self.extensions_tabs.tabText(i):
                    self.extensions_tabs.setCurrentIndex(i)
                    break
        
        # Open TapDance dialog
        self.add_tapdance_helper()

    def closeEvent(self, event):
        """Save settings and session state on application exit."""
        self.save_macros()
        self.save_profiles()
        self.save_session_state()
        event.accept()
    
    def keyPressEvent(self, event):
        """
        Handle keyboard navigation for keymap grid.
        
        Allows users to navigate the keymap grid using arrow keys and select
        keys without needing to use the mouse. This improves accessibility and
        workflow efficiency.
        
        Args:
            event: QKeyEvent containing the key press information
        
        Navigation:
            - Arrow Up/Down/Left/Right: Move selection in the grid
            - Enter/Return: Focus on keycode selector for quick assignment
            - Delete/Backspace: Clear selected key (set to KC.NO)
        
        Note:
            Grid coordinates are in physical board orientation (reversed for display)
        """
        key = event.key()
        
        # Arrow key navigation
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            if self.selected_key_coords is None:
                # No key selected, start at top-left (0, 0)
                self.on_key_selected(0, 0)
            else:
                row, col = self.selected_key_coords
                
                # Navigate based on arrow key
                if key == Qt.Key.Key_Up:
                    row = max(0, row - 1)
                elif key == Qt.Key.Key_Down:
                    row = min(self.rows - 1, row + 1)
                elif key == Qt.Key.Key_Left:
                    col = max(0, col - 1)
                elif key == Qt.Key.Key_Right:
                    col = min(self.cols - 1, col + 1)
                
                # Select the new key
                self.on_key_selected(row, col)
            
            event.accept()
        
        # Delete/Backspace to clear selected key
        elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.clear_selected_key()
            event.accept()
        
        # Enter/Return to focus keycode selector
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if hasattr(self, 'keycode_selector'):
                self.keycode_selector.setFocus()
            event.accept()
        
        else:
            # Pass other keys to parent
            super().keyPressEvent(event)

    # --- File I/O and Profile Management ---

    def save_macros(self):
        try:
            # MACRO_FILE is at BASE_DIR root, no subfolder needed
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
            # MACRO_FILE is at BASE_DIR root, no subfolder needed
            self.macros = {}
        self.update_macro_list()

    def get_macros_used_in_keymap(self):
        """Scan the current keymap and return macros that are actually used.
        
        Returns:
            dict: Dictionary of {macro_name: actions} for macros used in keymap
        """
        used_macros = {}
        
        # Scan all layers for macro references
        for layer in self.keymap_data:
            for row in layer:
                for key in row:
                    if isinstance(key, str) and key.startswith("MACRO(") and key.endswith(")"):
                        # Extract macro name from MACRO(name) format
                        macro_name = key[6:-1]  # Strip "MACRO(" and ")"
                        if macro_name in self.macros:
                            used_macros[macro_name] = self.macros[macro_name]
        
        return used_macros

    def _sanitize_macros(self, raw_macros):
        sanitized = {}
        if not isinstance(raw_macros, dict):
            return sanitized
        for name, entries in raw_macros.items():
            if not isinstance(name, str):
                continue
            cleaned = []
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, (list, tuple)) and len(entry) == 2:
                        action, value = entry
                        cleaned.append([str(action).strip().lower(), value])
            sanitized[name] = cleaned
        return sanitized

    def _export_rgb_config(self):
        merged = build_default_rgb_matrix_config()
        current = getattr(self, 'rgb_matrix_config', {}) or {}
        merged.update(current)
        merged['default_key_color'] = ensure_hex_prefix(
            merged.get('default_key_color', '#FFFFFF'), '#FFFFFF'
        )
        merged['default_underglow_color'] = ensure_hex_prefix(
            merged.get('default_underglow_color', '#000000'), '#000000'
        )

        key_colors_raw = current.get('key_colors', {}) or {}
        merged['key_colors'] = {
            str(k): ensure_hex_prefix(v, merged['default_key_color'])
            for k, v in key_colors_raw.items()
        }

        underglow_raw = current.get('underglow_colors', {}) or {}
        merged['underglow_colors'] = {
            str(k): ensure_hex_prefix(v, merged['default_underglow_color'])
            for k, v in underglow_raw.items()
        }

        layer_colors_raw = current.get('layer_key_colors', {}) or {}
        layer_colors = {}
        for layer, mapping in layer_colors_raw.items():
            if not isinstance(mapping, dict):
                continue
            sanitized = {
                str(k): ensure_hex_prefix(v, merged['default_key_color'])
                for k, v in mapping.items()
            }
            if sanitized:
                layer_colors[str(layer)] = sanitized
        merged['layer_key_colors'] = layer_colors
        return merged

    def save_profiles(self):
        try:
            with open(PROFILE_FILE, 'w') as f:
                json.dump(self.profiles, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save profiles:\n{e}")

    def load_profiles(self):
        if not hasattr(self, 'profile_combo'):
            return  # Profile UI disabled
        
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
        if not hasattr(self, 'profile_combo'):
            return  # Profile UI disabled
        
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and name:
            keymap_snapshot = json.loads(json.dumps(self.keymap_data))
            profile_payload = {
                "keymap_data": keymap_snapshot,
                "extensions": {
                    "encoder": {
                        "enabled": self.enable_encoder,
                        "config_str": self.encoder_config_str,
                        "divisor": self.encoder_divisor,
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
                "rgb": {
                    "enabled": self.enable_rgb,
                    "matrix": self._export_rgb_config(),
                },
                "boot_config": self.boot_config_str,  # Save boot.py config
            }
            self.profiles[name] = profile_payload
            self.save_profiles()
            self.load_profiles()
            self.profile_combo.setCurrentText(name)

    def load_selected_profile(self):
        if not hasattr(self, 'profile_combo'):
            return  # Profile UI disabled
        
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            profile = self.profiles.get(profile_name)
            if profile:
                self.keymap_data = profile.get("keymap_data", [])
                self.current_layer = 0

                rgb_section = profile.get("rgb", {}) if isinstance(profile, dict) else {}
                if rgb_section:
                    self.enable_rgb = rgb_section.get("enabled", True)
                    matrix_cfg = rgb_section.get("matrix", {})
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
                    layer_colors_raw = matrix_cfg.get('layer_key_colors', {}) or {}
                    layer_colors = {}
                    for layer, mapping in layer_colors_raw.items():
                        if not isinstance(mapping, dict):
                            continue
                        sanitized = {
                            str(k): ensure_hex_prefix(v, merged['default_key_color'])
                            for k, v in mapping.items()
                        }
                        if sanitized:
                            layer_colors[str(layer)] = sanitized
                    merged['layer_key_colors'] = layer_colors
                    self.rgb_matrix_config = merged

                extensions = profile.get("extensions", {}) if isinstance(profile, dict) else {}
                if extensions:
                    encoder_section = extensions.get("encoder", {})
                    self.enable_encoder = encoder_section.get("enabled", self.enable_encoder)
                    self.encoder_config_str = encoder_section.get("config_str", self.encoder_config_str)
                    self.encoder_divisor = int(encoder_section.get("divisor", self.encoder_divisor or 4))

                    analogin_section = extensions.get("analogin", {})
                    self.enable_analogin = analogin_section.get("enabled", self.enable_analogin)
                    self.analogin_config_str = analogin_section.get("config_str", self.analogin_config_str)

                    display_section = extensions.get("display", {})
                    self.enable_display = display_section.get("enabled", self.enable_display)
                    self.display_config_str = display_section.get("config_str", self.display_config_str)

                # Load boot.py configuration
                if "boot_config" in profile:
                    self.boot_config_str = profile.get("boot_config", "")
                    self.refresh_boot_config_ui()

                self.update_layer_tabs()
                try:
                    self.layer_tabs.setCurrentIndex(self.current_layer)
                except Exception:
                    pass
                self.recreate_macropad_grid()
                self.update_macropad_display()
                self.sync_extension_checkboxes()
                self.update_extension_button_states()
                try:
                    self.save_extension_configs()
                except Exception:
                    pass

    def delete_selected_profile(self):
        if not hasattr(self, 'profile_combo'):
            return  # Profile UI disabled
        
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            reply = QMessageBox.question(self, "Delete Profile", f"Are you sure you want to delete the '{profile_name}' profile?")
            if reply == QMessageBox.StandardButton.Yes:
                if profile_name in self.profiles:
                    del self.profiles[profile_name]
                    self.load_profiles()


            
    # --- Key Assignment ---
    def create_keycode_selector(self):
        """
        Create modern keycode selector with sidebar + content layout.
        
        Features:
        - Left sidebar with vertical category list
        - Right content area with keycode list
        - Global search across all categories
        - Separate Macros/TapDance section below
        - Quick action buttons (Combo, Clear, Transparent)
        - Keyboard navigation support
        
        Layout:
        1. Search bar at top
        2. Horizontal splitter: [Category Sidebar | Keycode Content]
        3. Quick action buttons below keycode list
        4. Macros/TapDance tabbed section at bottom
        
        Returns:
            QWidget container with complete keycode selector UI
        """
        container = QWidget()
        container.setMinimumWidth(450)
        container.setMinimumHeight(600)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # Global search bar
        self.keycode_search_box = QLineEdit()
        self.keycode_search_box.setPlaceholderText("🔍 Search all keycodes...")
        self.keycode_search_box.setClearButtonEnabled(True)
        self.keycode_search_box.textChanged.connect(self._filter_all_keycodes)
        main_layout.addWidget(self.keycode_search_box)

        # Horizontal splitter: Category Sidebar | Keycode Content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT: Category Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setMinimumWidth(140)
        sidebar_widget.setMaximumWidth(220)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(2)  # Very tight spacing for compact windowed display
        
        # Store category buttons for state management
        self.category_buttons = {}
        self.category_list = list(KEYCODES.keys())
        
        # Create category button for each keycode category
        for category in self.category_list:
            icon = self._get_category_icon(category)
            count = len(KEYCODES[category])
            btn = QPushButton(f"{icon} {category}\n({count})")
            btn.setObjectName("categoryButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(f"Show {category} keycodes")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)  # Smaller for windowed mode
            btn.setMaximumHeight(48)  # More compact maximum
            btn.setMinimumWidth(135)
            btn.setMaximumWidth(180)  # Narrower max to prevent stretching
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, cat=category: self.select_category(cat))
            sidebar_layout.addWidget(btn)
            self.category_buttons[category] = btn
        
        # Add Macros button to sidebar
        macro_count = len(self.macros) if hasattr(self, 'macros') else 0
        macros_btn = QPushButton(f"⚡ Macros\n({macro_count})")
        macros_btn.setObjectName("categoryButton")
        macros_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        macros_btn.setToolTip("Show available macros")
        macros_btn.setCheckable(True)
        macros_btn.setMinimumHeight(44)
        macros_btn.setMaximumHeight(48)
        macros_btn.setMinimumWidth(135)
        macros_btn.setMaximumWidth(180)
        macros_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        macros_btn.clicked.connect(lambda: self.select_category("Macros"))
        sidebar_layout.addWidget(macros_btn)
        self.category_buttons["Macros"] = macros_btn
        
        # Add TapDance button to sidebar
        tapdance_btn = QPushButton(f"🎯 TapDance\n(0)")
        tapdance_btn.setObjectName("categoryButton")
        tapdance_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tapdance_btn.setToolTip("Show TapDance keys from custom code")
        tapdance_btn.setCheckable(True)
        tapdance_btn.setMinimumHeight(44)
        tapdance_btn.setMaximumHeight(48)
        tapdance_btn.setMinimumWidth(135)
        tapdance_btn.setMaximumWidth(180)
        tapdance_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        tapdance_btn.clicked.connect(lambda: self.select_category("TapDance"))
        sidebar_layout.addWidget(tapdance_btn)
        self.category_buttons["TapDance"] = tapdance_btn
        
        # Add stretch at bottom to push buttons to top in fullscreen
        sidebar_layout.addStretch(1)
        
        # RIGHT: Keycode Content Area
        content_widget = QWidget()
        content_widget.setMinimumWidth(300)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Keycode list
        self.keycode_list = QListWidget()
        self.keycode_list.setSpacing(2)
        self.keycode_list.setMinimumHeight(300)
        self.keycode_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.keycode_delegate = self.KeycodeListItemDelegate(self.keycode_list)
        self.keycode_list.setItemDelegate(self.keycode_delegate)
        self.keycode_list.itemClicked.connect(self.on_keycode_assigned)
        self.keycode_list.itemDoubleClicked.connect(self.on_keycode_assigned)
        content_layout.addWidget(self.keycode_list, 1)  # Stretch factor to grow
        
        # Container for action buttons (will change based on category)
        self.action_buttons_container = QWidget()
        self.action_buttons_layout = QHBoxLayout(self.action_buttons_container)
        self.action_buttons_layout.setSpacing(8)
        self.action_buttons_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.action_buttons_container)
        
        # Add sidebar and content to splitter
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(content_widget)
        splitter.setSizes([180, 400])  # Give sidebar more room (was 150)
        splitter.setStretchFactor(0, 0)  # Sidebar fixed-ish
        splitter.setStretchFactor(1, 1)  # Content grows
        
        main_layout.addWidget(splitter, 1)  # Full height for splitter
        
        # Store references to macro and tapdance lists for compatibility
        self.macro_keycode_list = self.keycode_list
        self.tapdance_keycode_list = self.keycode_list
        
        # Initialize state
        self.current_category = None
        self._all_keycodes_flat = []
        
        # Build flat keycode list for search
        for category, key_list in KEYCODES.items():
            for keycode in key_list:
                self._all_keycodes_flat.append((category, keycode))
        
        # Select first category by default
        if self.category_list:
            self.select_category(self.category_list[0])
        
        return container

    def _add_keycode_list_item(self, keycode: str) -> None:
        """Insert a keycode row with metadata for custom delegate rendering."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.DisplayRole, keycode)
        item.setData(Qt.ItemDataRole.UserRole, keycode)
        label = KEYCODE_LABELS.get(keycode, "")
        if label:
            item.setData(Qt.ItemDataRole.UserRole + 1, label)
        self.keycode_list.addItem(item)
    
    def select_category(self, category_name: str) -> None:
        """
        Switch to selected category and populate keycode list.
        
        Updates sidebar button states and displays keycodes for the selected category.
        Handles special categories (Macros, TapDance) with appropriate action buttons.
        Saves the selection to session state for persistence across app restarts.
        
        Args:
            category_name: Name of the category to display (e.g., "Letters", "Modifiers", "Macros", "TapDance")
        """
        # Update button states (only one active at a time)
        for name, btn in self.category_buttons.items():
            if name == category_name:
                btn.setChecked(True)
                self._apply_active_button_style(btn)
            else:
                btn.setChecked(False)
                self._apply_inactive_button_style(btn)
        
        # Clear action buttons
        while self.action_buttons_layout.count():
            child = self.action_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Populate keycode list based on category
        self.keycode_list.clear()
        
        if category_name == "Macros":
            # Show macros
            macro_keys = [f"MACRO({name})" for name in sorted(self.macros.keys())]
            self.keycode_list.addItems(macro_keys)
            
            # Add macro action buttons
            create_btn = QPushButton("➕ Create")
            create_btn.clicked.connect(self.add_macro)
            create_btn.setToolTip("Create a new macro")
            self.action_buttons_layout.addWidget(create_btn)
            
            edit_btn = QPushButton("✎ Edit")
            edit_btn.clicked.connect(self.edit_macro)
            edit_btn.setToolTip("Edit selected macro")
            self.action_buttons_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑 Delete")
            delete_btn.clicked.connect(self.remove_macro)
            delete_btn.setToolTip("Delete selected macro")
            self.action_buttons_layout.addWidget(delete_btn)
            
            self.action_buttons_layout.addStretch()
            
        elif category_name == "TapDance":
            # Show tapdance keys (will be populated by update_tapdance_list)
            self.update_tapdance_list()
            
            # Add tapdance action buttons
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.clicked.connect(self.update_tapdance_list)
            refresh_btn.setToolTip("Refresh TapDance list from custom code")
            self.action_buttons_layout.addWidget(refresh_btn)
            
            self.action_buttons_layout.addStretch()
            
        elif category_name in KEYCODES:
            # Regular keycode category
            keycodes = KEYCODES[category_name]
            
            # Add keycodes with right-aligned labels (fixed position from right)
            for keycode in keycodes:
                self._add_keycode_list_item(keycode)
            
            # Add standard keycode action buttons
            combo_btn = QPushButton("⌨ Combo")
            combo_btn.setToolTip("Create a key combination")
            combo_btn.clicked.connect(self.assign_combo)
            self.action_buttons_layout.addWidget(combo_btn)
            
            clear_btn = QPushButton("✖ Clear")
            clear_btn.setToolTip("Set key to KC.NO (no action)")
            clear_btn.clicked.connect(lambda: self.set_key_value("KC.NO"))
            self.action_buttons_layout.addWidget(clear_btn)
            
            transparent_btn = QPushButton("🔄 Transparent")
            transparent_btn.setToolTip("Set key to KC.TRNS (pass-through to lower layer)")
            transparent_btn.clicked.connect(lambda: self.set_key_value("KC.TRNS"))
            self.action_buttons_layout.addWidget(transparent_btn)
            
            self.action_buttons_layout.addStretch()
        
        # Update current category tracking
        self.current_category = category_name
        
        # Save to session state
        self.save_session_state()
    
    def _apply_active_button_style(self, button: QPushButton) -> None:
        """
        Apply active (selected) styling to a category button.
        
        Args:
            button: The QPushButton to style as active
        """
        button.setStyleSheet("""
            QPushButton {
                background-color: #4a9aff;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 10px;
                text-align: center;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #60a5fa;
            }
        """)
    
    def _apply_inactive_button_style(self, button: QPushButton) -> None:
        """
        Apply inactive (unselected) styling to a category button.
        
        Args:
            button: The QPushButton to style as inactive
        """
        button.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #e5e7eb;
                border-radius: 6px;
                padding: 6px 10px;
                text-align: center;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
    
    def _get_category_icon(self, category):
        """Return an appropriate icon emoji for each category."""
        icons = {
            "Letters": "🔤",
            "Numbers & Symbols": "🔢",
            "Editing": "✏",
            "Modifiers": "⌨",
            "Navigation": "🧭",
            "Function Keys": "🔧",
            "Media & Volume": "🔊",
            "Brightness": "💡",
            "Numpad": "🔢",
            "Mouse": "🖱",
            "Layer Switching": "📚",
            "Special": "⭐"
        }
        return icons.get(category, "🔸")
    
    def _filter_all_keycodes(self, filter_text: str) -> None:
        """
        Search across all categories and display results grouped by category.
        
        When search is active, results are organized with category headers.
        When search is cleared, returns to showing the current category.
        
        Args:
            filter_text: User-entered search text (case-insensitive)
        """
        if not hasattr(self, "_all_keycodes_flat"):
            return

        search_value = (filter_text or "").strip().lower()

        # If search is empty, show current category
        if not search_value:
            if hasattr(self, 'current_category') and self.current_category:
                self.select_category(self.current_category)
            elif hasattr(self, 'category_list') and self.category_list:
                self.select_category(self.category_list[0])
            return

        # Search across all categories
        self.keycode_list.clear()
        found_any = False
        current_category_shown = None

        for category, keycode in self._all_keycodes_flat:
            # Get label for search matching
            label = KEYCODE_LABELS.get(keycode, "")
            search_text = f"{keycode} {label}".lower()
            
            if search_value in search_text:
                found_any = True
                
                # Add category header if this is first result from this category
                if category != current_category_shown:
                    header_item = QListWidgetItem(f"━━━ {category} ━━━")
                    header_item.setForeground(QColor("#9ca3af"))
                    header_item.setBackground(QColor("#1f2937"))
                    header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    self.keycode_list.addItem(header_item)
                    current_category_shown = category
                
                # Add matching keycode with right-aligned label (fixed position from right)
                self._add_keycode_list_item(keycode)

        if not found_any:
            no_results = QListWidgetItem("No matching keycodes found")
            no_results.setForeground(QColor("#9ca3af"))
            no_results.setFlags(no_results.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.keycode_list.addItem(no_results)

    def _on_search_result_selected(self, item: QListWidgetItem) -> None:
        """Assign keycode chosen from the global search result list."""
        keycode = item.data(Qt.ItemDataRole.UserRole)
        if keycode:
            proxy_item = QListWidgetItem(keycode)
            self.on_keycode_assigned(proxy_item)
            # Clear search to return to tab view
            self.keycode_search_box.clear()
    
    def _on_category_pill_clicked(self, index: int):
        """
        Handle category pill button clicks for quick navigation.
        
        Updates the active tab to match the clicked category pill and
        synchronizes the visual state of all pills (only one active).
        
        Args:
            index: Tab index to navigate to (matches pill button index)
        """
        # Update tab selection
        if hasattr(self, 'keycode_tabs') and self.keycode_tabs:
            self.keycode_tabs.setCurrentIndex(index)
        
        # Update pill visual states (uncheck all except clicked)
        for i, pill in enumerate(self.category_pills):
            pill.setChecked(i == index)
        
        # Save session state
        self.save_session_state()
    
    def _on_tab_changed(self, index: int):
        """
        Handle tab widget changes to synchronize category pills.
        
        When user clicks a tab directly (not via pill), this updates
        the pill button states to match the selected tab.
        
        Args:
            index: New active tab index
        """
        # Update pill visual states
        if hasattr(self, 'category_pills'):
            for i, pill in enumerate(self.category_pills):
                pill.setChecked(i == index)
        
        # Save session state
        self.save_session_state()
    
    def _get_category_icon(self, category):
        """Return an appropriate icon emoji for each category."""
        icons = {
            "Letters": "🔤",
            "Numbers & Symbols": "🔢",
            "Editing": "✏",
            "Modifiers": "⌨",
            "Navigation": "🧭",
            "Function Keys": "🔧",
            "Media & Volume": "🔊",
            "Brightness": "💡",
            "Numpad": "🔢",
            "Mouse": "🖱",
            "Layer Switching": "📚",
            "Special": "⭐"
        }
        return icons.get(category, "🔸")

    def on_keycode_assigned(self, item):
        # Extract actual keycode from UserRole data, fall back to text for macros/tapdance
        keycode = item.data(Qt.ItemDataRole.UserRole)
        if not keycode:
            keycode = item.text()  # For macros/tapdance which don't have UserRole data
        
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
        """
        Edit an existing macro.
        
        Opens the macro editor dialog pre-populated with the selected macro's
        data. If the macro name changes, updates all keymap references.
        Prompts user to select a macro from the list if none is selected.
        """
        selected_items = self.macro_keycode_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Macro Selected", "Please select a macro from the list to edit.")
            return
        
        # Extract macro name from "MACRO(name)" format
        item_text = selected_items[0].text()
        if item_text.startswith("MACRO(") and item_text.endswith(")"):
            name = item_text[6:-1]  # Strip "MACRO(" and ")"
        else:
            name = item_text
        
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
        """
        Remove a macro from the configuration.
        
        Prompts for confirmation before deletion. Replaces all keymap
        occurrences of the deleted macro with the default key (KC.NO).
        """
        selected_items = self.macro_keycode_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Macro Selected", "Please select a macro from the list to delete.")
            return
        
        # Extract macro name from "MACRO(name)" format
        item_text = selected_items[0].text()
        if item_text.startswith("MACRO(") and item_text.endswith(")"):
            name = item_text[6:-1]  # Strip "MACRO(" and ")"
        else:
            name = item_text
        
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
        """
        Refresh the macro list displays with current macro data.
        
        Updates the keycode list if Macros category is active, updates
        the Macros button count, and updates left panel list if it exists.
        """
        # Update left panel list if it exists
        if hasattr(self, 'macro_list_widget'):
            self.macro_list_widget.clear()
            self.macro_list_widget.addItems(sorted(self.macros.keys()))
            # Allow double-clicking a macro name in the left list to edit it
            self.macro_list_widget.itemDoubleClicked.connect(lambda item: self.edit_macro_by_name(item.text()))
        
        # Update keycode list if Macros category is active
        if hasattr(self, 'current_category') and self.current_category == "Macros":
            self.keycode_list.clear()
            macro_keys = [f"MACRO({name})" for name in sorted(self.macros.keys())]
            self.keycode_list.addItems(macro_keys)
        
        # Update Macros button count
        if hasattr(self, 'category_buttons') and "Macros" in self.category_buttons:
            self.category_buttons["Macros"].setText(f"⚡ Macros\n({len(self.macros)})")

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
                return macro_name[:4] if len(macro_name) > 4 else macro_name
            
            # Handle layer switches
            if "MO(" in key_str or "TG(" in key_str or "TO(" in key_str:
                return key_str.replace("KC.", "")[:4]
            
            # Handle key combinations (e.g., KC.LCTL(KC.C))
            if "(" in key_str:
                # Simplify combinations like LCTL(C) -> C^C
                parts = key_str.replace("KC.", "").replace("(", "+").replace(")", "")
                return parts[:4]
            
            # Standard keys - remove KC. prefix
            key = key_str.replace("KC.", "")
            
            # Common abbreviations for display (max 4 chars for small OLED)
            abbreviations = {
                # Modifiers (3 chars)
                "LCTL": "LCt", "RCTL": "RCt",
                "LSFT": "LSh", "RSFT": "RSh", 
                "LALT": "LAl", "RALT": "RAl",
                "LGUI": "LWi", "RGUI": "RWi",
                # Common actions (3-4 chars)
                "BSPC": "BkSp", "ENT": "Ent",
                "SPC": "Spc", "TAB": "Tab",
                "ESC": "Esc", "DEL": "Del",
                # Navigation (3-4 chars)
                "PGUP": "PgUp", "PGDN": "PgDn",
                "HOME": "Hom", "END": "End",
                "UP": "Up", "DOWN": "Dwn",
                "LEFT": "Lft", "RGHT": "Rgt",
                # Media (3-4 chars)
                "VOLU": "V+", "VOLD": "V-",
                "MUTE": "Mut", "MPLY": "Ply",
                "MNXT": "Nxt", "MPRV": "Prv",
                "MSTP": "Stp", "EJCT": "Ejt",
                "BRIU": "B+", "BRID": "B-",
                # Numbers stay as-is
                "N1": "1", "N2": "2", "N3": "3", "N4": "4", "N5": "5",
                "N6": "6", "N7": "7", "N8": "8", "N9": "9", "N0": "0",
                # Function keys
                "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4",
                "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8",
                "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
            }
            
            key = abbreviations.get(key, key)
            return key[:4] if len(key) > 4 else key
        
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

        keymap_layers = self.keymap_data or []
        num_layers = max(1, len(keymap_layers))
        layer_key_overrides = cfg.get('layer_key_colors', {}) or {}
        global_key_map = cfg.get('key_colors', {}) or {}
        default_key_rgb = hex_to_rgb_list(cfg['default_key_color'])
        default_under_rgb = hex_to_rgb_list(cfg['default_underglow_color'])

        key_entries_by_layer = []
        for layer_idx in range(num_layers):
            layer_data = keymap_layers[layer_idx] if 0 <= layer_idx < len(keymap_layers) else None
            entries = []
            overrides = layer_key_overrides.get(str(layer_idx), {}) or {}
            for idx in range(num_keys):
                override_color = overrides.get(str(idx)) or global_key_map.get(str(idx))
                if override_color:
                    rgb = hex_to_rgb_list(override_color)
                else:
                    row = idx // self.cols
                    col = idx % self.cols
                    keycode = DEFAULT_KEY
                    if layer_data and row < len(layer_data) and col < len(layer_data[row]):
                        keycode = layer_data[row][col]
                    elif keymap_layers:
                        base_layer = keymap_layers[0]
                        if row < len(base_layer) and col < len(base_layer[row]):
                            keycode = base_layer[row][col]
                    if keycode == "KC.TRNS" and layer_idx > 0 and key_entries_by_layer:
                        rgb = key_entries_by_layer[layer_idx - 1][idx][:]
                    elif keycode == "KC.NO":
                        rgb = [0, 0, 0]
                    else:
                        rgb = default_key_rgb.copy()
                entries.append(rgb)
            key_entries_by_layer.append(entries)

        under_map = cfg.get('underglow_colors', {}) or {}
        under_entries_rgb = []
        for idx in range(max(0, underglow_count)):
            custom = under_map.get(str(idx))
            if custom:
                under_entries_rgb.append(hex_to_rgb_list(custom))
            else:
                under_entries_rgb.append(default_under_rgb.copy())

        def format_entries(entries):
            if not entries:
                return "[]"
            chunks = []
            for start in range(0, len(entries), 8):
                chunk = ", ".join(f"[{rgb[0]}, {rgb[1]}, {rgb[2]}]" for rgb in entries[start:start+8])
                chunks.append(f"                {chunk}")
            return "[\n" + ",\n".join(chunks) + "\n            ]"

        keys_array = format_entries(key_entries_by_layer[0] if key_entries_by_layer else [])
        under_array = format_entries(under_entries_rgb)

        layer_rgb_maps = []
        for entries in key_entries_by_layer:
            combined = [list(rgb) for rgb in entries]
            if under_entries_rgb:
                combined.extend([list(rgb) for rgb in under_entries_rgb])
            layer_rgb_maps.append(combined)

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

        key_pixel_pos = KEY_PIXEL_ORDER[:num_keys]
        if len(key_pixel_pos) != num_keys:
            key_pixel_pos = list(range(num_keys))

        led_key_pos_entries = key_pixel_pos.copy()
        for idx in range(underglow_count):
            led_key_pos_entries.append(num_keys + idx)

        led_key_repr = ", ".join(str(p) for p in led_key_pos_entries)

        code_lines = [
            "# Peg RGB Matrix configuration",
            f"keyboard.rgb_pixel_pin = {pixel_pin}",
            f"keyboard.num_pixels = {total_pixels}",
            f"keyboard.brightness_limit = {brightness}",
            f"keyboard.led_key_pos = [{led_key_repr}]  # Key pixel mapping + underglow",
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

        layer_rgb_maps_str = json.dumps(layer_rgb_maps, indent=4)
        code_lines.append("layer_rgb_maps = " + layer_rgb_maps_str)
        code_lines.append("")
        code_lines.extend([
            "class LayerRgbSync:",
            '    """Update Peg RGB colors to match the active layer."""',
            "    def __init__(self, rgb_ext, layer_maps):",
            "        self.rgb_ext = rgb_ext",
            "        self.layer_maps = layer_maps or []",
            "        self._last_layer = None",
            "        self._applied_once = False",
            "",
            "    def _active_layer(self, keyboard):",
            "        try:",
            '            layers = getattr(keyboard, "active_layers", None)',
            "            if layers:",
            "                return layers[-1]",
            "        except Exception:",
            "            pass",
            "        return 0",
            "",
            "    def _apply(self, keyboard, layer):",
            "        if not self.rgb_ext or not self.layer_maps:",
            "            return",
            "        idx = layer if 0 <= layer < len(self.layer_maps) else 0",
            "        target_map = self.layer_maps[idx]",
            "        if not target_map:",
            "            return",
            "        self.rgb_ext.ledDisplay = [list(rgb) for rgb in target_map]",
            "        neopixel_obj = getattr(self.rgb_ext, 'neopixel', None)",
            "        if not neopixel_obj:",
            "            return",
            "        try:",
            "            self.rgb_ext.setBasedOffDisplay()",
            "            if getattr(self.rgb_ext, 'disable_auto_write', False):",
            "                neopixel_obj.show()",
            "            self._last_layer = layer",
            "            self._applied_once = True",
            "        except Exception:",
            "            pass",
            "",
            "    def _check(self, keyboard):",
            "        if not self.layer_maps:",
            "            return",
            "        layer = self._active_layer(keyboard)",
            "        if layer != self._last_layer or not self._applied_once:",
            "            self._apply(keyboard, layer)",
            "",
            "    def during_bootup(self, keyboard):",
            "        self._last_layer = None",
            "        self._applied_once = False",
            "        self._apply(keyboard, self._active_layer(keyboard))",
            "",
            "    def after_matrix_scan(self, keyboard):",
            "        self._check(keyboard)",
            "",
            "    def after_hid_send(self, keyboard):",
            "        self._check(keyboard)",
            "",
            "    def before_hid_send(self, keyboard):",
            "        self._check(keyboard)",
            "",
            "    def before_matrix_scan(self, keyboard):",
            "        return",
            "",
            "    def on_powersave_enable(self, keyboard):",
            "        return",
            "",
            "    def on_powersave_disable(self, keyboard):",
            "        return",
        ])
        code_lines.append("")
        code_lines.append("layer_rgb_sync = LayerRgbSync(rgb, layer_rgb_maps)")
        code_lines.append("keyboard.modules.append(layer_rgb_sync)\n")

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
        
        # Add custom extension code if present
        if self.custom_ext_code and self.custom_ext_code.strip():
            ext_snippets += "# Custom Extension Code:\n"
            ext_snippets += self.custom_ext_code.strip() + "\n\n"
        
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
        return BASE_DIR  # Fallback to application directory
    
    def find_board_drive(self, drive_name="CIRCUITPY"):
        """Find a specific board drive by name.
        
        Args:
            drive_name: Name of the drive to find (e.g., 'CIRCUITPY', 'CHRONOSPAD')
            
        Returns:
            str: Path to the drive if found, None otherwise
        """
        import platform
        system = platform.system()
        
        if system == "Windows":
            import string
            from ctypes import windll, create_unicode_buffer
            
            # Check all drive letters
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                # Check if drive exists
                drive_type = windll.kernel32.GetDriveTypeW(drive)
                # DRIVE_REMOVABLE = 2, DRIVE_FIXED = 3
                if drive_type in (2, 3):
                    # Get volume label
                    volume_name_buffer = create_unicode_buffer(261)
                    file_system_buffer = create_unicode_buffer(261)
                    
                    result = windll.kernel32.GetVolumeInformationW(
                        drive,
                        volume_name_buffer,
                        261,
                        None,
                        None,
                        None,
                        file_system_buffer,
                        261
                    )
                    
                    if result:
                        volume_label = volume_name_buffer.value
                        if volume_label == drive_name:
                            return drive
                    
        elif system == "Darwin":  # macOS
            path = f"/Volumes/{drive_name}"
            if os.path.exists(path):
                return path
                
        else:  # Linux
            username = os.getlogin()
            for base_path in [f"/media/{username}", f"/run/media/{username}"]:
                path = os.path.join(base_path, drive_name)
                if os.path.exists(path):
                    return path
        
        return None
    
    def select_board_dialog(self, found_drives):
        """Show dialog to select which board to flash when multiple are found.
        
        Args:
            found_drives: Dictionary of {drive_name: drive_path}
            
        Returns:
            str: Selected drive name, or None if cancelled
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Board")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel(
            f"<h3>Multiple Boards Found ({len(found_drives)})</h3>"
            "Select which board you want to flash:"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # List of drives
        drive_list = QListWidget()
        for drive_name, drive_path in found_drives.items():
            item = QListWidgetItem(f"{drive_name} ({drive_path})")
            item.setData(Qt.ItemDataRole.UserRole, drive_name)
            drive_list.addItem(item)
        
        drive_list.setCurrentRow(0)
        layout.addWidget(drive_list)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            current_item = drive_list.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
        
        return None

    def find_circuitpy_drive(self):
        """Legacy method - find CIRCUITPY drive specifically."""
        return self.find_board_drive("CIRCUITPY") or BASE_DIR

    def generate_code_py_dialog(self):
        """Generate code.py and offer to save to board drive.
        Checks for saved custom board names and auto-navigates to found drives."""
        
        # Check for any saved board names
        settings = load_settings()
        board_names = settings.get('board_names', [])
        
        # Always include CIRCUITPY as default
        all_drive_names = ['CIRCUITPY'] + board_names
        
        # Find which drives are currently mounted
        found_drives = {}
        for drive_name in all_drive_names:
            drive_path = self.find_board_drive(drive_name)
            if drive_path and os.path.exists(drive_path):
                found_drives[drive_name] = drive_path
        
        # Determine default path based on found drives
        default_path = BASE_DIR  # Fallback
        selected_drive_name = None
        
        if len(found_drives) == 0:
            # No drives found, use fallback
            default_path = BASE_DIR
        elif len(found_drives) == 1:
            # Only one drive found, use it automatically
            selected_drive_name = list(found_drives.keys())[0]
            default_path = found_drives[selected_drive_name]
        else:
            # Multiple drives found, ask user which one to use
            selected_drive_name = self.select_board_dialog(found_drives)
            if selected_drive_name:
                default_path = found_drives[selected_drive_name]
            else:
                default_path = BASE_DIR  # User cancelled
        
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
                    kmk_source = os.path.join(BASE_DIR, "libraries", "kmk")
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
                
                # Copy required libraries from bundled CircuitPython 10.x libs
                lib_source = os.path.join(BASE_DIR, "libraries", "lib")
                lib_dest = os.path.join(folder_path, "lib")
                
                if not os.path.exists(lib_source):
                    QMessageBox.warning(self, "Warning",
                        "CircuitPython 10.x libraries not found!\n\n"
                        "The application will download them automatically on next startup.\n"
                        "For now, code.py will be saved but libraries must be manually copied.\n\n"
                        "Required files:\n"
                        "  • adafruit_displayio_sh1106.mpy\n"
                        "  • adafruit_display_text/ (folder)\n"
                        "  • neopixel.mpy\n\n"
                        f"Expected location: {lib_source}")
                    lib_source = None
                
                # Create lib folder if it doesn't exist
                os.makedirs(lib_dest, exist_ok=True)
                
                # Required libraries list
                required_libs = [
                    "adafruit_displayio_sh1106.mpy",
                    "adafruit_display_text",  # folder
                    "neopixel.mpy"
                ]
                
                copied_files = []
                if lib_source:  # Only copy if libraries were found
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
                
                # Save boot.py if configured
                boot_saved = False
                if self.boot_config_str and self.boot_config_str.strip():
                    boot_path = os.path.join(folder_path, "boot.py")
                    try:
                        with open(boot_path, 'w') as f:
                            f.write(self.boot_config_str)
                        boot_saved = True
                        
                        # Extract and save custom drive name from boot.py
                        import re
                        label_match = re.search(r'storage\.getmount\("/"\)\.label\s*=\s*["\']([^"\']+)["\']', 
                                              self.boot_config_str)
                        if label_match:
                            custom_drive_name = label_match.group(1).strip()
                            if custom_drive_name and custom_drive_name != "CIRCUITPY":
                                # Save to settings for future auto-detection
                                settings = load_settings()
                                board_names = settings.get('board_names', [])
                                if custom_drive_name not in board_names:
                                    board_names.append(custom_drive_name)
                                    settings['board_names'] = board_names
                                    save_settings(settings)
                                    
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Could not save boot.py:\n{e}")
                
                msg = f"code.py saved successfully to:\n{file_path}\n\n"
                if kmk_copied:
                    msg += f"✓ KMK firmware copied to {kmk_dest}\n\n"
                if boot_saved:
                    msg += f"✓ boot.py saved to {os.path.join(folder_path, 'boot.py')}\n\n"
                
                if copied_files:
                    msg += f"✓ Libraries copied from CircuitPython 10.x bundle to {lib_dest}:\n" + "\n".join(f"  • {f}" for f in copied_files)
                else:
                    msg += f"⚠️ No libraries were copied.\n\n"
                    msg += "CircuitPython 10.x libraries not found.\n"
                    msg += "Please restart the app to download dependencies automatically."
                
                QMessageBox.information(self, "Success", msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save code.py file:\n{e}")

    def save_configuration_dialog(self):
        # Ensure config save directory exists
        os.makedirs(CONFIG_SAVE_DIR, exist_ok=True)
        
        # Set the initial directory to CONFIG_SAVE_DIR
        initial_path = os.path.join(CONFIG_SAVE_DIR, "config.json")
        
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
                # Refresh config list to include the newly saved file
                if hasattr(self, 'config_file_combo'):
                    self.populate_config_file_list()
                    # Try to set dropdown to the saved file (only works if in BASE_DIR)
                    try:
                        rel_path = os.path.relpath(file_path, BASE_DIR)
                        idx = self.config_file_combo.findText(rel_path)
                        if idx >= 0:
                            self.config_file_combo.setCurrentIndex(idx)
                    except ValueError:
                        # File is on a different drive, can't compute relative path
                        # This is fine - just skip updating the dropdown
                        pass
                QMessageBox.information(self, "Success", f"Configuration saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}\n\nTraceback:\n{traceback.format_exc()}")
        else:
            # User cancelled the dialog
            print("Save cancelled by user")

    def save_configuration_to_path(self, file_path):
        """Save complete configuration including all layers, RGB colors, extension settings, and used macros.
        
        Note: Only macros that are actually used in the keymap are saved with the config.
        All macros remain in the global macros.json file as well.
        """
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
            "macros": self.get_macros_used_in_keymap(),  # Save macros used in this config
            "rgb": {
                "enabled": self.enable_rgb,
                "matrix": self._export_rgb_config(),
            },
            "extensions": {
                "encoder": {
                    "enabled": self.enable_encoder,
                    "config_str": self.encoder_config_str,
                    "divisor": self.encoder_divisor,
                },
                "analogin": {
                    "enabled": self.enable_analogin,
                    "config_str": self.analogin_config_str,
                    "settings": load_settings().get('analog_input', {}),  # Save analog input settings
                },
                "display": {
                    "enabled": self.enable_display,
                    "config_str": self.display_config_str,
                },
            },
            "boot_config": self.boot_config_str,  # Save boot.py configuration
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save configuration file:\n{e}")
            raise e

    def load_config_from_dropdown(self):
        """Load configuration when selected from dropdown."""
        if not hasattr(self, 'config_file_combo'):
            return
        
        sel = self.config_file_combo.currentText()
        if not sel:
            return
            
        file_path = os.path.join(BASE_DIR, sel)
        if os.path.exists(file_path):
            self.load_configuration(file_path=file_path, show_message=True)

    def load_configuration(self, file_path=None, show_message=True):
        """Load a saved configuration from disk.
        
        When called from the Load button (file_path=None), ALWAYS opens file dialog.
        When called from dropdown or programmatically, uses the provided path.
        """
        selected_path = file_path

        if not selected_path:
            # Always open file dialog when Load button is clicked
            start_dir = CONFIG_SAVE_DIR if os.path.exists(CONFIG_SAVE_DIR) else BASE_DIR
            selected_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Load Configuration", 
                start_dir,  # Start in config save directory
                "JSON Files (*.json)"
            )
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
                
                # Load macros (check for new macros and offer to import)
                config_macros = self._sanitize_macros(config_data.get("macros", {}))
                if config_macros:
                    # Find macros that are NEW (not already in global store)
                    new_macros = {name: actions for name, actions in config_macros.items() 
                                 if name not in self.macros}
                    
                    if new_macros:
                        # Ask user if they want to import new macros
                        imported_macros = self.show_macro_import_dialog(new_macros)
                        if imported_macros:
                            # Merge imported macros into global store
                            self.macros.update(imported_macros)
                            try:
                                self.save_macros()
                            except Exception:
                                pass
                    
                    # Also merge any existing macros (in case config uses them)
                    existing_config_macros = {name: actions for name, actions in config_macros.items() 
                                            if name in self.macros}
                    if existing_config_macros:
                        # Silently include existing macros without asking
                        pass  # They're already in self.macros
                
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
                self.encoder_divisor = int(encoder_section.get("divisor", self.encoder_divisor or 4))
                
                analogin_section = extensions.get("analogin", {})
                self.enable_analogin = analogin_section.get("enabled", True)
                self.analogin_config_str = analogin_section.get("config_str", DEFAULT_ANALOGIN_CONFIG)
                
                display_section = extensions.get("display", {})
                self.enable_display = display_section.get("enabled", True)
                self.display_config_str = display_section.get("config_str", "")
                
                # Load boot.py configuration
                self.boot_config_str = config_data.get("boot_config", "")
                self.refresh_boot_config_ui()
                
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
            
            if hasattr(self, 'profile_combo'):
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
        """
        Clears and rebuilds the macropad grid buttons with enhanced modern visual design.
        
        Features:
        - 100×100px buttons (increased from 80×80)
        - 12px spacing for cleaner modern layout
        - Coordinate labels for easy identification
        - Visual hover effects and selection states
        - 180° rotation to match physical hardware orientation
        
        Note:
            Restores previous selection state if the key still exists after rebuild.
        """
        self.clear_macropad_grid()
        # Iterate in reverse (180° rotation) to match physical board orientation
        for r in range(self.rows - 1, -1, -1):
            for c in range(self.cols - 1, -1, -1):
                button = QPushButton()
                button.setObjectName("keymapButton")
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.setMinimumSize(100, 100)  # Increased from 80 to 100 for modern layout
                button.setCheckable(True)
                button.clicked.connect(partial(self.on_key_selected, r, c))
                # allow double-click detection via the main window's eventFilter
                button.installEventFilter(self)
                
                # Enable context menu (right-click)
                button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                button.customContextMenuRequested.connect(partial(self.show_key_context_menu, r, c))
                
                # Add coordinate label for easier identification
                button.setProperty("coords", f"({r},{c})")
                
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
        if hasattr(self, 'profile_combo'):
            self.profile_combo.setCurrentText("Custom")
        self.update_macropad_display()

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
            # Save session state when layer changes
            self.save_session_state()

    def update_layer_tabs(self):
        """Clears and rebuilds the layer tabs from the keymap data."""
        self.layer_tabs.blockSignals(True)
        current_index = self.layer_tabs.currentIndex()
        self.layer_tabs.clear()
        for i in range(len(self.keymap_data)):
            tab = QWidget()
            placeholder_layout = QVBoxLayout(tab)
            placeholder_layout.setContentsMargins(0, 0, 0, 0)
            placeholder_layout.addStretch()
            self.layer_tabs.addTab(tab, f"Layer {i}")
            self.layer_tabs.setTabToolTip(i, f"Layer {i}")

        if self.layer_tabs.count():
            target_index = current_index if 0 <= current_index < self.layer_tabs.count() else 0
            self.layer_tabs.setCurrentIndex(target_index)

        self.layer_tabs.blockSignals(False)

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
            # Update grid selection label if it exists
            if hasattr(self, 'grid_selection_label'):
                self.grid_selection_label.setText("Selected: None")
            # The button's check state is toggled automatically by PyQt
        else: # Otherwise, select the new key
            self.selected_key_coords = clicked_coords
            key_value = self.keymap_data[self.current_layer][row][col] if self.current_layer < len(self.keymap_data) else "KC.NO"
            self.selected_key_label.setText(f"Selected Key: ({row}, {col})")
            # Update grid selection label if it exists
            if hasattr(self, 'grid_selection_label'):
                self.grid_selection_label.setText(f"Selected: (Row {row}, Col {col}) | {key_value}")
            current_button = self.macropad_buttons.get(clicked_coords)
            if current_button:
                current_button.setChecked(True)
        
        # Save session state when key selection changes
        self.save_session_state()

    def update_macropad_display(self):
        """Updates the text on all grid buttons to reflect the current layer's keymap with enhanced formatting."""
        if self.current_layer >= len(self.keymap_data): return
        
        layer_data = self.keymap_data[self.current_layer]
        rgb_cfg = getattr(self, 'rgb_matrix_config', build_default_rgb_matrix_config())
        layer_colors = (rgb_cfg.get('layer_key_colors', {}) or {}).get(str(self.current_layer), {})
        key_colors = rgb_cfg.get('key_colors', {})
        
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                button = self.macropad_buttons.get((r, c))
                if button:
                    key_text = layer_data[r][c]
                    
                    # Format different key types for better readability
                    macro_match = re.match(r"MACRO\((\w+)\)", key_text)
                    if macro_match:
                        display_text = f"⚡ {macro_match.group(1)}"
                    elif key_text.startswith("TD_"):
                        # TapDance keys
                        display_text = f"🎯 {key_text[3:]}"
                    elif "MO(" in key_text or "TO(" in key_text or "TG(" in key_text or "DF(" in key_text:
                        # Layer switching keys
                        display_text = f"📚 {key_text.replace('KC.', '')}"
                    elif key_text == "KC.NO":
                        display_text = "✖"
                    elif key_text == "KC.TRNS":
                        display_text = "🔄 TRNS"
                    else:
                        # Standard keycodes - remove KC. prefix
                        display_text = key_text.replace("KC.", "")
                    
                    # Add coordinate label below for easier identification
                    full_text = f"{display_text}\n({r},{c})"
                    button.setText(full_text)
                    
                    # Apply RGB color if assigned to this key
                    color = layer_colors.get(str(idx)) or key_colors.get(str(idx))
                    if color:
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
                        
                        button.setStyleSheet(f'background-color: {color}; color: {text_color}; font-weight: bold; font-size: 9pt;')
                    else:
                        # Clear any previous color styling but keep the default button style
                        button.setStyleSheet('font-size: 9pt;')
                idx += 1
        self.macropad_group.setTitle(f"⌨ Keymap Grid (Layer {self.current_layer})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMKConfigurator()
    window.show()
    sys.exit(app.exec())


