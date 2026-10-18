# SACR R7.4.1 Archive Extension

Install this directory with Blender's **Get Extensions** menu. It packages the
legacy R7.4.1 controls with the shared `sacr_core.skin_api` skin service.

The panels appear only when the active armature advertises the matching SACR
R7 UI2 identifier. The extension requires Blender 5.0 or newer.

The SACR R7.5 controls appear in **SACR Config** when the active armature has
`rigID = "SACR.Rev_7.UI_3"`. The R7.4.1 controls remain available for their
matching rig. R7.5 skin texture controls use the shared image operators, while
the collection visibility toggle is registered with the R7.5 interface.
