"""Explicit registration order for the archived SACR R7.4.1 extension."""

from importlib import reload


if "prefs" in locals():
    reload(prefs)
else:
    from . import prefs

if "skin_ui" in locals():
    reload(skin_ui)
else:
    from .sedaia_ui import SKIN_utility_ui as skin_ui

if "skin_api" in locals():
    reload(skin_api)
else:
    from .sacr_core import skin_api

if "rig_ui" in locals():
    reload(rig_ui)
else:
    from .sedaia_ui import SACR_R7_UI2 as rig_ui


modules = (prefs, skin_ui, skin_api, rig_ui)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
