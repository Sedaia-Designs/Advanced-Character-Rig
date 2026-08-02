import os
from fnmatch import fnmatch
from pathlib import Path

from preferences import get_preferences

class finder:
    def __init__(self):
        self.path = get_preferences().addon_data_location

    def filtered_search(self, pattern: str | list[str]) -> list[str]:
        """
        Find files in the directory with the given pattern(s).

        @param pattern: The pattern(s) to match against the file names.
        """
        walkList: list[str] = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.path)
            for file in files
        ]
        if type(pattern) is str:
            pattern = [pattern]
        return [
            file
            for file in walkList
            if any(fnmatch(Path(file).name, pattern) for pattern in pattern)
        ]

    def walk(self) -> list[str]:
        """Get all files in the provided directory."""
        return [
            os.path.join(root, file)
            for root, _, files in os.walk(self.path)
            for file in files
        ]

if __name__ == '__main__':
    print(find_files_in_directory_with_filter('*.blend*'))
