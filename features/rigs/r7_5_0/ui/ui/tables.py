def eye_colors(parent_ui, material, grid, grid_label):
    """
    Generates a color table UI layout for managing material properties.

    This function creates a UI layout for manipulating specific material inputs,
    allowing the user to adjust a series of color-related properties such as the
    default values, gradients, and splits. The table is structured into rows, with
    interdependencies on whether gradients and splits are enabled.

    Parameters:
        parent_ui: The user interface layout to which the generated table will be added.
        material: The material object whose input properties are being modified.
        grid: List of input indices corresponding to material inputs to be displayed
            and manipulated in the table.
        grid_label: List of strings that provide labels for each input in the grid
            to be shown in the UI.

    Returns:
        None
    """
    color_gradient = material.inputs[grid[4]].default_value
    color_split = material.inputs[grid[5]].default_value

    table = parent_ui.column(align=True)  # Container

    row = table.row(align=True)  # Row 1
    l_col_r1 = row.row(align=True)
    l_col_r1.prop(material.inputs[grid[0]], "default_value", text=grid_label[0])

    r_col_r1 = row.row(align=True)
    r_col_r1.prop(material.inputs[grid[1]], "default_value", text=grid_label[1])
    r_col_r1.enabled = color_split

    row = table.row(align=True)  # Row 2
    l_col_r2 = row.row(align=True)
    l_col_r2.prop(material.inputs[grid[2]], "default_value", text=grid_label[2])
    l_col_r2.enabled = color_gradient

    r_col_r2 = row.row(align=True)
    r_col_r2.prop(material.inputs[grid[3]], "default_value", text=grid_label[3])
    r_col_r2.enabled = color_split and color_gradient

    row = table.row(align=True)  # Row 3
    l_col_r3 = row.row(align=True)
    l_col_r3.prop(
        material.inputs[grid[4]], "default_value", text=grid_label[4], toggle=True
    )

    r_col_r3 = row.row(align=True)
    l_col_r3.prop(
        material.inputs[grid[5]], "default_value", text=grid_label[5], toggle=True
    )
