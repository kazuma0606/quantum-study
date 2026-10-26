"""check_proposal.py のテスト。実行：uv run python -m pytest tools/hooks/test_check_proposal.py"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_proposal as cp  # noqa: E402

HOOK = Path(__file__).with_name("check_proposal.py")

GOOD = """# 案

## 検証表

| 対象の文 | 確かめた操作 | 結果 |
|---|---|---|
| (3) 代入 | NumPy で成分を計算 | 一致 |
"""


def test_good_table_passes():
    assert cp.check_text(GOOD) == []


def test_missing_heading():
    assert cp.check_text("# 案\n\n本文だけ\n")


def test_missing_result_column():
    t = "## 検証表\n\n| 対象の文 | 操作 |\n|---|---|\n| a | b |\n"
    assert cp.check_text(t)


def test_header_only_table():
    t = "## 検証表\n\n| 対象の文 | 確かめた操作 | 結果 |\n|---|---|---|\n"
    assert cp.check_text(t)


def test_unconfirmed_row_blocks():
    t = GOOD + "| (4) 巡回性 | 未実施 | 未確認 |\n"
    assert any("未確認" in m for m in cp.check_text(t))


def test_mismatch_row_blocks():
    t = GOOD + "| (5) 和 | 計算 | 不一致 |\n"
    assert cp.check_text(t)


def test_next_section_not_counted():
    t = GOOD + "\n## 備考\n\n| a | b |\n|---|---|\n| 未確認 | 不一致 |\n"
    assert cp.check_text(t) == []


def _transcript(tmp: Path, files: list[Path], after_user: bool = True) -> Path:
    rows = [{"type": "user", "message": {"content": "案を出して"}}]
    for f in files:
        rows.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": str(f), "content": "x"}}]}})
    tp = tmp / "t.jsonl"
    tp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return tp


def _run(tp: Path) -> str:
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"transcript_path": str(tp)}).encode(),
                       capture_output=True)
    return r.stdout.decode("utf-8")


def test_hook_blocks_bad_proposal(tmp_path):
    f = tmp_path / "proposal_x.md"
    f.write_text("# 案\n", encoding="utf-8")
    out = _run(_transcript(tmp_path, [f]))
    assert json.loads(out)["decision"] == "block"


def test_hook_passes_good_proposal(tmp_path):
    f = tmp_path / "proposal_x.md"
    f.write_text(GOOD, encoding="utf-8")
    assert _run(_transcript(tmp_path, [f])) == ""


def test_hook_ignores_other_files(tmp_path):
    f = tmp_path / "notes_x.md"
    f.write_text("# 案\n", encoding="utf-8")
    assert _run(_transcript(tmp_path, [f])) == ""


def test_hook_ignores_previous_turn(tmp_path):
    f = tmp_path / "proposal_x.md"
    f.write_text("# 案\n", encoding="utf-8")
    rows = [
        {"type": "user", "message": {"content": "案を出して"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": str(f), "content": "x"}}]}},
        {"type": "user", "message": {"content": "OK"}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "適用しました"}]}},
    ]
    tp = tmp_path / "t.jsonl"
    tp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    assert _run(tp) == ""


def test_other_result_words_blocked():
    t = "## 検証表\n\n| 対象の文 | 確かめた操作 | 結果 |\n|---|---|---|\n| a | skipped | pending |\n"
    assert cp.check_text(t)


def test_result_column_not_last():
    t = "## 検証表\n\n| 結果 | 対象の文 |\n|---|---|\n| 一致 | a |\n"
    assert cp.check_text(t) == []


def test_matching_with_note_passes():
    t = "## 検証表\n\n| 対象の文 | 確かめた操作 | 結果 |\n|---|---|---|\n| a | b | 一致（文面の照合） |\n"
    assert cp.check_text(t) == []


def test_row_with_wrong_cell_count_blocked():
    t = "## 検証表\n\n| 対象の文 | 確かめた操作 | 結果 |\n|---|---|---|\n| a | b | c | 一致 |\n"
    assert cp.check_text(t)


def test_not_matching_words_blocked():
    for w in ("一致しない", "不一致", "一致せず"):
        t = f"## 検証表\n\n| 対象の文 | 確かめた操作 | 結果 |\n|---|---|---|\n| a | b | {w} |\n"
        assert cp.check_text(t), w
