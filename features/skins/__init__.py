"""Minecraft skin feature registration boundary."""

from bpy.utils import register_class, unregister_class

from .menus import classes as menu_classes
from .operators import classes as operator_classes
from .panel import classes as panel_classes


classes = (*operator_classes, *menu_classes, *panel_classes)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
