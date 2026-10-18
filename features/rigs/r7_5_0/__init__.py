"""Registration for SACR R7.5.0 panels and operators."""

from . import operators, panels

modules = (operators, panels)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
