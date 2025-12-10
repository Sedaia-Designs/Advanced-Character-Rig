# Sakura's Advanced Character Rig

## File Info

Latest Stable: R7.4
Blender 5.0

---
R7.4 Summary

SACR R7.4 officially updates to Blender 5.0, and in the process large backend changes were made to better integrate the rig with the new UI addon which is now available on the Blender Extension Marketplace, as well as clean up a lot of unoptimized expressions.

---

## Changelog

### Changes and Adjustments

- Updated Rig UI to V2
  - Added new Skin Utility, allowing the downloading of skins from Java Edition Players
  - Updated Script Architecture to a cleaner, more powerful backend
- Driver Updates
  - Simplified many python expressions using less intensive methods
    - Mainly affects Arms and Eyelashes, which had some horrendous expressions
  - Some Drivers updated and changed to play nicer with the UI Script
- Arm Style/Arm Type switched to be controlled via an Enumerator, rather than an Integer
- Quick Parent Bones now within their own individual bone groups, allowing for further control over what ones are shown
- Changed SACR Base Shader for a new General Purpose Minecraft Shader
- Iris and Sclera Shader updated to R10
- 3x4 Armor Pauldrons now using the correct Material
- Each Armor Section now has it's own texture file, change made for Addon Compatability
- Arm Bone Shapes now scale appropriately with both Slim arm types.
- Reverted Molar Controls to a bone based system
- Changed Default Camera to 1920x1080 100% resolution
- Finally set Arms to use the proper Latticess
- Hidden Objects now hidden by default when Appending

### Additions

- Skin Utility bone for use with the new Skin Utility Feature
- Added Shallow Mouth option

### Removed

- "Extended Controls" custom props removed from Face Bone Configs, as they are now controlled via the Python UI and Bone Groups
- Removed a ton of old, unused custom properties from the scene

## Lite Rig Changes (From Standard)

- Removal of all objects in the "Accessories" collection
- Simplified Mesh Geometry
- Supporting Bones for the Hair rig removed
- All Properties associated with removed meshes deleted
- All Materials associated with removed meshes deleted
- Eyesparkle Removed
- Removed Lattices
- Removed all Bevel and Subdivision modifiers
- Facerig Disabled by Default
- Mesh Collection Dissolved
- Disabled Selection of all Meshes