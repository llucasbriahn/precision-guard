"""Install or remove local instructions. SPDX-License-Identifier: GPL-3.0-only."""

import argparse
import difflib
from pathlib import Path
import sys

from .protocol import protocol
from .installer import checked_path, transform, write_change

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--target", choices=("codex", "claude", "both"), help="Project instruction files; default: both")
    selection.add_argument("--file", help="Explicit instruction file for another agent or a global configuration")
    parser.add_argument("--project", help="Existing project directory; required with --target")
    parser.add_argument("--dry-run", action="store_true", help="Print a diff without creating files or backups")
    parser.add_argument("--remove", action="store_true", help="Remove only the managed instruction block")
    parser.add_argument("--print", dest="print_protocol", action="store_true", help="Print the complete protocol for chats or manual installation")
    args = parser.parse_args(argv)
    if args.print_protocol:
        if args.file or args.target or args.project or args.remove or args.dry_run:
            parser.error("--print cannot be combined with installation options")
    elif args.file:
        if args.project:
            parser.error("--file and --project cannot be combined")
    elif not args.project:
        parser.error("provide --project, --file, or --print")

    try:
        if args.print_protocol:
            print(protocol(), end="")
            return 0
        if args.file:
            paths = [checked_path(args.file)]
        else:
            project = Path(args.project).expanduser().absolute()
            if not project.is_dir():
                raise ValueError(f"Project directory does not exist: {project}")
            names = {"codex": ("AGENTS.md",), "claude": ("CLAUDE.md",), "both": ("AGENTS.md", "CLAUDE.md")}
            paths = [checked_path(project / name) for name in names[args.target or "both"]]
        body = b"" if args.remove else protocol().encode("utf-8")
        changes = []
        # Inspect all targets before writing any of them.
        for path in paths:
            override = path.with_name("AGENTS.override.md")
            if not args.remove and path.name == "AGENTS.md" and override.is_file() and override.read_bytes().strip():
                raise ValueError(f"{override} takes precedence. Select that file explicitly with --file if appropriate.")
            existed = path.exists()
            original = path.read_bytes() if existed else b""
            original.decode("utf-8")
            updated = transform(original, body, args.remove)
            changes.append((path, original, updated, existed))
        for path, original, updated, existed in changes:
            if original == updated:
                print(f"Unchanged: {path}")
            elif args.dry_run:
                diff = difflib.unified_diff(original.decode("utf-8").splitlines(keepends=True), updated.decode("utf-8").splitlines(keepends=True), fromfile=str(path), tofile=str(path) + " (proposed)")
                print("".join(diff), end="")
            else:
                backup = write_change(path, original, updated, existed)
                print(f"Updated: {path}")
                if backup:
                    print(f"Backup: {backup}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
