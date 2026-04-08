# Version 4.0.0 Alpha 3

## Summary

Version 4 Alpha 3 is largely focused on stability improvements and cleanup, ensuring that all features from V3 are implemented carefully and properly. 

## Changes

### General Improvements
- Cleaned up unnecessary imports

### Operators
- Updated `update_collection` logic in `OP_rig_rename` to use a toggle in user preferences instead of a hardcoded value in the UI.
- Hardened http request handling in `skin_utils.py` to close connections properly.

### Rig Manager
- SACR Manifest Downloader now properly refreshes the rig list upon completion.

# Version 4.0.0 Alpha 2

## Summary

Version 4.0.0 Alpha 2 introduces a dedicated Rig Preset system within the Rig Manager, allowing users to save, load, and manage custom rig configurations. This update also brings significant UI refinements across all dynamic lists to better align with standard Blender interface patterns, providing a more cohesive and efficient user experience.

## New Features

### Rig Preset Management
- Implemented a dynamic "Saved Presets" list in the Rig Manager panel.
- Added operators to Save, Load, and Delete rig presets directly from the UI.
- Integrated automatic directory handling for storing presets in the addon's data folder.
- Added a "New Preset Name" input field with automatic synchronization to the selected preset.
- Enhanced the "Import Preset" functionality to support both base rigs and saved presets.

### UI & UX Enhancements
- Standardized all dynamic lists (Base Presets, Saved Presets, and Skins) to mirror Blender's Material UI slot control pattern.
- Implemented dynamic row heights for `template_list` elements (expanding from 3 to 5 rows based on content).
- Added vertical slot control columns (Refresh, Save, Delete, etc.) next to all dynamic lists for better accessibility.
- Improved layout grouping with logical separators and icon-only buttons for a cleaner, more compact interface.

## General Improvements
- Added persistent load handlers to automatically refresh all lists (Rigs, Presets, Skins) when a file is opened or the addon is registered.
- Refined the "Save" logic to conditionally show Save or Load operators based on the current file's saved state and location.
- Optimized the `append_rig` operator to handle multiple list contexts seamlessly.

## Cleanup
- Completely removed the obsolete `MT_save_dialog` component and its associated registration logic.
- Conducted a project-wide cleanup of redundant UI labels and text.

---

# Version 4.0.0 Alpha 1

## Summary

Version 4.0.0 is a complete, ground-up refactor of the extension, transitioning from a monolithic legacy structure to a modern, modular extension architecture. This update focuses on scalability, rig-specific property management, and standardized development practices to ensure compatibility across multiple Sakura rig versions without property pollution or conflicts.

Key architectural shifts include moving UI properties from the global `Scene` and local `PoseBone` to individual `Object` data-blocks, allowing multiple rigs to coexist in a single scene with independent settings, and the implementation of a modular registration system for better maintainability.

## General Extension Changes

- Refactored the entire UI system into a multi-script submodule structure (`src/sacr_uis`)
- Ported and refactored core utility operators into a dedicated `src/operators` module
- Implemented `allow_online()` guardrails for all network-dependent operations
- Introduced a GitHub Actions workflow for automated building and releasing
- Implemented automatic inclusion of `beta_version` in the release filename and tag
- Standardized class registration using loop-based `register()`/`unregister()` functions

### Prefixer System

- Adopted a unified `Prefixer` system for `bl_idname` across all panels and operators
- Incorporated Major SACR and UI versions (e.g., `sacr_7_ui_2`) into the ID names
- Replaced the legacy and problematic `ids` dictionary system

### Security & Safety

- Added internet access checks to Download Manifest, Download Rig, Download Skin, and Update Player
- Ensures that network requests only occur if "Online Functionality" is enabled in Blender's system settings

## Rig UI Changes

### SACR R7 UI1 & UI2

- Split monolithic UI files into focused components like `global` settings and `face` settings
- Moved UI state storage from `bpy.types.PoseBone` to `bpy.types.Object`
- Attached properties directly to the rig object to prevent cross-rig interference
- Implemented a bidirectional synchronization system between new `Object` properties and legacy `PoseBone` custom properties

## Refactoring & Cleanup

### Legacy Removal

- Deleted `SACR_R7_UI1.py`, `SACR_R7_UI2.py`, and `sedaia_utils.py` after successful porting

### Code Standards

- Implemented project-wide use of standard Blender API aliases (`T`, `P`, `O`, `U`)
- Conducted a project-wide linting and formatting pass for PEP8 compliance
- Fixed multiple broken relative imports across all submodules after structural changes

---

# Version 3.1.0

## Summary

V3.1.0 is a small corrective release fixing some minor navigation issues I experienced with the UI in practical use as well as fixing some minor issues I personally noticed.

These issues and changes were brought about after a render that I worked on following the release of R7.4.0, in which I found the UI to be a bit cluttered and difficult to navigate, specifically around the face section. The changes made in this release are intended to make the UI more user friendly and easier to navigate. As well as adding in some missing Material options for the Irises and Sclera.

On the backend, a lot of dirty laundry was cleaned up, mainly regarding unused variables, useless characters, and bad naming semantics.


## General Extension Changes

- Replaced "module_info" with "bl_info" in all modules which still had it
  - This change is because bl_info already handles all the info I wanted module_info to handle, and having bl_info and module_info was just wasted space.
- Simplified the "Region" blocks, removing the Separator "Line."
- Moved all SACR UI's to "sedaia_ui"

### Sedaia Utils

- Removed "rig_download" entry from Ops ID list, as it is unused.
- Removed redundant Region calls and blocks.
- Removed useless "error.URLError" from retrieveJSON()
- Removed a lot of redundant parenthasis 
- Renamed multiple functions to use pascal_case instead of snakeCase
- Removed unused "FILE_delete" class
- Added `bl_options = {"REGISTER", "INTERNAL"}` to all Skin Operators
- Added new Backup function for the Skin downloader.

### Global UI -> Skin Utility UI

- Renamed module from "global_ui" to "SKIN_utility_ui"
- Moved module into "sedaia_ui" from Root
- Removed Panel Template
- Removed redundant Region Calls
- Removed region block separators
- Added "SEDAIA_SKIN_PT" to configure all current and future panels
- Made all Variables in the "Configs" array local class variables for "ui_skinUtility"
- Renamed Class from SEDAIA_MAIN_PT to SEDAIA_SKIN_PT
- Renamed the Tab from "Sedaia Skin Utility" to "Download Skins"


## Rig UI Changes

### SACR R7 UI Version 1.3.2

- Fixed a couple lingering semantic issues.

### SACR R7 UI Version 2.0.1:

- Added a new "SACR7_UI2_panel" class to store the Category and Space Information in a single location, making further development and maintenance easier.
- Removed the Configuration Atlas due to the new SACR7_UI2_panel class, where 
- Added "Opacity" to Iris and Sclera Emissive properties.
- Moved Iris and Sclera panels under the new Eyes Panel.
- Moved Eyebrow Controller visibility options to the Eyebrow Panel.
- Moved Eye Controller visibility options to the Eye Panel.
- Moved Mouth Controller visibility options to the Mouth Panel.
- Rebuilt the Eyebrow, Eyes, and Mouth visibility options backend to be cleaner and more readable
- Updated the Checkboxes in the Iris and Sclera sections to use a new method of defining UI spacing, fixing the inconsistent sizing issue with using a percentage split.
- Removed `if __init__ = "main"` statement as this module cannot be installed on it's own, and the statement's inclusion was redundant.
- Removed License Disclosure from the top of the Module.
- Restrict Select no longer available on the Lite Version of SACR R7.4.1
- Color ramp for Pupils now under a sub panel