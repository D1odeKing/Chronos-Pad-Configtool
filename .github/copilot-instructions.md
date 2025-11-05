# Chronos Pad Copilot Guide

## Documentation Standards
**CRITICAL**: All code, functions, classes, and UI components MUST have professional, comprehensive documentation.

### Documentation Requirements
- **Every Function**: Detailed docstring explaining purpose, parameters, return values, and side effects
- **Every Class**: Clear description of responsibility, state management, and usage patterns
- **Complex Logic**: Inline comments explaining WHY, not just WHAT
- **UI Components**: Purpose, user interaction flow, and data binding explanations
- **File Structure**: README or header comments explaining organization and relationships
- **Code Examples**: Include usage examples in docstrings for non-trivial functions
- **Error Handling**: Document expected exceptions and error recovery strategies

### Documentation Style Guide
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief one-line summary of what this function does.
    
    Detailed explanation of the function's purpose, behavior, and any important
    implementation details. Explain WHY this function exists and how it fits
    into the larger system architecture.
    
    Args:
        param1: Clear description of the parameter's purpose and valid values
        param2: Description including constraints, format requirements, or examples
    
    Returns:
        Description of return value, including structure for complex types
    
    Raises:
        ExceptionType: When and why this exception occurs
    
    Example:
        >>> result = function_name("value1", 42)
        >>> print(result)
        Expected output
    
    Note:
        Any important caveats, performance considerations, or usage warnings
    """
```

## Architecture Overview
- **Architecture** `main.py` drives everything through the `KMKConfigurator` PyQt6 window; the class sets up panels for file IO, extensions, a 5×4 key grid, macro tools, and keeps UI/state in sync.
- **Hardware Model** All configs assume the fixed Chronos Pad wiring declared near the top of `main.py` (`FIXED_ROW_PINS`, encoder pins, RGB pin, OLED I2C pins); do not rewrite these unless the hardware spec changes.
- **State Shape** `self.keymap_data` stores layers as row-major 5×4 lists using KC.* strings; macros live in `self.macros` as `{name: [(action, value)]}` tuples; RGB data sits in `self.rgb_matrix_config` with stringified indices for per-key color overrides.

## UI Structure & Resizability
- **Main Layout** Three-panel QSplitter design (Left: File/Extensions | Center: Keymap Grid | Right: Key Assignment/Macros/TapDance)
- **Resizable Panels** All panels user-resizable via QSplitter; sizes persist in session.json
- **Initial Sizes** Left=250px, Center=500px, Right=550px (user-adjustable, remembered between sessions)
- **Panel Contents**:
  - **Left**: File management, configuration profiles, extension toggles (Encoder, RGB, Display, Analog Input)
  - **Center**: Layer tabs, keymap grid (5×4 buttons with coordinates and icons), info bar
  - **Right**: Keycode selector with search, Macro/TapDance tabbed management, quick actions

## Keycode Organization
- **Categories** Letters, Numbers & Symbols, Editing, Modifiers, Navigation, Function Keys, Media & Volume, Brightness, Numpad, Mouse, Layer Switching, Special
- **Search** Each keycode tab has a search filter for quick lookup
- **Icons** Category-specific icons (🔤 🔢 ✏ ⌨ 🧭 🔧 🔊 💡 🖱 📚 ⭐) for visual identification
- **Dynamic Lists** Macros and TapDance tabs populated from user-defined content

## Session Persistence
- **Saves**: Current layer, selected key coordinates, active tab indices (extensions, keycodes), splitter panel sizes
- **Storage**: `kmk_Config_Save/session.json`
- **Auto-save Triggers**: Layer changes, key selection, tab switches, panel resizing, app close
- **Restoration**: Automatically restores complete UI state on next app launch

## Persistence Layer
- **Config Directory** `kmk_Config_Save/` holds user state: `config.json` (full snapshot), extension snippets (`encoder.py`, `analogin.py`, `display.py`), `rgb_matrix.json`, `session.json`
- **Global Macros** `data/macros.json` stores macros shared across all configurations
- **Profiles** `profiles.json` is bundled via `ChronosPadConfigurator.spec` and loaded in `setup_hardware_profile_ui`; keep backward compatibility when expanding its schema
- **Always update helper files** when changing serialization logic to maintain data integrity

## Dependency Management
- **DependencyDownloader** Pulls KMK firmware and the Adafruit CircuitPython bundle into `libraries/`
- **Skip Checks** Use `KMK_SKIP_DEP_CHECK=1` when running headless scripts or tests
- **Startup Dialog** Previous session prompt controlled by `KMK_SKIP_STARTUP_DIALOG`; headless helpers in `scripts/` set both skip variables

## Code Generation Pipeline
- **Primary Function** `get_generated_python_code()` is the single source for exported firmware
- **Merges**: Hardware pins, macros, encoder/analog/display snippets, RGB output from `_generate_rgb_matrix_code()`
- **Keep Consistent** Changes to any generator must be reflected across all helpers
- **Display Sync** Layer-aware OLED rendering from `generate_display_layout_code_with_layer_support()` plus `LayerDisplaySync`; update both if touching layer tracking
- **RGB Rules** `_generate_rgb_matrix_code()` mixes defaults with overrides and emits chunked arrays; adjust both JSON schema and formatter together

## Macro & TapDance System
- **Macro Storage** GUI macro builder stores sequences as `tap/press/release/delay/text` tuples
- **TapDance Integration** Parsed from custom extension code using regex (`TD_* = KC.TD(...)`)
- **Management UI** Tabbed interface (⚡ Macros | 🎯 TapDance) in right panel
- **Dynamic Updates** `update_tapdance_list()` scans custom code and populates both keycode selector and management tab
- **Action Types** Ensure any new action types are reflected in macro dialogs and export formatting

## File Export Workflow
- **Function** `generate_code_py_dialog()` saves `code.py` to CIRCUITPY drive
- **Copies Required** `kmk/` directory and required libs (`adafruit_displayio_sh1106`, `adafruit_display_text`, `neopixel`)
- **Update Path List** Keep this list current with new firmware dependencies

## Testing & Development
- **Testing Hooks** `scripts/preview_gen.py` and `scripts/test_rgb_map_emit.py` spin the app without dialogs to snapshot generated code
- **Pattern** Add similar scripts rather than embedding CLI paths in `main.py`
- **Build Workflow** 
  - Development: `python main.py` launches GUI
  - Production: `python build_exe.py` runs PyInstaller with `ChronosPadConfigurator.spec`
- **Bundled KMK** The repo contains a cached `kmk/` tree under `libraries/`; treat as vendor code—only patch via upstream sync scripts

## UI Theming & Styling
- **Theme Functions** `_apply_dark_stylesheet`, `_apply_light_stylesheet`, `_apply_cheerful_stylesheet`
- **Base Geometry** Shared geometry rules in `_base_geometry_qss()` to avoid regressions
- **Named Elements** Use objectName for theme-aware styling (e.g., `QLabel#infoBox`)
- **Theme-Aware** Info boxes and special elements adapt to current theme automatically

## Error Handling Patterns
- **File Operations** Surface via `QMessageBox` to inform user
- **Async Tasks** Follow pattern: emit progress through signals, guard UI with dialogs
- **Graceful Degradation** UI should remain functional even if optional components fail to initialize

## Configuration Versioning
- **Version Keys** Saved JSON uses `version` keys (`"2.0"` current)
- **Migration** Any schema change must migrate old payloads inside `load_configuration()`
- **Defaults** Keep defaults in `build_default_rgb_matrix_config()` for backward compatibility

## Keycode Management
- **Catalog** Key selection relies on categorized lists built in `create_keycode_selector()`
- **Adding Keycodes** Update data sets in KEYCODES dictionary and ensure category icons match
- **Search Filter** `_filter_keycode_list()` handles real-time filtering in each tab

## Code Quality Standards
1. **Function Length** Keep functions under 50 lines; extract complex logic into helpers
2. **Single Responsibility** Each function/class should do ONE thing well
3. **Type Hints** Use type hints for all function signatures
4. **Error Messages** User-facing errors must be clear, actionable, and helpful
5. **Comments** Explain WHY, not WHAT; code should be self-documenting through naming
6. **Naming Conventions**:
   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Constants: UPPER_SNAKE_CASE
   - Private methods: _leading_underscore
7. **Magic Numbers** Extract to named constants with clear documentation
8. **DRY Principle** Don't Repeat Yourself; create reusable functions for common patterns

## Git Commit Standards
- **Format**: `type: Brief description` followed by detailed bullet points
- **Types**: feat, fix, docs, refactor, test, style, chore
- **Detail Level**: Explain WHAT changed and WHY; technical details in sub-bullets
- **Breaking Changes**: Always document in commit message

## Next Steps & Maintenance
- **Adding Features** Start with documentation, then implementation
- **Refactoring** Always maintain or improve existing documentation
- **Bug Fixes** Document the root cause and solution in comments
- **UI Changes** Update this guide with new layout/interaction patterns
- **Questions** If any part of the pipeline, persistence model, or build story is unclear, request clarification before proceeding
