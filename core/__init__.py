"""Blender-agnostic core logic.

Modules in this package must not import `bpy`. Blender-facing packages
(operators, panels, menus) build on top of the core, never the reverse.
"""
