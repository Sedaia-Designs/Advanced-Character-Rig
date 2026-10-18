# `features.skins.repository`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

Local persistence for downloaded player data.

## `player_dir`

```python
player_dir(root: pathlib.Path, username: str) -> pathlib.Path
```

Return the storage directory assigned to a player name.

## `player_file`

```python
player_file(root: pathlib.Path, username: str) -> pathlib.Path
```

Return the player metadata JSON path within the player's directory.

## `exists`

```python
exists(root: pathlib.Path, username: str) -> bool
```

Check whether saved metadata exists for a player.

## `load`

```python
load(root: pathlib.Path, username: str) -> dict
```

Load a player's saved metadata from JSON.

## `save`

```python
save(root: pathlib.Path, username: str, data: dict) -> None
```

Persist player metadata using an atomic JSON replacement.
