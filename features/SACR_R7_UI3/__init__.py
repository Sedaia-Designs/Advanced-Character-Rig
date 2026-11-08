"""Registration layer for the SACR R7.5.0 rig UI feature.

Besides its Blender classes, the feature adds `constants.SKIN_TARGET` to the
Skin Manager's rig registry, so R7.5 rigs get the Skin Manager.
"""

from ...core.skin_targets import registry as skin_targets
from . import operators, panels
from .constants import SKIN_TARGET

modules = (operators, panels)


def register():
    """Register this module's Blender classes and its Skin Manager target."""
    for module in modules:
        module.register()
    skin_targets.register(SKIN_TARGET)


def unregister():
    """Remove this module's Skin Manager target and unregister its Blender classes."""
    skin_targets.unregister(SKIN_TARGET)
    for module in reversed(modules):
        module.unregister()
