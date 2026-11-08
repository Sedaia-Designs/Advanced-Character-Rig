"""Blender glue shared by every Skin Manager operator.

This is factored out because all five operators truly need the same
things, not to save a few lines:

- the same `poll`, so they appear only on rigs with a registered skin target
- the same lookup of the rig's target, settings bone, and username, with the
  same error reports when a bone is missing
- the same `SkinManager`, built from the extension's database and storage
  folders
- the same refusal to start a second sync while a background one runs

Skin application stays in `load.py`, the only operator that applies a skin.
"""

import sys
from pathlib import Path

import addon_utils
import bpy
import bpy.types as T

from ....core.databases.schema import SchemaVersionError
from ....core.mojang import MojangClient, MojangFormatError
from ....constants import ADDON_PACKAGE, StorageDir
from ....core.network import DEFAULT_USER_AGENT, HTTPClient, NetworkError
from ....core.skin_manager import SkinManager, SkinManagerError, sync_progress
from ....core.skin_targets import SkinTarget
from ....core.skin_targets import registry as skin_targets
from ....preferences.access import database, storage_dir

# The only errors an operator reports to the user. Anything else is a
# programming error and should surface as a traceback.
REPORTED_ERRORS = (NetworkError, MojangFormatError, SkinManagerError, SchemaVersionError, OSError)

OFFLINE_MESSAGE = "Online Access is off. Enable it in Preferences > System to download skins"


def user_agent() -> str:
    """Return the HTTP user agent, for example ``SakuraCharacterRig/4.0.0``.

    The version comes from the manifest Blender parsed when it loaded the
    extension, so the extension never reads the manifest itself.
    """
    version = addon_utils.module_bl_info(sys.modules[ADDON_PACKAGE]).get("version")
    if not version:
        return DEFAULT_USER_AGENT
    return f"{DEFAULT_USER_AGENT}/{'.'.join(str(part) for part in version)}"


def build_manager() -> SkinManager:
    """Return a `SkinManager` on the extension's database and player data folders.

    Call this on the main thread. Every path is resolved here with `bpy`, so
    the manager can then run on a worker thread without touching `bpy`.
    """
    http = HTTPClient().set_user_agent(user_agent())
    return SkinManager(
        database().session,
        MojangClient(http),
        Path(storage_dir(StorageDir.PLAYER_DATA)),
        # Not created until a purge with backup needs it.
        Path(storage_dir()) / StorageDir.PLAYER_DATA_PURGED,
    )


def call_operator(caller: T.Operator, idname: str, exec_context: str = "EXEC_DEFAULT", **properties) -> bool:
    """Run another operator by its full idname and return whether it finished or started.

    Pass ``exec_context="INVOKE_DEFAULT"`` to start a modal operator, which
    counts as success once it is running.

    When an operator reports an error, ``bpy.ops`` raises `RuntimeError` in the
    caller instead of returning ``{"CANCELLED"}``. That message is reported
    again through `caller`, so it reaches the user instead of a traceback.
    """
    module, name = idname.split(".")
    try:
        result = getattr(getattr(bpy.ops, module), name)(exec_context, **properties)
    except RuntimeError as error:
        caller.report({"ERROR"}, str(error).removeprefix("Error: ").strip())
        return False
    return bool(result & {"FINISHED", "RUNNING_MODAL"})


class SkinOperator:
    """Mixin for operators that work on the active rig's skin target.

    List it before `bpy.types.Operator`. It calls `self.report`, which the
    operator provides. Operators that start a download set
    `blocked_while_syncing`, so they are disabled while a background sync runs.
    """

    blocked_while_syncing = False

    @classmethod
    def poll(cls, context):
        """Only run on a rig whose feature registered a Skin Manager target."""
        if cls.blocked_while_syncing and sync_progress.running:
            cls.poll_message_set(f"Wait for the current download to finish: {sync_progress.text}")
            return False
        return skin_targets.for_rig(context.active_object) is not None

    def rig_target(self, context) -> tuple[T.Object, SkinTarget] | None:
        """Return the active rig and its target, or report an error and return `None`."""
        rig = context.active_object
        target = skin_targets.for_rig(rig)
        if target is None:
            self.report({"ERROR"}, "The active object is not a rig the Skin Manager supports")
            return None
        return rig, target

    def bone(self, rig: T.Object, target: SkinTarget, name: str) -> T.PoseBone | None:
        """Return pose bone `name`, or report it missing and return `None`."""
        bone = rig.pose.bones.get(name)
        if bone is None:
            self.report({"ERROR"}, f"{target.label} rig is missing its '{name}' bone")
        return bone

    def username(self, rig: T.Object, target: SkinTarget) -> str | None:
        """Return the username stored on the rig, or report an error and return `None`."""
        settings = self.bone(rig, target, target.username.bone)
        if settings is None:
            return None
        username = str(settings.get(target.username.key, "")).strip()
        if not username:
            self.report({"ERROR"}, "Enter a Minecraft Java Edition username first")
            return None
        return username
