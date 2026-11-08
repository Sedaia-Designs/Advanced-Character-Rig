"""Configuration shared by the Skin Manager's type packages.

Blender idnames live in each type package's own `constants.py`.
"""

from enum import StrEnum

# Feature namespace for idnames, e.g. `sedaia_rigs_skins_ot.skin_router`.
# Changing it renames every Skin Manager idname and breaks keymaps and scripts.
NAMESPACE = "SKINS"


class MojangURL(StrEnum):
    """Mojang endpoints. Append a username, UUID, or texture hash."""

    PROFILES = "https://api.mojang.com/users/profiles/minecraft/"
    SESSION = "https://sessionserver.mojang.com/session/minecraft/profile/"
    TEXTURES = "https://textures.minecraft.net/texture/"


class ConfigBone(StrEnum):
    """Python helper bones on SACR R7.5 rigs that the Skin Manager reads."""

    ARGUMENTS = "PythonConfig.Skin"
    MATERIAL_LIB = "PythonConfig.Materials"
