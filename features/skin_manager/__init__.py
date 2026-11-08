"""Registration layer for the Skin Manager feature.

Storage lives in `core.databases.skins`, which needs no Blender.
"""

from . import menus, operators, panels

# Dependency order: menus call operators, and panels draw both.
modules = (operators, menus, panels)


def register():
    """Register this module's Blender classes."""
    for module in modules:
        module.register()


def unregister():
    """Unregister this module's Blender classes."""
    for module in reversed(modules):
        module.unregister()
