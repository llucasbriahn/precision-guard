"""Installer integration tests. SPDX-License-Identifier: GPL-3.0-only."""

from pathlib import Path
import os
import stat
import subprocess
import sys
import tempfile
import unittest

INSTALLER = Path(__file__).resolve().parents[1] / "install.py"


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve() / "project with spaces"
        self.project.mkdir()

    def run_installer(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(INSTALLER), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def test_install_both_and_repeat_without_duplicate_or_backup(self):
        self.run_installer("--project", self.project)
        before = {p.name: p.read_bytes() for p in self.project.iterdir()}
        self.run_installer("--project", self.project)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.project.iterdir()})
        self.assertEqual(set(before), {"AGENTS.md", "CLAUDE.md"})
        self.assertEqual(before["AGENTS.md"], before["CLAUDE.md"])

    def test_round_trip_preserves_unicode_crlf_and_missing_final_newline(self):
        original = "# Existing rules\r\nPreserve café and λ.".encode()
        target = self.project / "AGENTS.md"
        target.write_bytes(original)
        self.run_installer("--project", self.project, "--target", "codex")
        backups = list(self.project.glob("*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.run_installer("--project", self.project, "--target", "codex", "--remove")
        self.assertEqual(target.read_bytes(), original)

    def test_remove_preserves_later_user_content(self):
        target = self.project / "CLAUDE.md"
        self.run_installer("--file", target)
        target.write_bytes(target.read_bytes() + b"\n# Later user rules\nKeep these.\n")
        self.run_installer("--file", target, "--remove")
        self.assertEqual(target.read_bytes(), b"\n# Later user rules\nKeep these.\n")

    def test_dry_run_creates_no_files_or_directories(self):
        target = self.project / "nested" / "INSTRUCTIONS.md"
        result = self.run_installer("--file", target, "--dry-run")
        self.assertIn("(proposed)", result.stdout)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_invalid_markers_abort_before_any_target_changes(self):
        target = self.project / "CLAUDE.md"
        original = b"User content\n<!-- precision-guard:start -->\nBroken block"
        target.write_bytes(original)
        self.run_installer("--project", self.project, expected=1)
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.assertEqual(list(self.project.iterdir()), [target])

    def test_duplicate_blocks_are_rejected(self):
        target = self.project / "AGENTS.md"
        self.run_installer("--file", target)
        duplicate = target.read_bytes() * 2
        target.write_bytes(duplicate)
        self.run_installer("--file", target, expected=1)
        self.assertEqual(target.read_bytes(), duplicate)

    def test_precedence_override_requires_explicit_target(self):
        override = self.project / "AGENTS.override.md"
        override.write_text("Existing override\n")
        self.run_installer("--project", self.project, expected=1)
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.run_installer("--file", override)
        self.assertTrue(override.read_text().startswith("Existing override\n"))

    @unittest.skipUnless(os.name == "posix", "POSIX symlink and mode behavior")
    def test_symlink_file_and_parent_are_rejected(self):
        real = self.project / "real"
        real.mkdir()
        destination = real / "rules.md"
        destination.write_text("Do not change\n")
        alias = self.project / "alias.md"
        alias.symlink_to(destination)
        self.run_installer("--file", alias, expected=1)
        directory_alias = self.project / "alias-dir"
        directory_alias.symlink_to(real, target_is_directory=True)
        self.run_installer("--file", directory_alias / "new.md", expected=1)
        self.assertEqual(destination.read_text(), "Do not change\n")
        self.assertFalse((real / "new.md").exists())

    @unittest.skipUnless(os.name == "posix", "POSIX file modes")
    def test_preserves_existing_permissions(self):
        target = self.project / "AGENTS.md"
        target.write_text("Private rules\n")
        target.chmod(0o600)
        self.run_installer("--file", target)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_remove_absent_block_is_no_op(self):
        self.run_installer("--project", self.project, "--remove")
        self.assertEqual(list(self.project.iterdir()), [])

    def test_print_exports_protocol_without_frontmatter_or_mutations(self):
        result = self.run_installer("--print")
        self.assertTrue(result.stdout.startswith("# Precision Guard\n"))
        self.assertNotIn("description:", result.stdout)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_conflicting_arguments_are_rejected(self):
        self.run_installer("--print", "--project", self.project, expected=2)
        self.run_installer("--file", self.project / "rules.md", "--project", self.project, expected=2)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_non_utf8_input_is_not_overwritten(self):
        target = self.project / "AGENTS.md"
        target.write_bytes(b"\xff\xfelegacy")
        self.run_installer("--file", target, expected=1)
        self.assertEqual(target.read_bytes(), b"\xff\xfelegacy")


if __name__ == "__main__":
    unittest.main()
