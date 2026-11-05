"""Filesystem failure tests. SPDX-License-Identifier: GPL-3.0-only."""

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from precision_guard.installer import checked_path, transform, write_change


class FilesystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "AGENTS.md"

    def test_updated_policy_replaces_only_managed_content(self):
        before = b"Custom prefix\r\n"
        after = b"Custom suffix\r\n"
        installed = transform(before, b"Old policy") + after
        updated = transform(installed, b"New policy")
        self.assertNotIn(b"Old policy", updated)
        self.assertIn(b"New policy", updated)
        self.assertEqual(transform(updated, b"", remove=True), before + after)

    def test_stale_plan_does_not_overwrite_user_edit(self):
        self.path.write_bytes(b"User changed this")
        with self.assertRaisesRegex(ValueError, "changed after inspection"):
            write_change(self.path, b"Earlier content", b"Proposed content", True)
        self.assertEqual(self.path.read_bytes(), b"User changed this")
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_replacement_failure_keeps_original_and_backup(self):
        self.path.write_bytes(b"Existing instructions")
        with patch("precision_guard.installer.os.replace", side_effect=OSError("Simulated failure")):
            with self.assertRaises(OSError):
                write_change(self.path, b"Existing instructions", b"New instructions", True)
        self.assertEqual(self.path.read_bytes(), b"Existing instructions")
        backups = list(self.root.glob("*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), b"Existing instructions")
        self.assertEqual(len(list(self.root.iterdir())), 2)

    def test_new_file_appearing_after_preflight_is_preserved(self):
        self.path.write_bytes(b"Created by someone else")
        with self.assertRaises(ValueError):
            write_change(self.path, b"", b"Our proposed content", False)
        self.assertEqual(self.path.read_bytes(), b"Created by someone else")

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks")
    def test_parent_traversal_does_not_hide_a_symlink(self):
        real = self.root / "real"
        real.mkdir()
        link = self.root / "link"
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            checked_path(link / ".." / "AGENTS.md")
