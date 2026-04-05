from pathlib import Path
import os
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
