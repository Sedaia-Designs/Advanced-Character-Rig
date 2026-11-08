# Changelog

Notable changes to the SACR rig and its Blender extension are recorded together.
Rig and extension versions retain their own version numbers.

## Unreleased

## SACR rig

## R7.5.0

SACR 7.5.0 focuses on corrective maintenance, general rig improvements, and
additional backend integration with the Rig UI.

Blender: 5.2.2

### Added

- Added purpose metadata to every material for Rig UI integration.
- Rebuilt the Rig UI and packaged it separately with the rig.
- Added Python helper bones for materials (`PythonConfig.Materials`) and UI panels (`PythonConfig.PanelHelper`).
- Added a unified armor shader based on the Sakura Weapon Shader, including
  enchantment overlays and every armor tier.
- Added full-body turtle armor based on Moon Studio's
  [Complete Turtle Armor](https://modrinth.com/mod/complete-turtle-armor).

### Changed

- Renamed the Arm Type property from `ArmType` to `Arm Type` and converted it to
  a native enum property.
- Converted the Eyelash property to a native enum property.
- Standardized mesh data names across all objects.
- Renamed `Sedaia.SkinUtilityBone` to `PythonConfig.Objects`, and moved the skin
  settings (`Username`, `SyncArms`, and `SyncName`) to the `PythonConfig.Skin`
  bone for the new Skin Manager.
- Increased bone wire thickness to improve selection in wireframe mode.
- Disabled Show Lattices and Wireframe Bones by default.
- Renamed the Boneshape Master collection to Boneshapes.
- Remodeled the head bone shape with thinner, fully three-dimensional wires.
- Simplified armor material names to identify only their armor section.
- Made the eyebrow Thickness shape key pixel-consistent.
  - Changed its range to `0.1`–`1.0`.
  - Made a value of `1.0` produce a one-pixel-thick eyebrow.
  - Changed the associated custom property to represent pixels.
- Made the eyebrow Depth shape key pixel-consistent.
  - Set its upper limit to `0.5`.
  - Updated its custom property and aligned the mesh state to pixels.
- Subdivided the No Face head and updated its UVs to support extrusion.
- Replaced the eyebrow shader's legacy SACR BSDF with the Sakura Minecraft BSDF.

### Fixed

- Corrected the UV map used by sclera gradients and heterochromia.
- Corrected the mapping and orientation of body-mesh end-cap UVs.
- Remapped Super Slim arms to Blockbench's 3x3-arm UV layout for compatible
  bespoke skins.

### Removed

- Removed redundant add-on custom properties from all objects.

## Blender extension

## [4.0.0] - 2026-10-18

### Added

- Added controls for SACR R7.5 rigs in the **SACR Config** sidebar, including main body, face, material, skin texture, and control-group options.
- Added R7.5 face controls for eyebrows, irises, scleras, and mouth settings.
- Added R7.5 control-group visibility controls for face and body rig collections.
- Added the **Skin Manager** in a new **Skins** tab of the 3D Viewport sidebar. Enter a Minecraft Java Edition username and click **Change Skin** to download and apply that player's skin.
  - Skins download in the background with a progress bar, so Blender stays responsive. Press Esc to cancel.
  - A skin that is already saved is never downloaded again. When a saved player is entered, a menu offers **Load Saved Skin**, **Check for New Skin**, **Back Up and Purge**, and **Purge**.
  - Saved skins load without Online Access.
  - **Saved Skins** lists every skin saved for a player, and loads any of them.
  - **Sync Arm Type** sets the rig's Arm Type from the skin's model, and **Set Rig Name to Username** renames the rig, and its default collection, to `<username> - SACR R7.5.0`.
  - The applied skin is packed into the `.blend` file.
- Added **Import Legacy Player Data** to the preferences, which imports player files saved by the legacy SR GUI skin utility.
- Added a SQLite database, `sakura.sqlite3`, in the extension's storage folder. The Skin Manager keeps its player and skin records there instead of one `<name>_Data.json` file per player. Downloaded skins are stored in `playerdata/`, one folder per player, so a player who changes their name keeps their saved skins.
- Added the Skin Manager operators under a new `sedaia_rigs_skins.*` namespace: `skin_router`, `skin_add`, `skin_load`, `skin_purge`, and `skin_import_legacy`.

### Changed

- Renamed the extension to **Sakura Character Rig Interface** and updated its product website.
- The extension now supports SACR R7.5.0 only. See **Removed** for earlier rigs.
- Raised the minimum supported Blender version to 5.2.
- Updated the extension permissions to describe skin-data downloads and extension-local storage.
- Rewrote skin management with a new backend. Players are identified by their Minecraft UUID, and every request has a timeout.
- **Prompt to Regen Player Data** now controls whether **Change Skin** asks what to do with a player who is already saved.
- Renamed the file, image, and rig operator identifiers from `sedaia_utils_ot.*` to `sedaia_rigs_utils.*`, for example `bpy.ops.sedaia_rigs_utils.image_pack()`. Operator idnames no longer repeat the `_OT_` type marker (`SEDAIA_RIGS_UTILS_OT_image_pack`, not `..._OT_OT_...`). Update keymaps and scripts that call them.

### Removed

- Removed the SACR R7 UI1 and SACR R7.4.1 (UI2) interfaces. To use SACR R7.4.1 or earlier, download the legacy SR GUI extension.
- Removed the `ArmType` and `Eyelashes` properties that the R7.4.1 interface added to every pose bone.
- Removed the `sedaia_prefs_ot.file_open` operator. Use `bpy.ops.sedaia_rigs_utils.file_open()` instead.
