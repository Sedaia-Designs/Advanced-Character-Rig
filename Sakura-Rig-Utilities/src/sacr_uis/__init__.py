from . import (
    sacr_r7_ui1,
    sacr_r7_ui2,
)

modules = [
    sacr_r7_ui1,
    sacr_r7_ui2,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
