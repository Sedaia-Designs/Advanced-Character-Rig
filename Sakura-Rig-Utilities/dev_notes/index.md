Naming Convensions

1. Python Files that correspond with a Blender type will have a prefix which follows the below convention:
   - `PANEL_` for Panels
   - `MENU_` for Menus
   - `OPERATOR_` for Operator
   - `PREFERENCES_` for Preferences
2. For Utility Classes and functions (e.g. the `lib` module), the classes must be immutable, and use getters and setters to access the data.
3. All classes must have a docstring with the class name and a brief description of what the class does, including any parameters and outputs.