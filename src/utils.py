"""Utility functions for file operations."""

import os
import tempfile
from pathlib import Path


def atomic_write(file_path: Path, content: str) -> None:
    """Write file atomically to prevent corruption.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Raises:
        OSError: If file write fails
    """
    # Get directory of target file
    directory = file_path.parent

    # Create temp file in same directory (ensures same filesystem)
    fd, temp_path = tempfile.mkstemp(dir=directory, suffix='.tmp', text=True)

    try:
        # Write content to temp file
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)

        # Atomic rename (replaces existing file)
        # On Windows, may need to remove existing file first
        if os.name == 'nt' and file_path.exists():
            os.remove(file_path)
        os.rename(temp_path, file_path)

    except Exception as e:
        # Clean up temp file on error
        try:
            os.remove(temp_path)
        except:
            pass
        raise e


def ensure_directory_exists(path: Path) -> None:
    """Create directory if it doesn't exist.

    Args:
        path: Path to the directory

    Raises:
        OSError: If directory creation fails
    """
    if not path.exists():
        path.mkdir(parents=True, mode=0o755)
    else:
        # Ensure proper permissions
        try:
            os.chmod(path, 0o755)
        except:
            pass  # Permissions may not be changeable on all systems
