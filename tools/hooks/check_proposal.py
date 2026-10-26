"""Stop フック：ノート本文の案のファイルに、検証表があるかを、返答を送る前に調べる。

対象：このターン（直前のユーザーのメッセージより後）に、Write または Edit で、
ファイル名が proposal_*.md のファイルを書いた場合。そのファイルを読み、次を調べる。

- 見出しに「検証表」を含む節がある。
- その節に、表の行（`|` で区切られた行）が 1 行以上あり、見出し行に「結果」の列がある。
- 表の中に「未確認」「不一致」が残っていない。

満たさなければ、送るのを止めて（decision: block）、直すよう差し戻す。
案でないファイルは `proposal_` で始めない。案を書かないターンは、何もしない。
差し戻したあと（stop_hook_active が true）も調べ、2 回止めたら 3 回目は通す（無限に繰り返さないため）。

入力（標準入力の JSON）：transcript_path、stop_hook_active など。出力：止めるときだけ JSON を書く。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STATE = Path(__file__).with_name(".check_proposal_state")
RESULT_OK = re.compile(r"一致")  # 結果の欄は「一致」だけ（補足は、操作の欄に書く）。「一致しない」「一致（未確認）」なども通さない
PROPOSAL = re.compile(r"(?:^|[\\/])proposal_[^\\/]*\.md$")


def load_rows(transcript: Path) -> list[dict]:
    rows = []
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def user_text(entry: dict) -> str | None:
    """ユーザー本人のメッセージなら本文を返す（ツールの結果やシステムの通知は None）。"""
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            return None
        texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
        return "\n".join(texts) if texts else None
    return None


def proposal_files(rows: list[dict]) -> list[str]:
    """このターンに、Write / Edit で書かれた proposal_*.md のパス（重複なし、書いた順）。"""
    start = 0
    for i, r in enumerate(rows):
        if r.get("type") != "user":
            continue
        text = user_text(r)
        if text and (not r.get("isMeta") or text.lstrip().startswith("Stop hook feedback")):
            start = i + 1
    found: list[str] = []
    for r in rows[start:]:
        if r.get("type") != "assistant":
            continue
        for c in r.get("message", {}).get("content", []) or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            if c.get("name") not in ("Write", "Edit"):
                continue
            path = (c.get("input") or {}).get("file_path", "")
            if PROPOSAL.search(path) and path not in found:
                found.append(path)
    return found


def _cells(row: str) -> list[str]:
    """表の1行を、セルに分ける（`\\|` は、セルの区切りにしない）。"""
    body = row.strip().strip("|").replace("\\|", "\x00")
    return [c.replace("\x00", "\\|").strip() for c in body.split("|")]


def check_text(text: str) -> list[str]:
    """案のファイルの本文を調べて、問題の説明を返す（空なら問題なし）。"""
    lines = text.splitlines()
    sections = [i for i, s in enumerate(lines) if re.match(r"#{1,6}\s", s) and "検証表" in s]
    if not sections:
        return ["「検証表」の見出しがありません（例：`## 検証表`）"]
    start = sections[0] + 1
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"#{1,6}\s", lines[j]):
            end = j
            break
    table = [s for s in lines[start:end] if s.strip().startswith("|") and s.strip().endswith("|")]
    # 区切り行（|---|---|）は行に数えない
    rows = [s for s in table if not re.fullmatch(r"[\s|:\-]+", s.strip())]
    if len(rows) < 2:
        return ["検証表に、見出し行とデータ行がありません（列：対象の文 / 確かめた操作 / 結果）"]
    head = _cells(rows[0])
    idx = next((k for k, c in enumerate(head) if "結果" in c), None)
    if idx is None:
        return ["検証表の見出し行に「結果」の列がありません"]
    problems = []
    for s in rows[1:]:
        cells = _cells(s)
        if len(cells) != len(head):
            problems.append("列の数が見出し行と合いません（セル内の `|` は `\\vert` に）：" + s.strip()[:80])
        elif not RESULT_OK.fullmatch(cells[idx]):
            problems.append("結果が「一致」ではありません（「一致」だけ）：" + s.strip()[:80])
    return problems


def main() -> None:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return
    tp = data.get("transcript_path")
    if not tp or not Path(tp).exists():
        return
    problems: list[str] = []
    for path in proposal_files(load_rows(Path(tp))):
        p = Path(path)
        if not p.exists():
            continue
        for msg in check_text(p.read_text(encoding="utf-8", errors="replace")):
            problems.append(f"{p.name}：{msg}")
    count = int(STATE.read_text()) if data.get("stop_hook_active") and STATE.exists() else 0
    if not problems or count >= 2:
        STATE.unlink(missing_ok=True)
        return
    STATE.write_text(str(count + 1))
    print(json.dumps({
        "decision": "block",
        "reason": "ノート本文の案に、検証表の不備があります。`research-note` Skill の「案を出す前の関門」に従い、"
                  "説明の文と式を1つずつ照らして検証表（列：対象の文 / 確かめた操作 / 結果）を付け、"
                  "未確認・不一致を解消してから出してください。\n" + "\n".join(f"- {m}" for m in problems[:5]),
    }, ensure_ascii=True))


if __name__ == "__main__":
    main()
