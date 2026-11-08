"""Draw helpers shared by every rig UI's panels."""

from ..core.images import is_packed
from ..operators.constants import OperatorID


def texture_row(layout, image):
    """Draw a pack button, file path field, and reload button for `image`.

    The path and reload controls are disabled while the image is packed.
    """
    row = layout.row(align=True)
    row.operator(
        OperatorID.IMAGE_PACK,
        icon="PACKAGE" if is_packed(image) else "UGLYPACKAGE",
        text="",
    ).path = image.name

    path_row = row.row(align=True)
    path_row.enabled = not is_packed(image)
    path_row.prop(image, "filepath", text="")
    path_row.operator(OperatorID.IMAGE_RELOAD, icon="FILE_REFRESH", text="").path = image.name
    return row
