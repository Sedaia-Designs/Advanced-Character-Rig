"""Table sets stored in the extension's SQLite database, one module per feature.

- `schema`: version tracking shared by every table set.
- `skins`: Skin Manager players, skins, and capes.

Every module here takes an open `sqlite3.Connection` and never opens the
database itself. Blender code opens one with `preferences.access.db_session()`.
Tables from different features share one file, so each module prefixes its
table names (``skin_``, and for example ``rig_`` later).
"""
