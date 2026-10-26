"""PreToolUse フック：検証済みの範囲（確定範囲）を壊す Edit / Write を止める。Stop フックとしても使う（--stop）。

記録は `.claude/frozen/` 以下（tools/frozen_range.py が作る。確認は `tools/frozen_range.py show <ノート>`）。
- PreToolUse（Edit / Write）：編集を、メモリ上で実行した結果を調べ、この編集で新たに壊れる確定範囲があれば、拒否する。
- Stop（--stop）：Bash などで、フックをすり抜けた変更があれば、一度だけ差し戻す。

拒否されたら：ユーザーに、変更前・変更後を示して、許可を求める。許可が出たら、
`uv run python tools/frozen_range.py release <ノート> --from-line A --to-line B --approved-by-user "引用"` で解除してから編集する。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import frozen_range as fr  # noqa: E402

STATE = Path(__file__).with_name(".check_frozen_state")

HOW = ("ユーザーに、変更前・変更後を示して許可を求めてください。許可が出たら、"
       "`uv run python tools/frozen_range.py release <ノート> --from-line A --to-line B "
       "--approved-by-user \"許可の言葉\"` で解除してから、編集します。"
       "解除の許可なしに、確定範囲を変えてはいけません。")


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=True))


def pre_tool(data: dict) -> None:
    ti = data.get("tool_input") or {}
    name = data.get("tool_name")
    path = ti.get("file_path")
    if name not in ("Edit", "Write") or not path:
        return
    note = Path(path)
    if not note.is_absolute():
        note = Path(data.get("cwd") or ROOT) / note
    try:
        st = fr.load_state(note)
    except SystemExit as e:  # 記録が別のノートのものなど。安全側で止める
        deny(f"確定範囲の記録を読めません：{e}")
        return
    if not st or not st.get("segments"):
        return
    before = note.read_text(encoding="utf-8", errors="replace") if note.exists() else ""
    if name == "Write":
        after = ti.get("content", "")
    else:
        old, new = ti.get("old_string", ""), ti.get("new_string", "")
        b = fr.normalize(before)
        old, new = fr.normalize(old), fr.normalize(new)
        if not old or old not in b:
            return  # 一致しない編集は、ツールが失敗する
        after = b.replace(old, new) if ti.get("replace_all") else b.replace(old, new, 1)
    broken = fr.check_edit(before, after, st)
    if broken:
        lines = "\n".join(f"- {fr.describe(s)}" for s in broken[:3])
        deny("この編集は、検証済み（確定）の範囲を変えます。\n" + lines + "\n" + HOW)


def stop(data: dict) -> None:
    bad = []
    for p in fr.FROZEN_DIR.glob("*.json"):
        st = json.loads(p.read_text(encoding="utf-8"))
        if not st.get("segments"):
            continue  # すべて解除された記録は、保護の対象がない
        note = fr.ROOT / st["note"]
        if not note.exists():
            bad.append(f"{st['note']}：ノートが見つかりません（削除または移動された）")
            continue
        bad += [f"{st['note']}：{fr.describe(s)}" for s in fr.broken_segments(note.read_text(encoding="utf-8"), st)]
    count = int(STATE.read_text()) if data.get("stop_hook_active") and STATE.exists() else 0
    if not bad or count >= 1:
        STATE.unlink(missing_ok=True)
        return
    STATE.write_text(str(count + 1))
    print(json.dumps({
        "decision": "block",
        "reason": "検証済み（確定）の範囲が、変わっています。自分の編集（Bash などを含む）で変えたなら、元に戻してください。"
                  "ユーザー自身が編集したなら、そのことをユーザーに伝え、再度確定するか解除するかを確かめてください。\n"
                  + "\n".join(f"- {b}" for b in bad[:5]),
    }, ensure_ascii=True))


def main() -> None:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return
    if "--stop" in sys.argv:
        stop(data)
    else:
        pre_tool(data)


if __name__ == "__main__":
    main()
