# Modern UI Vision - Chronos Pad Configurator
## Next Generation Layout Design

### Executive Summary
The current UI is functional but follows a traditional desktop pattern. This document proposes a modern, streamlined redesign using Material Design principles, card-based layouts, and improved visual hierarchy. The redesign maintains all functionality while dramatically improving user experience.

---

## Design Philosophy

### Core Principles
1. **Material Design 3**: Modern flat design with subtle depth, rounded corners (8px standard), smooth transitions
2. **Card-Based Architecture**: Related controls grouped into distinct, visually separated cards
3. **Visual Hierarchy**: Size, color, and spacing guide user attention to important actions
4. **Dark Mode First**: Design optimized for dark theme; light/cheerful themes are variants
5. **Keyboard & Mouse**: All features accessible via both input methods
6. **Accessibility**: WCAG AA compliance, high contrast, clear focus states

### Color System
- **Primary Blue**: `#4a9aff` - Active states, selections, interactive elements
- **Success Green**: `#4ade80` - Enabled features, successful operations
- **Warning Orange**: `#fb923c` - Warnings, alerts, non-critical issues
- **Error Red**: `#ef4444` - Destructive actions, critical errors
- **Dark Gray**: `#6b7280` - Disabled states, secondary text, subtle elements
- **Backgrounds**:
  - Dark: `#1f2937` (base), `#111827` (darker), `#2d3748` (elevated)
  - Light: `#f9fafb` (base), `#f3f4f6` (darker), `#e5e7eb` (subtle)

### Spacing System
- **Compact**: 4px - Micro-spacing between related elements
- **Standard**: 8px - Default spacing between components
- **Comfortable**: 16px - Spacing between major sections
- **Generous**: 24px - Top-level section separation

### Typography
- **Section Headers**: Bold, 13pt, tracking +0.5%, color: primary text
- **Subsection Labels**: Regular, 11pt, color: secondary text (70% opacity)
- **Button Text**: Medium weight, 10pt, uppercase, letter spacing +0.5%
- **Values/Keycodes**: Monospace, 10pt, color: primary text
- **Help Text**: Regular, 9pt, color: secondary text, italic

---

## Left Panel: File & Configuration Management

### Current State
```
- Simple vertical layout
- Basic buttons for Load/Save
- Checkbox for extensions
- Settings scattered vertically
```

### Modern Vision

#### Structure
```
LEFT PANEL LAYOUT
─────────────────────────────────
│ 📁 File Management
│ ┌─────────────────────────────┐
│ │ Current: Default Config  [▼] │
│ │ Open Recent: [Recent...] [+] │
│ └─────────────────────────────┘
│
│ 💾 Actions
│ ┌─────────────────────────────┐
│ │ [📂 Load]  [💾 Save]       │
│ │ [⚙ Generate code.py]       │
│ └─────────────────────────────┘
│
│ ⭐ Profiles
│ ┌─────────────────────────────┐
│ │ ▼ Saved Profiles (3)        │
│ │  • Default Config           │
│ │  • Gaming Setup             │
│ │  • Work Mode                │
│ └─────────────────────────────┘
│
│ 🔌 Extensions
│ ┌─────────────────────────────┐
│ │ ▼ Available Extensions      │
│ │ ⚙ Encoder         [●   ]   │
│ │ 🎨 RGB Lighting   [  ○]   │
│ │ 📺 OLED Display   [●   ]   │
│ │ 🎚 Analog Input   [  ○]   │
│ │ ⚡ Custom Code    [●   ]   │
│ └─────────────────────────────┘
│
│ 🎨 Theme
│ ┌─────────────────────────────┐
│ │ ● Dark   ○ Light   ○ Fun   │
│ └─────────────────────────────┘
```

#### Card Design Details

**File Management Card**
- Dropdown showing current configuration with file icon
- "Open Recent" button with submenu of last 5 files
- "New Configuration" button for templates
- Small "✓" indicator showing auto-save status

**Actions Card**
- Two-column button layout
- Load/Save with prominent styling
- Generate code.py with success confirmation
- Keyboard shortcuts shown on hover

**Profiles Card**
- Collapsible section (starts expanded)
- Shows profile count badge
- Each profile: name, key count, last modified date
- Star icon for favorites (drag-to-reorder future feature)
- Right-click menu: Rename, Delete, Duplicate

**Extensions Card**
- Collapsible section (starts expanded)
- Toggle switches (modern style, not checkboxes)
- Enabled = Blue toggle + blue label
- Disabled = Gray toggle + gray label
- Small gear icon + "Configure" link opens dialog
- Visual indicator shows if extension has unsaved changes

**Theme Card**
- Radio button group (horizontal)
- Icon + text for each theme
- Preview of active theme colors

#### Implementation Notes
```python
# Style: Rounded cards with subtle shadows
card_stylesheet = """
QFrame#card {
    border-radius: 8px;
    background-color: #2d3748;
    border: 1px solid #374151;
    padding: 12px;
    margin-bottom: 8px;
}

QLabel#cardTitle {
    font-weight: bold;
    font-size: 11pt;
    color: #ffffff;
    margin-bottom: 8px;
}

QCheckBox, QRadioButton {
    color: #e5e7eb;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 2px;
}

QCheckBox:checked::indicator {
    background-color: #4a9aff;
    border: 2px solid #4a9aff;
}
"""
```

---

## Center Panel: Keymap Grid & Layer Management

### Current State
```
- Layer tabs at top (text only)
- 5x4 grid of buttons
- Colored by key type
- Coordinates shown below each key
```

### Modern Vision

#### Structure
```
CENTER PANEL LAYOUT
─────────────────────────────────────
│ Layer Tabs (with preview icons)
│ ┌───────────┬───────────┬───────┐
│ │ ⬜ Layer 0 │ ⬜ Layer 1 │ ➕   │
│ │ [20 keys] │ [15 keys] │       │
│ └───────────┴───────────┴───────┘
│
│ Grid Actions Bar
│ ┌───────────────────────────────┐
│ │ [🗑 Clear] [📋 Copy] [📌 Paste] │
│ │ Selected: (Row 2, Col 3) KC.A  │
│ └───────────────────────────────┘
│
│ Keymap Grid (5×4)
│ ┌────────┐ ┌────────┐ ...
│ │  (4,0) │ │  (4,1) │
│ │ KC.ESC │ │  KC.1  │
│ │   ⌨   │ │   🔢   │
│ └────────┘ └────────┘
│
│ Legend (collapsible)
│ ┌───────────────────────────────┐
│ │ ⌨ Letter  🔢 Number          │
│ │ ✏ Editing ⚡ Macro            │
│ │ 🎯 TapDance 🔄 Transparent    │
│ └───────────────────────────────┘
```

#### Key Features

**Layer Tabs**
- Horizontal tab bar with layer preview icon (8x8px color swatch)
- Key count badge (e.g., "20 keys")
- "+" button to add layer
- Right-click menu: Duplicate, Delete, Rename, Clear All
- Smooth transition animation on layer switch

**Grid Actions Bar**
- Above grid: Clear Layer, Copy Layer, Paste Layer, Reset to Default
- Below: Current selection display "Selected: (Row 2, Col 3) | KC.A"
- Context-sensitive help text

**Key Buttons**
- Size: 100×100px with 12px spacing (vs current 80×80)
- Corner radius: 8px
- Hover effect: Subtle glow, color brightens slightly
- Selected key: 3px bright blue border (#4a9aff) + blue glow shadow
- Unselected: Neutral background matching key type color
- Layer indicator: Small badge top-left showing which layer has this key
- Icon + name visible even at compact sizes

**Key Type Indicators**
- ⌨️ Letters (teal)
- 🔢 Numbers (orange)
- ✏️ Editing (purple)
- ⚡ Macros (yellow)
- 🎯 TapDance (pink)
- 🔄 Transparent (gray)
- ✖️ No Key (very light gray)
- 📚 Layer Switching (blue)

**Interaction Flow**
1. User hovers key → subtle glow effect, cursor changes
2. User clicks key → blue border highlights, right panel updates
3. User presses arrow keys → smooth navigation to adjacent keys
4. User presses Delete → key set to KC.NO with confirmation toast
5. User presses Enter → focus moves to keycode selector

#### Implementation Notes
```python
# Enhanced grid button styling
keymap_button_style = """
QPushButton#keymapButton {
    min-width: 100px;
    min-height: 100px;
    border-radius: 8px;
    border: 2px solid transparent;
    background-color: #2d3748;
    color: #ffffff;
    font-weight: bold;
    font-size: 9pt;
    padding: 4px;
    transition: all 200ms ease;
}

QPushButton#keymapButton:hover {
    background-color: #374151;
    border: 2px solid #4b5563;
}

QPushButton#keymapButton:pressed {
    background-color: #1f2937;
}

QPushButton#keymapButton:checked {
    border: 3px solid #4a9aff;
    box-shadow: 0 0 12px rgba(74, 154, 255, 0.6);
    background-color: #2a5a8a;
    font-weight: bold;
}
```

---

## Right Panel: Key Assignment & Advanced Functions

### Current State
```
- Selected key display at top
- Tabs for key types (Letters, Numbers, etc.)
- Search box in each tab
- Macro/TapDance management below
- Quick action buttons
```

### Modern Vision

#### Structure
```
RIGHT PANEL LAYOUT
─────────────────────────────────────
│ Key Assignment Card
│ ┌───────────────────────────────┐
│ │ Selected: (2, 3)             │
│ │ ┌─────────────────────────────┐
│ │ │ ⌨️ KC.A                     │
│ │ │ Letter Key                   │
│ │ └─────────────────────────────┘
│ │ [⌨ Combo] [✖ Clear] [🔄 TRNS]│
│ └───────────────────────────────┘
│
│ Keycode Selector
│ ┌───────────────────────────────┐
│ │ Search Keycodes...            │
│ │                               │
│ │ Category Pills (scrollable)   │
│ │ [🔤 Ltr] [🔢 Num] [✏ Ed]...  │
│ │                               │
│ │ Keycode Grid (3 columns)      │
│ │ ┌────────┬────────┬────────┐ │
│ │ │🔤 KC.A │🔤 KC.B │🔤 KC.C │ │
│ │ ├────────┼────────┼────────┤ │
│ │ │🔤 KC.D │🔤 KC.E │🔤 KC.F │ │
│ │ └────────┴────────┴────────┘ │
│ └───────────────────────────────┘
│
│ Advanced: Macro & TapDance (Side-by-side)
│ ┌─────────────────┬─────────────────┐
│ │ ⚡ Macros (3)  │ 🎯 TapDance (2) │
│ ├─────────────────┼─────────────────┤
│ │ • ALT+S         │ • TAP_EDIT      │
│ │ • COPY          │ • TAP_LAYER     │
│ │ • PASTE         │                 │
│ │                 │                 │
│ │ [➕] [✏] [🗑]   │ [➕] [🔄]       │
│ └─────────────────┴─────────────────┘
```

#### Card Design Details

**Key Assignment Card**
- Shows selected key with large icon + name
- "No Key Selected" message when nothing selected
- Coordinates display: "(Row 2, Col 3)"
- Quick action buttons: Combo, Clear, Transparent
- Clear visual distinction: selected vs empty state

**Keycode Selector**
- Search bar with autocomplete (filters all categories)
- Horizontal category pills (scrollable list)
- Grid view: 3 columns × N rows (vs current vertical list)
- Each keycode shows:
  - Small icon (category-specific)
  - Keycode name (e.g., "KC.A")
  - Category badge (subtle background color)
- Hover: Full tooltip with description, common uses
- Click: Immediate assignment to selected key

**Category Pills**
- Horizontal scroll container
- Each pill: icon + label + keycode count
- Active pill: blue background, white text
- Inactive: gray background, light text
- Clicking pill filters grid below

**Macros & TapDance Section**
- Split 50/50 horizontal layout (vs stacked tabs)
- Each side independent scrollable list
- Macros left:
  - List of available macros with ⚡ icon
  - "ALT+S", "COPY", etc. displayed with full name
  - Add/Edit/Delete buttons in small button group
  - Click macro → assign to selected key
  
- TapDance right:
  - List of available TapDance keys with 🎯 icon
  - "TAP_EDIT", "TAP_LAYER", etc.
  - Create/Refresh buttons
  - Click TapDance → assign to selected key

#### Interaction Flow
1. User navigates keymap grid → right panel auto-updates
2. User searches "shift" → filters to modifiers + special keys with "shift"
3. User clicks "KC.A" → key assigned, grid updates immediately
4. User clicks "ALT+S" macro → macro assigned, shows confirmation toast
5. User presses Ctrl+Z → undo assignment

#### Implementation Notes
```python
# Grid view for keycodes
keycode_grid_style = """
QGridWidget {
    spacing: 8px;
    margin: 8px;
}

QKeycode_Item {
    min-width: 80px;
    min-height: 60px;
    border-radius: 6px;
    background-color: #2d3748;
    border: 1px solid #374151;
    padding: 4px;
}

QKeycode_Item:hover {
    background-color: #374151;
    border: 1px solid #4a9aff;
}

QKeycode_Item:pressed {
    background-color: #1f2937;
    border: 2px solid #4a9aff;
}
"""

# Category pill styling
category_pill_style = """
QPushButton#categoryPill {
    min-width: 60px;
    padding: 6px 12px;
    border-radius: 20px;
    background-color: #374151;
    color: #9ca3af;
    border: 1px solid #4b5563;
    font-size: 9pt;
    font-weight: 600;
}

QPushButton#categoryPill:checked {
    background-color: #4a9aff;
    color: #ffffff;
    border: 1px solid #4a9aff;
}
```

---

## Global UI Improvements

### Floating Action Buttons (FAB)
- Positioned bottom-right of relevant panels
- Context-sensitive (appears when relevant)
- Large, circular (56px diameter)
- Shadow with hover lift effect
- Examples:
  - Center panel: "+" to add layer
  - Macro section: "+" to create macro
  - TapDance section: "+" to create TapDance

### Tooltips & Help
- Every button has descriptive tooltip
- Keyboard shortcuts shown: "Save (Ctrl+S)"
- Extended help on hover for 1+ second
- Tooltip position: auto-position to avoid overlap

### Context Menus
- Right-click grid key → "Copy", "Paste", "Delete", "Set to Transparent", "Set to No Key"
- Right-click layer tab → "Duplicate", "Delete", "Rename", "Clear Layer"
- Right-click macro → "Edit", "Delete", "Duplicate", "Assign to Selected Key"
- Right-click TapDance → "Edit", "Delete", "Copy Code"

### Dialogs
- Centered on screen
- Rounded corners (8px)
- Semi-transparent backdrop
- Button group at bottom: [Cancel] [OK]
- Small preview/confirmation message

### Keyboard Shortcuts
- Arrow Keys: Navigate grid
- Enter: Assign selected keycode to selected key
- Delete: Clear selected key
- Ctrl+S: Save configuration
- Ctrl+Z: Undo
- Ctrl+Y: Redo
- Ctrl+F: Focus search
- Tab: Navigate form fields
- Escape: Close dialogs, deselect

### Visual Feedback
- **Toast notifications**: Brief messages for actions (bottom-right, auto-dismiss)
  - "Key assigned: KC.A"
  - "Configuration saved"
  - "Macro created: ALT+S"
- **Loading indicators**: Smooth spinner for async operations
- **Progress bars**: For long operations (code generation)
- **Inline validation**: Red text for form errors, green checkmarks for success

---

## Responsive Behavior

### Panel Resizing
- Minimum panel widths:
  - Left: 200px
  - Center: 400px
  - Right: 350px
- Smooth drag-to-resize with visual feedback
- Splitter highlight on hover
- Sizes auto-saved to session.json

### Compact Mode (small window)
- Hide non-essential labels
- Use icon-only buttons
- Reduce padding/spacing by 50%
- Single-column Macro/TapDance

### Full-Screen Mode
- Maximize button in title bar
- Full-screen keystroke works too (F11)
- Grid expands to fill space
- Larger buttons when more room available

---

## Implementation Roadmap

### Phase 1: Visual Polish (1-2 weeks)
Priority: Immediate visual improvements, no structural changes
- [ ] Update all buttons with rounded corners (8px)
- [ ] Add subtle shadows to raised elements
- [ ] Improve color consistency across panels
- [ ] Add hover/focus state animations
- [ ] Implement card styling for grouped controls
- [ ] Better spacing and alignment throughout

### Phase 2: Left & Center Panels (2-3 weeks)
Priority: File management and grid UX
- [ ] Redesign left panel with collapsible cards
- [ ] Add profile management UI
- [ ] Redesign extensions UI with toggle switches
- [ ] Expand grid buttons to 100×100px
- [ ] Add layer preview icons
- [ ] Implement layer management context menu

### Phase 3: Right Panel Redesign (2-3 weeks)
Priority: Key assignment and advanced features
- [ ] Redesign keycode selector with grid view
- [ ] Implement category pills
- [ ] Split Macros/TapDance into side-by-side layout
- [ ] Add FABs for common actions
- [ ] Enhance search with autocomplete

### Phase 4: Advanced Features (3-4 weeks)
Priority: Polish and convenience features
- [ ] Implement context menus (grid, layers, macros)
- [ ] Add undo/redo system with visual indicators
- [ ] Drag-and-drop layer reordering
- [ ] Toast notifications for all actions
- [ ] Keyboard shortcut help overlay (?)
- [ ] Export layout presets

### Phase 5: Accessibility & Polish (1-2 weeks)
Priority: Final refinements
- [ ] WCAG AA compliance audit
- [ ] Screen reader testing
- [ ] Keyboard-only navigation testing
- [ ] Light/Cheerful theme variant polish
- [ ] Performance optimization

---

## Code Style Guide for UI Implementation

### Stylesheet Organization
```python
# Create themed stylesheets as separate methods returning QSS strings
def _get_modern_card_stylesheet(self) -> str:
    """
    Generate QSS stylesheet for card-based layout.
    
    Cards use rounded corners (8px), subtle shadows, and consistent spacing.
    Returns color-independent rules that work across all themes.
    """
    return """
    QFrame#card {
        border-radius: 8px;
        border: 1px solid palette(midlight);
        padding: 12px;
        margin-bottom: 8px;
    }
    """

# Apply theme-specific colors in separate methods
def _apply_dark_stylesheet(self) -> str:
    """Apply dark theme with modern card styling."""
    card_styles = self._get_modern_card_stylesheet()
    dark_colors = """
    QFrame#card {
        background-color: #2d3748;
        border: 1px solid #374151;
    }
    """
    return card_styles + dark_colors
```

### Component Creation Pattern
```python
def create_profile_card(self, parent) -> QFrame:
    """
    Create a profile management card with collapsible sections.
    
    Structure:
        Card
        ├── Header: Title + expand/collapse icon
        └── Content: Profile list + action buttons
    
    Args:
        parent: Parent widget
        
    Returns:
        QFrame with profile management UI
        
    Note:
        Card state (expanded/collapsed) persists in session.json
    """
    card = QFrame(parent)
    card.setObjectName("card")
    
    # Implementation here
    return card
```

### Naming Conventions
- UI Elements: `{component}_{purpose}` (e.g., `profile_list_widget`, `category_pill_button`)
- Style Names: `{state}_{emphasis}` (e.g., `checked_active`, `hover_secondary`)
- Helper Methods: `_create_{component}()`, `_setup_{feature}()`

---

## Visual Examples

### Color Palette Reference
```
Dark Theme Base:
  Background: #1f2937
  Surface (elevated): #2d3748
  Border: #374151
  Text (primary): #ffffff
  Text (secondary): #9ca3af (70% opacity)

Accent Colors:
  Primary Blue: #4a9aff (active/interactive)
  Success Green: #4ade80 (enabled/success)
  Warning Orange: #fb923c (warnings/alerts)
  Error Red: #ef4444 (destructive/error)
```

### Typography Scale
```
Display (Large Headers):      16pt, bold
Section Headers:             13pt, bold, +0.5% tracking
Subsection Labels:           11pt, regular, 70% opacity
Body/Button Text:            10pt, regular
Monospace (keycodes):        10pt, monospace
Help Text:                   9pt, regular, italic, 70% opacity
Small Labels:                8pt, regular, uppercase, 60% opacity
```

---

## Success Criteria

The modern UI redesign is successful when:

✅ **Visual Hierarchy**: Users immediately see primary actions (grid, key assignment)
✅ **Keyboard Accessibility**: All features accessible without mouse
✅ **Responsive**: Works at 1024×768 and larger resolutions
✅ **Performance**: No lag when navigating grid or switching views
✅ **Consistency**: All panels follow same design language
✅ **Dark Mode**: Primary theme is pleasant for extended use
✅ **Discoverability**: Users don't need documentation for basic operations
✅ **Feedback**: Users understand result of every action (toasts, visual feedback)

---

## Notes for AI Coding Agent

When implementing these changes:

1. **Start with Phase 1** - Visual polish can be done incrementally without breaking functionality
2. **Preserve functionality** - Every change should improve UX, not remove features
3. **Test thoroughly** - Test at multiple window sizes and with keyboard navigation
4. **Document changes** - Update this file if implementation differs from vision
5. **Commit incrementally** - Each phase should be a complete, working commit
6. **Update copilot-instructions.md** - Keep this architecture guide updated as UI evolves

---

**Last Updated**: November 5, 2025
**Status**: Vision Document (Ready for Phase 1 Implementation)
