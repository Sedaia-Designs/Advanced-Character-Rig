"""Blender-free tests for `core.lookup`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.lookup import base_name  # noqa: E402


class BaseNameTests(unittest.TestCase):
    def test_strips_duplicate_suffix(self):
        self.assertEqual(base_name("Hidden Objects.001"), "Hidden Objects")
        self.assertEqual(base_name("Hidden Objects.1234"), "Hidden Objects")

    def test_keeps_other_dots(self):
        self.assertEqual(base_name("Default - SACR R7.5.0"), "Default - SACR R7.5.0")
        self.assertEqual(base_name("Default - SACR R7.5.0.002"), "Default - SACR R7.5.0")
        self.assertEqual(base_name("Hidden Objects.01"), "Hidden Objects.01")
        self.assertEqual(base_name("Hidden Objects"), "Hidden Objects")


if __name__ == "__main__":
    unittest.main()
