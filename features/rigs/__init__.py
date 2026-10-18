"""Rig-revision feature registry."""

from . import legacy, r7_4_1, r7_5_0, shared

modules = (shared, legacy, r7_4_1, r7_5_0)


def register():
    """Register this module's Blender classes."""
    for module in modules:
        module.register()


def unregister():
    """Unregister this module's Blender classes."""
    for module in reversed(modules):
        module.unregister()
