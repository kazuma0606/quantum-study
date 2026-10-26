"""frozen_range.py と check_frozen.py のテスト。実行：uv run python -m pytest tools/test_frozen_range.py"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import frozen_range as fr  # noqa: E402

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "check_frozen.py"

NOTE = """# 題

ヘッダー

段落A

$$
x=1
$$

段落B

段落C

段落D
"""


@pytest.fixture
def note(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "FROZEN_DIR", tmp_path / "frozen")
    monkeypatch.setattr(fr, "ROOT", tmp_path)
    p = tmp_path / "n.md"
    p.write_text(NOTE, encoding="utf-8")
    return p


def freeze_ab(note):
    # 段落A 〜 段落B（行 5〜 9 付近）
    text = note.read_text(encoding="utf-8").splitlines()
    a = text.index("段落A") + 1
    b = text.index("段落B") + 1
    fr.freeze(note, a, b, today="2026-10-26")
    return fr.load_state(note)


def test_paragraph_split(note):
    ps = fr.paragraphs(note.read_text(encoding="utf-8"))
    assert [p.text.splitlines()[0] for p in ps] == ["# 題", "ヘッダー", "段落A", "$$", "段落B", "段落C", "段落D"]


def test_freeze_range(note):
    st = freeze_ab(note)
    assert len(st["segments"]) == 1 and len(st["segments"][0]["hashes"]) == 3


def test_insert_inside_breaks(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    after = before.replace("$$\nx=1\n$$\n", "$$\nx=1\n$$\n\n挿入\n")
    assert fr.check_edit(before, after, st)


def test_edit_inside_breaks(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    assert fr.check_edit(before, before.replace("段落B", "段落b"), st)


def test_insert_before_and_after_ok(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    assert not fr.check_edit(before, before.replace("ヘッダー\n", "ヘッダー\n\n前の挿入\n"), st)
    assert not fr.check_edit(before, before.replace("段落B\n", "段落B\n\n後の挿入\n"), st)
    assert not fr.check_edit(before, before.replace("段落C", "段落c"), st)


def test_crlf_does_not_break(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    assert not fr.check_edit(before, before.replace("\n", "\r\n"), st)


def test_delete_breaks(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    assert fr.check_edit(before, before.replace("段落A\n\n", ""), st)


def test_move_breaks(note):
    st = freeze_ab(note)
    before = note.read_text(encoding="utf-8")
    after = before.replace("段落A\n\n", "").replace("段落C", "段落A\n\n段落C")
    assert fr.check_edit(before, after, st)


def test_already_broken_not_counted(note):
    st = freeze_ab(note)
    broken = note.read_text(encoding="utf-8").replace("段落B", "段落b")
    assert not fr.check_edit(broken, broken.replace("段落D", "段落d"), st)


def test_release_requires_quote(note):
    freeze_ab(note)
    with pytest.raises(SystemExit):
        fr.release(note, None, None, "")


def test_release_partial_and_log(note):
    freeze_ab(note)
    text = note.read_text(encoding="utf-8").splitlines()
    b = text.index("段落B") + 1
    st = fr.release(note, b, b, "段落Bは直してよい", today="2026-10-26")
    assert len(st["segments"][0]["hashes"]) == 2
    assert st["log"][-1]["approved_by_user"] == "段落Bは直してよい"
    before = note.read_text(encoding="utf-8")
    assert not fr.check_edit(before, before.replace("段落B", "段落b"), st)


def test_release_all(note):
    freeze_ab(note)
    st = fr.release(note, None, None, "全部解除", today="2026-10-26")
    assert st["segments"] == []


def run_hook(root, tool, tool_input, extra=()):
    import os
    payload = {"tool_name": tool, "tool_input": tool_input, "cwd": str(root)}
    env = {**os.environ, "FROZEN_ROOT": str(root)}
    r = subprocess.run([sys.executable, str(HOOK), *extra], input=json.dumps(payload).encode(), capture_output=True, env=env)
    return r.stdout.decode("utf-8")


@pytest.fixture
def real(tmp_path):
    """別プロセスのフック用：FROZEN_ROOT を tmp_path にして、記録とノートを作る。"""
    import os
    os.environ["FROZEN_ROOT"] = str(tmp_path)
    import importlib
    importlib.reload(fr)
    p = tmp_path / "n.md"
    p.write_text(NOTE, encoding="utf-8")
    freeze_ab(p)
    yield tmp_path, p
    del os.environ["FROZEN_ROOT"]
    importlib.reload(fr)


def test_hook_denies_edit_inside(real):
    root, p = real
    out = run_hook(root, "Edit", {"file_path": str(p), "old_string": "段落B", "new_string": "段落b"})
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_hook_allows_edit_outside(real):
    root, p = real
    assert run_hook(root, "Edit", {"file_path": str(p), "old_string": "段落D", "new_string": "段落d"}) == ""


def test_hook_denies_write_that_drops(real):
    root, p = real
    out = run_hook(root, "Write", {"file_path": str(p), "content": "# 題\n\n段落D\n"})
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_hook_ignores_other_tools_and_notes(real):
    root, p = real
    assert run_hook(root, "Read", {"file_path": str(p)}) == ""
    other = root / "other.md"
    other.write_text("x\n", encoding="utf-8")
    assert run_hook(root, "Write", {"file_path": str(other), "content": "y\n"}) == ""


def test_stop_blocks_once_when_broken(real):
    root, p = real
    p.write_text(NOTE.replace("段落B", "段落b"), encoding="utf-8")
    assert json.loads(run_hook(root, "", {}, ["--stop"]))["decision"] == "block"
