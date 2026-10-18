"""SACR R7.5 panel modules."""

from . import collections, face, main

modules = (main, face, collections)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
