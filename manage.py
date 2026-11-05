#!/usr/bin/env python3
"""Local validation and releases. SPDX-License-Identifier: GPL-3.0-only."""

import argparse
from pathlib import Path
import sys

from precision_guard.distribution import build, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "build"))
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    try:
        if args.command == "check":
            metadata = validate()
            print(f"Package structure valid: {metadata['name']} {metadata['version']}")
            print("Local checks do not establish vendor schema acceptance or model behavior.")
        else:
            for path in build(args.output):
                print(path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
