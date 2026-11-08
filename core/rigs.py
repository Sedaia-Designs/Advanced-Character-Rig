"""Rig identification checks used by rig UI `poll()` methods.

These take Blender objects as plain arguments and never import `bpy`, so they
can be tested with simple stand-in objects.
"""

from collections.abc import Container


def matches_rig_id(obj, prop: str, rig_ids: Container[str]) -> bool:
    """Return whether `obj` is an armature whose data property `prop` is one of `rig_ids`."""
    if obj is None or getattr(obj, "type", None) != "ARMATURE" or not obj.data:
        return False
    try:
        return obj.data[prop] in rig_ids
    except (KeyError, TypeError):
        return False
