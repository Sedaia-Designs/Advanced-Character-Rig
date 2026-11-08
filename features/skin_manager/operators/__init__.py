"""Registration layer for the Skin Manager operators."""

from bpy.utils import register_class, unregister_class

from .add import classes as add_classes
from .import_legacy import classes as import_legacy_classes
from .load import classes as load_classes
from .purge import classes as purge_classes
from .router import classes as router_classes

classes = (
    *load_classes,
    *add_classes,
    *purge_classes,
    *router_classes,
    *import_legacy_classes,
)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
