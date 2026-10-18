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

"""Generic file operators."""

from bpy.ops import wm
from bpy.props import StringProperty
from bpy.types import Operator
from bpy.utils import extension_path_user

from .. import prefs
from .lib import ID


class FILE_open(Operator):
    bl_label = "Open"
    bl_idname = ID("file_open").operator_for("UTIL")

    path: StringProperty(default=extension_path_user(prefs.bl_info["name"], create=True, path=""))

    def execute(self, context):
        wm.path_open(filepath=self.path)
        return {"FINISHED"}
