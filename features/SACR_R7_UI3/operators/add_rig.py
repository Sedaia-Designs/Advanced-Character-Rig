"""Append a new SACR R7.5 rig from the extension's bundled rig file at the 3D Cursor."""

import bpy
import bpy.types as T

from ....constants import LIB_DIR
from ....core.lookup import base_name
from ....core.rigs import matches_rig_id
from ..constants import RigAsset, RigID
from .constants import OperatorID


def rig_file():
    """Return the path of the bundled R7.5 rig file."""
    return LIB_DIR / RigAsset.FILE


class RIG_add(T.Operator):
    """Add a new SACR R7.5 rig to the scene at the 3D Cursor"""

    bl_idname = OperatorID.ADD_RIG
    bl_label = "Add SACR Rig"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # Appending while in Edit or Pose Mode would leave the new rig unselectable.
        return context.mode == "OBJECT" and context.collection is not None

    def execute(self, context):
        path = rig_file()
        if not path.is_file():
            self.report({"ERROR"}, f"The bundled rig file {RigAsset.FILE} is missing. Reinstall the extension")
            return {"CANCELLED"}

        # The fake-bpy stubs type `load()` as returning None; it is a context manager.
        with bpy.data.libraries.load(str(path), link=False) as (source, target):  # pyright: ignore[reportGeneralTypeIssues]
            target.collections = [name for name in source.collections if name == RigAsset.COLLECTION]
        collection = target.collections[0] if target.collections else None
        if collection is None:
            self.report({"ERROR"}, f"{RigAsset.FILE} has no '{RigAsset.COLLECTION}' collection")
            return {"CANCELLED"}

        # The rig file marks the collection as an asset; the user's copy is not one.
        if collection.asset_data:
            collection.asset_clear()
        context.collection.children.link(collection)
        self.hide_helpers(context, collection)

        rigs = [
            obj for obj in collection.all_objects
            if obj.parent is None and matches_rig_id(obj, RigID.PROPERTY, (RigID.SACR_R7_5,))
        ]
        cursor = context.scene.cursor.location
        for rig in rigs:
            rig.location = rig.location + cursor

        for obj in context.selected_objects or ():
            obj.select_set(False)
        if rigs:
            rigs[0].select_set(True)
            context.view_layer.objects.active = rigs[0]

        self.report({"INFO"}, f"Added {rigs[0].name if rigs else collection.name}")
        return {"FINISHED"}

    @staticmethod
    def hide_helpers(context, collection):
        """Exclude the rig's helper collection from the view layer, as the rig file does.

        View layer settings are not appended with a collection, so without this
        the bone shapes and booleans would show in the viewport.
        """
        def find(layer):
            if layer.collection == collection:
                return layer
            return next((found for child in layer.children if (found := find(child))), None)

        layer = find(context.view_layer.layer_collection)
        if layer is None:
            return
        for child in layer.children:
            if base_name(child.collection.name) == RigAsset.HIDDEN:
                child.exclude = True


classes = (
    RIG_add,
)
