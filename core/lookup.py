"""Name-based lookups over collections of named items."""


def lookup_name(bl_list, query: str):
    """Return the first item in `bl_list` whose `name` contains `query`, or None."""
    return next((item for item in bl_list if query in item.name), None)
