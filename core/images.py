"""Image state checks shared by the rig UIs and image operators."""


def is_packed(image) -> bool:
    """Return whether `image` exists and has packed file data."""
    return bool(image and image.packed_files)
