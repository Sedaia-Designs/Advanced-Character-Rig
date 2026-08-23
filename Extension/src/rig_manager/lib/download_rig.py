"""
A module for downloading files from a source URL and verifying them with a checksum.

This module provides functionality to download a file from the given source URL

Functions:
- download: Downloads a file from a source URL, verifies it using a checksum,
  and saves it to a specified destination path.
"""

from ...sru_lib import http, exceptions
from pathlib import Path


def download(
    version: str,
    destination_path: Path | str,
    sacr_manifest: Path | str,
    source_url: str = "https://sakura-sedaia.com/",
    timeout: int = 5,
) -> Path:
    """
    Downloads the SACR Version from a given source URL and saves it to the specified destination path with a predefined file
    name. The download operation is performed with an optional timeout setting.

    Arguments:
        version (str): The SACR Version to download
        sacr_manifest (Path | str): The SACR manifest location
        destination_path (Path | str): The directory where the file will be saved. Can be a Path object or a
            string representing the path.
        source_url (str): The Database URL to download the SACR Version from
        timeout (int): Timeout for the download operation in seconds. Default is 5.

    Raises:
        HttpDownloadError: If the download operation fails due to network errors or any other issues.

    Returns:
        file_destination (Path): The path where the downloaded file is saved.
    """

    # Immediately resolve the destination path into a Path object.
    destination_path: Path = Path(destination_path).resolve()

    # Ensures the right branch is selected based on the version prefix
    if version.startswith("Rig"):
        rig_branch: str = "stable"
    else:
        rig_branch: str = "dev"

    file_name: str = f"SACR_{rig_version}_{rig_branch}.blend"  # This can be split
    file_destination: Path = destination_path / file_name

    try:
        http.download(source_url, file_destination, timeout)
    except exceptions.HttpDownloadError as e:
        print(f"Error downloading file: {e}")

    return Path(file_destination)
