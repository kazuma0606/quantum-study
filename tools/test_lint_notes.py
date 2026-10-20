"""tools/lint_notes.py の検査（HTML コメント、コードブロックの除外、先取りの参照）。

実行:  uv run pytest tools/test_lint_notes.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint_notes as ln  # noqa: E402


def run(tmp_path: Path, text: str) -> dict[str, list[str]]:
    p = tmp_path / "note.md"
    p.write_text(text, encoding="utf-8")
    return ln.lint(p)


def test_multiline_html_comment_is_skipped(tmp_path: Path) -> None:
    res = run(tmp_path, "<!--\n同様に導く\n-->\n本文です。\n")
    assert res["飛ばし表現"] == []


def test_single_line_html_comment_is_skipped(tmp_path: Path) -> None:
    res = run(tmp_path, "本文<!-- 同様に -->です。\n")
    assert res["飛ばし表現"] == []


def test_skip_word_in_text_is_reported_after_a_comment(tmp_path: Path) -> None:
    res = run(tmp_path, "<!--\nコメント\n-->\n同様にして示せます。\n")
    assert len(res["飛ばし表現"]) == 1 and ":4：" in res["飛ばし表現"][0]


def test_code_block_is_skipped(tmp_path: Path) -> None:
    res = run(tmp_path, "```\n同様に\n```\n")
    assert res["飛ばし表現"] == []


def test_forward_reference_is_reported(tmp_path: Path) -> None:
    text = "ここで (A-1) を使います。\n\n$$\nx=1\\tag{A-1}\n$$\n"
    res = run(tmp_path, text)
    assert len(res["先取りの参照"]) == 1


def test_reference_to_another_note_is_not_reported(tmp_path: Path) -> None:
    text = "本編の (A-1) を使います。\n\n$$\nx=1\\tag{A-1}\n$$\n"
    res = run(tmp_path, text)
    assert res["先取りの参照"] == []
