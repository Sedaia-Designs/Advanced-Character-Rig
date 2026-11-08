"""Import player files written by the legacy skin utility."""

from pathlib import Path

import bpy.props as P
import bpy.types as T

from ....core.skin_manager import LEGACY_GLOB
from ....preferences.access import storage_dir
from ....preferences.constants import StorageDir
from .base import REPORTED_ERRORS, build_manager
from .constants import OperatorID

# How many failed files are listed individually before the rest are counted.
MAX_LISTED_FAILURES = 5


class SkinImportLegacy(T.Operator):
    """Import legacy <name>/<name>_Data.json player files into the Skin Manager database"""

    bl_idname = OperatorID.IMPORT_LEGACY
    bl_label = "Import Legacy Player Data"
    bl_options = {"REGISTER"}

    # No rig poll: the import touches only the database, and it is run from
    # the preferences, where the active object may not be a rig.

    directory: P.StringProperty(
        name="Folder",
        description="Legacy player data folder that holds one subfolder per player",
        subtype="DIR_PATH",
    )

    def invoke(self, context, event):
        if not self.directory:
            self.directory = storage_dir(StorageDir.PLAYER_DATA)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        folder = self.directory or storage_dir(StorageDir.PLAYER_DATA)
        try:
            report = build_manager().import_legacy_dir(Path(folder))
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        if not report.imported and not report.failed:
            self.report({"WARNING"}, f"No legacy player files ({LEGACY_GLOB}) found in {folder}")
            return {"CANCELLED"}
        for file, reason in report.failed[:MAX_LISTED_FAILURES]:
            self.report({"WARNING"}, f"Skipped {file.name}: {reason}")
        hidden = len(report.failed) - MAX_LISTED_FAILURES
        if hidden > 0:
            self.report({"WARNING"}, f"Skipped {hidden} more files")
        self.report(
            {"INFO"}, f"Imported {len(report.imported)} players, skipped {len(report.failed)} files"
        )
        return {"FINISHED"}


classes = (SkinImportLegacy,)
