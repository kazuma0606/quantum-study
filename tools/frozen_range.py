"""検証済みの範囲（確定範囲）の記録と検査。

ユーザーが「ここまで検証済み」と言った範囲を、段落ごとの内容のハッシュで、`.claude/frozen/<ノート名>.json` に記録する。
行番号ではなく内容で持つので、範囲の外で行が増減しても、範囲は動かない。

段落＝空行で区切られた塊。別行の数式（$$ … $$）も 1 つの段落。
記録は「連続した段落の並び」の組。編集の結果、その並びが、そのままの順で、連続して残っていなければ「壊れた」とみなす。
範囲の途中への挿入、書き換え、削除、移動は、すべて壊す。範囲の直前・直後への挿入は、壊さない。

使い方（リポジトリのルートで）：
  uv run python tools/frozen_range.py show   <ノート>
  uv run python tools/frozen_range.py freeze <ノート> --from-line A --to-line B     # 行 A〜B にかかる段落を確定する
  uv run python tools/frozen_range.py release <ノート> --from-line A --to-line B --approved-by-user "許可の言葉の引用"
  uv run python tools/frozen_range.py release <ノート> --all --approved-by-user "…"
  uv run python tools/frozen_range.py verify [<ノート>]    # 壊れていれば終了コード 1

解除は、ユーザーが許可した後にだけ行う。許可の言葉を引用して残す（記録は log に入る）。
フック（tools/hooks/check_frozen.py）が、Edit / Write の前に、この検査を行う。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(os.environ.get("FROZEN_ROOT") or Path(__file__).resolve().parents[1])  # FROZEN_ROOT はテスト用
FROZEN_DIR = ROOT / ".claude" / "frozen"


@dataclass
class Para:
    start: int  # 1 始まりの行番号
    end: int
    text: str

    @property
    def digest(self) -> str:
        norm = "\n".join(s.rstrip() for s in self.text.strip().splitlines())
        return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def paragraphs(text: str) -> list[Para]:
    out: list[Para] = []
    cur: list[str] = []
    start = 0
    for i, line in enumerate(normalize(text).split("\n"), start=1):
        if line.strip():
            if not cur:
                start = i
            cur.append(line)
        elif cur:
            out.append(Para(start, i - 1, "\n".join(cur)))
            cur = []
    if cur:
        out.append(Para(start, start + len(cur) - 1, "\n".join(cur)))
    return out


def state_path(note: Path) -> Path:
    return FROZEN_DIR / (note.stem + ".json")


def rel(note: Path) -> str:
    try:
        return note.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return note.as_posix()


def load_state(note: Path) -> dict | None:
    p = state_path(note)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(note: Path, st: dict) -> None:
    FROZEN_DIR.mkdir(parents=True, exist_ok=True)
    state_path(note).write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _positions(hashes: list[str], run: list[str]) -> list[int]:
    """run が現れる位置（先頭の番号）。重なる場合も数える。"""
    n = len(run)
    return [i for i in range(len(hashes) - n + 1) if hashes[i:i + n] == run]


def broken_segments(text: str, st: dict) -> list[dict]:
    """内容 text で、並びが壊れている確定範囲の組を返す。"""
    hashes = [p.digest for p in paragraphs(text)]
    # 同じ段落列が複数あるときは、確定したときの個数（count）より減っていれば、壊れとみなす
    # （どれが確定した方か区別できないので、1 つ消えたら必ず報告する）
    return [seg for seg in st.get("segments", [])
            if len(_positions(hashes, seg["hashes"])) < seg.get("count", 1)]


def describe(seg: dict) -> str:
    return f"「{seg['preview'][0]}」から「{seg['preview'][1]}」まで（{len(seg['hashes'])} 段落）"


def _runs(indices: list[int]) -> list[list[int]]:
    runs: list[list[int]] = []
    for i in sorted(set(indices)):
        if runs and runs[-1][-1] == i - 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    return runs


def _segment(paras: list[Para], idx: list[int], today: str) -> dict:
    hashes = [paras[i].digest for i in idx]
    return {
        "hashes": hashes,
        "count": len(_positions([p.digest for p in paras], hashes)),
        "preview": [paras[idx[0]].text.strip()[:30], paras[idx[-1]].text.strip()[:30]],
        "frozen_at": today,
    }


def frozen_indices(paras: list[Para], st: dict) -> list[int]:
    """いま確定されている段落の位置（先頭から数えた番号）。"""
    hashes = [p.digest for p in paras]
    idx: list[int] = []
    for seg in st.get("segments", []):
        n = len(seg["hashes"])
        for i in _positions(hashes, seg["hashes"]):  # 同じ内容が複数あれば、すべてを確定とみなす（安全側）
            idx.extend(range(i, i + n))
    return idx


def _build(paras: list[Para], idx: list[int], today: str) -> list[dict]:
    segs: list[dict] = []
    seen: set[tuple] = set()
    for run in _runs(idx):
        seg = _segment(paras, run, today)
        if tuple(seg["hashes"]) not in seen:
            seen.add(tuple(seg["hashes"]))
            segs.append(seg)
    return segs


def freeze(note: Path, from_line: int, to_line: int, today: str | None = None) -> dict:
    today = today or dt.date.today().isoformat()
    paras = paragraphs(note.read_text(encoding="utf-8"))
    st = load_state(note) or {"note": rel(note), "segments": [], "log": []}
    bad = broken_segments(note.read_text(encoding="utf-8"), st)
    if bad:
        raise SystemExit("壊れた確定範囲があります。freeze すると、その記録が消えます。先に元に戻すか、release してください：\n"
                         + "\n".join(describe(s) for s in bad))
    idx = frozen_indices(paras, st) + [i for i, p in enumerate(paras) if p.end >= from_line and p.start <= to_line]
    st["segments"] = _build(paras, idx, today)
    st["log"].append({"action": "freeze", "at": today, "lines": [from_line, to_line]})
    save_state(note, st)
    return st


def release(note: Path, from_line: int | None, to_line: int | None, quote: str, today: str | None = None) -> dict:
    if not quote.strip():
        raise SystemExit("--approved-by-user に、ユーザーの許可の言葉を引用してください")
    today = today or dt.date.today().isoformat()
    st = load_state(note)
    if st is None:
        raise SystemExit("このノートに確定範囲の記録はありません")
    paras = paragraphs(note.read_text(encoding="utf-8"))
    bad = broken_segments(note.read_text(encoding="utf-8"), st)
    if bad and from_line is not None:
        raise SystemExit("壊れた確定範囲があります。一部の解除は、その記録を消すので、できません。元に戻すか、--all で解除してください：\n"
                         + "\n".join(describe(s) for s in bad))
    cur = frozen_indices(paras, st)
    if from_line is None:
        keep: list[int] = []
    else:
        keep = [i for i in cur if not (paras[i].end >= from_line and paras[i].start <= to_line)]
    st["segments"] = _build(paras, keep, today)
    st["log"].append({"action": "release", "at": today, "lines": [from_line, to_line] if from_line else "all", "approved_by_user": quote})
    save_state(note, st)
    return st


def check_edit(before: str, after: str, st: dict) -> list[dict]:
    """編集で新たに壊れる確定範囲。編集前から壊れていたものは数えない。"""
    was = {tuple(s["hashes"]) for s in broken_segments(before, st)}
    return [s for s in broken_segments(after, st) if tuple(s["hashes"]) not in was]


def show(note: Path) -> None:
    st = load_state(note)
    if not st or not st["segments"]:
        print("確定範囲はありません")
        return
    paras = paragraphs(note.read_text(encoding="utf-8"))
    idx = frozen_indices(paras, st)
    for run in _runs(idx):
        print(f"確定：{paras[run[0]].start} 行〜{paras[run[-1]].end} 行（{len(run)} 段落）")
    for seg in broken_segments(note.read_text(encoding="utf-8"), st):
        print(f"壊れています：{describe(seg)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("show", "freeze", "release", "verify"):
        s = sub.add_parser(name)
        s.add_argument("note", nargs="?" if name == "verify" else None)
        if name in ("freeze", "release"):
            s.add_argument("--from-line", type=int)
            s.add_argument("--to-line", type=int)
        if name == "release":
            s.add_argument("--all", action="store_true")
            s.add_argument("--approved-by-user", default="")
    a = ap.parse_args()
    if a.cmd == "verify":
        notes = [Path(a.note)] if a.note else [ROOT / json.loads(p.read_text(encoding="utf-8"))["note"] for p in FROZEN_DIR.glob("*.json")]
        bad = 0
        for n in notes:
            st = load_state(n)
            if not st:
                continue
            for seg in broken_segments(n.read_text(encoding="utf-8"), st):
                print(f"{rel(n)}：壊れています：{describe(seg)}")
                bad += 1
        return 1 if bad else 0
    note = Path(a.note)
    if a.cmd == "show":
        show(note)
    elif a.cmd == "freeze":
        if a.from_line is None or a.to_line is None:
            raise SystemExit("--from-line と --to-line が要ります")
        freeze(note, a.from_line, a.to_line)
        show(note)
    else:
        if not a.all and (a.from_line is None or a.to_line is None):
            raise SystemExit("--all か、--from-line と --to-line が要ります")
        release(note, None if a.all else a.from_line, a.to_line, a.approved_by_user)
        show(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
