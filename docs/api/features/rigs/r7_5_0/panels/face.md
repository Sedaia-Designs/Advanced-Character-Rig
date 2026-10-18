# `features.rigs.r7_5_0.panels.face`

## `PT_Face`

Represents a Face Options panel in the user interface.

This class provides a panel for configuring face options within a
specific user interface system. It allows customization of multiple
face-related properties, including UV projection, eyelashes,
eyebrows, iris, sclera, and mouth through an organized and toggled
layout. The presence and behavior of certain features depend on the
feature set defined for the active object.

Attributes:
    bl_idname (str): Identifier for the panel.
    bl_label (str): Label displayed for the panel.
    bl_order (int): Defines the order of the panel in the UI.

Methods:
    draw(context): Renders the panel's layout and properties based on
    the current context.

### `bl_idname`

### `bl_label`

### `bl_order`

### `draw(self, context)`

Draw this UI element for the current Blender context.

## `panel_eyebrows(
    cls,
    parent_ui,
    pose,
    python,
    materials,
    collections,
    rig_feature_set
)`

Perform panel eyebrows.

## `panel_iris(parent_ui, pose, python, materials, collections, rig_feature_set)`

Perform panel iris.

## `panel_sclera(parent_ui, pose, python, materials, collections)`

Perform panel sclera.

## `panel_mouth(parent_ui, pose, python, materials, collections)`

Perform panel mouth.

## `register()`

Register this module's Blender classes.

## `unregister()`

Unregister this module's Blender classes.
