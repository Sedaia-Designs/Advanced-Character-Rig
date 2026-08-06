class ChecksumValidationError(Exception):
    """Exception raised when a checksum validation fails"""

class HttpDownloadError(RuntimeError):
    """Raised when an HTTP Download cannot be completed."""

class InvalidChecksumFileError(Exception):
    """Raised when a checksum file does not contain a valid checksum"""


class ArchiveExtractionError(RuntimeError):
    """Raised when an archive cannot be safely extracted."""


class UnsafeArchiveMemberError(ArchiveExtractionError):
    """Raised when an archive member would extract outside its destination."""
