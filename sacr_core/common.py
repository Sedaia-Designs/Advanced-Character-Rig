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

"""Reusable helpers shared by skin and rig utilities."""

import json
from pathlib import Path
from urllib import error, request

import bpy


def allow_online():
    return bpy.app.online_access


def file_exists(path):
    return Path(path).exists()


def is_packed(file):
    try:
        return file.packed_files.values() != []
    except:
        return False


def lookup_name(bl_list: dict, query: str):
    for i in enumerate(bl_list):
        if query in i[1].name:
            return bl_list[i[0]]
        else:
            continue

    return None




REQUEST_TIMEOUT_SECONDS = 15


def download(url, path):
    with request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        Path(path).write_bytes(response.read())


def retrieve_json(url):
    try:
        with request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read())
    except (error.HTTPError, error.URLError, json.JSONDecodeError):
        return "http_error"
