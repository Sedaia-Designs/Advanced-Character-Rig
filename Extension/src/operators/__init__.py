from . import OT_toggle_collection
from . import OT_pack_image
from . import OT_reload_image
from . import OT_set_name

modules = [
    OT_toggle_collection,
    OT_pack_image,
    OT_reload_image,
    OT_set_name,
]

def register():
    for m in modules:
        m.register()
        
def unregister():
    for m in reversed(modules):
        m.unregister()
