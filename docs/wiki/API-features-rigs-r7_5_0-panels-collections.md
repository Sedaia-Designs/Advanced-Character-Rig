# `features.rigs.r7_5_0.panels.collections`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

## `PT_Collections`

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

### `bl_idname`

### `bl_order`

### `draw`

```python
draw(self, context)
```

Draw this UI element for the current Blender context.

## `register`

```python
register()
```

Register this module's Blender classes.

## `unregister`

```python
unregister()
```

Unregister this module's Blender classes.
