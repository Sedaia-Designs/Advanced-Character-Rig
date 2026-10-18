"""Narrow helpers for safe access to Blender data."""

import bpy


def online_access_enabled() -> bool:
    """Return Blender's current Online Access preference."""
    return bpy.app.online_access


def is_packed(image) -> bool:
    """Return whether an image has one or more packed files."""
    return bool(getattr(image, "packed_file", None) or getattr(image, "packed_files", None))


def find_named(items, query: str):
    """Find the first item whose name contains query, if one exists."""
    return next((item for item in items if query in item.name), None)
