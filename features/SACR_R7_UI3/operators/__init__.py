"""Registration layer for the SACR R7.5 operators."""

from bpy.utils import register_class, unregister_class

from .collections import classes as collection_classes

classes = (
    *collection_classes,
)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
