"""Generate GitHub Wiki pages from extension docstrings."""

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

from pdoc.doc import Class, Function, Module, Variable

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "sacr_extension"
OUTPUT = ROOT / "docs" / "wiki"
WIKI_BASE = "https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki"


def _page_name(module_name: str) -> str:
    """Map a Python module to a unique, flat GitHub Wiki page name."""
    return "API-" + module_name.removeprefix(f"{PACKAGE}.").replace(".", "-")


def _wiki_link(label: str, page: str) -> str:
    """Link to a page in this repository's GitHub Wiki."""
    return f"[{label}]({WIKI_BASE}/{page})"


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
    lines = [f"{'#' * level} `{member.name}`", ""]
    if signature:
        lines.extend(("```python", f"{member.name}{signature}", "```", ""))
    if member.docstring:
        lines.extend((member.docstring.strip(), ""))
    if isinstance(member, Class):
        for child in member.own_members:
            if isinstance(child, (Function, Variable)) and not child.name.startswith("_"):
                lines.extend(_render_member(child, level + 1))
    return lines


def _render_module(name: str) -> None:
    """Write one flat Wiki page for an extension module."""
    module = Module.from_name(name)
    relative = name.removeprefix(f"{PACKAGE}.")
    destination = OUTPUT / f"{_page_name(name)}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# `{relative}`", "", _wiki_link("Home", "Home"), ""]
    if module.docstring:
        lines.extend((module.docstring.strip(), ""))
    for member in module.own_members:
        if isinstance(member, (Class, Function)) and not member.name.startswith("_"):
            lines.extend(_render_member(member))
    destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    """Generate a standalone Wiki export for the stable extension modules."""
    _install_blender_stubs()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for stale_page in OUTPUT.glob("API-*.md"):
        stale_page.unlink()
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
        name = f"{PACKAGE}.{relative}"
        _render_module(name)
        links.append(f"- {_wiki_link(relative, _page_name(name))}")
    skin_map = (ROOT / "features" / "skins" / "README.md").read_text(encoding="utf-8")
    (OUTPUT / "Skin-API-v1.md").write_text(skin_map.rstrip() + "\n", encoding="utf-8")
    home = "# SACR extension API\n\n" + _wiki_link("Skin API v1 workflow", "Skin-API-v1") + "\n\n## Modules\n\n" + "\n".join(links) + "\n"
    (OUTPUT / "Home.md").write_text(home, encoding="utf-8")
    sidebar = "**SACR extension API**\n\n- " + _wiki_link("Home", "Home") + "\n- " + _wiki_link("Skin API v1 workflow", "Skin-API-v1") + "\n\n" + "\n".join(links) + "\n"
    (OUTPUT / "_Sidebar.md").write_text(sidebar, encoding="utf-8")
    print(f"Generated GitHub Wiki pages in {OUTPUT}")


if __name__ == "__main__":
    main()
