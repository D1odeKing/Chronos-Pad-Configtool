# Architecture Guide

> **AI-Generated Documentation**: This architecture guide was written by GitHub Copilot AI based on requirements and feedback from David (D1odeKing).

---

## 🏗️ Overview

The Chronos Pad Configuration Tool is a PyQt6-based GUI application that generates KMK firmware configurations for custom macropads. The architecture follows a modular design with clear separation between UI, state management, and code generation.

## 🎯 Core Architecture

### Main Application Structure

```
main.py (8000+ lines)
├── KMKConfigurator (Main Window Class)
│   ├── UI Components
│   │   ├── Left Panel (File Management & Extensions)
│   │   ├── Center Panel (Keymap Grid & Layers)
│   │   └── Right Panel (Keycode Selector & Tools)
│   ├── State Management
│   │   ├── Keymap Data (layers)
│   │   ├── Macro Definitions
│   │   ├── RGB Configuration
│   │   └── Extension States
│   └── Code Generation
│       ├── Main code.py Generator
│       ├── Extension Code Generators
│       └── Helper File Writers
└── Utility Classes
    ├── CollapsibleCard
    ├── ToggleSwitch
    └── ToastNotification
```

### Hardware Model

**CRITICAL**: All configurations assume the fixed Chronos Pad hardware wiring:

```python
# Fixed Hardware Pins (DO NOT MODIFY without hardware changes)
FIXED_ROW_PINS = [GP0, GP1, GP2, GP3, GP4]    # 5 rows
FIXED_COL_PINS = [GP5, GP6, GP7, GP8]          # 4 columns
ENCODER_PINS = [GP10, GP11, GP14]               # Encoder A, B, Button
RGB_PIN = GP9                                    # SK6812MINI LEDs
OLED_I2C_PINS = [GP20, GP21]                    # SDA, SCL
ANALOG_PIN = GP28                                # Potentiometer slider
```

These pins are declared at the top of `main.py` and used throughout the application. Changes require hardware modifications to the Chronos Pad PCB.

## 📊 State Management

### Primary State Shape

```python
# Keymap Data: List of layers (each layer is 5×4 matrix)
self.keymap_data = [
    [
        ["KC.A", "KC.B", "KC.C", "KC.D"],      # Row 0
        ["KC.E", "KC.F", "KC.G", "KC.H"],      # Row 1
        ["KC.I", "KC.J", "KC.K", "KC.L"],      # Row 2
        ["KC.M", "KC.N", "KC.O", "KC.P"],      # Row 3
        ["KC.Q", "KC.R", "KC.S", "KC.T"]       # Row 4
    ],
    # ... additional layers
]

# Macro Data: Dictionary of macro sequences
self.macros = {
    "MACRO_NAME": [
        ("tap", "KC.A"),
        ("delay", "100"),
        ("text", "Hello")
    ]
}

# RGB Data: Per-key and per-layer color overrides
self.rgb_matrix_config = {
    "brightness": 0.5,
    "default_key_color": "#FFFFFF",
    "key_colors": {"0": "#FF0000", "1": "#00FF00"},  # Key index to color
    "layer_key_colors": {
        "0": {"0": "#FF0000"},  # Layer 0, Key 0
        "1": {"0": "#00FF00"}   # Layer 1, Key 0
    }
}
```

### State Persistence

**Storage Location**: `kmk_Config_Save/`

```
kmk_Config_Save/
├── config.json           # Full configuration snapshot
├── session.json          # UI state (layer, selection, tabs)
├── encoder.py           # Encoder extension code
├── analogin.py          # Analog input extension code
├── display.py           # Display extension code
├── rgb_matrix.json      # RGB configuration
└── profiles.json        # Saved profiles
```

**Session State** (automatically saved):
- Current layer index
- Selected key coordinates (row, col)
- Active extension tab index
- Active keycode selector tab index
- Panel splitter sizes

**Auto-save Triggers**:
- Layer changes (`on_layer_changed`)
- Key selection (`on_key_selected`)
- Tab switches (`currentChanged` signals)
- Panel resizing (`splitterMoved` signals)
- Application close (`closeEvent`)

## 🎨 UI Architecture

### Three-Panel Layout (QSplitter)

```
┌─────────────────────────────────────────────────────────────┐
│ Main Window (KMKConfigurator)                              │
├───────────┬─────────────────────────┬──────────────────────┤
│ LEFT      │ CENTER                  │ RIGHT                │
│ (250px)   │ (500px)                 │ (550px)              │
│           │                         │                      │
│ File Mgmt │ ┌─────────────────────┐ │ Keycode Selector    │
│ Profiles  │ │ Layer Tabs          │ │ ┌────────────────┐ │
│ Theme     │ ├─────────────────────┤ │ │ Search Bar     │ │
│ Actions   │ │                     │ │ ├────────────────┤ │
│           │ │  5×4 Keymap Grid    │ │ │ Category Pills │ │
│ ┌───────┐ │ │  (100×100px btns)   │ │ ├────────────────┤ │
│ │Encoder│ │ │                     │ │ │ Keycode Tabs   │ │
│ │ [⚫]  │ │ │  [A] [B] [C] [D]    │ │ │ • Letters      │ │
│ └───────┘ │ │  [E] [F] [G] [H]    │ │ │ • Numbers      │ │
│           │ │  [I] [J] [K] [L]    │ │ │ • Modifiers    │ │
│ ┌───────┐ │ │  [M] [N] [O] [P]    │ │ └────────────────┘ │
│ │RGB    │ │ │  [Q] [R] [S] [T]    │ │                    │
│ │ [⚫]  │ │ └─────────────────────┘ │ ┌────────────────┐ │
│ └───────┘ │                         │ │ Macro Manager  │ │
│           │ Grid Actions Bar:       │ │ TapDance       │ │
│ ┌───────┐ │ [Clear] [Copy] [Paste] │ └────────────────┘ │
│ │Display│ │ Selected: (R0, C0)      │                    │
│ │ [⚫]  │ │                         │                    │
│ └───────┘ │                         │                    │
└───────────┴─────────────────────────┴──────────────────────┘
```

**Panel Characteristics**:
- **Resizable**: User can drag splitter handles to adjust sizes
- **Persistent**: Sizes saved in `session.json` and restored on next launch
- **Initial Sizes**: Left=250px, Center=500px, Right=550px (user-adjustable)

### Left Panel Contents

**File Management Card** (Collapsible):
- Configuration file selector (dropdown)
- Load/Save/Save As buttons
- Recent files quick access

**Actions Card** (Collapsible):
- Generate code.py button
- Advanced settings button
- Export to CIRCUITPY button

**Quick Profiles Card** (Collapsible):
- Profile selector dropdown
- Save/Load profile buttons
- Profile management

**Theme Card** (Collapsible):
- Theme selector (Dark, Light, Cheerful)
- Apply theme button

**Extensions Card** (Tab Widget):
- **🎛 Rotary Encoder**: Toggle switch + configure button
- **📊 Analog Slider**: Toggle switch + configure button
- **🖥 OLED Display**: Toggle switch + preview button
- **💡 RGB Lighting**: Toggle switch + settings + per-key colors

**Custom Code Tab**:
- QTextEdit for custom Python snippets
- TapDance, Combos, StringSubs support

### Center Panel Contents

**Layer Tabs** (QTabWidget):
- Horizontal tabs showing layer numbers (0, 1, 2, ...)
- Add/Remove layer buttons
- Current layer highlighted

**Keymap Grid** (5×4 button grid):
- 100×100px buttons with 12px spacing
- Shows current key assignment (abbreviated)
- Click to select, right-click for context menu
- Selected key: Blue border (3px) + glow shadow

**Grid Actions Bar**:
- Clear Layer button (with confirmation)
- Copy Layer button (to clipboard)
- Paste Layer button (with confirmation)
- Selection display: "Selected: (Row X, Col Y) | KC.KEY"

**Info Bar** (bottom):
- Shows coordinates and current key value
- Updates in real-time on selection change

### Right Panel Contents

**Keycode Selector**:
- Global search bar (searches all categories)
- Category pills (horizontal scrollable):
  - 🔤 Letters | 🔢 Numbers | ✏ Editing | ⌨ Modifiers
  - 🧭 Navigation | 🔧 Function | 🔊 Media | 💡 Brightness
  - 🖱 Mouse | 📚 Layers | ⚡ Macros | 🎯 TapDance
- Tab widget with keycode lists (or grid view in future)
- Click keycode to assign to selected key

**Macro Manager** (Tabbed):
- **⚡ Macros Tab**:
  - List of available macros
  - Add/Edit/Delete buttons
  - Click macro to assign to key
- **🎯 TapDance Tab**:
  - List of TapDance keys from custom code
  - Parsed from `TD_*` variables
  - Refresh button to re-scan

## 🔧 Code Generation Pipeline

### Primary Function: `get_generated_python_code()`

This is the **single source of truth** for exported firmware. It orchestrates all code generation:

```python
def get_generated_python_code(self) -> str:
    """
    Generate complete KMK firmware code.py file.
    
    Merges:
    - Hardware pin definitions (FIXED_ROW_PINS, etc.)
    - Keymap layers (from self.keymap_data)
    - Macro definitions (from self.macros)
    - Encoder code (if enabled)
    - Analog input code (if enabled)
    - Display code (if enabled)
    - RGB matrix code (from _generate_rgb_matrix_code())
    - Custom extension code (from text editor)
    
    Returns:
        Complete Python code ready for CIRCUITPY drive
    """
```

### Code Generation Flow

```
User Action (Save Config)
        ↓
get_generated_python_code()
        ↓
    ┌───────────────────────────────────┐
    │ 1. Hardware Pin Declarations      │
    │    - Row/Col pins                 │
    │    - Encoder pins                 │
    │    - RGB pin                      │
    │    - Display I2C pins             │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2. Keymap Data                    │
    │    - Convert self.keymap_data     │
    │    - Format as Python lists       │
    │    - Include layer switching keys │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 3. Macro Definitions              │
    │    - Generate KC.MACRO() calls    │
    │    - Format actions as tuples     │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 4. Extension Code (if enabled)    │
    │    - Encoder setup + actions      │
    │    - Analog input handler         │
    │    - Display initialization       │
    │    - LayerDisplaySync module      │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 5. RGB Matrix Code                │
    │    - _generate_rgb_matrix_code()  │
    │    - Default colors               │
    │    - Per-key overrides            │
    │    - Layer-aware colors           │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 6. Custom Extension Code          │
    │    - User's Python snippets       │
    │    - TapDance definitions         │
    │    - Combo definitions            │
    └───────────────┬───────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 7. Keyboard Initialization        │
    │    - keyboard = KMKKeyboard()     │
    │    - keyboard.modules.append(...) │
    │    - keyboard.keymap = keymap     │
    │    - keyboard.go()                │
    └───────────────────────────────────┘
                    ↓
        Generated code.py file
```

### RGB Generation Rules

**Function**: `_generate_rgb_matrix_code()`

```python
# RGB Code Generation Logic:
# 1. Default colors for all keys
# 2. Per-key overrides (key_colors)
# 3. Layer-specific overrides (layer_key_colors)
# 4. Underglow colors
# 5. Output as chunked arrays for readability

# Example Output:
rgb_matrix_config = {
    "brightness": 0.5,
    "rgb_order": (1, 0, 2),  # GRB
    "default_key_color": (255, 255, 255),
    "led_key_pos": [...],  # LED positions
    "key_colors": [
        (255, 0, 0),   # Key 0: Red
        (0, 255, 0),   # Key 1: Green
        # ... 18 more keys
    ],
    "layer_colors": {
        0: [(255, 0, 0), ...],    # Layer 0 colors
        1: [(0, 255, 0), ...]     # Layer 1 colors
    }
}
```

**RGB Update Rule**: Changes to RGB config must update:
1. JSON schema (`rgb_matrix_config` dict)
2. Code formatter (`_generate_rgb_matrix_code()`)
3. UI dialogs (RGBConfigDialog, PerKeyColorDialog)

### Display Code with Layer Support

**Functions**:
- `generate_display_layout_code_with_layer_support()`: Generates display initialization
- `LayerDisplaySync` module: Handles layer-aware display updates

**Display Updates**:
- Layer changes trigger display refresh
- Shows abbreviated key names (3-4 chars)
- Updates happen automatically via KMK's `after_hid_send` hook

## 🔄 Dependency Management

### DependencyDownloader

**Purpose**: Downloads and manages external dependencies

```python
# What it downloads:
1. KMK Firmware (latest from GitHub)
2. Adafruit CircuitPython Bundle (9.x-mpy)
3. Required libraries:
   - adafruit_displayio_sh1106
   - adafruit_display_text
   - neopixel
```

**Storage**: `libraries/` directory

**Skip Checks**: Use environment variables for headless operation:
```bash
set KMK_SKIP_DEP_CHECK=1
set KMK_SKIP_STARTUP_DIALOG=1
python main.py
```

### File Export Workflow

**Function**: `generate_code_py_dialog()`

**Export Process**:
1. Generate `code.py` from `get_generated_python_code()`
2. Copy `kmk/` directory to CIRCUITPY
3. Copy required libraries:
   - `adafruit_displayio_sh1106.mpy`
   - `adafruit_display_text/`
   - `neopixel.mpy`
4. Show success message with toast notification

**IMPORTANT**: Keep library list current when adding new dependencies.

## 🎨 UI Theming System

### Theme Functions

```python
_apply_dark_stylesheet()      # Material Design dark theme
_apply_light_stylesheet()     # Clean light theme
_apply_cheerful_stylesheet()  # Colorful theme with gradients
```

### Shared Geometry

**Function**: `_base_geometry_qss()`

Returns common sizing/spacing rules used by all themes:
- Button padding: 8px/14px
- Input padding: 6px/10px
- Border radius: 8px (buttons), 6px (inputs), 4px (list items)
- Spacing system: 4px, 8px, 12px, 16px, 24px

### Theme-Aware Elements

**Named Elements** (using `setObjectName()`):
- `#cardTitle`: Bold card headers
- `#cardBadge`: Colored notification badges
- `#categoryPill`: Horizontal category buttons
- `#toggleSwitch`: Modern toggle switch widget
- `#infoBox`: Themed information boxes

**Usage**:
```python
info_label = QLabel("Important info")
info_label.setObjectName("infoBox")  # Applies theme-specific styling
```

## 🔌 Extension System

### Encoder Extension

**Configuration**:
- Rotation actions: Cycle Layers, Volume, Brightness, Media, Custom
- Button actions: Reset Layer 0, Toggle Layer 1, Mute, Play/Pause, Custom
- Invert direction: Reverses rotation direction
- Divisor: Adjusts sensitivity (1-10)

**Code Generation**:
- Creates `EncoderHandler` instance
- Configures callbacks for rotation and button press
- Integrates with display updates

### Analog Input Extension

**Configuration**:
- Mode: Volume control or LED brightness
- Pin: GP28 (10k potentiometer)
- Polling interval: 100ms

**Code Generation**:
- Analog read from GP28
- Maps 0-65535 to appropriate range
- Updates volume or RGB brightness

### Display Extension

**Configuration**:
- I2C pins: GP20 (SDA), GP21 (SCL)
- Display size: 128x64 pixels
- Layer-aware visualization
- Key abbreviations: 3-4 characters

**Code Generation**:
- Initializes SH1106 display
- Creates `LayerDisplaySync` module
- Updates display on layer changes
- Shows current keymap with labels

### RGB Matrix Extension

**Configuration**:
- Pin: GP9 (SK6812MINI LEDs)
- LED count: 20 (per-key) + underglow
- RGB order: GRB or RGB
- Brightness: 0.0-1.0
- Per-key colors: Individual LED colors
- Layer colors: Different colors per layer

**Code Generation**:
- Initializes RGB extension
- Sets default colors
- Applies per-key overrides
- Handles layer color switching

## 📝 Error Handling Patterns

### File Operations

**Pattern**: Surface errors via QMessageBox

```python
try:
    with open(filepath, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    QMessageBox.warning(self, "File Not Found", 
                       f"Configuration file not found: {filepath}")
except json.JSONDecodeError as e:
    QMessageBox.critical(self, "Parse Error",
                        f"Invalid JSON: {str(e)}")
```

### Async Tasks

**Pattern**: Use signals for progress updates

```python
# In long-running task:
self.progress_signal.emit(50)  # 50% complete

# In UI thread:
self.progress_signal.connect(self.update_progress_bar)
```

### Graceful Degradation

**Pattern**: Continue operation with reduced functionality

```python
if not os.path.exists(optional_file):
    # Log warning but continue
    print(f"Warning: {optional_file} not found, using defaults")
    return default_config
```

## 🔧 Configuration Versioning

### Version Keys

Current version: `"2.0"`

```json
{
  "version": "2.0",
  "keymap_data": [...],
  "macros": {...}
}
```

### Migration Strategy

**Function**: `load_configuration()`

```python
def load_configuration(self, filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    version = data.get("version", "1.0")
    
    if version == "1.0":
        # Migrate old format
        data = self.migrate_v1_to_v2(data)
    
    # Load migrated data
    self.keymap_data = data["keymap_data"]
    # ...
```

**IMPORTANT**: All schema changes must include migration logic to maintain backward compatibility.

### Defaults

**Function**: `build_default_rgb_matrix_config()`

Returns default configuration when:
- No saved config exists
- Migration fails
- User requests reset

## 🧪 Testing & Development

### Testing Hooks

**Scripts**:
- `scripts/preview_gen.py`: Generate code without GUI
- `scripts/test_rgb_map_emit.py`: Test RGB code generation

**Usage**:
```bash
set KMK_SKIP_DEP_CHECK=1
set KMK_SKIP_STARTUP_DIALOG=1
python scripts/preview_gen.py
```

**Pattern**: Add similar scripts for new features rather than embedding CLI in `main.py`

### Build Workflow

**Development**:
```bash
python main.py  # Launch GUI
```

**Production**:
```bash
python build_exe.py  # Run PyInstaller
# Uses ChronosPadConfigurator.spec
```

### Bundled Dependencies

**Location**: `libraries/`

- `kmk/` - KMK firmware (vendor code)
- `adafruit-circuitpython-bundle-9.x-mpy/` - Adafruit libraries

**IMPORTANT**: Treat as vendor code - only patch via upstream sync scripts.

## 🎯 Code Quality Standards

### Function Guidelines

1. **Length**: Keep functions under 50 lines
2. **Single Responsibility**: Each function does ONE thing
3. **Type Hints**: All function signatures use type hints
4. **Docstrings**: Every function has comprehensive docstring

### Naming Conventions

```python
# Classes: PascalCase
class CollapsibleCard(QWidget):
    pass

# Functions/Methods: snake_case
def generate_code_py_dialog(self):
    pass

# Constants: UPPER_SNAKE_CASE
FIXED_ROW_PINS = [GP0, GP1, GP2, GP3, GP4]

# Private methods: _leading_underscore
def _apply_dark_stylesheet(self):
    pass
```

### Magic Numbers

**Bad**:
```python
slider.setValue(100)
```

**Good**:
```python
DEFAULT_BRIGHTNESS = 100
slider.setValue(DEFAULT_BRIGHTNESS)
```

### DRY Principle

**Bad**:
```python
# Repeated validation logic
if row < 0 or row >= 5:
    return
# ... 10 more times in different methods
```

**Good**:
```python
def is_valid_coordinate(self, row: int, col: int) -> bool:
    """Validate grid coordinates."""
    return 0 <= row < 5 and 0 <= col < 4

# Use everywhere:
if not self.is_valid_coordinate(row, col):
    return
```

## 🔄 Development Workflow

### Adding New Features

1. **Documentation First**: Document the feature in this guide
2. **Implementation**: Write code following standards
3. **Testing**: Create test scripts in `scripts/`
4. **Documentation Update**: Update relevant docs
5. **Commit**: Follow commit standards

### Refactoring

1. **Maintain Documentation**: Update docs to match changes
2. **Preserve Behavior**: Existing features must keep working
3. **Add Tests**: Verify refactoring didn't break anything
4. **Update Comments**: Explain WHY changes were made

### Bug Fixes

1. **Document Root Cause**: Explain what caused the bug
2. **Document Solution**: Explain how it was fixed
3. **Add Prevention**: Add checks to prevent recurrence
4. **Update Tests**: Add test case for the bug

## 📚 Key Modules & Classes

### CollapsibleCard

**Purpose**: Reusable expandable card widget

**Usage**:
```python
card = CollapsibleCard("Section Title", badge_text="3")
layout = card.get_content_layout()
layout.addWidget(QLabel("Content"))
```

**Features**:
- Click header to expand/collapse
- Badge support for counts
- Theme-aware styling
- Smooth show/hide transitions

### ToggleSwitch

**Purpose**: Modern iOS/Material Design toggle switch

**Usage**:
```python
toggle = ToggleSwitch()
toggle.setChecked(True)
toggle.toggled.connect(self.on_toggle_changed)
```

**Features**:
- Blue when active (#4a9aff)
- Gray when inactive (#4b5563)
- Smooth transition animation
- Disabled state support

### ToastNotification

**Purpose**: Non-intrusive feedback messages

**Usage**:
```python
ToastNotification.show_message(
    self, 
    "Operation successful!", 
    ToastNotification.SUCCESS,
    duration=2000
)
```

**Message Types**:
- INFO: Blue background
- SUCCESS: Green background
- WARNING: Orange background
- ERROR: Red background

**Features**:
- Bottom-right positioning
- Fade-in/fade-out animations
- Auto-dismiss after timeout
- Multiple toasts stack vertically

## 🎨 Modern UI Components

### Category Pills

**Purpose**: Quick navigation for keycode categories

**Features**:
- Horizontal scrollable buttons
- Active pill: Blue (#4a9aff), bold
- Inactive pill: Gray, normal weight
- Bi-directional sync with tabs
- Touch-friendly size (min 80px width)

### Grid Actions Bar

**Purpose**: Layer-level operations toolbar

**Features**:
- Clear Layer: Resets all keys to KC.NO
- Copy Layer: Copies to internal clipboard
- Paste Layer: Overwrites current layer
- Selection Display: Shows current key info

### Context Menus

**Purpose**: Right-click operations on grid keys

**Menu Items**:
- Copy Key: Copies key value
- Paste Key: Applies clipboard value
- Set to Transparent (KC.TRNS)
- Set to No Key (KC.NO)
- Delete (alias for No Key)

## 🔍 Debugging Tips

### Enable Debug Logging

```python
# In main.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Code Generation

```bash
python scripts/preview_gen.py > test_output.txt
```

### Check RGB Output

```bash
python scripts/test_rgb_map_emit.py
```

### Bypass Startup Dialogs

```bash
set KMK_SKIP_STARTUP_DIALOG=1
python main.py
```

---

## 📖 Related Documentation

- **[Usage Guide](USAGE.md)** - Feature walkthrough
- **[API Reference](API_REFERENCE.md)** - Detailed code documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

---

**Documentation Generated By**: GitHub Copilot AI  
**Validated By**: David (D1odeKing)  
**Last Updated**: November 5, 2025
