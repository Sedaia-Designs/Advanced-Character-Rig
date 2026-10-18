"""Rig-revision feature registry."""

from . import legacy, r7_4_1, r7_5_0, shared

modules = (shared, legacy, r7_4_1, r7_5_0)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
