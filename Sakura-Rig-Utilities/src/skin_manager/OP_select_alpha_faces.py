# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from ..preferences import Prefixer
from .lib import skin_utils as lib
from typing import Dict

class OP_select_alpha_faces(bpy.types.Operator):
    """
    Select or delete transparent UV faces of a mesh

    Feature's code is largely lifted from MCPrep, repo can be found here https://github.com/Moo-Ack-Productions/MCprep#
    Changes Made:
    - Changed idname to use the Prefixer class, so that the feature doesn't conflict with MCPrep if both are installed.
    - Adjusted bpy calls to use single character calls, as opposed to full module names for applicable calls.
        - Ex: bpy.ops changed to O, bpy.props changed to P, etc.
    - Replaced all `env` calls with self.report where appropriate, otherwise removed.
    """
    bl_idname = Prefixer("select_alpha_faces").operator
    bl_label = "Select alpha faces"
    bl_description = "Select or delete transparent UV faces of a mesh"
    bl_options = {'REGISTER', 'UNDO'}

    delete: P.BoolProperty(
        name="Delete faces",
        description="Delete detected transparent mesh faces",
        default=False)
    threshold: P.FloatProperty(
        name="Threshold",
        description="How transparent pixels need to be to select",
        default=0.2,
        min=0.0,
        max=1.0)
    skipUsage: P.BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):

        ob = context.object
        if ob is None:
            self.report({"ERROR"}, "No active object found")
            return {"CANCELLED"}
        elif ob.type != 'MESH':
            self.report({"ERROR"}, "Active object must be a mesh")
            return {"CANCELLED"}
        elif not ob.data.polygons:
            self.report({"WARNING"}, "Active object has no faces")
            return {"CANCELLED"}
        elif not ob.material_slots:
            self.report({"ERROR"}, "Active object has no materials to check image for.")
            return {"CANCELLED"}
        if ob.data.uv_layers.active is None:
            self.report({"ERROR"}, "No active UV map found")

        # if doing multiple objects, iterate over loop of this function
        bpy.ops.mesh.select_mode(type='FACE')

        # UV data only available in object mode, have to switch there and back
        bpy.ops.object.mode_set(mode="OBJECT")
        ret = self.select_alpha(ob, self.threshold)
        bpy.ops.object.mode_set(mode="EDIT")
        if ret:
            self.report({"ERROR"}, ret)
            return {"CANCELLED"}

        if not ret and self.delete:
            bpy.ops.mesh.delete(type='FACE')

        return {"FINISHED"}

    def select_alpha(self, ob, threshold):
        """Core function to select alpha faces based on active material/image."""
        if not ob.material_slots:
            self.report({"ERROR"}, "No materials, skipping.")
            return "No materials"
        print("DEBUG: ", ob.material_slots)
        # pre-cache the materials and their respective images for comparing
        textures = []
        for index, mat_slot in enumerate(ob.material_slots):
            print("DEBUG: index", index, "|", mat_slot)
            mat = mat_slot.material
            if not mat:
                textures.append(None)
                continue
            try:
                tex_passes = self.get_textures(mat)
                image = tex_passes.get("diffuse")
            except Exception as e:
                self.report({"WARNING"}, f"Error getting textures for material {mat.name}: {e}")
                image = None

            if not image:
                textures.append(None)
                continue
            elif image.channels != 4:
                textures.append(None)  # no alpha channel anyways
                continue
            
            # Ensure pixels are loaded
            if not image.pixels:
                textures.append(None)
                continue

            textures.append(image)
        data = [None for tex in textures]

        uv = ob.data.uv_layers.active
        if not uv:
            self.report({"ERROR"}, "No active UV map found")
            return "No active UV map found"

        for f in ob.data.polygons:
            if len(f.loop_indices) < 3:
                continue  # don't select edges or vertices
            fnd = f.material_index
            if fnd >= len(textures) or fnd < 0:
                continue

            image = textures[fnd]
            if not image:
                # If no image found for this face's material, don't fail entire op, just skip face
                continue

            # lazy load alpha part of image to memory, hold for whole operator
            if not data[fnd]:
                try:
                    data[fnd] = list(image.pixels)[3::4]
                except Exception as e:
                    self.report({"ERROR"}, f"Failed to load pixels for {image.name}: {e}")
                    textures[fnd] = None # Mark as failed so we don't try again
                    continue

            # relate the polygon to the UV layer to the image coordinates
            shape = []
            for i in f.loop_indices:
                try:
                    loop = ob.data.loops[i]
                    x = uv.data[loop.index].uv[0] % 1  # TODO: fix this wraparound hack
                    y = uv.data[loop.index].uv[1] % 1
                    shape.append((x, y))
                except IndexError:
                    continue

            # could just do "the closest" pixel... but better is weighted area
            if not shape:
                continue

            try:
                xlist, ylist = tuple([list(tup) for tup in zip(*shape)])
                # not sure if I actually want to +0.5 to the values to get middle..
                xmin = round(min(xlist) * image.size[0]) - 0.5
                xmax = round(max(xlist) * image.size[0]) - 0.5
                ymin = round(min(ylist) * image.size[1]) - 0.5
                ymax = round(max(ylist) * image.size[1]) - 0.5
            except (ValueError, TypeError):
                continue

            # assuming faces are roughly rectangular, sum pixels a face covers
            asum = 0
            acount = 0
            for row in range(image.size[1]):
                if row < ymin or row > ymax:
                    continue
                for col in range(image.size[0]):
                    if col >= xmin and col <= xmax:
                        try:
                            asum += data[fnd][image.size[0] * row + col]
                            acount += 1
                        except IndexError:
                            pass

            if acount == 0:
                acount = 1
            ratio = float(asum) / float(acount)
            if ratio < float(threshold):
                f.select = True
            else:
                f.select = False
        return

    @staticmethod
    def get_textures(material: T.Material) -> Dict[str, T.Image]:
        """Extract the image datablocks for a given material (prefer cycles).

        Returns {"diffuse":texture.image, "normal":node.image "spec":None, ...}
        """
        passes = {
            "diffuse": None, "specular": None, "normal": None, "displace": None}

        if not material:
            return passes

        # first try cycles materials, fall back to internal if not present
        if material.use_nodes is True:
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    if not passes["diffuse"]:
                        passes["diffuse"] = node.image

        # look through internal, unless already found main diffuse pass
        # TODO: Consider checking more explicitly checking based on selected engine
        if hasattr(material, "texture_slots") and not passes["diffuse"]:
            for sl in material.texture_slots:
                if not (sl and sl.use and sl.texture is not None
                        and hasattr(sl.texture, "image")
                        and sl.texture.image is not None):
                    continue
                if sl.use_map_color_diffuse and passes["diffuse"] is None:
                    passes["diffuse"] = sl.texture.image
                elif sl.use_map_normal and passes["normal"] is None:
                    passes["normal"] = sl.texture.image
                elif sl.use_map_specular and passes["specular"] is None:
                    passes["specular"] = sl.texture.image
                elif sl.use_map_displacement and passes["displace"] is None:
                    passes["displace"] = sl.texture.image

        return passes


# Registering
def register():
    U.register_class(OP_select_alpha_faces)


def unregister():
    U.unregister_class(OP_select_alpha_faces)


if __name__ == "__main__":
    register()
