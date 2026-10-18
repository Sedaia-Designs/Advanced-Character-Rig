"""Stable Blender IDs and rig metadata used by the skin feature."""

from ...core.ids import ID


UTILITY_BONE_NAME = "Sedaia.Skin_Utility_Config"
PLAYER_DATA_SUFFIX = "_Data.json"
REQUEST_TIMEOUT_SECONDS = 15
MOJANG_URLS = {
    "api": "https://api.mojang.com/users/profiles/minecraft/",
    "profile": "https://sessionserver.mojang.com/session/minecraft/profile/",
}
OPS = {
    "router": ID("skin_router").operator_for("UTIL"),
    "get": ID("skin_get").operator_for("UTIL"),
    "add": ID("skin_add").operator_for("UTIL"),
    "load": ID("skin_load").operator_for("UTIL"),
    "purge": ID("skin_purge").operator_for("UTIL"),
}
MENUS = {
    "regen": ID("skin_regen").menu_for("UTIL"),
    "purge": ID("skin_purge").menu_for("UTIL"),
}
PANEL_ID = ID("skin_utility_ui").panel_for("MAIN")
