"""Validate and assemble local distributions. SPDX-License-Identifier: GPL-3.0-only."""

import hashlib
import json
from pathlib import Path
import re
import zipfile

from .protocol import ROOT, SKILL

ROOT_FILES = (
    "README.md", "CHAT.md", "EVALUATION.md", "VERIFICATION.md", "ARCHITECTURE.md",
    "CONTRIBUTING.md", "RELEASING.md", "CHANGELOG.md", "LICENSE", "NOTICE",
    ".gitignore", "install.py", "manage.py",
    "plugins/precision-guard/LICENSE", "plugins/precision-guard/NOTICE",
)
SOURCE_DIRS = ("precision_guard", "tests", "plugins", ".agents", ".claude-plugin", ".github")
EXTENSIONS = {".py", ".md", ".json", ".yml", ".yaml"}


def source_files(root=ROOT):
    """Use an explicit set of source areas; never archive the entire workspace."""
    files = [root / name for name in ROOT_FILES]
    for directory in SOURCE_DIRS:
        base = root / directory
        if base.is_symlink():
            raise ValueError(f"Release input is a symbolic link: {base}")
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Release input is a symbolic link: {path}")
            if path.is_file() and path.suffix in EXTENSIONS and "__pycache__" not in path.parts:
                files.append(path)
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or invalid release input: {path}")
    return sorted(files)


def validate(root=ROOT):
    plugin = root / "plugins/precision-guard"
    metadata = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
    if metadata.get("name") != "precision-guard":
        raise ValueError("The portable plugin must be named precision-guard.")
    if not re.fullmatch(r"\d+\.\d+\.\d+", metadata.get("version", "")):
        raise ValueError("Use a numeric major.minor.patch release version.")
    if not metadata.get("description") or metadata.get("license") != "GPL-3.0-only":
        raise ValueError("The plugin requires a description and GPL-3.0-only license.")
    for directory in (".claude-plugin", ".codex-plugin"):
        overlay = json.loads((plugin / directory / "plugin.json").read_text(encoding="utf-8"))
        for key in ("name", "version", "description", "license"):
            if overlay.get(key) != metadata[key]:
                raise ValueError(f"Inconsistent manifest field: {directory}/{key}")
    codex = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if codex.get("skills") != "./skills/":
        raise ValueError("Codex compatibility skills path must be ./skills/.")
    for name in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        marketplace = json.loads((root / name).read_text(encoding="utf-8"))
        if marketplace.get("name") != "precision-guard-local" or len(marketplace.get("plugins", [])) != 1:
            raise ValueError(f"Invalid marketplace: {name}")
        entry = marketplace["plugins"][0]
        path = entry["source"] if isinstance(entry["source"], str) else entry["source"]["path"]
        if entry.get("name") != metadata["name"] or path != "./plugins/precision-guard":
            raise ValueError(f"Invalid marketplace source: {name}")
    skill_path = root / SKILL.relative_to(ROOT)
    content = skill_path.read_text(encoding="utf-8")
    # This project deliberately uses a tiny frontmatter subset: one plain scalar
    # per line. This is not a general YAML parser or a vendor schema validator.
    parts = content.split("---\n", 2)
    if len(parts) != 3 or parts[0]:
        raise ValueError("Invalid skill frontmatter delimiters.")
    fields = {}
    for line in parts[1].strip().splitlines():
        key, separator, value = line.partition(": ")
        if not separator or key in fields or key not in {"name", "description", "license"}:
            raise ValueError("Use unique name, description, and license scalar fields in the skill.")
        if any(marker in value for marker in ("\n", "<", ">", ": ")):
            raise ValueError(f"Unsupported plain scalar in skill field: {key}")
        fields[key] = value
    if fields.get("name") != metadata["name"] or fields.get("license") != metadata["license"]:
        raise ValueError("Skill identity or license does not match the plugin.")
    if not 1 <= len(fields.get("description", "")) <= 1024 or not parts[2].strip():
        raise ValueError("The skill requires a bounded description and a nonempty body.")
    if "GNU GENERAL PUBLIC LICENSE" not in (root / "LICENSE").read_text(encoding="utf-8"):
        raise ValueError("Missing GPL license text.")
    for name in ("LICENSE", "NOTICE"):
        if (plugin / name).read_bytes() != (root / name).read_bytes():
            raise ValueError(f"Plugin {name} must match the root copy for marketplace distribution.")
    files = source_files(root)
    for path in files:
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    if not (path.parent / target.split("#")[0]).exists():
                        raise ValueError(f"Broken local link in {path}: {target}")
    return metadata


def archive(path, entries):
    """Fixed order, timestamps, modes, and uncompressed bytes give stable ZIPs."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as bundle:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)


def build(output, root=ROOT):
    metadata = validate(root)
    output = Path(output).resolve()
    plugin = root / "plugins/precision-guard"
    inputs = source_files(root)
    # Never let a distribution overwrite source files in a packaged source area.
    for directory in SOURCE_DIRS:
        if output == (root / directory).resolve() or (root / directory).resolve() in output.parents:
            raise ValueError("Choose an output directory outside packaged source areas.")
    output.mkdir(parents=True, exist_ok=True)
    stem = f"precision-guard-{metadata['version']}"
    source = {"precision-guard/" + p.relative_to(root).as_posix(): p.read_bytes() for p in inputs}
    native = {"precision-guard/" + p.relative_to(plugin).as_posix(): p.read_bytes() for p in inputs if plugin in p.parents}
    for name in ("LICENSE", "NOTICE"):
        native["precision-guard/" + name] = (root / name).read_bytes()
    products = [output / (stem + "-source.zip"), output / (stem + "-plugin.zip")]
    # Refuse a symlink destination, including a pre-existing checksum file.
    checksums = output / "SHA256SUMS"
    for destination in [*products, checksums]:
        if destination.is_symlink():
            raise ValueError(f"Refusing a symbolic-link output: {destination}")
    archive(products[0], source)
    archive(products[1], native)
    checksums.write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in products), encoding="utf-8")
    return [*products, checksums]
