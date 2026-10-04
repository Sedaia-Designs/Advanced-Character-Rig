# Sakura's Advanced Character Rig

## File Info

Latest Stable: R7.4.1
Blender 5.1

---

R7.5 Summary

R7.5 is a Corrective Release, featuring primarily bug fixes and general improvements, as well as some extra backend integration for use with the Rig UI.

---

## Changelog

### Additions

- Custom properties to all materials denoting the purpose of that material.
- Rebuilt Rig UI from scratch, and packaged with rig separately.
- New Unified Armor Shader.
  - Uses my Weapon Shader, which enables Enchantment overlay.
  - Includes all material tiers, including full body turtle armour.
    - Credit to Moon Studio's "Complete Turtle Armor" mod for the full-body turtle armor
    - https://modrinth.com/mod/complete-turtle-armor?version=1.21.10&loader=fabric

### Changes and Adjustments

- The "Hidden Stuff" Bone Collection now hidden by default.
- Updated ArmType Property
    - Renamed "ArmType" property to "Arm Type"
    - Converted prop to a native EnumProperty
- Eyelash Property converted to native EnumProperty
- Renamed the MeshData of all objects to align with the defined naming convention
- Renamed "Sedaia.SkinUtilityBone" to "PythonReference_OBJ"
    - All Skin related settings moved to scene space, due to the new Skin Manager utility
- Increased Wire thickness of all bones, making them more selectable in wireframe mode
- Show Lattices options default set to False
- Set Wireframe Bones default to False
- Renamed Boneshape collection to "Boneshapes" from "Boneshape Master"
- Remodelled the Head Boneshape
    - Each "Wire" now properly 3D, and made thinner.
- Renamed Armor materials to only be the Armor section.
- Adjusted Eyebrow "Thickness" shape key to be pixel consistent:
  - Set Limits to Min `0.1` and Max `1.0`
  - Adjusted the mesh to be 1px thick when factor set to `1`
  - Custom Prop changed to pixel
- Adjusted Eyebrow "Depth" shape key to be pixel consistent
  - Set Upper Limit to `0.5`
  - Adjusted associated custom property
  - Adjusted Mesh State to be pixel aligned.


### Fixes

- Fixed Pupil Opacity being inverted, meaning that 0 was On and 1 was Blackout.
- Fixed Iris and Sclera Color reverting to white when turning on Emission Mask
- Sclera Gradient/Heterochromia now uses the correct UV Map

### Removed

- Cleaned up redundant custom properties from addons on all objects.

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
