# Changelog

All notable changes to the Chronos Pad Configuration Tool are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-08

### Added
- **Boot Configuration System**
  - Full boot.py control panel with checkboxes for read-only mode, USB HID, and drive rename
  - Real-time boot config generation from UI controls
  - Automatic boot.py file persistence to `kmk_Config_Save/boot.py`
  - Boot settings included in saved configurations and profiles
  
- **Boot Configuration Persistence**
  - `refresh_boot_config_ui()` method to sync UI with stored boot configuration
  - `on_boot_setting_changed()` handler for real-time config updates
  - `on_rename_drive_toggled()` for drive name control state management
  - `_extract_custom_boot_code()` to parse custom boot code from full script
  - Auto-refresh after loading configs, profiles, or resetting to defaults

- **Keycode Selector Rendering**
  - `KeycodeListItemDelegate` custom delegate for professional text alignment
  - Right-aligned labels independent of keycode length
  - `_add_keycode_list_item()` helper for consistent metadata storage
  - Proper rendering in both category view and search results

- **Config File Management**
  - `populate_config_file_list()` scans `kmk_Config_Save` for `config*.json` files
  - Backward compatibility with root-level configs
  - Sorted display by directory then filename
  - Auto-refresh after saving new configuration files
  - Combo box disabled when no configs exist

- **Boot.py File Handling**
  - Boot configuration loaded from disk during startup
  - Boot script persisted to `kmk_Config_Save/boot.py` on save
  - Boot settings reset with other defaults

### Changed
- **Boot Toggle Handler**: `on_boot_toggle()` now calls `on_boot_setting_changed()` for consistency
- **Config Save Flow**: Now refreshes config file list after saving and selects the new file
- **Reset to Defaults**: Also resets `boot_config_str` and refreshes boot UI

### Fixed
- **Boot Configuration Persistence**: Boot.py settings now correctly saved to `config.json` and survive config loads
- **Keycode Label Alignment**: Labels now properly right-aligned using delegate rendering instead of space padding
- **Config File Discovery**: Now correctly finds all `config*.json` files, not just `kmk_config*`
- **Boot UI Sync**: UI controls properly reflect stored boot configuration when loading

### Technical Details

#### KeycodeListItemDelegate
- Custom `QStyledItemDelegate` for `QListWidget` items
- Renders keycode on left, label on right with proper alignment
- Stores label in `UserRole + 1` for custom painting
- Minimum height of 28px for readable display

#### Boot Configuration Flow
1. User changes boot setting (checkbox, text, drive name)
2. Signal triggers `on_boot_setting_changed()`
3. Calls `generate_boot_config()` to create new script
4. Updates `self.boot_config_str`
5. Calls `save_extension_configs()` to persist boot.py file
6. Configuration saved to JSON on next config save

#### Config File Discovery
- Scans `kmk_Config_Save` first (primary location)
- Includes root-level configs for backward compatibility
- Sorts by directory, then filename
- Returns relative paths for display
- Disabled when no configs found

## [1.1.0] - 2025-11-01

### Added
- **OLED Display Enhancements**
  - Layer-aware display updates in real-time
  - Correct left/right orientation (column mirroring)
  - Fixed top-to-bottom row ordering
  - `LayerDisplaySync` module for automatic layer tracking

- **Encoder Improvements**
  - Layer cycling with display integration
  - Custom keycodes for layer navigation
  - Configurable sensitivity (1-16 steps)

- **RGB Matrix Refactor**
  - Migrated to `rgb_matrix.json` storage format
  - Per-key and underglow color mapping
  - Automatic legacy file migration

### Known Issues
- Analog input functionality under active development

## [1.0.0-beta] - 2025-10-25

### Added
- **Initial Release**
  - Fixed 5×4 matrix configuration for Chronos Pad
  - Visual grid-based keymap editor with multi-layer support
  - OLED display integration with keymap visualization
  - RGB lighting control with per-key colors
  - Rotary encoder configuration with sensitivity control
  - Analog input slider configuration
  - Complete macro system with visual builder
  - One-click code generation and CIRCUITPY deployment
  - Profile management and session persistence
  - Multiple UI themes (Dark, Light, Cheerful)
  - Dependency auto-download (KMK firmware, CircuitPython libraries)

### Features
- Support for all KMK keycodes and modifiers
- Full extension system (Encoder, RGB, Display, Analog Input)
- Session state persistence
- Backward compatibility with older config formats
- Automatic CircuitPython version detection

---

## How to Upgrade

### From v1.1.0 to v1.2.0
1. Update the configurator: `git pull` or download new executable
2. Launch the application
3. Your existing configs are automatically compatible
4. Boot.py settings are now persisted - use the Advanced tab to configure them

### From v1.0.0 to v1.1.0 or Later
1. Update the configurator
2. Existing configurations will be automatically migrated
3. RGB matrix data migrated to new `rgb_matrix.json` format
4. Legacy files cleaned up automatically

---

## Contributing

When contributing, please:
1. Maintain the existing code style and documentation standards
2. Update CHANGELOG.md with your changes
3. Follow the AI attribution notice in README.md
4. Write comprehensive docstrings for all functions and classes

---

## Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/D1odeKing/Chronos-Pad-Configtool/issues)
- Check [Documentation](docs/) for usage guides
- Review [KMK Firmware Docs](https://github.com/KMKfw/kmk_firmware/tree/main/docs/en) for firmware-specific details

