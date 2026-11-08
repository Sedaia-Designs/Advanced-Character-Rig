"""Mojang API endpoints and texture host used by the Skin Manager.

Only constants live here for now. The `MojangClient` Adapter that turns
Mojang's profile JSON into project records is added in this module next; see
``docs/skin-manager-plan.md`` (Phase 1).

Pattern: none yet. Constants and enums need no pattern.
"""

from enum import StrEnum

# The only host texture URLs may point at. Texture URLs come from a server
# response, so they are checked against this before anything is downloaded.
TEXTURE_HOST = "textures.minecraft.net"


class MojangURL(StrEnum):
    """Mojang endpoints. Append a username, UUID, or texture hash."""

    PROFILES = "https://api.mojang.com/users/profiles/minecraft/"
    SESSION = "https://sessionserver.mojang.com/session/minecraft/profile/"
    TEXTURES = f"https://{TEXTURE_HOST}/texture/"
