"""Collapsible sections backed by the rig's panel helper properties."""


def sub_panel(ui, helper_obj, prop, label):
    column = ui.column(align=True)
    column.row().prop(
        helper_obj,
        f'["{prop}"]',
        text=label,
        icon="TRIA_DOWN" if helper_obj[prop] else "TRIA_RIGHT",
    )
    return column.box() if helper_obj[prop] else None
