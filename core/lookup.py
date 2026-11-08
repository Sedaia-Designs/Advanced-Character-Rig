"""Name-based lookups over collections of named items."""

import re

# Blender's suffix for a duplicate name, such as `.001` in `Hidden Objects.001`.
_DUPLICATE_SUFFIX = re.compile(r"\.\d{3,}$")


def lookup_name(bl_list, query: str):
    """Return the first item in `bl_list` whose `name` contains `query`, or None."""
    return next((item for item in bl_list if query in item.name), None)


def base_name(name: str) -> str:
    """Return `name` without Blender's duplicate suffix: `Hidden Objects.001` -> `Hidden Objects`.

    Only a trailing dot and three or more digits count, so names with other
    dots, such as `Default - SACR R7.5.0`, are kept whole.
    """
    return _DUPLICATE_SUFFIX.sub("", name)
