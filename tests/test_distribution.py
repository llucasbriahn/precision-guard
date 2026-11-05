"""Distribution contract tests. SPDX-License-Identifier: GPL-3.0-only."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from precision_guard.distribution import build, validate
from precision_guard.protocol import ROOT


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name).resolve()
        self.root = self.work / "source"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("dist", "__pycache__", "*.pyc", "*.bak", ".git"))

    def test_version_mismatch_is_rejected(self):
        path = self.root / "plugins/precision-guard/.claude-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "9.9.9"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "manifest field"):
            validate(self.root)

    def test_unsafe_marketplace_path_is_rejected(self):
        path = self.root / ".agents/plugins/marketplace.json"
        data = json.loads(path.read_text())
        data["plugins"][0]["source"]["path"] = "../../outside"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "marketplace source"):
            validate(self.root)

    def test_marketplace_plugin_carries_the_same_license(self):
        path = self.root / "plugins/precision-guard/LICENSE"
        path.write_text("Incomplete terms")
        with self.assertRaisesRegex(ValueError, "must match the root copy"):
            validate(self.root)

    def test_builds_are_reproducible_and_checksums_match(self):
        first = build(self.work / "first", self.root)
        os.utime(self.root / "README.md", (1000000000, 1000000000))
        second = build(self.work / "second", self.root)
        self.assertEqual([p.read_bytes() for p in first], [p.read_bytes() for p in second])
        for line in first[-1].read_text().splitlines():
            digest, name = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((first[-1].parent / name).read_bytes()).hexdigest())

    def test_archives_include_licenses_and_exclude_local_artifacts(self):
        (self.root / ".env").write_text("PRIVATE=not-a-real-secret")
        (self.root / "tests/example.bak").write_text("Private backup")
        products = build(self.work / "out", self.root)
        for path in products[:2]:
            with zipfile.ZipFile(path) as bundle:
                names = set(bundle.namelist())
                self.assertIn("precision-guard/LICENSE", names)
                self.assertIn("precision-guard/NOTICE", names)
                self.assertFalse(any(name.endswith((".env", ".bak", ".pyc")) for name in names))
        with zipfile.ZipFile(products[1]) as bundle:
            self.assertIn("precision-guard/.claude-plugin/plugin.json", bundle.namelist())
            self.assertIn("precision-guard/.codex-plugin/plugin.json", bundle.namelist())
            self.assertNotIn("precision-guard/install.py", bundle.namelist())

    def test_extracted_source_can_validate_and_install_without_repository(self):
        products = build(self.work / "out", self.root)
        extracted = self.work / "extracted"
        with zipfile.ZipFile(products[0]) as bundle:
            bundle.extractall(extracted)
        source = extracted / "precision-guard"
        check = subprocess.run([sys.executable, str(source / "manage.py"), "check"], cwd=self.work, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        project = self.work / "target-project"
        project.mkdir()
        result = subprocess.run([sys.executable, str(source / "install.py"), "--project", str(project)], cwd=self.work, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "CLAUDE.md").is_file())

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks")
    def test_symlinked_release_input_is_rejected(self):
        (self.root / "tests/leak.md").symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            build(self.work / "out", self.root)

    def test_broken_documentation_link_is_rejected(self):
        with (self.root / "README.md").open("a") as stream:
            stream.write("\n[Missing document](does-not-exist.md)\n")
        with self.assertRaisesRegex(ValueError, "Broken local link"):
            validate(self.root)

    def test_output_inside_source_area_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside packaged source"):
            build(self.root / "plugins/artifacts", self.root)


if __name__ == "__main__":
    unittest.main()
