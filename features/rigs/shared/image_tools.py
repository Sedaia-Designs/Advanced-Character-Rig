# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Generic Blender image helpers and operators."""

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from ....core.blender import is_packed
from ....core.ids import ID


def pack_img(name):
    image = get_img(name)
    if is_packed(image):
        if bpy.data.is_saved:
            image.unpack()
        else:
            image.unpack(method="USE_LOCAL")
    else:
        image.pack()


def get_img(path):
    return bpy.data.images[path]


def reload_img(name):
    get_img(name).reload()




class IMAGE_pack(Operator):
    bl_label = ""
    bl_idname = ID("image_pack").operator_for("UTIL")
    bl_options = {"REGISTER", "UNDO"}

    path: StringProperty()

    def execute(self, context):
        pack_img(self.path)
        return {"FINISHED"}


class IMAGE_reload(Operator):
    bl_label = ""
    bl_idname = ID("image_reload").operator_for("UTIL")
    bl_options = {"REGISTER", "UNDO"}

    path: StringProperty()

    def execute(self, context):
        reload_img(self.path)
        return {"FINISHED"}
