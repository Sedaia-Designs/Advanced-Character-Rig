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

if "sacr_r741" in locals():
    reload(sacr_r741)
else:
    from .sedaia_ui import SACR_R7_UI2 as sacr_r741


if "sacr_r750" in locals():
    reload(sacr_r750)
else:
    from .sedaia_ui import SACR_R7_UI3 as sacr_r750


modules = (prefs, skin_ui, skin_api, sacr_r741, sacr_r750)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
