from ...sru_lib import Search
from typing import TypedDict
from pathlib import Path


class Rig(TypedDict):
    name: str
    id: str
    version: str
    branch: str
    filepath: Path


def find_rigs(search_path: Path | str) -> list[Rig]:
    """
    Finds rig objects by searching through a specified directory.

    This function scans the given directory path to find
    and return a list of rig objects that match certain
    criteria, which are determined during the search process.
    If the path provided is not absolute, it is resolved to
    an absolute path.

    Args:
        search_path (Path | str): The directory path where
            the rig search will be performed. It can be
            provided as a string or a Path object.

    Returns:
        list[Rig]: A list of found rig objects.
    """
    search_path = Path(search_path).resolve()

    # TODO: When saving SACR Rigs, make sure to name them the following: SACR.<Version>.<Branch>.blend for proper data extraction.
    # This is a temporary to do until the Rig Downloader is written properly.
    discovered_blend = Search(search_path).filtered_walk("*.blend")

    return []
