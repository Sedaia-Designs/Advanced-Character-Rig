"""Image state used by the R7.5 texture controls."""


def is_packed(image):
    """Return whether packed."""
    return bool(image and image.packed_files)
