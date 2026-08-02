# Changelog

All notable changes to Sakura's Advanced Character Rig (SACR), and its predecessor
SAMR, are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and SACR uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Blender versions marked **stated** come from the release's original changelog.
Versions marked **current at release** were the latest stable Blender feature
release on that date because the original changelog did not name one. They provide
historical context, not a guarantee of compatibility. These versions were determined
from Blender's [official release history](https://www.blender.org/download/releases/).

## [Unreleased]

> Target release: SACR 7.5.0 RC3
> Blender 5.1 (stated)

SACR 7.5.0 focuses on corrective maintenance, general rig improvements, and
additional backend integration with the Rig UI.

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
- Renamed `Sedaia.SkinUtilityBone` to `PythonConfig.Objects` and moved skin settings
  to the scene for the new Skin Manager utility.
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

## [7.4.1] - 2025-12-20

> Blender 5.0 (stated)

### Fixed

- Corrected inverted pupil opacity, where `0` enabled the pupil and `1` caused a blackout.
- Prevented iris and sclera colors from reverting to white when the emission mask is enabled.
- Made the Hidden Stuff bone collection hidden by default.

### Lite Rig

- Removed all objects in the Accessories collection.
- Simplified mesh geometry.
- Removed supporting bones for the hair rig.
- Removed properties and materials associated with removed meshes.
- Removed eye sparkles and lattices.
- Removed all bevel and subdivision modifiers.
- Disabled the face rig by default.
- Dissolved the Mesh collection.
- Disabled selection of all meshes.

## [7.4.0] - 2025-12-10

> Blender 5.0 (stated)

SACR 7.4 updates the rig to Blender 5.0 and makes substantial backend changes
for the V2 UI add-on available through the Blender Extensions platform.

### Added

- Added a Skin Utility bone for the new Skin Utility feature, which can download
  Java Edition player skins.
- Added a shallow mouth option.

### Changed

- Updated the rig UI to V2 with a cleaner, more capable script architecture.
- Simplified Python driver expressions, especially for arms and eyelashes.
- Updated drivers to integrate more reliably with the UI script.
- Changed Arm Style and Arm Type from integer properties to an enum.
- Moved Quick Parent bones into individual bone groups for more granular visibility control.
- Replaced the SACR Base Shader with a general-purpose Minecraft shader.
- Updated the iris and sclera shaders to R10.
- Assigned the correct material to 3x4 armor pauldrons.
- Gave each armor section its own texture file for add-on compatibility.
- Made arm bone shapes scale correctly with both slim-arm types.
- Reverted molar controls to a bone-based system.
- Changed the default camera resolution to 1920x1080 at 100%.
- Corrected the arm lattice assignments.
- Made hidden objects remain hidden when appended.

### Removed

- Removed Extended Controls custom properties from face bone configurations;
  these are now controlled by the Python UI and bone groups.
- Removed obsolete scene custom properties.

### Lite Rig

- Removed all objects in the Accessories collection.
- Simplified mesh geometry.
- Removed supporting bones for the hair rig.
- Removed properties and materials associated with removed meshes.
- Removed eye sparkles and lattices.
- Removed all bevel and subdivision modifiers.
- Disabled the face rig by default.
- Dissolved the Mesh collection.
- Disabled selection of all meshes.

## [7.3.0] - 2025-09-03

> Blender 4.5 (stated)

This release cleans up the add-on integration and refines existing features.

### Changed

- Reset the rig position.
- Parented the armor master object to the armature.
- Changed the `sacr_id` property to `SACR.Rev_7`.
- Disabled the Properties bone layer by default.

### Removed

- Removed the `script_format` property.

## [7.2.1] - 2025-08-09

> Blender 4.5 (stated)

This hotfix corrects features that were incomplete or broken in 7.2.0.

### Added

- Added more default workspaces.
- Added Face Properties text to the Face Properties bone container.
- Added a new custom property for the armature.

### Changed

- Renamed the scene to match the major version.
- Made automatic molar and canine adjustment depend on cheek bones instead of jaw movement.
- Moved molar and canine height and width controls to Mouth custom properties.
- Updated the eyebrow shader to R4.1 and added a UV Map node for gradient and split-color settings.
- Updated the iris shader to R9.1.
  - Moved the Pupil toggle to Pupil Settings.
  - Renamed the Pupil Color panel to Pupil Settings.
- Updated the sclera shader to R9.1.

### Fixed

- Applied the teeth material to the teeth meshes.

### Removed

- Removed redundant drivers.
- Removed obsolete molar and canine adjustment bones and shapes.
- Removed the redundant Sparkle toggle from Eye properties.
- Removed the redundant UV map from the eyebrow object.

### Lite Rig

- Removed all objects in the Accessories collection.
- Simplified mesh geometry.
- Removed supporting bones for the hair rig.
- Removed properties and materials associated with removed meshes.
- Removed eye sparkles and lattices.
- Removed all bevel and subdivision modifiers.
- Disabled the face rig by default.
- Dissolved the Mesh collection.
- Disabled selection of all meshes.

## [7.2.0] - 2025-06-05

> Blender 4.4 (stated)

This release addresses issues in 7.1.1 while improving performance, reducing file
size, correcting drivers, and standardizing names.

### Added

- Added a 3x3x12 arm mesh option.
- Restored eye-sparkle objects.
- Added a driver to the extruded head.
- Added drivers that hide arm IK locators and pointers when they are inactive.
- Added a separate Wrist IK Auto-Rotation control.

### Changed

- Renamed the scene to match the major version.
- Set the default view transform to AgX and Look to Base Contrast.
- Cleared the default keying set.
- Changed playback sync from Play Every Frame to Frame Dropping.
- Organized armature drivers by type.
- Standardized names for eyelashes, arms, armor, bones, objects, and shape-key groups.
- Renamed Steve arms to `Arm.4x4.(side)` and Alex arms to `Arm.3x4.(side)`.
- Moved eyelashes into the Accessories collection.
- Made arm IK and stretch blend smoothly instead of snapping between states.
- Improved the arm and leg IK systems.
  - Adjusted the leg and arm armatures.
  - Removed IK constraints from upper-arm and upper-leg bones.
  - Updated IK constraints on forearm and shin bones.
- Allowed shaped controllers to switch between solid and wireframe display.
- Recolored arm IK pointer bones to match their limbs.
- Replaced driver-controlled ankle restrictions with transform constraints.
- Converted integer custom properties to booleans where applicable.
- Combined the square and round mouth into one face mesh and bone setup.
- Increased rendered subdivision levels to 4 for face objects and 2 for torso and arms.
- Consolidated Smooth by Angle geometry node groups.
- Updated the Base shader to R4.1.
- Updated the iris and sclera shaders to R9 with a substantially simplified setup.
- Updated the eye-sparkle shader so emission is visible only to the camera.

### Fixed

- Fixed the right leg IK locator name.
- Fixed Alex-arm Transform Fix constraints on the shoulder bones.
- Hid the right arm IK pointer when right arm IK is inactive.
- Fixed the eyebrow driver, which used Armor Toggle instead of No Face.
- Fixed UVs on the bottom of the head.

### Removed

- Removed the Armor prefix from armor object names.
- Unmarked the Master collection as an asset.
- Removed the half-pixel downward adjustment from slim-arm transforms.
- Removed 16 redundant angular ankle bones.
- Removed duplicate drivers, bone shapes, and add-on custom properties.
- Removed double-layer emission from the Base shader.
- Removed shader sparkles because of their performance cost.

### Lite Rig

- Removed the Accessories collection, hair-rig support bones, eye sparkles, lattices,
  and all bevel and subdivision modifiers.
- Simplified mesh geometry and the iris and sclera shaders.
- Removed pupils from the iris shader.
- Removed properties and materials associated with removed meshes.

## [7.1.1] - 2024-12-01

> Blender 4.3 (current at release; no version stated)

### Fixed

- Fixed condensed logic nodes in the sclera and iris materials that broke the
  sclera gradient and heterochromia.

## [7.1.0] - 2024-11-02

> Blender 4.2 LTS (stated)

### Added

- Added a square-mouth face-rig option and its new face mesh.
- Added a separate Wrist IK Auto-Rotation control.
- Added drivers that hide inactive arm IK locators and pointers.
- Added an eyebrow-width shape key and driver.
- Restored the Armor collection.

### Changed

- Set the default view transform to AgX and Look to Base Contrast.
- Optimized the blend files.
- Made arm IK and stretch blend smoothly instead of snapping between states.
- Improved the arm and leg IK systems.
  - Adjusted the leg and arm armatures.
  - Removed IK constraints from upper-arm and upper-leg bones.
  - Updated IK constraints on forearm and shin bones.
- Updated arm bone colors.
- Allowed deform controllers to switch between solid and wireframe display.
- Updated face-control bone shapes with more consistent fillets.
- Reorganized molar controls.
- Enabled fang controls by default.
- Improved face-controller spacing.
- Adjusted Fancy Feet for more movement and better tracking.
- Added the `Face.` prefix to face objects.
- Increased rendered subdivision levels to 4 for face objects and 2 for torso and arms.
- Updated the iris and sclera material to Gen 7.
  - Integrated pupils into the iris node group.
  - Simplified color, luminance, and global illumination handling.
  - Consolidated gradient and heterochromia into a node group.
  - Exposed advanced emission controls.

### Fixed

- Fixed rotation locks on mouth bone shapes.
- Locked Z-axis movement for jaw and cheek controls.
- Added limits to four middle-corner bones to prevent Z-fighting.
- Fixed Global Mouth Position rotation and made teeth follow it and their respective jaw.
- Corrected reversed left and right cheek bones.
- Fixed transform space on Fancy Feet deform drivers.
- Fixed the eyebrow driver, which used Armor Toggle instead of No Face.

### Removed

- Removed redundant `mmd` and `ant-landscape` custom properties.
- Removed deprecated pupil drivers and the separate pupil material.
- Removed the extruded head's hat layer.

### Lite Rig

- Removed the long hair rig, eyelashes, armor, extruded head, and eye sparkles.
- Simplified mesh geometry.
- Removed subdivision and auto-smooth modifiers.
- Removed gradients from the iris and sclera materials.

## [7.0.0] - 2024-07-15

> Blender 4.1 (stated)

### Added

- Added a separate pupil object and material.
- Added a new SSS Weight input to the Gen 4 Base shader.
- Added reflection light-path handling to the emission pass.
- Added new bone shapes.
- Added auto-smoothing modifiers to the arms, head, and torso.

### Changed

- Simplified the armor mesh and material to one included texture.
- Merged individual-properties controls into the main global-properties bone.
- Updated the rig for Blender 4.1.
- Increased mouth depth to five Minecraft pixels.
- Reshaped the teeth into a horseshoe.
- Remodeled the face mesh to prevent mouth clipping.
- Reset custom vectors.
- Adjusted the eye-sparkle shape key and driver.
- Rebuilt face controls and divided properties among Total, Mouth, Eyes, and Eyebrows bones.
- Made individual eye controls always visible.
- Made the Flip bone optional and disabled it by default.
- Disabled In Front display.
- Renamed driver shape-key objects with the `_shape` suffix.
- Replaced `cos(var)` inversion expressions with `1-var` and shortened driver variable names.
- Made molars optional and disabled them by default.
- Merged the hair rig into the SACR armature.
- Renamed materials and fixed eye-white UVs.
- Changed the default inner-mouth color to dark red.
- Updated the Base shader to Gen 4, the Eyewhites shader to Gen 2, the Iris shader
  to Gen 6, and the Eyebrow shader to Gen 3.
- Updated all remaining shaders to use the new Base shader.
- Set CPU rendering as the default and disabled viewport denoising and viewport noise threshold.
- Disabled Film Transparent and reset color-management exposure.

### Removed

- Removed pupil controls and drivers from the Iris Gen 6 shader except textured pupils.
- Removed obsolete add-on custom properties.
- Removed the internal changelog document to reduce file size.

## [6.1.0] - 2024-08-28

> Blender 4.2 LTS (current at release; no version stated)

The original changelog for this release is lost.

## [6.0.0] - 2022-01-26

> Blender 3.0 (current at release; no version stated)

### Added

- Added an improved female mesh.
- Added five eyelash types.
- Added an arm IK control to disable wrist auto-rotation.
- Added a Master label to the master rig collection.

### Changed

- Increased loop creases on the eyelash lattice.
- Removed the camera from the SACR collection.
- Optimized the rig and reorganized its controls.
- Enabled smooth mode on arms.
- Renamed the hair rig object to SAHR V1 (Sakura's Advanced Hair Rig).
- Changed the SACR armature's internal ID to SACR R3 to reflect its architecture.

### Fixed

- Enabled Z locks on affected face bones.
- Removed a duplicate skin file and the PurgeThis material.
- Renamed `EyeTex_Cat.png.001` to `EyeTex_Cat.png`.
- Corrected weighting on the left eye's middle side-control pins.
- Corrected the square mouth shape.
- Updated the iris-scale math expression.
- Applied the teeth material to the teeth.
- Replaced default object names and matched mesh names to object names.

### Removed

- Removed adjustable iris size in favor of automatic pupil scaling.
- Removed the text beside the head and a stray square from the face control panel.

## [5.2.0] - 2021-11-11

> Blender 2.93 LTS (current at release; no version stated)

### Added

- Added the square mouth and control-panel labels.
- Restored armor with an updated control interface.
- Added rigged hair.

### Changed

- Simplified pupil controls and made pupils scale from the pupil control.
- Moved the pupil control and made fang effectors always visible.
- Added a separate SSS color input.
- Expanded and reorganized iris and eye-white materials.
- Reorganized and simplified the default UI.

### Fixed

- Fixed iris scaling, eyebrow normals, and Alex arm normals.

### Removed

- Removed the Pupil Size face property and diffuse shader option.

## [5.0.0] - 2021-05-27

> Blender 2.92 (current at release; no version stated)

### Added

- Added separate emission-mask inputs for each eye.
- Added pupils and custom-pupil support.
- Added arm and leg stretching.
- Added lattice shape keys for custom deformations.
- Added scale restrictions for easier child presets.
- Added two-step toggles for eyes and eyebrows and a separate mouth toggle.
- Added simple smoothing controls for arms and torso.

### Changed

- Changed pupil scaling, arm anchor points, and eyebrow thickness handling.
- Updated bone shapes, female deformation, the default workspace, image names,
  collection names, arm IK, eyebrow controls, and skeleton-layer organization.
- Combined armature and mesh collections.
- Set the Steve skin and materials as defaults.

### Fixed

- Corrected and realigned UV maps.
- Removed broken settings and drivers.

### Removed

- Removed round eyes, automatic HD skin compatibility, and the diffuse material.

### Notes

- To enable HD eyes, add UV Map and Image nodes manually. Set the UV Map node to
  `HD_Map`, connect it to the texture, and connect that texture to the first color
  input for both the left and right eyes. Repeat for HD eye whites.

## [4.2.0] - 2021-02-24

> Blender 2.91 (current at release; no version stated)

### Added

- Added Easy Parent Objects support for the head and wrists.

### Changed

- Disabled the denoiser by default for systems without SSE4.2 support.
- Re-enabled Extras and Origins in viewport display settings.
- Updated materials, the default HD eye texture, and the template eye-white texture.
- Redesigned bone shapes and changed the default skin.
- Dropped the LTS tag.

### Fixed

- Fixed parenting of extruded meshes, leg lattice alignment, eye UVs, teeth
  alignment, eye-white emission controls, and subdivision on main meshes.
- Optimized memory usage.

### Removed

- Removed the hybrid IK/FK system and restored a traditional switch.

## [4.1.1] - 2020-11-01

> Blender 2.90 (current at release; no version stated)

### Added

- Added eye derp controls.
- Added HD compatibility to every build.
- Added eyebrow emission support.

### Changed

- Updated all materials to the Gen 2 skin shader with built-in SSS.
- Updated eyebrow controls and optimized the outliner.
- Made the Extrude build the standard build.
- Adjusted chest and hip pivots and redesigned hip and pelvis bone shapes.
- Offset pupils and removed subdivision from everything except the head and eyebrows.
- Remodeled pupil and mouth control shapes.
- Changed the rig text to an extruded version object and character name.
- Split eye, pupil, and eyebrow materials into left and right variants.
- Updated the default skin, eye, and eyebrow materials.
- Added two slim-arm modes: 1.16 and 1.8.
- Reduced distribution to Standard and Lite builds.

### Fixed

- Parented eyelashes to the Eyelashes empty.
- Improved performance.

### Removed

- Removed MC Damage Hue, the gradient world setup, Anti-Lag, and armor.

## [4.1.0] - 2020-07-24

> Blender 2.83 LTS (current at release; no primary version stated)

### Added

- Added a legacy build for Blender 2.7x users.

### Fixed

- Corrected the rig scale.
- Removed a missing-file warning for `sakura.MEDIEVAL.png`.

## [4.0.0] - 2020-07-19

> Blender 2.83 LTS (current at release; no primary version stated)

### Added

- Added IK arms with automatic wrist rotation.
- Restored molar controls from SACR V2.
- Added a legacy build for Blender 2.7x users.

### Changed

- Combined the faceplate and head into one mesh for subsurface scattering.
- Overhauled the skin material with emission, simpler controls, and diffuse shading.
- Replaced the upper-arm bone shape to improve selection through armor.
- Adjusted torso pivot points and face-rig controls.
- Overhauled eyebrow and eye-white materials.
- Updated default materials and colors.

### Fixed

- Prevented round eyes from rendering when disabled.
- Corrected the left leg lattice assignment.
- Fixed face subdivision clipping at the lowest eye setting.
- Corrected smooth shading on torso and hip objects.
- Made torso bone shapes protrude through armor.

## [3.0.0] - 2020-06-25

> Blender 2.83 LTS (current at release; no version stated)

SACR R3 is a complete rebuild of the rig.

### Added

- Added Fancy Feet.

### Changed

- Redesigned the rig UI and moved property panels to the right side of the head.
- Reworked armor, pupil, and eyebrow materials.
- Simplified the 125-degree sharp-bend shape key.
- Replaced female shape-key deformations with lattice deformations.
- Rebuilt round eyes as one object.
- Redesigned bone shapes and reduced the rig scale.
- Adjusted default specular and roughness values and moved MC Damage to the skin material.
- Rebuilt the face rig with a round mouth and new hierarchy.
- Rebuilt the torso with smooth shading and bendy bones.
- Reverted the material selector to a cube head.

## [2.0.0] - 2020-04-28

> Blender 2.82a (current at release; no version stated)

### Added

- Added IK foot switches, armor, a face control panel, female mode, mouth emotion
  controls, pointy teeth, and an extrudable rig build.
- Made pupils scale with the main controller.

### Changed

- Moved face controls to the Face Control object.
- Improved mouth behavior, Alex arms, torso rotation, and wrist shape keys.
- Updated the material object to display face materials when the face is enabled.
- Increased viewport mesh detail and made pupils selectable by default.

### Removed

- Removed Easy Pupil UVs; edit eye UVs manually instead.

## [1.0.0] - 2020-03-25

> Blender 2.8 (stated; Blender 2.82a was current at release)

The first full release of Sakura's Advanced Character Rig. SACR succeeded SAMR V2
(Spatial's Advanced Minecraft Rig) after the project was renamed.

### Added

- Added an advanced face rig.
- Added HD skin and eye support.
- Added 125-degree sharp bends.
- Added FK, global IK, and local IK arm controls.

## [SAMR 0.1.5] - 2020-03-15

> Blender 2.82a (current at release; no version stated)

### Added

- Added wrists, global and local IK, and controls for toggling objects and modes.

### Changed

- Rebuilt the torso.

### Known Issues

- The rig did not yet include a face rig.

## [SAMR 0.1.0] - 2020-03-15

> Blender 2.82a (current at release; no version stated)

Initial SAMR release.
