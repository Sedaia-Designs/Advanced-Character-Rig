import hashlib
from pathlib import Path
from .exceptions import InvalidChecksumFileError

class SHA256:
    """
    Provides functionality for handling and processing SHA-256 checksums.

    The SHA256 class is designed to work with files to manage SHA-256 checksum
    operations. It provides methods to read an existing checksum from a file
    and calculate the checksum directly from the file's content. The class ensures
    the integrity of the checksum by validating its format and value.

    Attributes:
        file (Path): The path to the file to perform checksum operations on.

    Raises:
        InvalidChecksumFileError: Raised when the checksum file is invalid,
        missing, or its content does not match the expected SHA-256 format.
    """
    def __init__(self, file: str | Path) -> str:
        self.file = Path(file)

    def read(self) -> str:
        """
        Reads and validates the SHA-256 checksum from a file. The method ensures that the checksum file exists, is readable,
        and contains a valid hexadecimal SHA-256 checksum string. If the file or its content is invalid, appropriate exceptions are raised.

        Raises:
            InvalidChecksumFileError: If the checksum file does not exist.
            InvalidChecksumFileError: If the checksum file cannot be read due to an OS error.
            InvalidChecksumFileError: If the checksum in the file is of invalid length or format.

        Returns:
            str: The valid hexadecimal SHA-256 checksum string extracted from the file.
        """
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()

        if not self.file.exists():
            raise InvalidChecksumFileError(
                f"Checksum File does not exist: {self.file}"
            )

        try:
            contents = self.file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise InvalidChecksumFileError(
                f"Could not read the provided checksum file: {self.file}"
            ) from exc
        try:
            checksum = contents.split(maxsplit=1)[0].lower()
        except IndexError as exc:
            raise InvalidChecksumFileError(
                f"Could not read the provided checksum file: {self.file}"
            ) from exc

        if len(checksum) != 64:
            raise InvalidChecksumFileError(
                f"Invalid SHA-256 checksum: {checksum}"
            )

        try:
            int(checksum, 16)
        except ValueError as exc:
            raise InvalidChecksumFileError(
                f"Invalid SHA-256 checksum: {checksum}"
            ) from exc

        return checksum

    def calculate(self) -> str:
        """
        Calculates the SHA-256 hash of the file provided during the class instance creation.

        The method reads the file in chunks to conserve memory and computes the SHA-256
        checksum.

        Returns:
            str: The computed SHA-256 hash of the file in hexadecimal format.

        Raises:
            OSError: If the file cannot be opened or read due to a filesystem
                error, such as a missing file or insufficient permissions.
        """
        sha256 = hashlib.sha256()
        buffer = 65536

        with open(self.file, "rb") as f:
            while True:
                data = f.read(buffer)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()
