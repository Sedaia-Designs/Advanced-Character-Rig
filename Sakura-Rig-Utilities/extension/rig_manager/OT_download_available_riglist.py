
import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from ..lib import ID, exceptions
from .lib import manifest
from ..preferences import get_preferences as prefs

class OT_download_available_riglist(T.Operator):
    """Download the SACR manifest from https://sakura-sedaia.com"""
    bl_idname = ID("download_sacr_manifest").operator
    bl_label = "Update SACR Manifest"

    download_to: P.StringProperty(name="Download To", default="")

    def execute(self, context):

        isOnlineAllowed = bpy.app.online_access

        if not isOnlineAllowed:
            self.report({"ERROR"}, "Online access is disabled")
            return {"CANCELLED"}

        # Sets the default download location if none is provided
        if self.download_to == "":
            download_to = prefs().json_data_location
        else:
            download_to = self.download_to

        try:
            # Attempt to download the manifest
            manifest.download(destination=download_to, timeout=prefs().online_access_timeout)
        except exceptions.HttpDownloadError as e:
            self.report({"ERROR"}, f"Error downloading SACR manifest: {e}")
            return {"CANCELLED"}
        except exceptions.ChecksumValidationError as e:
            self.report({"ERROR"}, f"Error validating checksum for SACR manifest: {e}")
            return {"CANCELLED"}
        except ValueError as e:
            self.report({"ERROR"}, f"Function could not run due to invalid parameter: {e}")
            return {"CANCELLED"}
        except OSError as e:
            self.report({"ERROR"}, f"A file operation error has occurred: {e}")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"An unexpected error occurred: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


def register():
    U.register_class(OT_download_available_riglist)

def unregister():
    U.unregister_class(OT_download_available_riglist)