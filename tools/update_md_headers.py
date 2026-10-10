"""Markdown の先頭の見出し（作成日・更新日・要約）を、git の記録からそろえる。

各ファイルのタイトル（最初の `# ` の行）のすぐ下に、次の形の引用ブロックを置く：

    > **作成** 2026-10-08　**更新** 2026-10-09
    > 何についてのファイルかの要約（2〜3 行）

- 作成日：そのファイルがリポジトリに最初に入った日（`git log --follow` の一番古いコミット）。
- 更新日：本文（この見出しのブロックを除いた部分）が最後に変わったコミットの日。見出しだけの変更は数えない。
  コミットしていない本文の変更があれば、今日の日付にする。
- 要約は人が書く。このスクリプトは日付の行だけを書き直す（見出しが無いファイルは --check で知らせる）。
  初めて見出しを入れるときは、--init <要約の JSON>（ファイルのパス → 要約の文字列のリスト）で入れる。

対象：git が追跡している .md のうち、Claude Code の設定（.claude/、CLAUDE.md）と、自動で作られる表（results/ の下）を除くもの。

実行（リポジトリのルートから）:
    uv run python tools/update_md_headers.py           # 日付を書き直す（コミットの前に実行する）
    uv run python tools/update_md_headers.py --check   # 見出しが無い・日付が古いファイルを知らせる（書き込まない）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE_RE = re.compile(r"^> \*\*作成\*\* (\d{4}-\d{2}-\d{2})　\*\*更新\*\* (\d{4}-\d{2}-\d{2})\s*$")
EXCLUDE = (".claude/", "CLAUDE.md")


def git(*args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8").stdout


def targets() -> list[str]:
    files = [f for f in git("ls-files", "*.md").splitlines() if f]
    return [f for f in files if not f.startswith(EXCLUDE) and "/results/" not in f]


def split_header(text: str) -> tuple[int, int, int] | None:
    """(タイトルの行, 見出しのブロックの最初の行, 最後の行の次) を返す。見出しのブロックが無ければ (タイトルの行, -1, -1)。"""
    lines = text.split("\n")
    title = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if title is None:
        return None
    j = title + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and DATE_RE.match(lines[j]):
        k = j
        while k < len(lines) and lines[k].startswith(">"):
            k += 1
        return title, j, k
    return title, -1, -1


def strip_header(text: str) -> str:
    """見出しのブロックを除いた本文（更新日の判定に使う）。"""
    pos = split_header(text)
    if not pos or pos[1] < 0:
        return text
    lines = text.split("\n")
    title, a, b = pos
    rest = lines[b:]
    while rest and not rest[0].strip():
        rest = rest[1:]
    return "\n".join(lines[: title + 1] + [""] + rest)


def history(path: str) -> list[tuple[str, str, str]]:
    """(コミット, 日付, そのときのパス) を新しい順に。名前の変更もたどる。"""
    out = git("log", "--follow", "--name-only", "--format=@@%H %ad", "--date=short", "--", path)
    hist, cur = [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            h, d = line[2:].split()
            cur = [h, d]
        elif line.strip() and cur:
            hist.append((cur[0], cur[1], line.strip()))
            cur = None
    return hist


def dates(path: str) -> tuple[str, str]:
    today = dt.date.today().isoformat()
    hist = history(path)
    if not hist:
        return today, today
    created = hist[-1][1]
    work = (ROOT / path).read_text(encoding="utf-8")
    head = git("show", f"HEAD:{path}")
    if strip_header(work) != strip_header(head):
        return created, today
    # 本文が最後に変わったコミット：新しい順に、ひとつ前の版と本文（見出しを除く）を比べる
    versions = [strip_header(git("show", f"{h}:{p}")) for h, _, p in hist]
    for i in range(len(hist) - 1):
        if versions[i] != versions[i + 1]:
            return created, hist[i][1]
    return created, created


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--init", help="見出しが無いファイルに、要約を入れて見出しを作る（JSON：パス → 要約の行のリスト）")
    args = ap.parse_args()
    summaries = json.loads(Path(args.init).read_text(encoding="utf-8")) if args.init else {}
    missing, changed = [], []
    for f in targets():
        p = ROOT / f
        text = p.read_text(encoding="utf-8")
        pos = split_header(text)
        if pos is None:
            missing.append(f"{f}（タイトルの行が無い）")
            continue
        created, updated = dates(f)
        date_line = f"> **作成** {created}　**更新** {updated}"
        lines = text.split("\n")
        title, a, b = pos
        if a < 0:
            if f not in summaries:
                missing.append(f)
                continue
            block = [date_line] + [f"> {s}" for s in summaries[f]]
            rest = lines[title + 1:]
            while rest and not rest[0].strip():
                rest = rest[1:]
            new_lines = lines[: title + 1] + [""] + block + [""] + rest
        else:
            if lines[a] == date_line:
                continue
            new_lines = lines[:a] + [date_line] + lines[a + 1:]
        changed.append(f"{f}：{date_line[2:]}")
        if not args.check:
            p.write_text("\n".join(new_lines), encoding="utf-8")
    for c in changed:
        print(("直すべき：" if args.check else "書き直し：") + c)
    for m in missing:
        print(f"見出しが無い：{m}")
    print(f"対象 {len(targets())} 件、{'直すべき' if args.check else '書き直し'} {len(changed)} 件、見出しが無い {len(missing)} 件")
    if args.check and (changed or missing):
        sys.exit(1)


if __name__ == "__main__":
    main()
