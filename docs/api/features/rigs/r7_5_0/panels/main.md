# `features.rigs.r7_5_0.panels.main`

## `toggle_collection(parent_ui, context, prop, label='Collection')`

Perform toggle collection.

## `armor_material_panel(parent_ui, props, materials, section)`

Perform armor material panel.

## `PT_Main`

Represents a UI panel within the 3D Viewport for SACR configuration.

This class defines a custom UI panel in Blender's 3D Viewport. The panel is
categorized under "SACR Config". It includes a poll method to check whether
the active object meets specific criteria before displaying the panel.

Attributes:
    bl_category: Specifies the label for the panel's tab in the UI.
    bl_space_type: Specifies the Blender editor type where the panel will appear.
    bl_region_type: Specifies the region of the editor where the panel will be located.

Methods:
    poll(cls, context):
        Determines whether the panel should be displayed based on the context.

### `bl_label`

### `bl_order`

### `bl_idname`

### `draw(self, context)`

Draw this UI element for the current Blender context.

## `panel_arms(parent_ui, panel_helper, props)`

Perform panel arms.

## `panel_legs(panel_ui, panel_helper, props)`

Perform panel legs.

## `register()`

Register this module's Blender classes.

## `unregister()`

Unregister this module's Blender classes.
