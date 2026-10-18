# `features.rigs.r7_5_0.ui.ui.tables`

## `eye_colors(parent_ui, material, grid, grid_label)`

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
