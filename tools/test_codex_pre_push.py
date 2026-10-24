"""Focused regression checks for the local pre-push audit."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import codex_pre_push as hook
import audit_db
import audit_eval


class PendingAuditTest(unittest.TestCase):
    def test_failed_audit_retries_from_original_base_after_remote_advances(self) -> None:
        old_base = "a" * 40
        first_head = "b" * 40
        next_head = "c" * 40
        state = "refs/heads/master"

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(hook, "PENDING", Path(directory)):
                path = hook.pending_file("origin", state)
                attempts: list[tuple[str | None, str, bool, str]] = []

                def fake_audit(base: str | None, head: str, dry_run: bool, scope: str) -> bool:
                    attempts.append((base, head, dry_run, scope))
                    return len(attempts) == 2

                with patch.object(hook, "audit", side_effect=fake_audit), patch.object(
                    hook, "commit_exists", return_value=True
                ), redirect_stdout(StringIO()):
                    with patch.object(sys, "argv", ["audit", "--remote", "origin"]), patch.object(
                        sys, "stdin", StringIO(f"refs/heads/master {first_head} {state} {old_base}\n")
                    ):
                        self.assertEqual(hook.main(), 1)
                    self.assertEqual(hook.read_pending(path), old_base)

                    with patch.object(sys, "argv", ["audit", "--remote", "origin"]), patch.object(
                        sys, "stdin", StringIO(f"refs/heads/master {next_head} {state} {first_head}\n")
                    ):
                        self.assertEqual(hook.main(), 0)

                self.assertEqual(attempts, [(old_base, first_head, False, path.stem),
                                            (old_base, next_head, False, path.stem)])
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
                    self.assertEqual(hook.main(), 1)

                audit.assert_called_once_with(current_base, head, False, path.stem)
                self.assertEqual(hook.read_pending(path), current_base)
                self.assertIn("saved base", stderr.getvalue())
                self.assertIn("current push range", stderr.getvalue())

    def test_blank_line_only_diff_is_reviewed_along_with_content_change(self) -> None:
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
                self.assertIn("+\n", blank_patch)
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

    def test_findings_block_push_and_cached_findings_still_block(self) -> None:
        base, head, files = "a" * 40, "b" * 40, ["研究ノート/note.md"]
        answer = {
            "findings": [{"path": files[0], "line": 7, "category": "説明の順序",
                          "problem": "記号を定義前に使う", "evidence": "7行目で初出",
                          "correction": "式の前で記号を定義する"}],
            "checked": ["7行目の記号と導出の順序"], "unverified": [],
            "claims": [], "resolutions": [],
        }

        def fake_codex(args, **kwargs):
            Path(args[args.index("--output-last-message") + 1]).write_text(
                json.dumps(answer, ensure_ascii=False), encoding="utf-8"
            )
            return subprocess.CompletedProcess(args, 0)

        with tempfile.TemporaryDirectory() as directory, patch.object(hook, "REPORTS", Path(directory)), patch.object(
            audit_db, "DEFAULT_DB", Path(directory) / "audit.sqlite3"
        ), patch.object(
            hook, "changes", return_value=(files, "+new text\n")
        ), patch.object(hook, "extract_snapshot"), patch.object(hook.shutil, "which", return_value="codex"), patch.object(
            hook.subprocess, "run", side_effect=fake_codex
        ) as run, redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertFalse(hook.audit(base, head, False))
            self.assertFalse(hook.audit(base, head, False))
            self.assertEqual(run.call_count, 1)
            report = next(Path(directory).glob("*.md"))
            self.assertIn("push を中断", report.read_text(encoding="utf-8"))
            db = audit_db.connect()
            try:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM findings").fetchone()[0], 1)
            finally:
                db.close()

    def test_clean_audit_passes_and_invalid_response_blocks(self) -> None:
        files = ["研究ノート/note.md"]
        good = {"findings": [], "checked": ["変更節の導出を確認"], "unverified": [],
                "claims": [], "resolutions": []}
        self.assertEqual(hook.validate_answer(good, files), good)
        with self.assertRaises(ValueError):
            hook.validate_answer({**good, "checked": []}, files)
        with self.assertRaises(ValueError):
            hook.validate_answer({**good, "findings": [{"path": "other.md", "line": 1,
                "category": "論理", "problem": "問題", "evidence": "根拠", "correction": "修正"}]}, files)

    def test_response_and_followup_resolution_are_linked(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        with tempfile.TemporaryDirectory() as directory:
            db = audit_db.connect(Path(directory) / "audit.sqlite3")
            try:
                first = audit_db.save_audit(db, "first", "branch", "a" * 40, "b" * 40,
                    None, "findings", None, {"findings": [finding], "claims": [],
                    "resolutions": [], "checked": ["端点"], "unverified": []})
                prior_id, rows = audit_db.previous_findings(db, "branch", "a" * 40, "c" * 40)
                self.assertEqual(prior_id, first)
                finding_id = rows[0]["id"]
                with db:
                    db.execute("INSERT INTO responses(finding_id,decision,rationale,evidence_ref) VALUES(?,?,?,?)",
                               (finding_id, "fix", "範囲を修正", "研究ノート/note.md:3"))
                _, rows = audit_db.previous_findings(db, "branch", "a" * 40, "c" * 40)
                self.assertEqual(rows[0]["decision"], "fix")
                answer = {"findings": [], "claims": [], "checked": ["端点"], "unverified": [],
                          "resolutions": [{"prior_finding_id": finding_id, "status": "resolved",
                                           "evidence": "修正後は端点を除外"}]}
                hook.validate_answer(answer, [finding["path"]], {finding_id})
                second = audit_db.save_audit(db, "second", "branch", "a" * 40, "c" * 40,
                                             first, "pass", None, answer)
                self.assertEqual(db.execute("SELECT prior_audit_id FROM audits WHERE id=?",
                                            (second,)).fetchone()[0], first)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM resolutions").fetchone()[0], 1)
                with self.assertRaises(ValueError):
                    hook.validate_answer({**answer, "resolutions": []}, [finding["path"]], {finding_id})

                third = audit_db.save_audit(db, "third", "branch", "a" * 40, "d" * 40,
                    second, "findings", None, {**answer, "resolutions": [
                        {"prior_finding_id": finding_id, "status": "persists", "evidence": "端点が残る"}]})
                latest, inherited = audit_db.previous_findings(db, "branch", "a" * 40, "e" * 40)
                self.assertEqual(latest, third)
                self.assertEqual([item["id"] for item in inherited], [finding_id])
            finally:
                db.close()

    def test_resolved_findings_are_not_inherited_again(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        with tempfile.TemporaryDirectory() as directory:
            db = audit_db.connect(Path(directory) / "audit.sqlite3")
            try:
                first = audit_db.save_audit(db, "first", "branch", "a" * 40, "b" * 40,
                    None, "findings", None, {"findings": [finding], "claims": [],
                    "resolutions": [], "checked": ["端点"], "unverified": []})
                finding_id = audit_db.previous_findings(db, "branch", "a" * 40, "c" * 40)[1][0]["id"]
                audit_db.save_audit(db, "second", "branch", "a" * 40, "c" * 40, first, "pass", None,
                    {"findings": [], "claims": [], "checked": ["端点"], "unverified": [],
                     "resolutions": [{"prior_finding_id": finding_id, "status": "resolved",
                                      "evidence": "修正後は端点を除外"}]})
                self.assertEqual(audit_db.previous_findings(db, "branch", "a" * 40, "d" * 40), (None, []))
            finally:
                db.close()

    def test_audit_can_be_retried_after_report_write_failure(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        answer = {"findings": [finding], "claims": [], "resolutions": [],
                  "checked": ["端点"], "unverified": []}
        with tempfile.TemporaryDirectory() as directory:
            db = audit_db.connect(Path(directory) / "audit.sqlite3")
            try:
                audit_id = audit_db.save_audit(db, "key", "branch", "a" * 40, "b" * 40,
                                               None, "findings", None, answer)
                audit_db.mark_error(db, audit_id, "disk full")
                self.assertEqual(db.execute("SELECT status FROM audits WHERE id=?",
                                            (audit_id,)).fetchone()[0], "error")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM findings WHERE audit_id=?",
                                            (audit_id,)).fetchone()[0], 0)
                again = audit_db.save_audit(db, "key", "branch", "a" * 40, "b" * 40,
                                            None, "findings", None, answer)
                self.assertNotEqual(again, audit_id)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM findings WHERE audit_id=?",
                                            (again,)).fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT status FROM audits WHERE id=?",
                                            (audit_id,)).fetchone()[0], "error")
            finally:
                db.close()

    def test_range_refs_resolve_to_commit_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def run(*args: str) -> None:
                subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)

            run("init", "-q")
            run("config", "user.email", "test@example.com")
            run("config", "user.name", "test")
            (repo / "a.txt").write_text("1", encoding="utf-8")
            run("add", "a.txt")
            run("commit", "-q", "-m", "one")
            with patch.object(hook, "ROOT", repo):
                first = hook.resolve_commit("HEAD")
                (repo / "a.txt").write_text("2", encoding="utf-8")
                run("commit", "-q", "-am", "two")
                second = hook.resolve_commit("HEAD")
                self.assertEqual(hook.resolve_commit("HEAD~1"), first)
                with self.assertRaises(subprocess.CalledProcessError):
                    hook.resolve_commit("no-such-ref")
            self.assertEqual((len(first), len(second)), (40, 40))
            self.assertNotEqual(first, second)

    def test_cached_verdict_uses_prior_ids_stored_with_its_audit(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.sqlite3"
            db = audit_db.connect(path)
            try:
                first = audit_db.save_audit(db, "first", "branch", "a" * 40, "b" * 40, None, "findings", None,
                    {"findings": [finding], "claims": [], "resolutions": [],
                     "checked": ["端点"], "unverified": []})
                finding_id = db.execute("SELECT id FROM findings WHERE audit_id=?", (first,)).fetchone()[0]
                resolved = {"findings": [], "claims": [], "checked": ["端点"], "unverified": [],
                            "resolutions": [{"prior_finding_id": finding_id, "status": "resolved",
                                             "evidence": "修正後は端点を除外"}]}
                audit_db.save_audit(db, "second", "branch", "a" * 40, "c" * 40, first, "pass", None, resolved)
                audit_db.save_audit(db, "third", "branch", "a" * 40, "d" * 40, first, "findings", None,
                    {"findings": [finding], "claims": [], "resolutions": [
                        {"prior_finding_id": finding_id, "status": "resolved", "evidence": "解消"}],
                     "checked": ["端点"], "unverified": []})
            finally:
                db.close()
            verdict = Path(directory) / "second.json"
            verdict.write_text(json.dumps(resolved, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(hook.load_cached("second", verdict, [finding["path"]], path), resolved)
            with self.assertRaises(ValueError):
                hook.load_cached("missing", verdict, [finding["path"]], path)

    def test_retry_is_a_new_record_in_completion_order(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        empty = {"findings": [], "claims": [], "resolutions": [], "checked": ["端点"], "unverified": []}
        with tempfile.TemporaryDirectory() as directory:
            db = audit_db.connect(Path(directory) / "audit.sqlite3")
            try:
                failed = audit_db.save_audit(db, "retry", "branch", "a" * 40, "c" * 40, None, "error",
                                             None, error="timeout")
                again = audit_db.save_audit(db, "retry", "branch", "a" * 40, "c" * 40, None, "error",
                                            None, error="timeout again")
                self.assertEqual(again, failed)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM audits").fetchone()[0], 1)
                newer = audit_db.save_audit(db, "newer", "branch", "a" * 40, "d" * 40, None, "pass", None, empty)
                retried = audit_db.save_audit(db, "retry", "branch", "a" * 40, "c" * 40, newer, "findings",
                                              None, {**empty, "findings": [finding]})
                self.assertGreater(retried, newer)
                prior_id, rows = audit_db.previous_findings(db, "branch", "a" * 40, "e" * 40)
                self.assertEqual(prior_id, retried)
                self.assertEqual(len(rows), 1)
                self.assertEqual(db.execute("SELECT prior_audit_id FROM audits WHERE id=?",
                                            (retried,)).fetchone()[0], newer)
                with self.assertRaises(ValueError):
                    audit_db.save_audit(db, "retry", "branch", "a" * 40, "c" * 40, newer, "pass", None, empty)
            finally:
                db.close()

    def test_eval_scoring_uses_the_judge_for_each_finding(self) -> None:
        related = {"id": 1, "problem": "端点で不成立", "evidence": "θ=0 で sin=0", "line": 6}
        keyword_only = {"id": 2, "problem": "端点は定義済みだが別件", "evidence": "端点", "line": 6}

        def judge(finding: dict, defect: str) -> tuple[bool, str]:
            return finding["id"] == 1, "判定"

        self.assertEqual(audit_eval.score([related, keyword_only], "端点の誤り", judge),
                         {"tp": 1, "fn": 0, "fp": 1, "tn": 0})
        self.assertEqual(audit_eval.score([keyword_only], "端点の誤り", judge),
                         {"tp": 0, "fn": 1, "fp": 1, "tn": 0})
        self.assertEqual(audit_eval.score([], "端点の誤り", judge), {"tp": 0, "fn": 1, "fp": 0, "tn": 0})

    def test_eval_scoring_of_safe_case_counts_every_finding_as_false(self) -> None:
        def judge(finding: dict, defect: str) -> tuple[bool, str]:
            raise AssertionError("a safe case must not call the judge")

        findings = [{"id": 1, "problem": "別件", "evidence": "関係なし", "line": 2},
                    {"id": 2, "problem": "別件2", "evidence": "関係なし", "line": 3}]
        self.assertEqual(audit_eval.score(findings, None, judge), {"tp": 0, "fn": 0, "fp": 2, "tn": 0})
        self.assertEqual(audit_eval.score([], None, judge), {"tp": 0, "fn": 0, "fp": 0, "tn": 1})

    def test_eval_scoring_caps_judged_findings(self) -> None:
        calls: list[int] = []

        def judge(finding: dict, defect: str) -> tuple[bool, str]:
            calls.append(finding["id"])
            return False, "判定"

        findings = [{"id": number, "problem": "別件", "evidence": "関係なし", "line": 1}
                    for number in range(1, audit_eval.MAX_JUDGED + 3)]
        result = audit_eval.score(findings, "期待する欠陥", judge)
        self.assertEqual(len(calls), audit_eval.MAX_JUDGED)
        self.assertEqual(result["fp"], len(findings))

    def test_judge_answers_are_cached_and_failures_are_not_guessed(self) -> None:
        finding = {"path": "研究ノート/note.md", "line": 3, "category": "端点",
                   "problem": "端点で不成立", "evidence": "0で不成立", "correction": "範囲を狭める"}
        empty = {"findings": [finding], "claims": [], "resolutions": [], "checked": ["端点"], "unverified": []}
        with tempfile.TemporaryDirectory() as directory:
            db = audit_db.connect(Path(directory) / "audit.sqlite3")
            try:
                audit_id = audit_db.save_audit(db, "k", "branch", "a" * 40, "b" * 40, None, "findings", None, empty)
                finding_id = db.execute("SELECT id FROM findings WHERE audit_id=?", (audit_id,)).fetchone()[0]
                calls: list[int] = []

                def judge(item: dict, defect: str) -> tuple[bool, str]:
                    calls.append(item["id"])
                    return True, "一致"

                wrapped = audit_eval.cached_judge(db, "case", judge)
                item = {"id": finding_id}
                self.assertEqual(wrapped(item, "欠陥"), (True, "一致"))
                self.assertEqual(wrapped(item, "欠陥"), (True, "一致"))
                self.assertEqual(calls, [finding_id])
                self.assertEqual(wrapped(item, "書き直した欠陥"), (True, "一致"))
                self.assertEqual(calls, [finding_id, finding_id])

                def failing(item: dict, defect: str) -> tuple[bool, str]:
                    raise RuntimeError("Codex judge exited 1")

                with self.assertRaises(RuntimeError):
                    audit_eval.cached_judge(db, "other", failing)(item, "欠陥")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM eval_matches WHERE case_name='other'"
                                            ).fetchone()[0], 0)
            finally:
                db.close()


    def test_old_eval_matches_table_is_rebuilt_with_defect_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.sqlite3"
            import sqlite3
            old = sqlite3.connect(path)
            old.execute("CREATE TABLE eval_matches (id INTEGER PRIMARY KEY, finding_id INTEGER NOT NULL, "
                        "case_name TEXT NOT NULL, matched INTEGER NOT NULL, reason TEXT NOT NULL)")
            old.commit()
            old.close()
            db = audit_db.connect(path)
            try:
                columns = {row["name"] for row in db.execute("PRAGMA table_info(eval_matches)")}
                self.assertIn("defect_hash", columns)
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
