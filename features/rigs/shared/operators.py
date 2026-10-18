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

"""Shared file and rig operators used by SACR interface features."""

from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from bpy.ops import wm
from bpy.utils import extension_path_user

from .... import prefs
from ....core.ids import ID


class FILE_open(Operator):
    bl_label = "Open"
    bl_idname = ID("file_open").operator_for("UTIL")

    path: StringProperty(default=extension_path_user(prefs.bl_info["name"], create=True, path=""))

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        wm.path_open(filepath=self.path)
        return {"FINISHED"}


class RIGS_set_name(Operator):
    bl_idname = ID("rig_rename").operator_for("UTIL")
    bl_label = "Set Rig Name"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty()
    update_collection: BoolProperty()

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        obj = context.active_object
        obj.name = self.name
        obj.data.name = self.name

        if self.update_collection is True:
            try:
                obj.users_collection[0].name = self.name
            except (AttributeError, KeyError):
                context.asset.name = self.name

        return {"FINISHED"}
