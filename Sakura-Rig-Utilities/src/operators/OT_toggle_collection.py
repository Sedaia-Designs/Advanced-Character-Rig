import bpy.types as T
import bpy.utils as U

# Operators
class OT_toggle_collection(T.Operator):
    bl_idname = ID("toggle_collection").operator
    bl_label="Toggle Collection"

    collection : P.StringProperty()

    def execute(self, context):
        obj = context.active_object

        py_ref = obj.pose.bones["PythonConfig.Objects"]
        collection = bpy.data.collections[self.collection]

        if collection.hide_viewport == True:
            collection.hide_viewport = False
            collection.hide_render = False
        else:
            collection.hide_viewport = True
            collection.hide_render = True

        return {'FINISHED'}

def register():
    U.register_class(OT_toggle_collection)

def unregister():
    U.unregister_class(OT_toggle_collection)