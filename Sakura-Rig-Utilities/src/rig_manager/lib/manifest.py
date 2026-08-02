from pathlib import Path

from ...lib import http, hash, exceptions

def download(
        source_url: str = "https://sakura-sedaia.com/json/sacr-index.json",
        checksum_url: str = "https://sakura-sedaia.com/json/sacr-index.json.sha256",
        destination: str | Path | None = None,
        timeout: int = 5,
) -> Path:
    """
    Download, update, or repair the local SACR manifest.

    A missing manifest or checksum triggers a complete validated download.
    Otherwise, the remote checksum is compared with both the stored checksum
    and the calculated hash of the local manifest. An unchanged valid manifest
    is reused without downloading the payload. A stale checksum is repaired
    directly when the local manifest already matches the remote checksum;
    otherwise, a replacement manifest is installed only after validation.
    Temporary download files are removed before the function exits.

    Args:
        source_url: URL of the SACR manifest payload.
        checksum_url: URL of the manifest's SHA-256 checksum file.
        destination: Directory in which the manifest and checksum are stored.
        timeout: Maximum number of seconds to wait for each network request.

    Returns:
        Path: The path to the validated local `sacr-index.json` manifest.

    Raises:
        ValueError: If no destination directory is provided.
        HttpDownloadError: If the checksum or manifest cannot be downloaded or
            written to its destination.
        ChecksumValidationError: If the remote checksum is malformed or a
            downloaded manifest does not match it.
        OSError: If a validated temporary artifact cannot replace its local
            destination or temporary-file cleanup fails.
    """

    if destination is None:
        raise ValueError("Destination path must be provided")

    # Relevant Starting Paths
    destination_dir = Path(destination).resolve()
    manifest_local = destination_dir / "sacr-index.json"
    checksum_local = manifest_local.with_name(f"{manifest_local.name}.sha256")

    # Download a complete validated pair if either local artifact is missing.
    if not manifest_local.exists() or not checksum_local.exists():
        return http.download_with_checksum(source_url, checksum_url, manifest_local, timeout)["file_path"]

    checksum_remote = destination_dir / "sacr-index.json.sha256.tmp"
    manifest_remote = destination_dir / "sacr-index.json.tmp"
    # If the Manifest Files are valid or the local files are invalid, perform an update.
    try:
        http.download(checksum_url, checksum_remote, timeout)

        # Reads the downloaded checksum file to ensure validity, raising an exception to immediately stop the update process
        try:
            sha256_remote = hash.SHA256(checksum_remote).read()
        except exceptions.InvalidChecksumFileError as e:
            raise exceptions.ChecksumValidationError(
                f"Could not validate the new manifest checksum. {e}"
            ) from e

        # Reads the local checksum file to ensure validity, returning None if the file is invalid
        try:
            sha256_local = hash.SHA256(checksum_local).read()
        except exceptions.InvalidChecksumFileError:
            sha256_local = None

        # Retrieves the local file checksum, returning None if the file is invalid
        try:
            local_file_checksum = hash.SHA256(manifest_local).calculate()
        except OSError:
            local_file_checksum = None

        # Flags used to determine correct course of action, allowing this utility to perform repairs instead of straight overrides.
        local_manifest_match_remote_sha = local_file_checksum == sha256_remote
        local_remote_checksum_match = sha256_local == sha256_remote

        # If both flags return True, the local files are valid and no action is needed.
        if local_remote_checksum_match and local_manifest_match_remote_sha:
            return manifest_local

        # If the Manifest is invalid or does not match the remote checksum, download the new copy.
        if not local_manifest_match_remote_sha:
            try:
                http.download(source_url, manifest_remote, timeout)
            except exceptions.HttpDownloadError as e:
                raise exceptions.HttpDownloadError(
                    f"Could not download the new manifest. {e}"
                ) from e

            if hash.SHA256(manifest_remote).calculate() != sha256_remote:
                raise exceptions.ChecksumValidationError(f"Could not validate remote manifest file.")

            manifest_remote.replace(manifest_local)

        # If the local checksum file is invalid or does not match the remote checksum, replace the stale checksum file with the new one.
        if not local_remote_checksum_match:
            checksum_remote.replace(checksum_local)

        return manifest_local

    finally:
        manifest_remote.unlink(missing_ok=True)
        checksum_remote.unlink(missing_ok=True)
