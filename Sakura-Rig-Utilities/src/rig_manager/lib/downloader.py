import json
import os
import shutil
import zipfile
from shutil import copyfileobj
from urllib import request
from urllib.parse import quote
from ...lib.blender_utils import get_addon_directory
from ...lib.file_utils import ensure_directory, delete_directory
from ...preferences import get_preferences

class SacrDownloader:
    BASE_URL = "https://sakura-sedaia.com/lib"

    def __init__(self, branch_id: str):
        # "0" for stable, "1" for dev
        self.branch_id = branch_id

    def _extract_blend_from_zip(self, zip_path, extract_dir):
        """Extract only .blend files from a zip into the target directory."""
        ensure_directory(extract_dir)
        extract_root = os.path.realpath(extract_dir)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(".blend"):
                    # Flatten archive paths so .blend files are written directly under extract_dir.
                    target_name = os.path.basename(file_info.filename)
                    if not target_name:
                        continue
                    target_path = os.path.realpath(os.path.join(extract_dir, target_name))
                    # Guard against path traversal and duplicate flattened filenames.
                    if os.path.commonpath([extract_root, target_path]) != extract_root:
                        raise ValueError(
                            f"Unsafe archive entry path: {file_info.filename}"
                        )
                    if os.path.exists(target_path):
                        raise FileExistsError(
                            f"Cannot extract duplicate .blend filename: {target_name}"
                        )
                    with zip_ref.open(file_info, "r") as source_file, open(
                        target_path, "wb"
                    ) as dest_file:
                        copyfileobj(source_file, dest_file)

    def get_version_info(self, version_str: str):
        """Returns the version entry and branch info for a given version string."""
        addon_dir = get_addon_directory()
        manifest_path = addon_dir / "Manifest.json"

        if not manifest_path.exists():
            return None, None

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None, None

        sacr = manifest_data.get("SACR", {})
        branches = sacr.get("branches", {})
        branch_key = "stable" if self.branch_id == "0" else "dev"
        branch_info = branches.get(branch_key)

        if not branch_info:
            return None, None

        # Find the version
        target_version = None
        for v in branch_info.get("versions", []):
            version_value = v.get("version")
            prefixed_version = f"{'R' if branch_key == 'stable' else 'D'}{version_str}"
            if version_value == version_str or version_value == prefixed_version:
                target_version = v
                break
        
        return target_version, branch_info

    def get_download_url(self, version_str: str):
        """Calculates the download URL for a given version string."""
        target_version, branch_info = self.get_version_info(version_str)
        if not target_version or not branch_info:
            return None

        # Prioritize .zip files with a .blend fallback
        builds = target_version.get("builds", [])
        if not builds:
            return None

        build = None
        for b in builds:
            if b.get("fileName", "").lower().endswith(".zip"):
                build = b
                break
        
        if not build:
            for b in builds:
                if b.get("fileName", "").lower().endswith(".blend"):
                    build = b
                    break
        
        if not build:
            build = builds[0]

        file_name = build.get("fileName")
        branch_path = branch_info.get("path")

        if not file_name or not branch_path:
            return None

        # Keep slashes in branch path, encode file name safely for URL usage.
        encoded_branch_path = quote(branch_path.strip("/"), safe="/")
        encoded_file_name = quote(file_name, safe="")
        return f"{self.BASE_URL}/{encoded_branch_path}/{encoded_file_name}"

    @staticmethod
    def download_manifest(progress_callback=None):
        """Download the manifest from the remote server."""
        def reporthook(count, block_size, total_size):
            if progress_callback:
                progress_callback(count, block_size, total_size)

        try:
            manifest_url = "https://sakura-sedaia.com/docs/sacr-index.json"
            manifest_path = get_addon_directory() / "Manifest.json"
            request.urlretrieve(manifest_url, str(manifest_path), reporthook=reporthook)
            
            prefs = get_preferences()
            import time
            prefs.last_manifest_refresh = time.time()
            return True, "Manifest downloaded successfully"
        except Exception as e:
            return False, str(e)

    def download_version(self, version_str: str, progress_callback=None):
        target_version, branch_info = self.get_version_info(version_str)
        
        if not target_version:
             # Keep previous error for consistency
             branch_key = "stable" if self.branch_id == "0" else "dev"
             raise ValueError(f"Version '{version_str}' not found in {branch_key} branch or manifest missing")

        # Prioritize .zip files with a .blend fallback
        builds = target_version.get("builds", [])
        if not builds:
            raise ValueError(f"No builds found for version {version_str}")

        build = None
        for b in builds:
            if b.get("fileName", "").lower().endswith(".zip"):
                build = b
                break
        
        if not build:
            for b in builds:
                if b.get("fileName", "").lower().endswith(".blend"):
                    build = b
                    break
        
        if not build:
            build = builds[0]

        file_name = build.get("fileName")
        branch_path = branch_info.get("path")

        if not file_name:
            raise ValueError(f"Build entry missing fileName for version '{version_str}'")
        if not branch_path:
            branch_key = "stable" if self.branch_id == "0" else "dev"
            raise ValueError(
                f"Branch '{branch_key}' is missing download path in manifest"
            )

        # Use the new helper for URL
        download_url = self.get_download_url(version_str)
        if not download_url:
            raise ValueError(f"Could not construct download URL for version '{version_str}'")

        prefs = get_preferences()
        addon_dir = prefs.addon_directory
        os.makedirs(addon_dir, exist_ok=True)
        
        addon_root = os.path.realpath(addon_dir)
        destination = os.path.realpath(os.path.join(addon_dir, file_name))
        if os.path.commonpath([addon_root, destination]) != addon_root:
            raise ValueError(f"Unsafe fileName path in manifest: {file_name}")
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Reuse existing downloaded files instead of failing the workflow.
        should_download = not os.path.exists(destination)

        # Use a wrapper for progress_callback to match urllib.request.urlretrieve's reporthook
        def reporthook(count, block_size, total_size):
            if progress_callback:
                progress_callback(count, block_size, total_size)

        if should_download:
            request.urlretrieve(download_url, destination, reporthook=reporthook)

        # Automatically extract .blend files from the downloaded zip into
        # a version-specific `sacr/<version>` directory.
        version_dir_name = target_version.get("version") or version_str
        extract_dir = os.path.join(addon_dir, "sacr", version_dir_name)
        
        if file_name.lower().endswith(".zip"):
            self._extract_blend_from_zip(destination, extract_dir)
            return extract_dir
        elif file_name.lower().endswith(".blend"):
            os.makedirs(extract_dir, exist_ok=True)
            new_destination = os.path.join(extract_dir, file_name)
            # Move or copy the blend file to the version directory
            shutil.copy2(destination, new_destination)
            return extract_dir

        return destination

    @staticmethod
    def delete_version(version_str: str):
        version_dir = get_addon_directory() / "sacr" / version_str
        delete_directory(version_dir)
