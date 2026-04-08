from . import PANEL_get_online_permission

modules = [
    PANEL_get_online_permission,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()
