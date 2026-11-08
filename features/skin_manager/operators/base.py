"""Blender glue shared by every Skin Manager operator.

This is factored out because all five operators truly need the same three
things, not to save a few lines:

- the same `poll`, so they appear only on rigs with a registered skin target
- the same lookup of the rig's target, settings bone, and username, with the
  same error reports when a bone is missing
- the same `SkinManager`, built from the extension's database and storage
  folders

Skin application stays in `load.py`, the only operator that applies a skin.
"""

from pathlib import Path

import bpy
import bpy.types as T

from ....core.databases.schema import SchemaVersionError
from ....core.mojang import MojangClient, MojangFormatError
from ....core.network import HTTPClient, NetworkError
from ....core.skin_manager import SkinManager, SkinManagerError
from ....core.skin_targets import SkinTarget
from ....core.skin_targets import registry as skin_targets
from ....preferences.access import db_session, storage_dir
from ....preferences.constants import MANIFEST, StorageDir

# The only errors an operator reports to the user. Anything else is a
# programming error and should surface as a traceback.
REPORTED_ERRORS = (NetworkError, MojangFormatError, SkinManagerError, SchemaVersionError, OSError)

OFFLINE_MESSAGE = "Online Access is off. Enable it in Preferences > System to download skins"


def build_manager() -> SkinManager:
    """Return a `SkinManager` on the extension's database and player data folders."""
    http = HTTPClient().set_user_agent(f"SakuraCharacterRig/{MANIFEST.version}")
    return SkinManager(
        db_session,
        MojangClient(http),
        Path(storage_dir(StorageDir.PLAYER_DATA)),
        # Not created until a purge with backup needs it.
        Path(storage_dir()) / StorageDir.PLAYER_DATA_PURGED,
    )


def call_operator(caller: T.Operator, idname: str, **properties) -> bool:
    """Run another operator by its full idname and return whether it finished.

    When an operator reports an error, ``bpy.ops`` raises `RuntimeError` in the
    caller instead of returning ``{"CANCELLED"}``. That message is reported
    again through `caller`, so it reaches the user instead of a traceback.
    """
    module, name = idname.split(".")
    try:
        result = getattr(getattr(bpy.ops, module), name)(**properties)
    except RuntimeError as error:
        caller.report({"ERROR"}, str(error).removeprefix("Error: ").strip())
        return False
    return "FINISHED" in result


class SkinOperator:
    """Mixin for operators that work on the active rig's skin target.

    List it before `bpy.types.Operator`. It calls `self.report`, which the
    operator provides.
    """

    @classmethod
    def poll(cls, context):
        """Only run on a rig whose feature registered a Skin Manager target."""
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
