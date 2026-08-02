from importlib import reload

if "preferences" in locals():
    reload(preferences)
else:
    from . import preferences

if "operators" in locals():
    reload(operators)
else:
    from . import operators

if "rig_manager" in locals():
    reload(rig_manager)
else:
    from . import rig_manager

if "interface" in locals():
    reload(interface)
else:
    from . import interface

module = (
    preferences,
    operators,
    interface,
)

def register():
    for m in module:
        m.register()

def unregister():
    for m in reversed(module):
        m.unregister()

def reload_rig():
    for m in module:
        reload(m)