"""Registration layer for the Skin Manager panels. Their idnames are declared in `constants.py`."""

from bpy.utils import register_class, unregister_class

from .main import classes as main_classes
from .main import clear_history_cache

# MAIN before HISTORY: a sub-panel's parent must be registered first.
classes = (*main_classes,)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes and forget the cached history."""
    for cls in reversed(classes):
        unregister_class(cls)
    clear_history_cache()
