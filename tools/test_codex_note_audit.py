"""codex_note_audit.py の、Codex を呼ばない部分のテスト（Part の検出、指示の組み立て、差分の書き出し）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_note_audit as cna  # noqa: E402

NOTE = """# 題 ―副題―

## 目次

# Part I：予想の文

## 1. 節

# Part II：離散立方体

# 付録A：補足

# まとめ
"""


def test_find_parts_returns_parts_and_appendices_in_order():
    assert cna.find_parts(NOTE) == ["Part I", "Part II", "付録A"]


def test_find_parts_ignores_sections_and_summary():
    assert cna.find_parts("# 題\n\n## 1. 節\n\n# まとめ\n") == []


def test_build_jobs_splits_granularity_by_part():
    jobs = cna.build_jobs(Path("note.md"), NOTE, {"math", "consistency", "granularity", "diff"}, None)
    assert list(jobs) == ["math", "consistency", "granularity-PartI", "granularity-PartII", "granularity-付録A"]
    assert "「Part II」だけ" in jobs["granularity-PartII"]
    assert "note.md" in jobs["math"]


def test_build_jobs_without_parts_audits_whole_note():
    jobs = cna.build_jobs(Path("note.md"), "# 題\n本文\n", {"granularity"}, None)
    assert list(jobs) == ["granularity"]
    assert "ノートの全体" in jobs["granularity"]


def test_build_jobs_adds_diff_only_with_patch():
    assert "diff" not in cna.build_jobs(Path("note.md"), NOTE, {"diff"}, None)
    jobs = cna.build_jobs(Path("note.md"), NOTE, {"diff"}, Path("changes.patch"))
    assert list(jobs) == ["diff"]
    assert "changes.patch" in jobs["diff"]


def test_make_patch_writes_unified_diff(tmp_path):
    base = tmp_path / "old.md"
    note = tmp_path / "new.md"
    base.write_text("一行目\n二行目\n", encoding="utf-8")
    note.write_text("一行目\n直した二行目\n", encoding="utf-8")
    patch = cna.make_patch(base, note, tmp_path)
    text = patch.read_text(encoding="utf-8")
    assert "-二行目" in text and "+直した二行目" in text


def test_codex_command_is_read_only():
    command = cna.codex_command("codex", Path("answer.md"))
    assert command[:5] == ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only"]
    assert command[-1] == "-"


def test_dry_run_lists_jobs(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text(NOTE, encoding="utf-8")
    assert cna.main([str(note), "--dry-run", "--only", "math", "granularity"]) == 0
    out = capsys.readouterr().out
    assert "math" in out and "granularity-PartI" in out


def test_only_diff_without_base_is_an_error(tmp_path, capsys):
    note = tmp_path / "note.md"
    note.write_text(NOTE, encoding="utf-8")
    assert cna.main([str(note), "--dry-run", "--only", "diff"]) == 1
    assert "--base" in capsys.readouterr().err
    assert cna.main([str(note), "--only", "math", "diff"]) == 1


def test_default_runs_diff_only_with_base(tmp_path, capsys):
    note = tmp_path / "note.md"
    base = tmp_path / "old.md"
    note.write_text(NOTE, encoding="utf-8")
    base.write_text(NOTE, encoding="utf-8")
    assert cna.main([str(note), "--dry-run"]) == 0
    assert "diff" not in capsys.readouterr().out
    assert cna.main([str(note), "--dry-run", "--base", str(base)]) == 0
    assert "diff" in capsys.readouterr().out


def test_missing_note_returns_error(tmp_path):
    assert cna.main([str(tmp_path / "none.md"), "--dry-run"]) == 1
