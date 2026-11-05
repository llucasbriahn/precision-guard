"""Canonical protocol loading. SPDX-License-Identifier: GPL-3.0-only."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/precision-guard/skills/precision-guard/SKILL.md"
START_TOKEN = b"<!-- precision-guard:start -->"
END_TOKEN = b"<!-- precision-guard:end -->"
START = b"\n\n" + START_TOKEN + b"\n"
END = b"\n" + END_TOKEN + b"\n"


def protocol():
    content = SKILL.read_text(encoding="utf-8")
    parts = content.split("---\n", 2)
    if len(parts) != 3 or parts[0]:
        raise ValueError("The packaged skill has invalid frontmatter.")
    return parts[2].strip() + "\n"
