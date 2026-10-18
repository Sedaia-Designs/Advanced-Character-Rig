# `features.skins.service`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

Network and storage workflow for Minecraft player skins.

## `SkinServiceError`

Unspecified run-time error.

## `skin_data_is_slim`

```python
skin_data_is_slim(skin_data: dict) -> bool
```

Check whether Mojang marks the skin as using the slim arm model.

## `fetch_player`

```python
fetch_player(username: str) -> sacr_extension.features.skins.models.RemotePlayer
```

Resolve a player profile and decode its skin and cape metadata.

## `download`

```python
download(url: str, destination: pathlib.Path) -> None
```

Download a texture and translate network failures for callers.

## `download_player_textures`

```python
download_player_textures(
    root: pathlib.Path,
    username: str,
    player: sacr_extension.features.skins.models.RemotePlayer,
    index: int
) -> dict
```

Save indexed skin and cape images and return their local metadata.
