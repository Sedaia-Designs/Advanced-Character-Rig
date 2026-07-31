from importlib import reload

if "rig_manager" in locals():
    reload(rig_manager)
else:
    from . import rig_manager

if "preferences" in locals():
    reload(preferences)
else:
    from . import preferences

module = (
    preferences,
    rig_manager,
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