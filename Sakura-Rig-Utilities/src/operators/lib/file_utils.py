from pathlib import Path
import shutil

def file_exists(path):
    """Check if a file or directory exists."""
    if not path:
        return False
    return Path(path).exists()

def ensure_directory(path):
    """Ensure that a directory exists, creating it if necessary."""
    p = Path(path)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    return p

def delete_directory(path):
    """Recursively delete a directory and all its contents."""
    p = Path(path)
    if p.exists() and p.is_dir():
        shutil.rmtree(p)
        return True
    return False

def get_file_size(path):
    """Get the size of a file in bytes."""
    p = Path(path)
    if p.exists() and p.is_file():
        return p.stat().st_size
    return 0

def get_manifest_key(key):
    """Get a key from the blender_manifest.toml file."""
    import os
    import re
    
    # Path to blender_manifest.toml
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "blender_manifest.toml")
    
    if not os.path.exists(manifest_path):
        return ""
    
    with open(manifest_path, 'r') as f:
        content = f.read()
    
    # Very simple TOML parser for basic keys (string/int)
    # Match key = "value" or key = value
    match = re.search(rf'^{key}\s*=\s*"?([^"\n]+)"?', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    return ""
