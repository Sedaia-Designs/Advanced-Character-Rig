"""Registration layer for the Skin Manager menus. Their idnames are declared in `constants.py`."""

from bpy.utils import register_class, unregister_class

from .existing import classes as existing_classes

classes = (*existing_classes,)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
