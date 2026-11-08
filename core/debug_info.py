"""Build the debug report users paste into bug reports and support chats.

The operator in `operators/debug.py` collects the values from Blender and the
extension's storage, then calls `format_report` to turn them into a JSON code
block that reads well in Discord and GitHub issues.

The report never includes file paths, usernames, or other personal data, so
users can paste it in public.

Pattern: none. These are pure functions over plain values; there is no
subsystem to wrap, no options to build, and no behaviour to swap.
"""

import json
import tomllib
from collections.abc import Mapping

# Shown in place of a value that could not be read.
UNKNOWN = "unknown"


def manifest_version(text: str) -> str | None:
    """Return the `version` string from manifest TOML `text`, or `None` if it has none.

    Blender's own copy of the version is a tuple that drops the pre-release
    part (`4.0.0-beta.1` becomes `(4, 0, 0)`), so the report reads the
    manifest to show the exact build.
    """
    try:
        version = tomllib.loads(text).get("version")
    except tomllib.TOMLDecodeError:
        return None
    return version if isinstance(version, str) and version else None


def version_text(version: object) -> str:
    """Return a version for the report: `(5, 2, 2)` -> `5.2.2`, a string as is, else `unknown`."""
    if isinstance(version, str) and version:
        return version
    if isinstance(version, (tuple, list)) and version:
        return ".".join(str(part) for part in version)
    return UNKNOWN


def text(value: object) -> str:
    """Return `value` as report text, decoding bytes such as `bpy.app.build_hash`."""
    if value is None:
        return UNKNOWN
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace") or UNKNOWN
    return str(value)


def format_report(sections: Mapping[str, Mapping[str, object]]) -> str:
    """Return `sections` as an indented JSON code block for pasting into chat.

    Keys keep the order they were given in. Values that JSON cannot hold are
    written with `str()`.
    """
    body = json.dumps(sections, indent=4, default=str, ensure_ascii=False)
    return f"```json\n{body}\n```"
