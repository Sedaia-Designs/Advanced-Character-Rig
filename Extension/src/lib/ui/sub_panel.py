def sub_panel(ui, helper_obj, prop, label: str):
    """
    Defines a function to create a collapsible sub-panel in a user interface, with a toggleable
    header and corresponding content box.

    Parameters:
        ui (object): The user interface layout to which the sub-panel will be added. Typically
            an instance of a UI layout object.
        helper_obj (object): An object with a dictionary-like component used to determine
            the toggle state of the sub-panel.
        prop (str): The key in the helper object used to determine whether the sub-panel
            is expanded or collapsed.
        label (str): The text label displayed in the sub-panel header.

    Returns:
        object or None: Returns a box object where UI elements can be added if the
            sub-panel is expanded. Otherwise, returns None.
    """
    col = ui.column(align=True)
    header = col.row()
    toggle = header.column()
    toggle.scale_x = 1
    toggle.prop(
        helper_obj,
        f'["{prop}"]',
        text=label,
        icon="TRIA_DOWN" if helper_obj[prop] else "TRIA_RIGHT",
    )
    if helper_obj[prop]:
        box = col.box()
        return box
    else:
        return None
