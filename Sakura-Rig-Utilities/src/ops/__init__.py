from . import OP_open_directory

modules = [
    OP_open_directory,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()