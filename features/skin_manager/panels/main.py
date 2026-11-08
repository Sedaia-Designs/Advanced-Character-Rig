"""The Skin Manager sidebar panel and its Saved Skins sub-panel.

Laid out after the legacy "Skin Utility" panel: the username, *Change Skin*
and *Player Data* buttons, then the rig's sync options. While a background
download runs, a progress bar replaces the buttons.
"""

import os
import sqlite3

import bpy.types as T

from ....core.skin_manager import sync_progress
from ....core.skin_targets import registry as skin_targets
from ....operators.constants import OperatorID as SharedOperatorID
from ....preferences.access import database_path, storage_dir
from ....preferences.constants import StorageDir
from ..operators.base import REPORTED_ERRORS, build_manager
from ..operators.constants import OperatorID
from .constants import CATEGORY, PanelID


class SkinPanel:
    """Placement and `poll` shared by the Skin Manager panels."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY

    @classmethod
    def poll(cls, context):
        """Same check as the operators: a rig whose feature registered a skin target."""
        return skin_targets.for_rig(context.active_object) is not None


class PT_SkinManager(SkinPanel, T.Panel):
    bl_idname = PanelID.MAIN
    bl_label = "Skin Manager"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        rig = context.active_object
        target = skin_targets.for_rig(rig)
        if target is None:
            return
        bones = rig.pose.bones

        settings = bones.get(target.username.bone)
        if settings is None:
            layout.label(text=f"Missing bone '{target.username.bone}'", icon="ERROR")
            return

        layout.label(text="Minecraft Username")
        col = layout.column(align=True)
        col.prop(settings, f'["{target.username.key}"]', text="")
        if sync_progress.running:
            col.progress(factor=sync_progress.fraction, type="BAR", text=sync_progress.text)
            layout.label(text="Press Esc to cancel", icon="INFO")
        else:
            row = col.row(align=True)
            row.operator(OperatorID.ROUTER, text="Change Skin", icon="URL")
            row.operator(SharedOperatorID.FILE_OPEN, text="Player Data", icon="FILEBROWSER").path = (
                storage_dir(StorageDir.PLAYER_DATA)
            )

        options = []
        if target.arm_type is not None:
            options.append((target.arm_type.toggle, "Sync Arm Type"))
        if target.sync_name is not None:
            options.append((target.sync_name, "Set Rig Name to Username"))
        if options:
            layout.separator(type="LINE")
            layout.label(text="Options")
            col = layout.column()
            for prop, text in options:
                bone = bones.get(prop.bone)
                if bone is None:
                    col.label(text=f"Missing bone '{prop.bone}'", icon="ERROR")
                else:
                    col.prop(bone, f'["{prop.key}"]', text=text)


# Last history read, reused until the username or the database file changes,
# so the sub-panel does not query SQLite on every redraw.
_history_cache: dict = {"key": None, "rows": [], "error": ""}


def _database_stamp() -> int:
    """Return the database file's modification time, which changes on every commit."""
    try:
        return os.stat(database_path()).st_mtime_ns
    except OSError:
        return 0


def saved_skin_rows(username: str) -> tuple[list[tuple[int, str, str, bool]], str]:
    """Return ``(index, model, date, file exists)`` rows, newest first, and an error message.

    Read from the database only when `username` or the database changed.
    """
    key = (username.strip().lower(), _database_stamp())
    if _history_cache["key"] != key:
        rows, error = [], ""
        try:
            manager = build_manager()
            for skin in manager.saved_skins(username):
                exists = manager.skin_path(skin).is_file()
                rows.append((skin.index, skin.model.value, skin.added_at[:10], exists))
        except (*REPORTED_ERRORS, sqlite3.Error) as caught:
            error = str(caught)
        _history_cache.update(key=key, rows=rows, error=error)
    return _history_cache["rows"], _history_cache["error"]


def clear_history_cache() -> None:
    """Forget the cached history, such as on unregister."""
    _history_cache.update(key=None, rows=[], error="")


class PT_SkinHistory(SkinPanel, T.Panel):
    bl_idname = PanelID.HISTORY
    bl_label = "Saved Skins"
    bl_parent_id = PanelID.MAIN
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        rig = context.active_object
        target = skin_targets.for_rig(rig)
        settings = rig.pose.bones.get(target.username.bone) if target is not None else None
        username = str(settings.get(target.username.key, "")).strip() if settings is not None else ""
        if not username:
            layout.label(text="Enter a username to see saved skins")
            return

        rows, error = saved_skin_rows(username)
        if error:
            layout.label(text="Could not read saved skins", icon="ERROR")
            layout.label(text=error)
            return
        if not rows:
            layout.label(text=f"No skins saved for {username}")
            return

        col = layout.column(align=True)
        for index, model, date, exists in rows:
            row = col.row(align=True)
            row.label(text=f"#{index}   {date}   {model.title()}", icon="BLANK1" if exists else "ERROR")
            load = row.row(align=True)
            load.enabled = exists
            load.operator(OperatorID.LOAD, text="Load", icon="IMPORT").index = index
        if not all(exists for *_, exists in rows):
            layout.label(text="Missing files can't be loaded. Check for New Skin restores the current skin", icon="INFO")


classes = (PT_SkinManager, PT_SkinHistory)
