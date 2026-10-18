"""Thin Blender operator adapters for the skin feature."""

from pathlib import Path
from shutil import rmtree

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import Operator

from ... import prefs
from ...core.blender import find_named, is_packed, online_access_enabled
from . import repository, service
from .constants import MENUS, OPS
from .context import has_skin_metadata, skin_metadata


def _storage_root() -> Path:
    """Return the extension-local directory used for player data."""
    return Path(prefs.config["player_default_dir"])


class _SkinOperator(Operator):
    @classmethod
    def poll(cls, context):
        """Return whether the current Blender context supports this UI element."""
        return has_skin_metadata(context)


class SKIN_router(_SkinOperator):
    bl_idname = OPS["router"]
    bl_label = "Skin Utility Router"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        metadata = skin_metadata(context)
        username = metadata.get("Username", "").strip()
        if not username:
            self.report({"ERROR"}, "Enter a Minecraft username first.")
            return {"CANCELLED"}
        if repository.exists(_storage_root(), username):
            preferences = prefs.get_prefs()
            if online_access_enabled() and preferences and preferences.prompt_to_refresh_player_data:
                bpy.ops.wm.call_menu(name=MENUS["regen"])
            else:
                bpy.ops.sedaia_rigs_util_ot.skin_load(index=-1)
            return {"FINISHED"}
        if not online_access_enabled():
            self.report({"ERROR"}, "Enable Online Access in Preferences > System to download player data.")
            return {"CANCELLED"}
        bpy.ops.sedaia_rigs_util_ot.skin_get()
        return {"FINISHED"}


class SKIN_get(_SkinOperator):
    bl_idname = OPS["get"]
    bl_label = "Retrieve Player Data"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        username = skin_metadata(context)["Username"]
        try:
            player = service.fetch_player(username)
            data = service.download_player_textures(_storage_root(), username, player, 0)
        except service.SkinServiceError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        repository.save(_storage_root(), username, {"UUID": player.uuid, "NAME": player.name, "SKINS": [data["skin"]], "CAPES": [data["cape"]]})
        bpy.ops.sedaia_rigs_util_ot.skin_load(index=0)
        return {"FINISHED"}


class SKIN_add(_SkinOperator):
    bl_idname = OPS["add"]
    bl_label = "Add to Index"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        username = skin_metadata(context)["Username"]
        try:
            stored = repository.load(_storage_root(), username)
            player = service.fetch_player(username)
        except (OSError, ValueError, service.SkinServiceError) as exc:
            self.report({"ERROR"}, f"Could not refresh player data: {exc}")
            return {"CANCELLED"}
        if stored["SKINS"][-1]["hash"] == player.skin.texture_hash:
            self.report({"INFO"}, "Skin has not changed.")
            bpy.ops.sedaia_rigs_util_ot.skin_load(index=-1)
            return {"FINISHED"}
        try:
            data = service.download_player_textures(_storage_root(), username, player, stored["SKINS"][-1]["index"] + 1)
        except service.SkinServiceError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        stored["SKINS"].append(data["skin"])
        stored["CAPES"].append(data["cape"])
        repository.save(_storage_root(), username, stored)
        bpy.ops.sedaia_rigs_util_ot.skin_load(index=-1)
        return {"FINISHED"}


class SKIN_load(_SkinOperator):
    bl_idname = OPS["load"]
    bl_label = "Load Player Data"
    bl_options = {"REGISTER", "INTERNAL"}
    index: IntProperty(default=-1, min=-1)

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        metadata = skin_metadata(context)
        username = metadata["Username"]
        try:
            entry = repository.load(_storage_root(), username)["SKINS"][self.index]
            material_object = find_named(context.active_object.children, metadata["MatObj"])
            image = material_object.material_slots[0].material.node_tree.nodes[metadata["SkinImageNodeID"]].image
        except (KeyError, IndexError, OSError, AttributeError, TypeError) as exc:
            self.report({"ERROR"}, f"Could not load skin data: {exc}")
            return {"CANCELLED"}
        if is_packed(image):
            image.unpack(method="USE_LOCAL")
        image.filepath = entry["path"]
        image.pack()
        if metadata.get("SyncArms"):
            arm_bone = context.active_object.pose.bones[metadata["ArmPropBone"]]
            try:
                arm_bone.ArmType = entry["model"]
            except AttributeError:
                arm_bone[metadata["ArmPropName"]] = int(entry["model"])
        if metadata.get("SyncName"):
            rig_name = f"{username} - {metadata['RigName']}"
            context.active_object.name = rig_name
            context.active_object.data.name = rig_name
            context.active_object.data["Rig Name"] = rig_name
        return {"FINISHED"}


class SKIN_purge(_SkinOperator):
    bl_idname = OPS["purge"]
    bl_label = "Purge and Retrieve"
    bl_options = {"REGISTER", "INTERNAL"}
    backup: BoolProperty(default=False)
    confirm: BoolProperty(default=False)

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        source = repository.player_dir(_storage_root(), skin_metadata(context)["Username"])
        if self.backup:
            target_root = _storage_root().with_name(f"{_storage_root().name}_purge")
            target_root.mkdir(parents=True, exist_ok=True)
            target = target_root / f"{source.name}_old"
            index = 1
            while target.exists():
                target = target_root / f"{source.name}_old_{index}"
                index += 1
            source.rename(target)
        elif self.confirm:
            rmtree(source)
        else:
            return {"CANCELLED"}
        bpy.ops.sedaia_rigs_util_ot.skin_get()
        return {"FINISHED"}


classes = (SKIN_router, SKIN_get, SKIN_add, SKIN_load, SKIN_purge)
