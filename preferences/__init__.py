"""Registration layer for the extension's preferences.

`modules.py` registers this package first so other packages can read
preferences during their own registration.

Other packages read preferences through `preferences.access`, never
`preferences.addon_preferences`. The panel module imports
`operators.constants`, so importing it from an operator would be circular.
"""

from bpy.utils import register_class, unregister_class

from .addon_preferences import classes as addon_preferences_classes

classes = (
    *addon_preferences_classes,
)


def register():
    """Register this package's Blender classes."""
    for cls in classes:
        register_class(cls)


def unregister():
    """Unregister this package's Blender classes."""
    for cls in reversed(classes):
        unregister_class(cls)
