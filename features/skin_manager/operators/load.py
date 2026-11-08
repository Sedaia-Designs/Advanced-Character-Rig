"""Apply a stored skin to the active rig, without going online."""

import bpy.props as P
import bpy.types as T

from ....core.skin_targets import SkinTarget
from ....operators.constants import OperatorID as SharedOperatorID
from .base import REPORTED_ERRORS, SkinOperator, build_manager, call_operator
from .constants import OperatorID


class SkinLoad(SkinOperator, T.Operator):
    """Apply a stored skin of the player named on the rig"""

    bl_idname = OperatorID.LOAD
    bl_label = "Load Saved Skin"
    bl_options = {"REGISTER", "UNDO"}

    index: P.IntProperty(
        name="Index",
        description="Stored skin to apply, counting from 0. -1 applies the newest",
        default=-1,
        min=-1,
    )

    def execute(self, context):
        found = self.rig_target(context)
        if found is None:
            return {"CANCELLED"}
        rig, target = found
        username = self.username(rig, target)
        if username is None:
            return {"CANCELLED"}

        # Resolve everything that can be missing before changing anything, so
        # a broken rig never ends up with half a skin applied.
        image = self.skin_image(rig, target)
        if image is None:
            return {"CANCELLED"}
        sync = target.arm_type
        arm_bones = None
        if sync is not None:
            arm_bones = (self.bone(rig, target, sync.toggle.bone), self.bone(rig, target, sync.target.bone))
            if None in arm_bones:
                return {"CANCELLED"}
        name_bone = None
        if target.sync_name is not None:
            name_bone = self.bone(rig, target, target.sync_name.bone)
            if name_bone is None:
                return {"CANCELLED"}

        manager = build_manager()
        try:
            player = manager.find_local(username)
            if player is None:
                self.report({"ERROR"}, f"No skin is stored for {username}. Go online to download it")
                return {"CANCELLED"}
            selection = manager.selection(player.uuid, self.index)
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        # Drop the packed copy without writing it to disk, point the image at
        # the stored file, then pack it so shared .blend files stay portable.
        if image.packed_file is not None:
            image.unpack(method="REMOVE")
        image.filepath = str(selection.path)
        image.reload()
        image.pack()

        if sync is not None and arm_bones is not None:
            toggle, arm_bone = arm_bones
            if toggle.get(sync.toggle.key):
                arm_bone[sync.target.key] = sync.value_for(selection.model)
                rig.update_tag()  # Re-evaluate drivers that read the Arm Type property.

        if target.sync_name is not None and name_bone is not None and name_bone.get(target.sync_name.key):
            if not self.rename(rig, target, player.name):
                return {"CANCELLED"}

        self.report({"INFO"}, f"Applied {player.name}'s skin ({selection.model.value} arms)")
        return {"FINISHED"}

    def skin_image(self, rig: T.Object, target: SkinTarget) -> T.Image | None:
        """Return the image the target's skin node shows, or report why it cannot be changed."""
        slot = target.skin
        bone = self.bone(rig, target, slot.material.bone)
        if bone is None:
            return None
        material = bone.get(slot.material.key)
        if not isinstance(material, T.Material) or material.node_tree is None:
            self.report({"ERROR"}, f"{target.label} rig has no skin material in '{slot.material.key}'")
            return None
        node = material.node_tree.nodes.get(slot.node)
        image = getattr(node, "image", None)
        if image is None:
            self.report({"ERROR"}, f"Skin material '{material.name}' has no image in node '{slot.node}'")
            return None
        if image.library is not None:
            self.report({"ERROR"}, f"Image '{image.name}' is linked from a library and cannot be changed")
            return None
        return image

    def rename(self, rig: T.Object, target: SkinTarget, player_name: str) -> bool:
        """Rename the rig after the player, as ``<player> - <rig label>``. Return whether it worked.

        The rig's collection is renamed too, but only when it already follows
        the ``<name> - <rig label>`` pattern, so a user's own collection is
        never renamed.
        """
        suffix = f" - {target.label}"
        collections = rig.users_collection
        update_collection = bool(collections) and collections[0].name.endswith(suffix)
        return call_operator(
            self,
            SharedOperatorID.RIG_RENAME,
            name=f"{player_name}{suffix}",
            update_collection=update_collection,
        )


classes = (SkinLoad,)
