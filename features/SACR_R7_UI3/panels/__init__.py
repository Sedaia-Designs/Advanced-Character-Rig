"""Registration layer for the SACR R7.5 panels."""

from bpy.utils import register_class, unregister_class

from .main import classes as main_classes
from .face import classes as face_classes
from .collections import classes as collection_classes
from .add_rig import classes as add_rig_classes

classes = (
    *main_classes,
    *face_classes,
    *collection_classes,
    *add_rig_classes,
)


def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
