"""Registration layer for complete features (rig UIs, skin management, rig management)."""

from . import SACR_R7_UI3

modules = (
    SACR_R7_UI3,
)


def register():
    """Register every feature package."""
    for module in modules:
        module.register()


def unregister():
    """Unregister every feature package."""
    for module in reversed(modules):
        module.unregister()
