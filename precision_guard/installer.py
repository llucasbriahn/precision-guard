"""Byte-preserving file operations. SPDX-License-Identifier: GPL-3.0-only."""

import os
from pathlib import Path
import stat
import tempfile

from .protocol import START, END, START_TOKEN, END_TOKEN

def transform(original, body, remove=False):
    """Preserve every byte outside the block, including existing line endings."""
    starts, ends = original.count(START_TOKEN), original.count(END_TOKEN)
    block = START + body.rstrip(b"\n") + END
    if starts == ends == 0:
        return original if remove else original + block
    if starts != 1 or ends != 1 or START not in original or END not in original:
        raise ValueError("Invalid or duplicate Precision Guard markers; repair them manually.")
    begin = original.index(START)
    finish = original.index(END)
    if finish < begin:
        raise ValueError("Precision Guard markers are out of order.")
    return original[:begin] + (b"" if remove else block) + original[finish + len(END):]


def checked_path(raw):
    path = Path(raw).expanduser().absolute()
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError(f"Refusing a symbolic link: {component}. Use its real path explicitly.")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    return Path(os.path.abspath(path))


def write_change(path, original, updated, existed):
    # Detect ordinary concurrent changes. This is not an adversarial filesystem sandbox.
    if path.exists() != existed or (existed and path.read_bytes() != original):
        raise ValueError(f"File changed after inspection: {path}. Run the command again.")
    checked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if existed else 0o644
    backup = None
    if existed:
        fd, backup_name = tempfile.mkstemp(prefix=path.name + ".precision-guard-", suffix=".bak", dir=path.parent)
        backup = Path(backup_name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(original)
    fd, temporary = tempfile.mkstemp(prefix=".precision-guard-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return backup
