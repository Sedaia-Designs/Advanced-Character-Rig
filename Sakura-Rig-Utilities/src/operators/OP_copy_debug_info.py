import bpy
import json
import platform
from .lib.blender_utils import Prefixer
from .lib.file_utils import get_manifest_key

class OP_copy_debug_info(bpy.types.Operator):
    """Copy relevant debug information to the clipboard for support"""
    bl_idname = Prefixer("copy_debug_info").operator
    bl_label = "Copy Debug Info"
    bl_description = "Click here to copy debug information for support!"

    def execute(self, context):
        # Addon info
        addon_version = get_manifest_key("version")
        addon_release_channel = get_manifest_key("release_channel")
        addon_beta_version = get_manifest_key("beta_version")
        
        # Blender info
        blender_version = bpy.app.version
        portable = bpy.app.portable
        
        # Scene/Render info
        render_engine = context.scene.render.engine
        cycles_feature_set = "(disabled)"
        cycles_scene_device = "(disabled)"
        if render_engine == "CYCLES":
            cycles_feature_set = context.scene.cycles.feature_set
            cycles_scene_device = context.scene.cycles.device

        # System info
        os_name = str(platform.uname().system)
        arch = str(platform.uname().machine)
        os_version = str(platform.uname().release)

        information_dict = {
            "addon version": addon_version,
            "addon release": f"{addon_release_channel}",
            "addon beta": addon_beta_version,
            "blender": ".".join(map(str, blender_version)),
            "system": f"{os_name} {os_version}",
            "arch": arch,
            "portable": portable,
            "render engine": f"{render_engine}",
            "cycles feature set": f"{cycles_feature_set}",
            "cycles device": f"{cycles_scene_device}"
        }

        information_json = json.dumps(information_dict, indent=4)
        discord_pretty = f"```json\n{information_json}\n```"

        context.window_manager.clipboard = discord_pretty

        self.report({'INFO'}, "Copied relevant information to your clipboard!")

        print(information_json)
        return {"FINISHED"}

def register():
    bpy.utils.register_class(OP_copy_debug_info)

def unregister():
    bpy.utils.unregister_class(OP_copy_debug_info)
