
from . import (
    PANEL_skins,
    OP_download_skin,
    OP_apply_skin,
    OP_delete_skin,
    OP_delete_skin_texture,
    OP_refresh_skin_list,
    UI_skin_list,
    OP_open_in_viewer,
    OP_update_player,
    MT_choose_skin_source,
    OP_import_skin_file,
    OP_rename_skin
)

modules = [
    UI_skin_list,
    PANEL_skins,
    OP_download_skin,
    OP_apply_skin,
    OP_delete_skin,
    OP_delete_skin_texture,
    OP_refresh_skin_list,
    OP_open_in_viewer,
    OP_update_player,
    MT_choose_skin_source,
    OP_import_skin_file,
    OP_rename_skin
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()