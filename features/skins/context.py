"""Blender context validation shared by skin panels and operators."""

from .constants import UTILITY_BONE_NAME


def skin_metadata(context):
    """Return the skin configuration pose bone, or ``None`` when unavailable."""
    obj = getattr(context, "active_object", None)
    if obj is None or obj.type != "ARMATURE" or obj.pose is None:
        return None
    return obj.pose.bones.get(UTILITY_BONE_NAME)


def has_skin_metadata(context):
    """Return whether skin metadata."""
    return skin_metadata(context) is not None
