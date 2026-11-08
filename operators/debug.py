"""Copy a debug report for bug reports and support chats.

The report lists the extension, the active rig, Blender, the render engine,
the database, Python, and the operating system. It is formatted by
`core.debug_info` and holds no paths or personal data.
"""

import os
import platform
import sqlite3
import sys
from pathlib import Path

import addon_utils
import bpy
import bpy.types as T

from ..constants import ADDON_PACKAGE, EXTENSION_DIR
from ..core.databases.schema import schema_versions
from ..core.debug_info import UNKNOWN, format_report, manifest_version, text, version_text
from ..core.skin_targets import registry as skin_targets
from ..preferences.access import database_path
from .constants import OperatorID

MANIFEST_FILE = EXTENSION_DIR / "blender_manifest.toml"

# Armature data property that holds the rig's own version, such as "7.5.0".
RIG_VERSION_PROPERTY = "rig_version"


def extension_section() -> dict[str, object]:
    """The extension's name and exact version."""
    info = addon_utils.module_bl_info(sys.modules[ADDON_PACKAGE])
    try:
        version = manifest_version(MANIFEST_FILE.read_text(encoding="utf-8"))
    except OSError:
        version = None
    return {
        "name": info.get("name", UNKNOWN),
        "version": version or version_text(info.get("version")),
    }


def rig_section(obj) -> dict[str, object]:
    """The active object's rig, or a note that no supported rig is active."""
    if obj is None or obj.type != "ARMATURE":
        return {"active": "no armature selected"}
    target = skin_targets.for_rig(obj)
    data = obj.data
    return {
        "rig": target.label if target else "not a supported rig",
        "rig id": text(data.get(target.rig_id_property)) if target else UNKNOWN,
        "rig version": text(data.get(RIG_VERSION_PROPERTY)),
    }


def blender_section() -> dict[str, object]:
    """The Blender build and its relevant settings."""
    app = bpy.app
    return {
        "version": app.version_string,
        "cycle": app.version_cycle,
        "build": f"{text(app.build_hash)} ({text(app.build_branch)}, {text(app.build_date)})",
        "portable": app.portable,
        "online access": app.online_access,
    }


def render_section(scene) -> dict[str, object]:
    """The scene's render engine, and its Cycles device when it uses Cycles."""
    engine = scene.render.engine
    section: dict[str, object] = {"engine": engine}
    if engine == "CYCLES":
        section["cycles device"] = scene.cycles.device
        # Blender 5.2 removed the Experimental feature set; older builds still have it.
        feature_set = getattr(scene.cycles, "feature_set", None)
        if feature_set is not None:
            section["cycles feature set"] = feature_set
    return section


def database_section() -> dict[str, object]:
    """The SQLite library version and the extension database's schema versions.

    The database is opened read-only, so copying debug info never creates it.
    """
    section: dict[str, object] = {"sqlite": sqlite3.sqlite_version}
    path = Path(database_path())
    if not path.exists():
        section["schemas"] = "no database yet"
        return section
    try:
        with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as conn:
            section["schemas"] = schema_versions(conn) or "none"
    except sqlite3.Error as error:
        section["schemas"] = f"unreadable ({error.__class__.__name__})"
    return section


class DEBUG_copy_info(T.Operator):
    """Copy the extension, rig, Blender, and system versions for a bug report"""

    bl_idname = OperatorID.DEBUG_COPY_INFO
    bl_label = "Copy Debug Info"

    def execute(self, context):
        uname = platform.uname()
        report = format_report({
            "extension": extension_section(),
            "rig": rig_section(context.active_object),
            "blender": blender_section(),
            "render": render_section(context.scene),
            "database": database_section(),
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
            },
            "system": {
                "os": f"{uname.system} {uname.release}",
                "arch": uname.machine,
                "cpu count": os.cpu_count(),
            },
        })
        context.window_manager.clipboard = report
        print(report)
        self.report({"INFO"}, "Copied debug info to the clipboard")
        return {"FINISHED"}


classes = (
    DEBUG_copy_info,
)
