"""Registration layer for the operators package"""

from bpy.utils import register_class, unregister_class

from .file import classes as file_classes
from .image import classes as image_classes
from .rig import classes as rig_classes

classes = (
    *file_classes,
    *image_classes,
    *rig_classes,
)



def register():
    """Register this module's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this module's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
