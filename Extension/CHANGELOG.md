# Changelog

All notable changes to Sedaia Rig Interfaces are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Development toward 4.0.0 Alpha 4 is in progress. However, it is a clean rewrite from Alpha 3, focusing more on usability and stability while Alpha 3 was primarily focused on feature completeness without regard
for stability.

### Added

- SACR R7.5.0 Support

## [4.0.0 Alpha 3]

### Added

- Added an "Online Access Disabled" warning with a shortcut for enabling online
  access when network-dependent features are unavailable.
- Added local skin-file imports, custom skin names, and per-skin renaming to the
  Skin Manager profile workflow.

### Changed

- Moved profile creation into a dialog that supports either downloading a Mojang
  profile or importing a local skin file.
- Moved the Skin Selector's "Apply Skin" action below the skin list.
- Made collection updates during rig renaming respect the corresponding user
  preference.
- Refresh the available rig list after downloading a SACR manifest.

### Fixed

- Fixed an error when deleting a skin texture that has no cape.
- Ensured HTTP responses used by skin operations are closed reliably.

## [4.0.0 Alpha 2]

### Added

- Added a saved-preset list to the Rig Manager with controls for saving, loading,
  deleting, and importing rig presets.
- Added automatic storage-directory creation for rig presets.
- Added automatic list refreshes for rigs, presets, and skins when the extension
  is registered or a Blender file is loaded.

### Changed

- Standardized the rig, preset, and skin lists around Blender's slot-list layout,
  including contextual controls and row counts that adapt to their contents.
- Made the Rig Manager show the appropriate save or load action for the current
  Blender file and its location.
- Allowed the rig-appending workflow to operate on base rigs and saved presets.

### Removed

- Removed the obsolete save dialog and redundant list labels.

## [4.0.0 Alpha 1]

### Added

- Added a modular extension loader and registration lifecycle for feature
  packages.
- Added a shared ID-prefixing system for Blender operators and panels.
- Added online-access checks for manifest, rig, skin, and player downloads.
- Added object-level rig UI state and synchronization with legacy pose-bone
  custom properties so multiple rigs can retain independent settings.
- Added automated development-package builds with prerelease names in generated
  archives and tags.

### Changed

- Rebuilt the extension as a multi-module Blender Extension.
- Split the SACR R7 UI1 and UI2 interfaces into focused components.
- Moved shared utility operators into a dedicated package.

### Removed

- Removed the legacy monolithic SACR R7 UI and utility modules after their
  features were migrated.

## [3.2.4]

### Added

- Added the initial modular SACR R8 UI1 interface.
- Added shared file, image, rig, and skin utility modules.
- Added a shared top-level interface for Sakura rig tools.

### Changed

- Split SACR R7 UI2 into smaller interface modules.
- Reorganized extension preferences and feature loading in preparation for the
  4.0 rewrite.

## [3.1.0]

### Added

- Added iris and sclera emissive opacity controls to SACR R7 UI2.
- Added a backup operation for downloaded skins.

### Changed

- Reorganized the iris, sclera, eyebrow, eye, and mouth controls into their
  corresponding face panels.
- Renamed the skin utility tab to "Download Skins" and consolidated its panel
  configuration.
- Updated face-property checkboxes to use consistent Blender layout spacing.
- Moved the pupil color ramp into a subpanel.

### Removed

- Removed Restrict Select from the Lite version of SACR R7.4.1.
- Removed obsolete separators and duplicate region blocks from the interface.

### Fixed

- Fixed remaining naming and UI-navigation inconsistencies in the SACR R7
  interfaces.

## [3.0.0]

### Added

- Added dynamic module discovery and registration for rig interfaces.
- Added a rewritten SACR R7 UI2 interface with Restrict Select and rig-scale
  reset controls.
- Added player-skin downloads with support for retaining multiple skins per
  player.
- Added user preferences and shared utilities for extension-local files.
- Added a packaging script for extension archives.

### Changed

- Renamed the extension to Sakura's Rig Interfaces and reorganized it as a
  container for multiple rig interfaces.
- Updated network operations to report when Blender's online access is disabled.
- Updated operators to report results through Blender instead of console output.
- Designated SACR R7 UI1 as maintenance-only after the introduction of UI2.

## [2.0.2]

### Added

- Added player-skin downloading and local player-profile storage.
- Added development diagnostics and additional extension preferences.

### Changed

- Expanded the SACR R8 interface and reorganized its panels.

## [2.0.1]

### Added

- Added the SACR R8 interface and its supporting global controls.

### Changed

- Updated shared operators and the SACR R7 interface for the expanded
  multi-interface extension.

### Fixed

- Fixed duplicate Blender class registrations and inconsistent module names.

## [2.0.0]

### Added

- Added separate modules for the global interface, shared operators, and the SACR
  R7 interface.
- Added a global utility interface for extension-wide actions.
- Added more reliable material-object detection based on material keywords.

### Changed

- Reorganized the extension from a single module into feature-focused modules.
- Raised the minimum supported Blender version from 4.2 to 4.5.
- Expanded and refreshed the SACR R7 controls.

## [1.3.0]

### Changed

- Replaced material-object detection with a keyword-based lookup that supports
  the expanded rig materials more reliably.

### Fixed

- Fixed missed and incorrectly matched material objects in the SACR R7 UI.

## [1.2.0]

### Added

- Added the first rig-appending workflow.
- Added more SACR R7 rig and material controls.

### Changed

- Updated the SACR R7 interface to UI version 1.2.0.

### Fixed

- Fixed material-object detection for supported rig materials.

## [1.1.0]

### Added

- Added the remaining SACR R7 rig controls that were absent from the initial
  interface.
- Added a Quick Parents action.
- Added Blender Extensions installation support and manifest metadata.

### Changed

- Consolidated non-rig controls into the main interface.
- Reordered SACR R7 panels to improve navigation.

## [1.0.1]

### Added

- Added missing SACR R7 controls to the initial interface.

### Fixed

- Fixed errors in panel and operator execution paths.

## [1.0.0]

### Added

- Added the initial Blender interface for editing supported SACR R7 rig settings
  without selecting each underlying control bone.
- Added controls for SACR R7.2.1 rigs, with partial compatibility for R7.2.0.

## [0.1.0]

### Added

- Added the first development implementation of the SACR control interface.
