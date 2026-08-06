import zipfile

from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath, PureWindowsPath

from . import exceptions


class Zip:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def extract(
        self,
        destination: Path | str,
        only_glob: list[str],
        max_depth: int | None = None,
    ) -> None:
        """
        Extracts files from a zip archive to a specified destination directory.

        The method provides functionality to extract files from the zip archive stored
        at the path represented by the `self.path` attribute to the `destination`
        directory. Users can specify certain file patterns to extract by using the
        `only_glob` parameter. The method creates the destination directory if it
        does not exist.

        Parameters:
            destination (Path | str): The destination directory where files will
                                      be extracted.
            only_glob (list[str]): A list of file patterns to filter the files to
                                   be extracted. If empty, all files in the archive
                                   will be extracted.
            max_depth (int | None): Maximum depth of the directory structure to extract.
                             Default is None, which means all files will be extracted.

        Raises:
            ArchiveExtractionError: If the archive is invalid or cannot be extracted.
            UnsafeArchiveMemberError: If a member path is absolute or escapes the
                destination directory.

        Returns:
            None
        """
        if max_depth is not None and max_depth < 0:
            raise ValueError("max_depth must be zero or greater.")

        destination_root = Path(destination).resolve()

        try:
            destination_root.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.path, "r") as archive:
                for member in archive.infolist():
                    member_path = self._member_path(member.filename)
                    target = destination_root.joinpath(*member_path.parts)

                    if not target.resolve().is_relative_to(destination_root):
                        raise exceptions.UnsafeArchiveMemberError(
                            f"Archive member escapes the destination: {member.filename}"
                        )

                    depth = len(member_path.parts)
                    if not member.is_dir():
                        depth -= 1

                    if max_depth is not None and depth > max_depth:
                        continue

                    if only_glob and not any(
                        fnmatchcase(member_path.as_posix(), pattern)
                        for pattern in only_glob
                    ):
                        continue

                    archive.extract(member, destination_root)
        except exceptions.ArchiveExtractionError:
            raise
        except (zipfile.BadZipFile, OSError, RuntimeError, NotImplementedError) as exc:
            raise exceptions.ArchiveExtractionError(
                f"Could not extract {self.path} to {destination_root}: {exc}"
            ) from exc

    @staticmethod
    def _member_path(filename: str) -> PurePosixPath:
        """Return a safe, portable ZIP member path or raise an archive error."""
        member_path = PurePosixPath(filename)

        if (
            not member_path.parts
            or member_path.is_absolute()
            or "\\" in filename
            or PureWindowsPath(filename).drive
            or ".." in member_path.parts
        ):
            raise exceptions.UnsafeArchiveMemberError(
                f"Archive member has an unsafe path: {filename}"
            )

        return member_path
