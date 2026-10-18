"""Explicit registration order for supported SACR R7 interfaces."""

from importlib import reload


if "prefs" in locals():
    reload(prefs)
else:
    from . import prefs

if "skins" in locals():
    reload(skins)
else:
    from .features import skins

if "rigs" in locals():
    reload(rigs)
else:
    from .features import rigs


modules = (prefs, rigs, skins)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
