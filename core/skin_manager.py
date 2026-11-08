"""Skin Manager workflow shared by every Skin Manager operator.

Only enums live here for now. The `SkinManager` Facade over `SkinDatabase`,
`MojangClient`, and the player data folder is added in this module next; see
``docs/skin-manager-plan.md`` (Phase 2).

Nothing here is specific to one rig. Rig names and values come from the
active rig's `core.skin_targets.SkinTarget`.

Pattern: none yet. Enums need no pattern.
"""

from enum import StrEnum


class Route(StrEnum):
    """What the Skin Manager router does with the username on the rig."""

    LOAD = "load"  # Stored locally and offline or no prompt: apply the newest stored skin.
    PROMPT = "prompt"  # Stored locally and online: ask whether to load, check for new, or purge.
    DOWNLOAD = "download"  # Not stored yet and online: download and apply.
    OFFLINE_ERROR = "offline_error"  # Not stored yet and offline: nothing can be done.
