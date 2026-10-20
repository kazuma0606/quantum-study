"""tools/lint_notes.py の検査（コメント・コードの除外、別行の数式、先取りの参照、ファイルの収集）。

実行:  uv run pytest tools/test_lint_notes.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint_notes as ln  # noqa: E402

BS = chr(92)  # バックスラッシュ（\tag を、エスケープの事故なく書くため）


def run(tmp_path: Path, text: str) -> dict[str, list[str]]:
    p = tmp_path / "note.md"
    p.write_text(text, encoding="utf-8")
    return ln.lint(p)


def tagged(tag: str) -> str:
    return "$$\nx=1" + BS + "tag{" + tag + "}\n$$\n"


# ---- HTML コメント ----
def test_multiline_html_comment_is_skipped(tmp_path: Path) -> None:
    assert run(tmp_path, "<!--\n同様に導く\n-->\n本文です。\n")["飛ばし表現"] == []


def test_single_line_html_comment_is_skipped(tmp_path: Path) -> None:
    assert run(tmp_path, "本文<!-- 同様に -->です。\n")["飛ばし表現"] == []


def test_skip_word_in_text_is_reported_after_a_comment(tmp_path: Path) -> None:
    res = run(tmp_path, "<!--\nコメント\n-->\n同様にして示せます。\n")
    assert len(res["飛ばし表現"]) == 1 and ":4：" in res["飛ばし表現"][0]


def test_code_fence_inside_a_comment_does_not_toggle_the_fence() -> None:
    assert (4, "同様に示す") in ln.strip_code(["<!--", "```", "-->", "同様に示す"])


def test_comment_marker_inside_inline_code_is_not_a_comment() -> None:
    lines = ["The syntax `<!--` begins a comment.", "ordinary text"]
    got = ln.strip_code(lines)
    assert (2, "ordinary text") in got and got[0][1] == lines[0]


def test_comment_marker_inside_double_backtick_code_is_not_a_comment() -> None:
    lines = ["``a <!-- b`` text", "next"]
    assert (2, "next") in ln.strip_code(lines)


def test_comment_ends_at_the_first_close_marker_even_inside_backticks() -> None:
    """HTML では、コメントの中のバッククォートは特別扱いされず、最初の --> で閉じる"""
    got = dict(ln.strip_code(["<!-- `-->`", "同様に", "後続"]))
    assert got[2] == "同様に" and got[3] == "後続"


def test_inline_code_tag_is_not_a_definition(tmp_path: Path) -> None:
    text = "例：`" + BS + "tag{A-1}` と書く。\n\n" + tagged("A-1")
    res = run(tmp_path, text)
    assert res["タグの重複"] == [] and res["先取りの参照"] == []


def test_text_around_a_same_line_display_is_counted_as_separate_paragraphs(tmp_path: Path) -> None:
    side = "".join(f"式$a_{k}$を使い、" for k in range(4)) + "あ" * 260
    res = run(tmp_path, side + " $$x=1$$ " + side + "\n")
    assert res["式の埋没"] == []


def test_degenerate_empty_comments_close_immediately() -> None:
    got = dict(ln.strip_code(["<!-->", "同様に", "<!--->", "次"]))
    assert got[2] == "同様に" and got[4] == "次"


def test_two_comments_on_one_line() -> None:
    assert ln.remove_comments("a <!-- x --> b <!-- y --> c", False) == ("a  b  c", False)


def test_unclosed_comment_hides_the_rest() -> None:
    got = ln.strip_code(["<!-- 開いたまま", "同様に"])
    assert all(t == "" for _, t in got)


# ---- コードブロック ----
def test_code_block_is_skipped(tmp_path: Path) -> None:
    assert run(tmp_path, "```\n同様に\n```\n")["飛ばし表現"] == []


def test_tilde_fence_is_skipped() -> None:
    assert ln.strip_code(["~~~", "同様に", "~~~", "x"]) == [(4, "x")]


def test_longer_fence_can_contain_a_shorter_fence() -> None:
    assert ln.strip_code(["````", "```", "同様に", "````", "x"]) == [(5, "x")]


def test_fence_with_language_and_indentation() -> None:
    assert ln.strip_code(["  ```python", "同様に", "  ```", "x"]) == [(4, "x")]


def test_comment_markers_inside_a_code_block_are_literal() -> None:
    assert ln.strip_code(["```", "<!--", "```", "本文"]) == [(4, "本文")]


# ---- インラインコード ----
def test_skip_word_inside_inline_code_is_not_reported(tmp_path: Path) -> None:
    res = run(tmp_path, "`同様に` と `(A-1)` です。\n\n" + tagged("A-1"))
    assert res["飛ばし表現"] == [] and res["先取りの参照"] == []


# ---- 別行の数式と段落 ----
def test_display_math_in_the_middle_splits_the_paragraph() -> None:
    got = ln.paragraphs([(1, "para"), (2, "$$x$$"), (3, "more")])
    assert [p for _, p in got] == ["para", "more"]


def test_display_with_text_before_and_after_the_markers() -> None:
    got = ln.paragraphs([(1, "文 $$"), (2, "x"), (3, "$$ 後"), (4, "次")])
    assert "次" in got[-1][1]


def test_display_spanning_lines_each_with_one_marker() -> None:
    got = ln.paragraphs([(1, "$$x"), (2, "y$$"), (3, "after")])
    assert got and "after" in got[-1][1]


def test_many_inline_formulas_in_a_long_paragraph_are_reported(tmp_path: Path) -> None:
    para = "".join(f"式$a_{k}$を使い、" for k in range(12)) + "あ" * 400 + "\n"
    assert len(run(tmp_path, para)["式の埋没"]) == 1


def test_many_inline_formulas_in_display_form_are_not_reported(tmp_path: Path) -> None:
    text = "".join("$$\nx=" + str(k) + "\n$$\n\n" for k in range(12)) + "短い文。\n"
    assert run(tmp_path, text)["式の埋没"] == []


# ---- 式番号 ----
def test_forward_reference_is_reported(tmp_path: Path) -> None:
    res = run(tmp_path, "ここで (A-1) を使います。\n\n" + tagged("A-1"))
    assert len(res["先取りの参照"]) == 1


def test_reference_after_the_definition_is_not_reported(tmp_path: Path) -> None:
    assert run(tmp_path, tagged("A-1") + "\nここで (A-1) を使います。\n")["先取りの参照"] == []


def test_reference_to_another_note_is_not_reported(tmp_path: Path) -> None:
    assert run(tmp_path, "本編の (A-1) を使います。\n\n" + tagged("A-1"))["先取りの参照"] == []


def test_reference_to_an_appendix_of_another_note_is_not_reported(tmp_path: Path) -> None:
    assert run(tmp_path, "本編の付録A-1 の (A-1) を使います。\n\n" + tagged("A-1"))["先取りの参照"] == []


def test_exclusion_is_not_triggered_by_the_word_alone(tmp_path: Path) -> None:
    res = run(tmp_path, "本編と同じ (A-1) を使います。\n\n" + tagged("A-1"))
    assert len(res["先取りの参照"]) == 1


def test_fullwidth_parentheses_are_recognized(tmp_path: Path) -> None:
    assert len(run(tmp_path, "先に（A-1）を使う\n\n" + tagged("A-1"))["先取りの参照"]) == 1


def test_three_part_tags_are_recognized(tmp_path: Path) -> None:
    assert len(run(tmp_path, "先に (A-5-1) を使う\n\n" + tagged("A-5-1"))["先取りの参照"]) == 1


def test_expression_like_n_minus_1_in_math_is_not_a_reference(tmp_path: Path) -> None:
    res = run(tmp_path, "和は $(n-1)$ まで。\n\n" + tagged("n-1"))
    assert res["先取りの参照"] == []


def test_duplicate_tags_are_reported(tmp_path: Path) -> None:
    res = run(tmp_path, tagged("A-1") + "\n" + tagged("A-1"))
    assert len(res["タグの重複"]) == 1


# ---- ファイルの収集 ----
def test_note_files_skips_excluded_directories_by_relative_path(tmp_path: Path) -> None:
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures" / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "b.md").write_text("x", encoding="utf-8")
    (tmp_path / "c.md").write_text("x", encoding="utf-8")
    (tmp_path / "D.MD").write_text("x", encoding="utf-8")
    files, missing = ln.note_files([str(tmp_path)])
    assert sorted(f.name for f in files) == ["D.MD", "c.md"] and missing == []


def test_note_files_works_when_the_given_folder_is_named_figures(tmp_path: Path) -> None:
    d = tmp_path / "figures"
    d.mkdir()
    (d / "a.md").write_text("x", encoding="utf-8")
    files, _ = ln.note_files([str(d)])
    assert [f.name for f in files] == ["a.md"]


def test_missing_path_is_reported() -> None:
    files, missing = ln.note_files(["this/path/does/not/exist.md"])
    assert files == [] and missing == ["this/path/does/not/exist.md"]


def test_main_does_not_crash_for_a_file_outside_the_repository(tmp_path: Path, capsys, monkeypatch) -> None:
    p = tmp_path / "n.md"
    p.write_text("同様に示す。\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["lint_notes.py", str(p)])
    assert ln.main() == 0
    assert "飛ばし表現 1" in capsys.readouterr().out
