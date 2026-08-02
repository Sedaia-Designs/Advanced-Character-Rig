from pathlib import Path
from urllib import request, error
from typing import TypedDict

from . import exceptions
from .hash import SHA256

class DownloadWithChecksumResult(TypedDict):
    """
    Represents the result of a file download operation, including the file path,
    checksum path, and SHA-256 string.

    This class is a TypedDict used to enforce the structure of the result
    returned from a download operation that includes a checksum. It provides
    a standardized way to handle and access the file's download information
    and its associated checksum data.

    Attributes:
        file_path (Path): The path where the downloaded file is stored.
        checksum_path (Path): The path where the checksum file is saved.
        sha256_string (str): The SHA-256 hash of the downloaded file as a
            string.
    """
    file_path: Path
    checksum_path: Path
    sha256_string: str

def download(url: str, destination: str | Path, timeout: int) -> Path:
    """
    Download a file from a URL to a local destination.

    The response is first written to a temporary sibling file. After the download
    completes successfully, the temporary file replaces the destination. This
    preserves an existing destination if the request or file write fails.

    Args:
        url: URL of the file to download.
        destination: Local path where the completed file will be stored.
        timeout: Maximum number of seconds to wait for the network request.

    Returns:
        The resolved destination as a `Path`.

    Raises:
        HttpDownloadError: If the network request, temporary file write, or final
            file replacement fails.
    """
    destination_tmp = Path(f"{destination}.artifact")
    destination = Path(destination)

    try:
        with request.urlopen(
                url,
                timeout=timeout,
        ) as response:
            with destination_tmp.open("wb") as destination_file:
                destination_file.write(response.read())

    except error.HTTPError as exc:
        destination_tmp.unlink(missing_ok=True)
        raise exceptions.HttpDownloadError(
            f"Could not connect while downloading {url}"
        ) from exc

    except error.URLError as exc:
        destination_tmp.unlink(missing_ok=True)
        raise exceptions.HttpDownloadError(
            f"Could not write download to {url}"
        ) from exc

    except OSError as exc:
        destination_tmp.unlink(missing_ok=True)
        raise exceptions.HttpDownloadError(
            f"Could not write download to {destination_tmp}: {exc}"
        ) from exc
    try:
        destination_tmp.replace(destination)

    except OSError as exc:
        destination_tmp.unlink(missing_ok=True)
        raise exceptions.HttpDownloadError(
            f"Could not write download to {destination}: {exc}"
        ) from exc

    return destination


def download_with_checksum(url: str, checksum_url: str, destination: str | Path, timeout: int) -> DownloadWithChecksumResult:
    """
    Download a file and its SHA-256 checksum.

    The downloaded files are removed if downloading, parsing, or checksum
    validation fails.

    Returns:
        DownloadWithChecksumResult: Paths to the downloaded artifacts and the validated
    SHA-256 checksum.

    Raises:
        HttpDownloadError: If either download fails.
        ChecksumValidationError: If the checksum is malformed or does not match.
    """
    file_path: Path = Path(destination)
    # This needs to have the same filename and extension as the file_path, but with .sha256 added on the back, hence the strange string/path manipulation
    checksum_path: Path = file_path.with_name(f"{file_path.name}.sha256")

    # Temporary File positions
    file_tmp: Path = file_path.with_name(f"{file_path.name}.tmp")
    checksum_path_tmp: Path = checksum_path.with_name(f"{checksum_path.name}.tmp")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        download(checksum_url, checksum_path_tmp, timeout)

        try:
            checksum = SHA256(checksum_path_tmp).read()
        except exceptions.InvalidChecksumFileError as exc:
            raise exceptions.ChecksumValidationError(f"Checksum validation failed for {url}") from exc

        download(url, file_tmp, timeout)


        if SHA256(file_tmp).calculate() != checksum:
            raise exceptions.ChecksumValidationError(f"Checksum validation failed for {url}")

        file_tmp.replace(file_path)
        checksum_path_tmp.replace(checksum_path)

        return {
            "file_path" : file_path,
            "checksum_path" : checksum_path,
            "sha256_string" : checksum
        }

    except Exception:
        file_tmp.unlink(missing_ok=True)
        checksum_path_tmp.unlink(missing_ok=True)
        raise