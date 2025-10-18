import sys
import re
import ast
import json
import os
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QGridLayout, QSpinBox, QListWidget,
    QTabWidget, QSizePolicy, QLineEdit, QFileDialog, QMessageBox,
    QComboBox, QDialog, QDialogButtonBox, QCheckBox, QInputDialog, QColorDialog
)
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QObject
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from functools import partial

# --- Default Values ---
DEFAULT_ROWS = 3
DEFAULT_COLS = 4
DEFAULT_KEY = "KC.NO"
CONFIG_SAVE_DIR = os.path.join(os.getcwd(), "kmk_Config_Save")
MACRO_FILE = os.path.join(CONFIG_SAVE_DIR, "macros.json")
PROFILE_FILE = "profiles.json"


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
        "KC.VOLU", "KC.VOLD", "KC.MUTE", "KC.PLAY",
        "KC.NEXT", "KC.PREV", "KC.STOP", "KC.EJCT"
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
        "KC.NO", "KC.TRNS", "KC.RESET", "KC.CAPS", "KC.PSCR", "KC.SLCK",
        "KC.PAUS", "KC.NUM", "KC.APP"
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
    Qt.Key.Key_Equal: "KC.EQL", Qt.Key.Key_A: "KC.A", Qt.Key.Key_B: "KC.B",
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
        
        keycode = QT_TO_KMK.get(key)
        if keycode:
            # Record the press and remember when/where it was added so we
            # can convert it to a 'tap' later if released quickly.
            now = time.monotonic()
            self.sequence.append(('press', keycode))
            self.sequence_list.addItem(f"Press: {keycode}")
            self.press_timestamps[key] = (now, len(self.sequence) - 1)
            self.press_timestamps[key] = (now, len(self.sequence) - 1)

    def keyReleaseEvent(self, event):
        if not self.recording or event.isAutoRepeat():
            super().keyReleaseEvent(event)
            return

        key = event.key()
        if key not in self.pressed_keys:
            return
            
        self.pressed_keys.discard(key)
        
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
    """Form-based editor for Encoder configuration.
    Produces a small Python snippet that sets up encoder_handler.pins and encoder_handler.map.
    """
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Encoder Configuration")
        self.resize(700, 500)

        self.encoders = []  # list of dicts

        main_layout = QVBoxLayout(self)

        # List of encoders
        enc_list_layout = QHBoxLayout()
        self.encoder_list = QListWidget()
        enc_list_layout.addWidget(self.encoder_list, 2)

        enc_form_layout = QVBoxLayout()
        enc_form_layout.addWidget(QLabel("Pin A:"))
        self.pin_a_input = QLineEdit()
        enc_form_layout.addWidget(self.pin_a_input)
        enc_form_layout.addWidget(QLabel("Pin B:"))
        self.pin_b_input = QLineEdit()
        enc_form_layout.addWidget(self.pin_b_input)
        enc_form_layout.addWidget(QLabel("Button Pin (or leave blank):"))
        self.button_pin_input = QLineEdit()
        enc_form_layout.addWidget(self.button_pin_input)
        self.invert_checkbox = QCheckBox("Invert direction")
        enc_form_layout.addWidget(self.invert_checkbox)
        enc_form_layout.addWidget(QLabel("Divisor (2 or 4):"))
        self.divisor_input = QLineEdit()
        self.divisor_input.setText("4")
        enc_form_layout.addWidget(self.divisor_input)

        add_enc_btn = QPushButton("Add / Update Encoder")
        add_enc_btn.clicked.connect(self.add_or_update_encoder)
        enc_form_layout.addWidget(add_enc_btn)

        remove_enc_btn = QPushButton("Remove Selected Encoder")
        remove_enc_btn.clicked.connect(self.remove_selected_encoder)
        enc_form_layout.addWidget(remove_enc_btn)
        enc_list_layout.addLayout(enc_form_layout, 1)

        main_layout.addLayout(enc_list_layout)

        # Encoder map area (simple free text; user can paste a list structure)
        main_layout.addWidget(QLabel("Optional encoder.map (Python list literal). Example: [( (KC.VOLD, KC.VOLU, KC.MUTE), ), ]"))
        self.map_editor = QTextEdit()
        main_layout.addWidget(self.map_editor)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # If initial_text is provided, attempt to load it into map_editor
        if initial_text:
            self.map_editor.setPlainText(initial_text)

        # Wire list selection
        self.encoder_list.itemClicked.connect(self.on_encoder_item_clicked)

    def add_or_update_encoder(self):
        a = self.pin_a_input.text().strip()
        b = self.pin_b_input.text().strip()
        btn = self.button_pin_input.text().strip() or None
        inv = bool(self.invert_checkbox.isChecked())
        try:
            divisor = int(self.divisor_input.text().strip())
        except Exception:
            divisor = 4

        if not a or not b:
            QMessageBox.warning(self, "Invalid", "Pin A and Pin B are required")
            return

        entry = {"a": a, "b": b, "btn": btn, "invert": inv, "divisor": divisor}

        # If an item is selected, update it; otherwise append
        sel = self.encoder_list.selectedItems()
        if sel:
            idx = self.encoder_list.row(sel[0])
            self.encoders[idx] = entry
            sel[0].setText(f"{a},{b},{btn or 'None'}, inv={inv}, div={divisor}")
        else:
            self.encoders.append(entry)
            self.encoder_list.addItem(f"{a},{b},{btn or 'None'}, inv={inv}, div={divisor}")

    def remove_selected_encoder(self):
        sel = self.encoder_list.selectedItems()
        if not sel:
            return
        idx = self.encoder_list.row(sel[0])
        self.encoder_list.takeItem(idx)
        del self.encoders[idx]

    def on_encoder_item_clicked(self, item):
        idx = self.encoder_list.row(item)
        e = self.encoders[idx]
        self.pin_a_input.setText(e['a'])
        self.pin_b_input.setText(e['b'])
        self.button_pin_input.setText(e['btn'] or '')
        self.invert_checkbox.setChecked(bool(e['invert']))
        self.divisor_input.setText(str(e.get('divisor', 4)))

    def get_config(self):
        # Build a Python snippet from entries
        lines = []
        lines.append("encoder_handler = EncoderHandler()")
        pins_repr = []
        for e in self.encoders:
            btn = 'None' if e['btn'] is None else e['btn']
            pins_repr.append(f"({e['a']}, {e['b']}, {btn}, {str(bool(e['invert']))}, {e.get('divisor',4)})")
        if pins_repr:
            lines.append(f"encoder_handler.pins = ({', '.join(pins_repr)},)")
        map_text = self.map_editor.toPlainText().strip()
        if map_text:
            lines.append(f"encoder_handler.map = {map_text}")
        lines.append("keyboard.modules.append(encoder_handler)")
        return "\n".join(lines)


class AnalogInConfigDialog(QDialog):
    """Form-based editor for AnalogIn configuration.
    Lets you add Analog inputs (pin) and an optional evtmap as a Python literal.
    """
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("AnalogIn Configuration")
        self.resize(700, 500)

        self.inputs = []

        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.analog_list = QListWidget()
        top_layout.addWidget(self.analog_list, 2)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Analog Pin (e.g., board.A0):"))
        self.analog_pin_input = QLineEdit()
        form_layout.addWidget(self.analog_pin_input)
        add_btn = QPushButton("Add Analog Input")
        add_btn.clicked.connect(self.add_analog_input)
        form_layout.addWidget(add_btn)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected_analog)
        form_layout.addWidget(remove_btn)
        top_layout.addLayout(form_layout, 1)

        main_layout.addLayout(top_layout)

        main_layout.addWidget(QLabel("Optional evtmap (Python list literal). Example: [[AnalogKey(KC.X)], [KC.TRNS]]"))
        self.evtmap_editor = QTextEdit()
        if initial_text:
            self.evtmap_editor.setPlainText(initial_text)
        main_layout.addWidget(self.evtmap_editor)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.analog_list.itemClicked.connect(self.on_analog_item_clicked)

    def add_analog_input(self):
        pin = self.analog_pin_input.text().strip()
        if not pin:
            QMessageBox.warning(self, "Invalid", "Analog pin is required")
            return
        self.inputs.append(pin)
        self.analog_list.addItem(pin)

    def remove_selected_analog(self):
        sel = self.analog_list.selectedItems()
        if not sel:
            return
        idx = self.analog_list.row(sel[0])
        self.analog_list.takeItem(idx)
        del self.inputs[idx]

    def on_analog_item_clicked(self, item):
        self.analog_pin_input.setText(item.text())

    def get_config(self):
        lines = []
        if self.inputs:
            lines.append("# Analog inputs")
            for i, pin in enumerate(self.inputs):
                lines.append(f"a{i} = AnalogInput(AnalogIn({pin}))")
            var_list = ", ".join([f"a{i}" for i in range(len(self.inputs))])
            lines.append(f"analog = AnalogInputs([{var_list}], {self.evtmap_editor.toPlainText().strip() or '[]'})")
            lines.append("keyboard.modules.append(analog)")
        else:
            # If only an evtmap is provided, include it as a hint
            evtmap_text = self.evtmap_editor.toPlainText().strip()
            if evtmap_text:
                lines.append(f"# evtmap provided:\n# analog = AnalogInputs([a0], {evtmap_text})")
        return "\n".join(lines)


class PegRgbConfigDialog(QDialog):
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Peg RGB Matrix Configuration")
        self.resize(600, 380)
        layout = QVBoxLayout(self)

        # Default num keys based on parent rows/cols if available
        default_keys = None
        try:
            if parent and hasattr(parent, 'rows') and hasattr(parent, 'cols'):
                default_keys = parent.rows * parent.cols
        except Exception:
            default_keys = None

        # Number of keys
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Number of per-key LEDs (keys):"))
        self.num_keys_spin = QSpinBox()
        self.num_keys_spin.setMinimum(1)
        self.num_keys_spin.setMaximum(1000)
        if default_keys:
            self.num_keys_spin.setValue(default_keys)
        else:
            self.num_keys_spin.setValue(12)
        hl.addWidget(self.num_keys_spin)
        layout.addLayout(hl)

        # Underglow count
        hl2 = QHBoxLayout()
        hl2.addWidget(QLabel("Number of underglow LEDs:"))
        self.underglow_spin = QSpinBox()
        self.underglow_spin.setMinimum(0)
        self.underglow_spin.setMaximum(1000)
        self.underglow_spin.setValue(0)
        hl2.addWidget(self.underglow_spin)
        layout.addLayout(hl2)

        # Key color and underglow color fields (accept Color.* or [r,g,b])
        layout.addWidget(QLabel("Key color (Color.* or [r,g,b]):"))
        self.key_color_input = QLineEdit()
        self.key_color_input.setText("Color.WHITE")
        layout.addWidget(self.key_color_input)

        layout.addWidget(QLabel("Underglow color (Color.* or [r,g,b]):"))
        self.ug_color_input = QLineEdit()
        self.ug_color_input.setText("Color.OFF")
        layout.addWidget(self.ug_color_input)

        layout.addWidget(QLabel("Optional extra snippet (appended):"))
        self.extra_editor = QTextEdit()
        if initial_text:
            # If previous content exists, try to pre-fill extra editor
            self.extra_editor.setPlainText(initial_text)
        layout.addWidget(self.extra_editor)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_config(self):
        num_keys = self.num_keys_spin.value()
        ug = self.underglow_spin.value()
        key_col = self.key_color_input.text().strip() or 'Color.WHITE'
        ug_col = self.ug_color_input.text().strip() or 'Color.OFF'

        lines = []
        lines.append(f"# Peg RGB Matrix configuration (auto-generated)")
        lines.append(f"rgb = Rgb_matrix(ledDisplay=Rgb_matrix_data(keys=[{key_col}]*{num_keys}, underglow=[{ug_col}]*{ug}))")
        lines.append("keyboard.extensions.append(rgb)")
        extra = self.extra_editor.toPlainText().strip()
        if extra:
            lines.append('\n# Extra user snippet:')
            lines.append(extra)
        return "\n".join(lines)


class PerKeyColorDialog(QDialog):
    """Dialog to pick per-key colors for each layer. Returns a mapping {layer: {index: '#RRGGBB'}}."""
    def __init__(self, parent=None, rows=3, cols=4, layers=1, initial_map=None):
        super().__init__(parent)
        self.setWindowTitle("Per-key RGB Colors")
        self.rows = rows
        self.cols = cols
        self.layers = layers
        self.map = initial_map or {}  # {layer: {index: hexcolor}}

        self.resize(600, 480)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Layer:"))
        self.layer_spin = QSpinBox()
        self.layer_spin.setMinimum(0)
        self.layer_spin.setMaximum(max(0, layers-1))
        top.addWidget(self.layer_spin)
        self.layer_spin.valueChanged.connect(self.refresh_grid)
        layout.addLayout(top)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        layout.addWidget(self.grid_widget)

        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Layer Colors")
        clear_btn.clicked.connect(self.clear_layer)
        btn_layout.addWidget(clear_btn)
        fill_btn = QPushButton("Fill Layer with Color")
        fill_btn.clicked.connect(self.fill_layer_color)
        btn_layout.addWidget(fill_btn)
        layout.addLayout(btn_layout)

        self.fill_color_btn = QPushButton("Pick Fill Color")
        self.fill_color_btn.clicked.connect(self.pick_fill_color)
        btn_layout.addWidget(self.fill_color_btn)

        self.fill_color = '#FF0000'

        # Key type preset colors - one for each keycode category
        preset_group = QGroupBox("Assign Colors by Keycode Category")
        preset_layout = QVBoxLayout()
        
        # Define all 8 categories with default colors
        self.category_colors = {
            'macro': '#FF6B6B',      # Red for macros
            'basic': '#4ECDC4',      # Teal for basic keys (letters, numbers, etc)
            'modifiers': '#A8E6CF',  # Mint for modifiers
            'navigation': '#FFD93D', # Yellow for navigation
            'function': '#95E1D3',   # Light cyan for function keys
            'media': '#F38181',      # Coral for media controls
            'mouse': '#AA96DA',      # Purple for mouse keys
            'layers': '#FCBAD3',     # Pink for layer switches
            'misc': '#B4B4B4'        # Gray for misc keys
        }
        
        category_labels = {
            'macro': 'Macros',
            'basic': 'Basic (Letters/Numbers)',
            'modifiers': 'Modifiers',
            'navigation': 'Navigation',
            'function': 'Function Keys',
            'media': 'Media Controls',
            'mouse': 'Mouse Keys',
            'layers': 'Layer Switches',
            'misc': 'Misc Keys'
        }
        
        # Create UI for each category
        for cat_key, cat_label in category_labels.items():
            cat_layout = QHBoxLayout()
            cat_layout.addWidget(QLabel(f"{cat_label}:"))
            
            # Color button
            color_btn = QPushButton()
            color_btn.setFixedSize(30, 30)
            color_btn.setStyleSheet(f'background-color: {self.category_colors[cat_key]};')
            color_btn.clicked.connect(lambda checked, k=cat_key: self.pick_category_color(k))
            setattr(self, f'{cat_key}_color_btn', color_btn)
            cat_layout.addWidget(color_btn)
            
            # Apply button
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(lambda checked, k=cat_key: self.apply_category_color(k))
            cat_layout.addWidget(apply_btn)
            
            cat_layout.addStretch()
            preset_layout.addLayout(cat_layout)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Store parent reference to access keymap
        self.parent_ref = parent

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

        self._make_buttons()
        self.refresh_grid()

    def _make_buttons(self):
        # create buttons for a grid of rows x cols
        self.key_buttons = []
        for r in range(self.rows):
            for c in range(self.cols):
                btn = QPushButton(f"{r},{c}")
                # Make buttons larger for easier color picking
                btn.setFixedSize(64, 56)
                # Slightly larger label for readability
                btn.setStyleSheet("font-size: 12px; padding: 4px;")
                btn.clicked.connect(self.on_key_clicked)
                self.key_buttons.append(btn)
                self.grid_layout.addWidget(btn, r, c)
                try:
                    self._install_hover_effect(btn)
                except Exception:
                    pass

    def _install_hover_effect(self, button: QPushButton):
        """Adds a subtle scale animation on hover for the given button."""
        # Avoid double-installing
        if hasattr(button, '_hover_filter'):
            return
        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(140)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        # store on the object to prevent GC
        button._hover_anim = anim
        # shadow effect for subtle depth
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor('#00000033'))
        button.setGraphicsEffect(shadow)
        # Note: actual geometry changes are handled by the animation when hovered
        # We will connect enter/leave events via eventFilter on the button
        class _Filter(QObject):
            def __init__(self, btn, anim):
                super().__init__(btn)
                self.btn = btn
                self.anim = anim
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
        flt = _Filter(button, anim)
        button.installEventFilter(flt)
        button._hover_filter = flt

    def install_global_hover_effects(self):
        """Install hover effects on all QPushButton instances in the main window.

        This uses findChildren to locate buttons and applies the same subtle
        animation/shadow used in the per-key controls. It's safe to call multiple
        times because _install_hover_effect is idempotent.
        """
        try:
            for btn in self.findChildren(QPushButton):
                try:
                    self._install_hover_effect(btn)
                except Exception:
                    # Don't break if one button can't be instrumented
                    pass
        except Exception:
            pass

    def refresh_grid(self):
        layer = str(self.layer_spin.value())  # Convert to string for consistency
        lm = self.map.get(layer, {})
        for idx, btn in enumerate(self.key_buttons):
            color = lm.get(str(idx), None)
            if color:
                btn.setStyleSheet(f'background-color: {color}; font-size: 12px; padding: 4px;')
                btn.setToolTip(f"Index: {idx}\nLayer: {self.layer_spin.value()}\nColor: {color}")
            else:
                # Clear background and reset to default button styling
                btn.setStyleSheet('font-size: 12px; padding: 4px;')
                btn.setToolTip(f"Index: {idx}\nLayer: {self.layer_spin.value()}\nColor: (none)")

    def on_key_clicked(self):
        btn = self.sender()
        idx = self.key_buttons.index(btn)
        color = QColorDialog.getColor(QColor(self.fill_color), self, "Select Color")
        if color.isValid():
            hexc = color.name()
            layer = str(self.layer_spin.value())
            lm = self.map.setdefault(layer, {})
            lm[str(idx)] = hexc
            btn.setStyleSheet(f'background-color: {hexc};')
            btn.setToolTip(f"Index: {idx}\nLayer: {layer}\nColor: {hexc}")

    def clear_layer(self):
        layer = str(self.layer_spin.value())
        if layer in self.map:
            del self.map[layer]
        self.refresh_grid()

    def pick_fill_color(self):
        color = QColorDialog.getColor(QColor(self.fill_color), self, "Pick fill color")
        if color.isValid():
            self.fill_color = color.name()

    def fill_layer_color(self):
        layer = str(self.layer_spin.value())
        lm = self.map.setdefault(layer, {})
        for idx in range(self.rows * self.cols):
            lm[str(idx)] = self.fill_color
        self.refresh_grid()

    def pick_category_color(self, category):
        """Pick a color for a keycode category."""
        current = self.category_colors.get(category, '#FFFFFF')
        color = QColorDialog.getColor(QColor(current), self, f"Pick {category} color")
        if color.isValid():
            hexc = color.name()
            self.category_colors[category] = hexc
            btn = getattr(self, f'{category}_color_btn', None)
            if btn:
                btn.setStyleSheet(f'background-color: {hexc};')

    def apply_category_color(self, category):
        """Apply a color to all keys of a specific category on the current layer."""
        if not hasattr(self, 'parent_ref') or not self.parent_ref:
            QMessageBox.warning(self, "Error", "Cannot access keymap data")
            return
        
        layer_idx = self.layer_spin.value()
        parent = self.parent_ref
        
        # Check if parent has keymap_data
        if not hasattr(parent, 'keymap_data') or layer_idx >= len(parent.keymap_data):
            QMessageBox.warning(self, "Error", "Invalid layer index")
            return
        
        layer_data = parent.keymap_data[layer_idx]
        color = self.category_colors.get(category, '#FFFFFF')
        layer_str = str(layer_idx)
        lm = self.map.setdefault(layer_str, {})
        
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if r < len(layer_data) and c < len(layer_data[r]):
                    key = layer_data[r][c]
                    should_color = False
                    
                    if category == 'macro' and key.startswith('MACRO('):
                        should_color = True
                    elif category == 'basic':
                        # Check against all Basic keycodes
                        if key in KEYCODES.get('Basic', []):
                            should_color = True
                    elif category == 'modifiers':
                        if key in KEYCODES.get('Modifiers', []):
                            should_color = True
                    elif category == 'navigation':
                        if key in KEYCODES.get('Navigation', []):
                            should_color = True
                    elif category == 'function':
                        if key in KEYCODES.get('Function', []):
                            should_color = True
                    elif category == 'media':
                        if key in KEYCODES.get('Media', []):
                            should_color = True
                    elif category == 'mouse':
                        if key in KEYCODES.get('Mouse', []):
                            should_color = True
                    elif category == 'layers':
                        # Check for layer switching keys (MO, TG, DF)
                        if key in KEYCODES.get('Layers', []) or key.startswith('KC.MO(') or key.startswith('KC.TG(') or key.startswith('KC.DF('):
                            should_color = True
                    elif category == 'misc':
                        if key in KEYCODES.get('Misc', []):
                            should_color = True
                    
                    if should_color:
                        lm[str(idx)] = color
                idx += 1
        
        self.refresh_grid()

    def get_map(self):
        return self.map


# --- Main Application Window ---
class KMKConfigurator(QMainWindow):
    """The main application window for configuring KMK-based macropads."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KMK Macropad Configurator")
        self.setGeometry(100, 100, 1400, 900)

        # default theme (can be changed by the user)
        self.current_theme = 'Dark'
        # Load persisted UI settings (theme) if available
        self.load_ui_settings()
        self._set_stylesheet()

        # --- Application State ---
        self.selected_key_coords = None
        self.macropad_buttons = {}
        self.current_layer = 0
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS
        self.macros = {}
        self.profiles = {}
        # Extension toggles and configs (simple free-form config text entered by user)
        self.enable_encoder = False
        self.encoder_config_str = ""  # user-provided python snippet for encoder setup
        self.enable_analogin = False
        self.analogin_config_str = ""
        self.enable_rgb = False
        self.rgb_config_str = ""
        self.col_pins = [f"board.GP{i}" for i in range(self.cols)]
        self.row_pins = [f"board.GP{i+self.cols}" for i in range(self.rows)]

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
        # Install hover/animation effects across all buttons in the UI
        try:
            self.install_global_hover_effects()
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
                "enable_encoder": bool(self.enable_encoder),
                "enable_analogin": bool(self.enable_analogin),
                "enable_rgb": bool(self.enable_rgb),
            }
            with open(os.path.join(CONFIG_SAVE_DIR, 'extensions.json'), 'w') as f:
                json.dump(meta, f, indent=2)

            # Save snippets to separate files for easier editing
            with open(os.path.join(CONFIG_SAVE_DIR, 'encoder.py'), 'w') as f:
                f.write(self.encoder_config_str or '')
            with open(os.path.join(CONFIG_SAVE_DIR, 'analogin.py'), 'w') as f:
                f.write(self.analogin_config_str or '')
            with open(os.path.join(CONFIG_SAVE_DIR, 'peg_rgb.py'), 'w') as f:
                f.write(self.rgb_config_str or '')
            # Save per-key color map if present
            try:
                if hasattr(self, 'peg_rgb_colors') and self.peg_rgb_colors:
                    with open(os.path.join(CONFIG_SAVE_DIR, 'peg_rgb_colors.json'), 'w') as f:
                        json.dump(self.peg_rgb_colors, f, indent=2)
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save extension configs:\n{e}")

    def load_extension_configs(self):
        try:
            if os.path.exists(os.path.join(CONFIG_SAVE_DIR, 'extensions.json')):
                with open(os.path.join(CONFIG_SAVE_DIR, 'extensions.json'), 'r') as f:
                    meta = json.load(f)
                self.enable_encoder = bool(meta.get('enable_encoder', False))
                self.enable_analogin = bool(meta.get('enable_analogin', False))
                self.enable_rgb = bool(meta.get('enable_rgb', False))
            # Load snippet files if present
            enc_path = os.path.join(CONFIG_SAVE_DIR, 'encoder.py')
            if os.path.exists(enc_path):
                with open(enc_path, 'r') as f:
                    self.encoder_config_str = f.read()
            an_path = os.path.join(CONFIG_SAVE_DIR, 'analogin.py')
            if os.path.exists(an_path):
                with open(an_path, 'r') as f:
                    self.analogin_config_str = f.read()
            rgb_path = os.path.join(CONFIG_SAVE_DIR, 'peg_rgb.py')
            if os.path.exists(rgb_path):
                with open(rgb_path, 'r') as f:
                    self.rgb_config_str = f.read()
            # load per-key color mapping
            colors_path = os.path.join(CONFIG_SAVE_DIR, 'peg_rgb_colors.json')
            if os.path.exists(colors_path):
                try:
                    with open(colors_path, 'r') as f:
                        self.peg_rgb_colors = json.load(f)
                except Exception:
                    self.peg_rgb_colors = {}
            else:
                self.peg_rgb_colors = {}
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

        # Encoder
        enc_layout = QHBoxLayout()
        self.encoder_checkbox = QCheckBox("Enable Encoder")
        self.encoder_checkbox.stateChanged.connect(self.on_encoder_toggled)
        self.encoder_checkbox.setChecked(bool(self.enable_encoder))
        enc_layout.addWidget(self.encoder_checkbox)
        enc_cfg_btn = QPushButton("Configure")
        enc_cfg_btn.clicked.connect(self.configure_encoder)
        enc_layout.addWidget(enc_cfg_btn)
        layout.addLayout(enc_layout)

        # AnalogIn
        an_layout = QHBoxLayout()
        self.analog_checkbox = QCheckBox("Enable AnalogIn")
        self.analog_checkbox.stateChanged.connect(self.on_analog_toggled)
        self.analog_checkbox.setChecked(bool(self.enable_analogin))
        an_layout.addWidget(self.analog_checkbox)
        an_cfg_btn = QPushButton("Configure")
        an_cfg_btn.clicked.connect(self.configure_analogin)
        an_layout.addWidget(an_cfg_btn)
        layout.addLayout(an_layout)

        # Peg RGB Matrix
        rgb_layout = QHBoxLayout()
        self.rgb_checkbox = QCheckBox("Enable Peg RGB Matrix")
        self.rgb_checkbox.stateChanged.connect(self.on_rgb_toggled)
        self.rgb_checkbox.setChecked(bool(self.enable_rgb))
        rgb_layout.addWidget(self.rgb_checkbox)
        rgb_cfg_btn = QPushButton("Configure")
        rgb_cfg_btn.clicked.connect(self.configure_rgb)
        rgb_layout.addWidget(rgb_cfg_btn)
        # Quick access button for per-key color mapping
        rgb_colors_btn = QPushButton("Per-key Colors")
        def open_per_key_colors():
            rows = getattr(self, 'rows', DEFAULT_ROWS)
            cols = getattr(self, 'cols', DEFAULT_COLS)
            layers = max(1, len(self.keymap_data) if hasattr(self, 'keymap_data') else 1)
            initial = getattr(self, 'peg_rgb_colors', {})
            pc = PerKeyColorDialog(self, rows=rows, cols=cols, layers=layers, initial_map=initial)
            if pc.exec():
                self.peg_rgb_colors = pc.get_map()
                self.save_extension_configs()
        rgb_colors_btn.clicked.connect(open_per_key_colors)
        rgb_layout.addWidget(rgb_colors_btn)
        layout.addLayout(rgb_layout)

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

    # --- Extension toggles and configuration handlers ---
    def on_encoder_toggled(self, state):
        self.enable_encoder = bool(state == Qt.CheckState.Checked)

    def on_analog_toggled(self, state):
        self.enable_analogin = bool(state == Qt.CheckState.Checked)

    def on_rgb_toggled(self, state):
        self.enable_rgb = bool(state == Qt.CheckState.Checked)

    def configure_encoder(self):
        dlg = EncoderConfigDialog(self, self.encoder_config_str)
        # Try to prepopulate dialog from previous snippet (best-effort)
        try:
            txt = self.encoder_config_str.strip()
            if txt.startswith('encoder_handler.pins') or txt.startswith('encoder_handler ='):
                # put full snippet into map editor so user can edit
                dlg.map_editor.setPlainText(txt)
        except Exception:
            pass
        if dlg.exec():
            self.encoder_config_str = dlg.get_config()
            self.encoder_checkbox.setChecked(True)
            self.save_extension_configs()

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
            self.analog_checkbox.setChecked(True)
            self.save_extension_configs()

    def configure_rgb(self):
        dlg = PegRgbConfigDialog(self, self.rgb_config_str)
        # Provide access to per-key colors via dialog button
        dlg_colors_btn = QPushButton("Configure per-key colors")
        def open_colors():
            rows = getattr(self, 'rows', DEFAULT_ROWS)
            cols = getattr(self, 'cols', DEFAULT_COLS)
            layers = max(1, len(self.keymap_data) if hasattr(self, 'keymap_data') else 1)
            initial = getattr(self, 'peg_rgb_colors', {})
            pc = PerKeyColorDialog(self, rows=rows, cols=cols, layers=layers, initial_map=initial)
            if pc.exec():
                self.peg_rgb_colors = pc.get_map()
                self.save_extension_configs()

        # place the button into the PegRgbConfigDialog layout (top)
        try:
            dlg.layout().insertWidget(0, dlg_colors_btn)
            dlg_colors_btn.clicked.connect(open_colors)
        except Exception:
            # fallback: attach to main window post-show
            dlg_colors_btn.clicked.connect(open_colors)
        if dlg.exec():
            self.rgb_config_str = dlg.get_config()
            self.rgb_checkbox.setChecked(True)
            self.save_extension_configs()

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
        group = QGroupBox("Hardware")
        layout = QVBoxLayout()
        
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

        # Grid dimensions, diode orientation, and pins
        current_hw_layout = QGridLayout()
        current_hw_layout.addWidget(QLabel("Rows:"), 0, 0)
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setMinimum(1)
        self.rows_spinbox.setValue(self.rows)
        current_hw_layout.addWidget(self.rows_spinbox, 0, 1)

        current_hw_layout.addWidget(QLabel("Cols:"), 1, 0)
        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setMinimum(1)
        self.cols_spinbox.setValue(self.cols)
        current_hw_layout.addWidget(self.cols_spinbox, 1, 1)

        current_hw_layout.addWidget(QLabel("Diode:"), 2, 0)
        self.diode_orientation_combo = QComboBox()
        self.diode_orientation_combo.addItems(["COL2ROW", "ROW2COL"])
        current_hw_layout.addWidget(self.diode_orientation_combo, 2, 1)
        layout.addLayout(current_hw_layout)

        update_grid_button = QPushButton("Update Grid")
        update_grid_button.clicked.connect(self.update_grid_dimensions)
        layout.addWidget(update_grid_button)

        edit_pins_btn = QPushButton("Edit Pins...")
        edit_pins_btn.clicked.connect(self.edit_pins)
        layout.addWidget(edit_pins_btn)

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
            self.profiles[name] = {
                "rows": self.rows,
                "cols": self.cols,
                "col_pins": self.col_pins,
                "row_pins": self.row_pins,
                "diode_orientation": self.diode_orientation_combo.currentText()
            }
            self.load_profiles()
            self.profile_combo.setCurrentText(name)

    def load_selected_profile(self):
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            profile = self.profiles.get(profile_name)
            if profile:
                self.rows = profile["rows"]
                self.cols = profile["cols"]
                self.col_pins = profile["col_pins"]
                self.row_pins = profile["row_pins"]
                
                self.rows_spinbox.setValue(self.rows)
                self.cols_spinbox.setValue(self.cols)
                
                diode_index = self.diode_orientation_combo.findText(profile["diode_orientation"])
                if diode_index != -1:
                    self.diode_orientation_combo.setCurrentIndex(diode_index)

                self.update_grid_dimensions(force_update=True)

    def delete_selected_profile(self):
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != "Custom":
            reply = QMessageBox.question(self, "Delete Profile", f"Are you sure you want to delete the '{profile_name}' profile?")
            if reply == QMessageBox.StandardButton.Yes:
                if profile_name in self.profiles:
                    del self.profiles[profile_name]
                    self.load_profiles()

    def edit_pins(self):
        """Opens a dialog to edit the row and column pin assignments."""
        dialog = PinEditorDialog(self.rows, self.cols, self.row_pins, self.col_pins, self)
        if dialog.exec():
            self.col_pins, self.row_pins = dialog.get_pins()
            self.profile_combo.setCurrentText("Custom")
            
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
            for row in layer:
                row_str = []
                for key in row:
                    macro_match = re.match(r"MACRO\((\w+)\)", key)
                    if macro_match:
                        row_str.append(macro_match.group(1)) # Use the macro variable name
                    else:
                        row_str.append(key) # This is a regular keycode or combo
                keymap_str += "        " + ", ".join(row_str) + ",\n"
            keymap_str += "    ],\n"
        keymap_str += "]\n"

        # --- Python File Template ---
        diode_orientation = self.diode_orientation_combo.currentText()
        
        imports = [
            "import board",
            "from kmk.kmk_keyboard import KMKKeyboard",
            "from kmk.keys import KC",
            "from kmk.scanners import DiodeOrientation",
            "from kmk.modules.layers import Layers",
        ]
        if macros_exist:
            imports.append("from kmk.modules.macros import Macros, Tap, Press, Release, Delay")
        # Optional extension imports
        if self.enable_encoder:
            imports.append("from kmk.modules.encoder import EncoderHandler")
        if self.enable_analogin:
            imports.append("from kmk.modules.analogin import AnalogInputs, AnalogInput")
        if self.enable_rgb:
            imports.append("from kmk.extensions.peg_rgb_matrix import Rgb_matrix, Rgb_matrix_data, Color")

        # Build extension snippets provided by the user
        ext_snippets = ""
        if self.enable_encoder and self.encoder_config_str:
            ext_snippets += "# Encoder configuration provided by user:\n"
            ext_snippets += self.encoder_config_str + "\n\n"
        if self.enable_analogin and self.analogin_config_str:
            ext_snippets += "# AnalogIn configuration provided by user:\n"
            ext_snippets += self.analogin_config_str + "\n\n"
        if self.enable_rgb and self.rgb_config_str:
            ext_snippets += "# Peg RGB Matrix configuration provided by user:\n"
            ext_snippets += self.rgb_config_str + "\n\n"
        # Provide sensible default templates for enabled modules (placed before user snippets)
        default_snippets = ""
        if self.enable_encoder:
            default_snippets += "# --- Encoder Handler (auto-generated) ---\n"
            default_snippets += (
                "encoder_handler = EncoderHandler()\n"
                "# Configure pins and map for your hardware. Examples:\n"
                "# encoder_handler.pins = ((board.GP17, board.GP15, board.GP14),)\n"
                "# encoder_handler.map = [ ((KC.VOLD, KC.VOLU, KC.MUTE),), ]\n"
                "keyboard.modules.append(encoder_handler)\n\n"
            )
        if self.enable_analogin:
            default_snippets += "# --- Analog Inputs (auto-generated) ---\n"
            default_snippets += (
                "# Example usage (requires 'analogio' on target device):\n"
                "# from analogio import AnalogIn\n"
                "# a0 = AnalogInput(AnalogIn(board.A0))\n"
                "# analog = AnalogInputs([a0], [[AnalogKey(KC.X)]])\n"
                "# keyboard.modules.append(analog)\n\n"
            )
        if self.enable_rgb:
            default_snippets += "# --- Peg RGB Matrix (auto-generated) ---\n"
            num_keys = self.rows * self.cols
            default_snippets += (
                "# Detected key count (rows * cols) = %d\n" % num_keys
                + "# Example usage (adjust colors and underglow as needed):\n"
                + ("rgb = Rgb_matrix(ledDisplay=Rgb_matrix_data(keys=[Color.WHITE]*%d, underglow=[]))\n" % num_keys)
                + "# keyboard.extensions.append(rgb)\n\n"
            )
            # If per-key layer colors exist, emit them as RGB_LAYER_COLORS
            if getattr(self, 'peg_rgb_colors', None):
                try:
                    # peg_rgb_colors is {layer: {index: '#RRGGBB'}}
                    rgb_map = self.peg_rgb_colors
                    # Build python literal for mapping
                    def hex_to_color_tuple(hexs):
                        h = hexs.lstrip('#')
                        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

                    rgb_lines = ["# Per-layer per-key color mapping (auto-generated)", "def _hex_to_color(h):", "    h=h.lstrip('#')", "    return Color(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))", ""]
                    rgb_lines.append("RGB_LAYER_COLORS = {")
                    for layer, lm in rgb_map.items():
                        entries = []
                        for idx, hexc in lm.items():
                            entries.append(f"{idx}: _hex_to_color('{hexc}')")
                        rgb_lines.append(f"    {layer}: {{{', '.join(entries)}}},")
                    rgb_lines.append("}\n")
                    default_snippets += "\n".join(rgb_lines) + "\n"
                except Exception:
                    # if anything goes wrong, skip emitting layer colors
                    pass

        # Final extension snippets: defaults first, then user-provided overrides/additions
        ext_snippets_final = default_snippets + ext_snippets
        code_template = f"""# Generated by KMK Configurator
{chr(10).join(imports)}

keyboard = KMKKeyboard()

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
if __name__ == '__main__':
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
                with open(file_path, 'w') as f:
                    f.write(py_code_str)
                QMessageBox.information(self, "Success", f"code.py saved successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save code.py file:\n{e}")

    def save_configuration_dialog(self):
        save_dir = "kmk_Config_Save"
        os.makedirs(save_dir, exist_ok=True)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration As",
            save_dir,
            "JSON Files (*.json)"
        )

        if file_path:
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            try:
                self.save_configuration_to_path(file_path)
                QMessageBox.information(self, "Success", f"Configuration saved to:\n{file_path}")
            except Exception:
                # The helper function already shows a critical error message
                pass

    def save_configuration_to_path(self, file_path):
        config_data = {
            "rows": self.rows,
            "cols": self.cols,
            "col_pins": self.col_pins,
            "row_pins": self.row_pins,
            "diode_orientation": self.diode_orientation_combo.currentText(),
            "keymap_data": self.keymap_data,
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save configuration file:\n{e}")
            raise e

    def load_configuration(self):
        # If a file is selected in the config combo, use that; otherwise open a file dialog
        file_path = None
        if hasattr(self, 'config_file_combo') and self.config_file_combo.count() > 0:
            sel = self.config_file_combo.currentText()
            if sel:
                candidate = os.path.join(os.getcwd(), sel)
                if os.path.exists(candidate):
                    file_path = candidate

        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
            if not file_path:
                return

        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)

            # --- Update state from loaded data ---
            self.rows = config_data.get("rows", DEFAULT_ROWS)
            self.cols = config_data.get("cols", DEFAULT_COLS)
            self.col_pins = config_data.get("col_pins", [f"board.GP{i}" for i in range(self.cols)])
            self.row_pins = config_data.get("row_pins", [f"board.GP{i+self.cols}" for i in range(self.rows)])
            diode_orientation = config_data.get("diode_orientation", "COL2ROW")
            self.keymap_data = config_data.get("keymap_data", [])
            # Do not override the global macros when loading a configuration file
            # Macros are stored independently in macros.json and loaded on startup.

            # --- Refresh UI ---
            self.rows_spinbox.setValue(self.rows)
            self.cols_spinbox.setValue(self.cols)

            diode_index = self.diode_orientation_combo.findText(diode_orientation)
            if diode_index != -1:
                self.diode_orientation_combo.setCurrentIndex(diode_index)
            
            if not self.keymap_data:
                 self.initialize_keymap_data()
            
            self.current_layer = 0
            self.profile_combo.setCurrentText("Custom")

            self.recreate_macropad_grid()
            self.update_layer_tabs()
            self.update_macro_list()
            self.update_macropad_display()
            
            QMessageBox.information(self, "Success", "Configuration loaded successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load configuration:\n{e}")
    
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
        for r in range(self.rows):
            for c in range(self.cols):
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
                self.macropad_layout.addWidget(button, r, c)
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
        """
        Resizes the internal keymap data and recreates the UI grid
        when the user changes the number of rows or columns.
        """
        new_rows = self.rows_spinbox.value()
        new_cols = self.cols_spinbox.value()
        if force_update or new_rows != self.rows or new_cols != self.cols:
            old_rows, old_cols = self.rows, self.cols
            self.rows, self.cols = new_rows, new_cols
            
            # Resize pin arrays
            self.col_pins = (self.col_pins + [''] * self.cols)[:self.cols]
            self.row_pins = (self.row_pins + [''] * self.rows)[:self.rows]

            # Resize all existing layers, preserving existing key assignments
            new_keymap_data = []
            for layer in self.keymap_data:
                new_layer = self._create_new_layer()
                for r in range(min(self.rows, old_rows)):
                    for c in range(min(self.cols, old_cols)):
                        new_layer[r][c] = layer[r][c]
                new_keymap_data.append(new_layer)
            self.keymap_data = new_keymap_data

            self.recreate_macropad_grid()
            self.current_layer = min(self.current_layer, len(self.keymap_data) - 1)
            self.update_layer_tabs()
            self.update_macropad_display()
            self.profile_combo.setCurrentText("Custom")

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
        # Get RGB color map if available
        rgb_colors = getattr(self, 'peg_rgb_colors', {})
        layer_colors = rgb_colors.get(str(self.current_layer), {})
        
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
                    if str(idx) in layer_colors:
                        color = layer_colors[str(idx)]
                        button.setStyleSheet(f'background-color: {color}; color: #ffffff;')
                    else:
                        # Clear any previous color styling but keep checked state styling
                        button.setStyleSheet('')
                idx += 1
        self.macropad_group.setTitle(f"Keymap (Layer {self.current_layer})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KMKConfigurator()
    window.show()
    sys.exit(app.exec())


