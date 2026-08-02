from . import OT_toggle_collection

modules = [
    OT_toggle_collection,
]

def register():
    for m in modules:
        m.register()
        
def unregister():
    for m in reversed(modules):
        m.unregister()