"""Generate portable Markdown API pages from extension docstrings."""

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

from pdoc.doc import Class, Function, Module, Variable

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "sacr_extension"
OUTPUT = ROOT / "docs" / "api"


def _module(name: str) -> ModuleType:
    """Create an importable module with name."""
    module = ModuleType(name)
    module.__spec__ = ModuleSpec(name, loader=None)
    sys.modules[name] = module
    return module


def _install_blender_stubs() -> None:
    """Provide import-time Blender names without running Blender."""
    bpy = _module("bpy")
    types, props, utils, ops = (_module(f"bpy.{name}") for name in ("types", "props", "utils", "ops"))
    for name in ("AddonPreferences", "Context", "Menu", "Operator", "Panel", "PoseBone", "Preferences"):
        setattr(types, name, type(name, (), {}))
    for name in ("BoolProperty", "EnumProperty", "IntProperty", "StringProperty"):
        setattr(props, name, lambda **kwargs: None)
    utils.register_class = lambda cls: None
    utils.unregister_class = lambda cls: None
    utils.extension_path_user = lambda *args, **kwargs: str(ROOT / "playerdata")
    ops.wm = SimpleNamespace(path_open=lambda **kwargs: None)
    bpy.types, bpy.props, bpy.utils, bpy.ops = types, props, utils, ops
    bpy.app = SimpleNamespace(online_access=False)
    bpy.context = SimpleNamespace()
    bpy.data = SimpleNamespace()
    package = _module(PACKAGE)
    package.__path__ = [str(ROOT)]
    package.__spec__.submodule_search_locations = package.__path__


def _render_member(member, level: int = 2) -> list[str]:
    """Render a class or function, including its public methods."""
    signature = str(getattr(member, "signature", ""))
    lines = [f"{'#' * level} `{member.name}{signature}`", ""]
    if member.docstring:
        lines.extend((member.docstring.strip(), ""))
    if isinstance(member, Class):
        for child in member.own_members:
            if isinstance(child, (Function, Variable)) and not child.name.startswith("_"):
                lines.extend(_render_member(child, level + 1))
    return lines


def _render_module(name: str) -> None:
    """Write a Markdown page for one extension module."""
    module = Module.from_name(name)
    relative = name.removeprefix(f"{PACKAGE}.").replace(".", "/")
    destination = OUTPUT / f"{relative}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# `{relative.replace('/', '.')}`", ""]
    if module.docstring:
        lines.extend((module.docstring.strip(), ""))
    for member in module.own_members:
        if isinstance(member, (Class, Function)) and not member.name.startswith("_"):
            lines.extend(_render_member(member))
    destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    """Generate Markdown for all stable extension modules outside skins_v2."""
    _install_blender_stubs()
    paths = [ROOT / "modules.py", ROOT / "prefs.py"]
    paths += sorted((ROOT / "core").rglob("*.py"))
    paths += sorted((ROOT / "features" / "rigs").rglob("*.py"))
    paths += sorted((ROOT / "features" / "skins").rglob("*.py"))
    links = []
    for path in paths:
        parts = path.relative_to(ROOT).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        relative = ".".join(parts)
        _render_module(f"{PACKAGE}.{relative}")
        links.append(f"- [{relative}]({relative.replace('.', '/')}.md)")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "README.md").write_text("# Extension API\n\n" + "\n".join(links) + "\n", encoding="utf-8")
    print(f"Generated Markdown API documentation in {OUTPUT}")


if __name__ == "__main__":
    main()
