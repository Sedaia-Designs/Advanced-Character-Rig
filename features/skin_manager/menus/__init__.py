"""Registration layer for the Skin Manager menus.

Empty for now. Import each module's `classes` here as menus are added, and
give this package a `constants.py` for their idnames.
"""

from bpy.utils import register_class, unregister_class

classes = ()


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
