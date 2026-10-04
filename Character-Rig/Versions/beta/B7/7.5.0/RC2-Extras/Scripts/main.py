import bpy
import bpy.types as T
import bpy.ops as O
import bpy.props as P
import bpy.utils as U

bl_info = {
    "name": "SACR R7 UI Dev",
    "author": "Sakura Sedaia <sakusedaia@outlook.com>",
    "category": "Interface",
    "version": (3, 0, 0),
    "blender": (5, 1, 0),
    "location": "View 3D > Tool Window (N) > SACR R7.5"
}

feature_set_enum = {
    0: "Standard",
    1: "Lite",
    2: "Python"
}

#
# Here is a list of features changed when the rig is set to Lite
# - Long hair Rig Removed
# - Eyelashes Removed
# - Body Lattices Removed
# - Eyesparkles
#

# Data
def enumerate_build(i):
    if i == 0:
        return "Standard"
    elif i == 1:
        return "Lite"

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

class ID(str):
    addon_id = "SEDAIA_SACR_R75"
    @property
    def panel(self):
        return f"{self.addon_id}_PT_{self}"

    @property
    def operator(self):
        return f"{self.addon_id.lower()}_ot.{self}"

    @property
    def menu(self):
        return f"{self.addon_id}_MT_{self}"

    @property
    def list(self):
        return f"{self.addon_id}_UL_{self}"


# Helper Functions
def sub_panel(ui, python, property, label: str):
    col = ui.column(align=True)
    header = col.row()
    toggle= header.column()
    toggle.scale_x = 1
    toggle.prop(
        python,
        f'["{property}"]',
        text=label,
        icon="TRIA_DOWN" if python[property] else "TRIA_RIGHT"
    )
    # title = header.column()
    # title.label(text=label)
    if python[property]:
        box = col.box()
        return box
    else:
        return None

def armor_material_panel(ui, props, materials, section):
    armor_enum = { # (Toggle Index, Material Index)
        "Helmet" : (0, 8),
        "Chestplate" : (1, 9),
        "Leggings" : (2, 10),
        "Boots" : (3, 11)
    }

    material = materials.material_slots[armor_section[1]].material.node_tree.nodes["MC Armor BSDF"]
    armor_section = armor_enum[section]
    row = ui.row(align=True)
    row.prop(props, '["Armor Toggle"]', index=armor_section[0], text=section, toggle=True)
    row2 = row.row(align=True)
    row2.enabled = props["Armor Toggle"][armor_section[0]]
    row2.prop(material.inputs["Tier"], 'default_value', text="")

    if props["Armor Toggle"][armor_section[0]]:
        mat_column = ui.box().column(align=True)
        mat_column.label(text="Material")
        input = "IOR"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Metalic"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Specular"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Roughness"
        mat_column.prop(material.inputs[input], "default_value", text=input)
        mat_column.separator(type="SPACE")
        box = mat_column.box()
        mat = material.inputs["Enchant"]
        box.prop(mat, "default_value", text="Enchanted", toggle=True, icon="CHECKBOX_HLT" if mat.default_value else "CHECKBOX_DEHLT")
        if mat.default_value:
            input = "Strength"
            box.prop(material.inputs[input], "default_value", text=input)

            input = "Glint Offset"
            box.prop(material.inputs["Location"], "default_value", text=input)

def color_table(ui, material, grid, grid_label):
    color_gradient = material.inputs[grid[4]].default_value
    color_split = material.inputs[grid[5]].default_value

    color_table = ui.column(align=True) # Container

    row = color_table.row(align=True) # Row 1
    l_col_r1 = row.row(align=True)
    l_col_r1.prop(material.inputs[grid[0]], "default_value", text=grid_label[0])

    r_col_r1 = row.row(align=True)
    r_col_r1.prop(material.inputs[grid[1]], "default_value", text=grid_label[1])
    r_col_r1.enabled=color_split

    row = color_table.row(align=True) # Row 2
    l_col_r2 = row.row(align=True)
    l_col_r2.prop(material.inputs[grid[2]], "default_value", text=grid_label[2])
    l_col_r2.enabled=color_gradient

    r_col_r2 = row.row(align=True)
    r_col_r2.prop(material.inputs[grid[3]], "default_value", text=grid_label[3])
    r_col_r2.enabled=(color_split and color_gradient)

    row = color_table.row(align=True) # Row 3
    l_col_r3 = row.row(align=True)
    l_col_r3.prop(material.inputs[grid[4]], "default_value", text=grid_label[4], toggle=True)

    r_col_r3 = row.row(align=True)
    l_col_r3.prop(material.inputs[grid[5]], "default_value", text=grid_label[5], toggle=True)

def is_packed(file):
    try:
        return file.packed_files.values() != []
    except:
        return False
    

def get_img(path):
    return bpy.data.images[path]

# Operators
class OT_toggle_collection(T.Operator):
    bl_idname = ID("toggle_collection").operator
    bl_label="Toggle Collection"

    collection : P.StringProperty()

    def execute(self, context):
        obj = context.active_object

        py_ref = obj.pose.bones["PythonReference_OBJ"]
        collection = bpy.data.collections[self.collection]

        if collection.hide_viewport == True:
            collection.hide_viewport = False
            collection.hide_render = False
        else:
            collection.hide_viewport = True
            collection.hide_render = True

        return {'FINISHED'}

class OT_set_name(T.Operator):
    bl_idname = ID("set_name").operator
    bl_label = "Set Rig Name"
    bl_options = {"REGISTER", "UNDO"}

    name: P.StringProperty()
    update_collection: P.BoolProperty()

    def execute(self, context):
        obj = context.active_object
        obj.name = self.name
        obj.data.name = self.name

        if self.update_collection is True:
            try:
                obj.users_collection[0].name = self.name
            except (AttributeError, KeyError):
                context.asset.name = self.name

        return {"FINISHED"}

class OT_pack(T.Operator):
    bl_label = ""
    bl_idname = ID("image_pack").operator
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):
        self.report({"PROPERTY"}, self.path)
        image = get_img(self.path)
        if is_packed(image):
            if bpy.data.is_saved:
                image.unpack()
            else:
                image.unpack(method="USE_LOCAL")
        else:
            image.pack()
        return {"FINISHED"}

class OT_reload(T.Operator):
    bl_label = ""
    bl_idname = ID("image_reload").operator
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):

        get_img(self.path).reload()
        return {"FINISHED"}

def toggle_collection(ui, context, prop, label="Collection"):
    
    # Panel Variables
    collection_inst = context.active_object.pose.bones["PythonReference_OBJ"].get(prop)
    inst_toggle = ui.operator(ID("toggle_collection").operator,
                              text=label,
                              depress= not collection_inst.hide_viewport,
                              icon="RESTRICT_VIEW_ON" if collection_inst.hide_viewport else "RESTRICT_VIEW_OFF"
                              )
    inst_toggle.collection = collection_inst.name


# Main UI
class PT_Main(SACR_Panel):
    bl_label="Main Panel"
    bl_order=0
    bl_idname=ID("main").panel

    def draw(self, context):
        
        # Panel Variables
        obj= context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all
        main = pose["Rig_Properties"]
        face = pose["Face_Properties"]
        eyebrow = pose["Eyebrow_Properties"]
        eyes = pose["Eye_Properties"]
        mouth = pose["Mouth_Properties"]
        python = pose["PythonReference_OBJ"]
        root = pose["SACR_Root"]
        
        feature_set = feature_set_enum[obj.data["feature_set"]]
        
        materials = python.get("MatObj")
        skin = materials.material_slots["Skin"].material.node_tree.nodes["Skin_Texture"].image
        
        # Panel Layout
        ui = self.layout
        
        if feature_set is "Python":
            ui.prop(
                collections["Python"], 
                "is_visible", 
                text="Python Config", 
                icon="PLUGIN"
            )

        ui.prop(
            root.constraints["NormalizeScale"],
            "enabled",
            text="Reset Rig Scale",
            invert_checkbox=True,
            icon="CHECKBOX_DEHLT" if root.constraints["NormalizeScale"].enabled else "CHECKBOX_HLT"
        )
        
        ui.label(text="Skin Texture")
        row = ui.row(align=True)
        row.operator(ID("image_pack").operator, icon="PACKAGE" if is_packed(
            skin) else "UGLYPACKAGE", text="").path = skin.name
        
        filepath_ui = row.row(align=True)
        filepath_ui.enabled = not is_packed(skin)
        filepath_ui.prop(skin, "filepath", text="")
        filepath_ui.operator(ID("image_reload").operator, icon="FILE_REFRESH", text="").path = skin.name
        
        row = ui.row(align=True)
        toggle_collection(row, context, prop="HatLayer", label="Show Jacket Layer")
        toggle_collection(row, context, prop="ExtrudeMeshes", label="Show Extrude Heads")

        ui.separator(type="LINE")
        
        
        ui.label(text="Extras")
        
        col = ui.column(align=True)
        col.prop(
            collections["Flip"],
            "is_visible",
            text="Flip Bone",
            toggle=True,
            icon="HIDE_OFF" if collections["Flip"].is_visible else "HIDE_ON"
        )
        
        col.prop(
            main,
            '["Wireframe Bones"]',
            toggle=True,
            icon="CHECKBOX_HLT" if main["Wireframe Bones"] else "CHECKBOX_DEHLT"    
        )
        
        col.separator(type="LINE")
        
        if feature_set is not "Lite":
            col.prop(
                main,
                '["Long Hair Rig"]',
                text="Long Hair",
                toggle=True,
                icon="HIDE_OFF" if main["Long Hair Rig"] else "HIDE_ON"
            )
            
            hair_box = col.box()
            hair_box.enabled = main["Long Hair Rig"]
            hair_box.prop(
                collections["Hair_Adv"],
                "is_visible",
                text="Hair Extra Controls",
                icon="HIDE_OFF" if collections["Hair_Adv"].is_visible else "HIDE_ON"
            )

            ui.separator(type="LINE")
            ui.label(text="Deformations")
            
            col = ui.column(align=True)
            row = col.row(align=True)
            row.prop(main, '["Show Lattices"]', index=0, text="Body Lattices",
                    icon="HIDE_OFF" if main["Show Lattices"][0] else "HIDE_ON")
            row.prop(main, '["Show Lattices"]', index=1, text="Eyelash Lattices",
                    icon="HIDE_OFF" if main["Show Lattices"][1] else "HIDE_ON")
                     
            ui.prop(main, '["Female Curves"]', text="Female Curvature")

        # Sub Panels
        
        ui.separator(type="LINE")
        
        ui.label(text="Sections")

        panel_arms(ui, python, main)
        
        ui.separator(type="LINE")
        
        panel_legs(ui, python, main)
        
        ui.separator(type="LINE")
        
        armor = sub_panel(ui, python, property="ArmorPanel", label="Armor")
        if armor:
            armor_enum = (
                "Helmet",
                "Chestplate",
                "Leggings",
                "Boots",
            )
            for item in armor_enum:
                armor_material_panel(armor, main, materials, item)

def panel_arms(ui, python, props):
    arms = sub_panel(ui, python, property="ArmPanel", label="Arms")
    if arms:
        row = arms.row()
        row.label(text="Arm Type")
        row = arms.row()
        row.prop(props, '["Arm Type"]', expand=True)

        arms.separator(type="SPACE")

        row = arms.row(align=True)
        col = row.column(align=True)
        col.label(text="Left")
        col.prop(props, '["Arm IK"]', index=0, text="IK")
        col.prop(props, '["Arm Stretch"]', index=0, text="Stretch")
        col.prop(props, '["Arm Wrist IK"]', index=0, text="Wrist IK")

        col = row.column(align=True)
        col.label(text="Right")
        col.prop(props, '["Arm IK"]', index=1, text="IK")
        col.prop(props, '["Arm Stretch"]', index=1, text="Stretch")
        col.prop(props, '["Arm Wrist IK"]', index=1, text="Wrist IK")

def panel_legs(ui, python, props):
    legs = sub_panel(ui, python, property="LegPanel", label="Legs")
    if legs:
        row = legs.row(align=True)
        col = row.column(align=True)
        col.label(text="Left")
        col.prop(props, '["Leg FK"]', index=0, text="IK")
        col.prop(props, '["Leg Stretch"]', index=0, text="Stretch")

        col = row.column(align=True)
        col.label(text="Right")
        col.prop(props, '["Leg FK"]', index=1, text="IK")
        col.prop(props, '["Leg Stretch"]', index=1, text="Stretch")

# Face Panel
class PT_Face(SACR_Panel):
    bl_idname = ID("face").panel
    bl_label = "Face Options"
    bl_order = 1
    
    def draw(self, context):
        
        # Panel Variables
        obj= context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all
        main = pose["Rig_Properties"]
        face = pose["Face_Properties"]
        eyes = pose["Eye_Properties"]
        python = pose["PythonReference_OBJ"]
        
        feature_set = feature_set_enum[obj.data["feature_set"]]
        
        materials = python.get("MatObj")
        
        # Panel Layout
        ui = self.layout
        ui.prop(main, '["Face Toggle"]', toggle=True)
        
        if main["Face Toggle"]:
            ui.separator(type="LINE")
            
            ui.prop(face, '["UV Projection"]', text="Face UV Projection", toggle=True)
            
            if feature_set is not "Lite":
                ui.prop(eyes, '["Eyelashes"]', text="Eyelash")
            
            ui.separator(type="LINE")
            
            ui.separator(type="LINE")
            panel_eyebrows(ui, pose, python, materials, collections)
            ui.separator(type="LINE")
            panel_iris(ui, pose, python, materials, collections)
            ui.separator(type="LINE")
            panel_sclera(ui, pose, python, materials, collections)
            ui.separator(type="LINE")
            panel_mouth(ui, pose, python, materials, collections)

def panel_eyebrows(ui, pose, python, materials, collections):
    props_eb = pose["Eyebrow_Properties"]
    
    panel = sub_panel(ui, python, property="EyebrowPanel", label="Eyebrows")
    if panel:
        panel.label(text="Eyebrows")
        
        
        
        col = panel.column(align=True)
        col.prop(props_eb, '["Depth"]')
        col.prop(props_eb, '["Thickness"]')
        col.prop(props_eb, '["Width"]')
        
        try:
            mat = materials.material_slots["Eye Brow"].material.node_tree.nodes["Eyebrow_Shader"]
            node = mat.inputs
            color_table(
                ui = panel,
                material = mat,
                grid = (
                    "L.Color In","R.Color In",
                    "L.Color Out","R.Color Out",
                    "Gradient","Split Color",
                ),
                grid_label = (
                    "","",
                    "","",
                    "Gradient","Separate"
                )
            )
        
            col = panel.column(heading="Reflections")
            col.prop(node["IOR"], "default_value", text="IOR")
            col.prop(node["Metalic"], "default_value", text="Specular")
            col.prop(node["Specular"], "default_value", text="Roughness")
            
            col = panel.column(heading="Coat/Sheet")
            col.prop(node["Coat IOR"], "default_value", text="IOR")
            col.prop(node["Sheen Roughness"], "default_value", text="Roughness")
            
            col = panel.column(heading="Emission")
            row = col.row()
            row.prop(node[12], "default_value", text="Emission", toggle=True)
            row2 = row.row()
            row2.enabled == node[12].default_value
            row2.prop(node[13], "default_value", text="Strength")
        except:
            pass
        

def panel_iris(ui, pose, python, materials, collections):
    eyes = pose["Eye_Properties"]
    panel = sub_panel(ui, python, property="IrisPanel", label="Iris")
    if panel:
        col = panel.column()
        col.prop(eyes, '["Iris Inset"]')
        col.prop(
            eyes,
            '["Eyesparkle"]',
            toggle=True
        )
        
        panel.separator(type="LINE")
        
        col = panel.column()
        col.label(text="Colors", icon="COLOR")
        try:
            mat = materials.material_slots["Iris"].material.node_tree.nodes["Iris_Shader"]
            color_table(
                ui = col,
                material = mat,
                grid = (
                    "Color1.L","Color1.R",
                    "Color2.L","Color2.R",
                    "Gradient","Heterochromia",
                ),
                grid_label = (
                    "","",
                    "","",
                    "Gradient","Heterochromia"
                )
            )
            col = panel.column()
            col.label(text="Reflections", icon="SHADING_RENDERED")
            col.prop(mat.inputs[7], "default_value", text="IOR")
            col.prop(mat.inputs[19], "default_value", text="Metallic")
            col.prop(mat.inputs[20], "default_value", text="Specular")
            col.prop(mat.inputs[21], "default_value", text="Roughness")

            col = panel.column(heading="Clearcoat")
            col.prop(mat.inputs[24], "default_value", text="Weight")
            col.prop(mat.inputs[25], "default_value", text="Roughness")
            col.prop(mat.inputs[26], "default_value", text="IOR")

            col = panel.column(heading="Emissions")
            col.prop(mat.inputs[31], "default_value", text="Emission", toggle=True)
            if mat.inputs[31].default_value:
                col.prop(mat.inputs[33], "default_value", text="Split", toggle=True)

                if mat.inputs[33].default_value:
                    col = panel.box().column()
                    col.label(text="Emission Strength")
                    color_table(
                        ui=col,
                        material=mat,
                        grid=(
                            36,38,
                            37,39,
                            35,34
                        ),
                        grid_label=(
                            "", "",
                            "", "",
                            "Gradient", "Heterochromia"
                        )
                    )
                else:
                    panel.prop(mat.inputs[36], "default_value", text="Strength")

            col.separator(type="LINE")
            col.prop(mat.inputs["Pupils"], "default_value", text="Pupuls", toggle=True)
            if mat.inputs["Pupils"].default_value:
                box = col.box()
                box.prop(mat.inputs[41], "default_value", text="Color")
                box.prop(mat.inputs[42], "default_value", text="Opacity")
                box.prop(mat.inputs[43], "default_value", text="Custom Texture")

                if mat.inputs[43].default_value:
                    pass
                    # Need Image Switcher setup here
                else:
                    col = box.column()
                    col.label(text="Size")
                    row = col.row(align=True)
                    row.prop(mat.inputs[45], "default_value", text="X")
                    row.prop(mat.inputs[46], "default_value", text="Y")
        except:
            pass

def panel_sclera(ui, pose, python, materials, collections):
    eyes = pose["Eye_Properties"]
    panel = sub_panel(ui, python, property="ScleraPanel", label="Scleras")
    if panel:
        panel.label(text="Settings")
        panel.prop(eyes, '["Sclera Depth"]')
        
        try:
            mat=materials.material_slots["Sclera"].material.node_tree.nodes["Sclera_Shader"]
            color_table(
                ui = panel,
                material = mat,
                grid = (
                    "Color1.L","Color1.R",
                    "Color2.L","Color2.R",
                    "Gradient","Heterochromia",
                ),
                grid_label = (
                    "","",
                    "","",
                    "Gradient","Heterochromia"
                )
            )
            
            col = panel.column(heading="Reflections")
            col.prop(mat.inputs[7], "default_value", text="IOR")
            col.prop(mat.inputs[19], "default_value", text="Metallic")
            col.prop(mat.inputs[20], "default_value", text="Specular")
            col.prop(mat.inputs[21], "default_value", text="Roughness")


            col = panel.column(heading="Clearcoat")
            col.prop(mat.inputs[24], "default_value", text="Weight")
            col.prop(mat.inputs[25], "default_value", text="Roughness")
            col.prop(mat.inputs[26], "default_value", text="IOR")


            col = panel.column(heading="Emissions")
            col.prop(mat.inputs[31], "default_value", text="Emission", toggle=True)
            if mat.inputs[31].default_value:
                col.prop(mat.inputs[33], "default_value", text="Split", toggle=True)
                if mat.inputs[33].default_value:
                    col = panel.box().column()
                    col.label(text="Emission Strength")
                    color_table(
                        ui=col,
                        material=mat,
                        grid=(
                            36,38,
                            37,39,
                            35,34
                        ),
                        grid_label=(
                            "", "",
                            "", "",
                            "Gradient", "Heterochromia"
                        )
                    )
                else:
                    panel.prop(mat.inputs[36], "default_value", text="Strength")
        except:
            pass

def panel_mouth(ui, pose, python, materials, collections):
    props = pose["Mouth_Properties"]
    panel = sub_panel(ui, python, property="MouthPanel", label="Mouth")
    if panel:
        panel.prop(props, '["Classic Mouth"]', text="Shallow Mouth", toggle=True)
        panel.prop(props, '["Square Mouth"]')
        
        try:
            mouth_inside = materials.material_slots[3].material.node_tree.nodes["Mouth BSDF"]
            teeth = materials.material_slots[4].material.node_tree.nodes["Teeth BSDF"]

            panel.prop(mouth_inside.inputs["Base Color"], "default_value", text="Mouth Inside Color")


            panel.prop(teeth.inputs["Base Color"], "default_value", text="Teeth Color")
            panel.prop(teeth.inputs["Emission"], "default_value", text="Emission Toggle", toggle=True)
            if teeth.inputs["Emission"].default_value:
                box = panel.box()
                box.prop(teeth.inputs[31], "default_value", text="Emission Color")

                box.prop(teeth.inputs[32], "default_value", text="Emission Strength")
        except:
            pass
class PT_Collections(SACR_Panel):
    bl_label = "Control Groups"
    bl_idname = ID("collections").panel
    bl_order = 2
    
    def draw(self, context):
        
        def collection(ui, group: str, name: str, toggle = True):
            ui.prop(collections[group], "is_visible", text=name, toggle=toggle)
        
        def is_on(collection: str):
            return collections[collection].is_visible
        
        def group_header(ui, group: str, label: str):
            row = ui.row()
            row.prop(
                collections[group],
                "is_visible",
                text="",
                icon="CHECKBOX_HLT" if is_on(group) else "CHECKBOX_DEHLT"
            )
            row.label(text=label)
            
        
        obj= context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all
        python = pose["PythonReference_OBJ"]
        
        ui = self.layout
        
        panel = sub_panel(ui, python, "FaceBoneColPanel", "Face")
        if panel:
            box = panel.box()
            col = box.column()
            group_header(col, "Eyebrows", "Eyebrow Controls")
            row = col.row(align=True)
            row.enabled = collections["Eyebrows"].is_visible
            col2 = row.column(align=True, heading="Left")
            c_row = col2.row(align=True)
            c_row.prop(collections["Eyebrow_Left_Simplified"], "is_visible", text="Simple", toggle=True)
            
            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eyebrow_Left_Simplified")
            c_row2.prop(collections["Eyebrow_Left_Advanced"], "is_visible", text="Advanced", toggle=True)
                
            col2 = row.column(align=True, heading="Right")
            c_row = col2.row(align=True)
            c_row.prop(collections["Eyebrow_Right_Simplified"], "is_visible", text="Simple", toggle=True)
                
            c_row2 = col2.row(align=True)
            c_row2.enabled = collections["Eyebrow_Right_Simplified"].is_visible
            c_row2.prop(collections["Eyebrow_Right_Advanced"], "is_visible", text="Advanced", toggle=True)
            
            panel.separator(type="LINE")
        
            box = panel.box()
            col = box.column()
            group_header(col, "Eyes", "Eye Controls")
            row = col.row(align=True)
            row.enabled = is_on("Eyes")
            
            col2 = row.column(align=True, heading="Left")
            c_row = col2.row(align=True)
            collection(c_row, "Eye_Left_Simplified", "Simple")
            
            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eye_Left_Simplified")
            collection(c_row2, "Eye_Left_Advanced", "Advanced")
                
            col2 = row.column(align=True, heading="Right")
            c_row = col2.row(align=True)
            collection(c_row, "Eye_Right_Simplified", "Simple")
                
            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eye_Right_Simplified")
            collection(c_row2, "Eye_Right_Advanced", "Advanced")
            
            panel.separator(type="LINE")
            
            box = panel.box()
            col = box.column()
            group_header(col, "Mouth", "Mouth Controls")
            row = col.row(align=True)
            
            row = col.row(align=True)
            row.enabled = collections["Mouth"].is_visible
            collection(row, "Mouth_Advanced", "Extra")
            
        
        ui.separator(type="LINE")
        panel = sub_panel(ui, python, "BodyBoneColPanel", "Body")
        if panel:
            col = panel.column(heading="Upper Body")
            row = col.row()
            collection(row, "Torso", "Torso")
            
            row_u = col.row(align=True)
            collection(row_u, "Arm_Left", "Left Arm")
            collection(row_u, "Arm_Right", "Right Arm")
            
            col = panel.column(heading="Lower Body")
            row_l = col.row()
            collection(row_l, "Leg_Left", "Left Leg")
            collection(row_l, "Leg_Right", "Right Leg")

classes = [
    OT_toggle_collection,
    OT_set_name,
    OT_pack,
    OT_reload,
    PT_Main,
    PT_Face,
    PT_Collections
]

def register():
    for cls in classes:
        U.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
        
if __name__ == "__main__":
    register()
