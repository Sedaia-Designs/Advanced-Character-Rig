"""SACR R7.5 panel modules."""

from . import collections, face, main

modules = (main, face, collections)


def register():
    """Register this module's Blender classes."""
    for module in modules:
        module.register()


def unregister():
    """Unregister this module's Blender classes."""
    for module in reversed(modules):
        module.unregister()
