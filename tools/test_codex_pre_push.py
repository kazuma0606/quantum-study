"""Focused regression checks for the local pre-push audit."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import codex_pre_push as hook


class PendingAuditTest(unittest.TestCase):
    def test_failed_audit_retries_from_original_base_after_remote_advances(self) -> None:
        old_base = "a" * 40
        first_head = "b" * 40
        next_head = "c" * 40
        state = "refs/heads/master"

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(hook, "PENDING", Path(directory)):
                path = hook.pending_file("origin", state)
                attempts: list[tuple[str | None, str, bool]] = []

                def fake_audit(base: str | None, head: str, dry_run: bool) -> bool:
                    attempts.append((base, head, dry_run))
                    return len(attempts) == 2

                with patch.object(hook, "audit", side_effect=fake_audit), patch.object(
                    hook, "commit_exists", return_value=True
                ), redirect_stdout(StringIO()):
                    with patch.object(sys, "argv", ["audit", "--remote", "origin"]), patch.object(
                        sys, "stdin", StringIO(f"refs/heads/master {first_head} {state} {old_base}\n")
                    ):
                        self.assertEqual(hook.main(), 0)
                    self.assertEqual(hook.read_pending(path), old_base)

                    with patch.object(sys, "argv", ["audit", "--remote", "origin"]), patch.object(
                        sys, "stdin", StringIO(f"refs/heads/master {next_head} {state} {first_head}\n")
                    ):
                        self.assertEqual(hook.main(), 0)

                self.assertEqual(attempts, [(old_base, first_head, False), (old_base, next_head, False)])
                self.assertFalse(path.exists())

    def test_missing_saved_base_falls_back_to_current_range(self) -> None:
        missing_base = "a" * 40
        current_base = "b" * 40
        head = "c" * 40
        state = "refs/heads/master"

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(hook, "PENDING", Path(directory)):
                path = hook.pending_file("origin", state)
                hook.write_pending(path, missing_base)
                stderr = StringIO()
                with patch.object(hook, "commit_exists", return_value=False), patch.object(
                    hook, "audit", return_value=False
                ) as audit, patch.object(sys, "argv", ["audit", "--remote", "origin"]), patch.object(
                    sys, "stdin", StringIO(f"refs/heads/master {head} {state} {current_base}\n")
                ), redirect_stderr(stderr):
                    self.assertEqual(hook.main(), 0)

                audit.assert_called_once_with(current_base, head, False)
                self.assertEqual(hook.read_pending(path), current_base)
                self.assertIn("saved base", stderr.getvalue())
                self.assertIn("current push range", stderr.getvalue())

    def test_blank_line_only_diff_is_skipped_but_content_change_is_kept(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def git(*args: str) -> str:
                result = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
                return result.stdout.decode().strip()

            git("init", "-q")
            git("config", "user.name", "Audit Test")
            git("config", "user.email", "audit@example.invalid")
            note = repo / "note.md"
            note.write_text("alpha\nbeta\n", encoding="utf-8")
            git("add", "note.md")
            git("commit", "-qm", "initial")
            base = git("rev-parse", "HEAD")

            note.write_text("alpha\n\nbeta\n", encoding="utf-8")
            git("commit", "-qam", "blank line")
            blank_head = git("rev-parse", "HEAD")

            note.write_text("alpha\n\ngamma\n", encoding="utf-8")
            git("commit", "-qam", "content change")
            content_head = git("rev-parse", "HEAD")

            code = repo / "sample.py"
            code.write_text('VALUE = """alpha\nbeta"""\n', encoding="utf-8")
            git("add", "sample.py")
            git("commit", "-qm", "add code")
            code_base = git("rev-parse", "HEAD")
            code.write_text('VALUE = """alpha\n\nbeta"""\n', encoding="utf-8")
            git("commit", "-qam", "blank line in string")
            code_head = git("rev-parse", "HEAD")

            with patch.object(hook, "ROOT", repo):
                files, blank_patch = hook.changes(base, blank_head)
                self.assertEqual(files, ["note.md"])
                self.assertEqual(blank_patch, "")
                files, content_patch = hook.changes(blank_head, content_head)
                self.assertEqual(files, ["note.md"])
                self.assertIn("gamma", content_patch)
                files, code_patch = hook.changes(code_base, code_head)
                self.assertEqual(files, ["sample.py"])
                self.assertIn("+\n", code_patch)

    def test_root_retry_diff_includes_older_and_newer_commits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def git(*args: str) -> str:
                result = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
                return result.stdout.decode().strip()

            git("init", "-q")
            git("config", "user.name", "Audit Test")
            git("config", "user.email", "audit@example.invalid")
            (repo / "first.md").write_text("first commit\n", encoding="utf-8")
            git("add", "first.md")
            git("commit", "-qm", "root")
            (repo / "second.py").write_text("SECOND = True\n", encoding="utf-8")
            git("add", "second.py")
            git("commit", "-qm", "later")
            head = git("rev-parse", "HEAD")

            with patch.object(hook, "ROOT", repo):
                files, patch_text = hook.changes(None, head)
                self.assertEqual(files, ["first.md", "second.py"])
                self.assertIn("first commit", patch_text)
                self.assertIn("SECOND = True", patch_text)


if __name__ == "__main__":
    unittest.main()
