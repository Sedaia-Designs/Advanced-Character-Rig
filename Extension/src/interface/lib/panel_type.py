import bpy.types as T



class SACR_Panel(T.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SACR R7.5"

    @classmethod
    def poll(self, context):
        rig_id = "SACR.Rev_7.UI_3"
        prop_name = "rigID"

        try:
            r = context.active_object
            if r and r.type == "ARMATURE" and r.data:
                rData = r.data
                return rData[prop_name] == rig_id
            else:
                return False
        except (AttributeError, KeyError, TypeError):
            return False
