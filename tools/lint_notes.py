"""研究ノートの「説明の粒度」を機械的に点検する（報告だけで、ファイルは編集しない）。

点検すること（方針は docs/note_style.md）：

1. 飛ばし表現：「同様に」「容易に」「明らか」「自明」「つもり」など、途中式を省くときの言い回し。
   （直後に手順が書いてあれば問題ないので、あくまで「確認のきっかけ」を出す。）
2. 式の埋没：文中の式（$...$）が多い段落。別行の数式にすると読みやすい。
3. 先取りの参照：式番号 (X-n) が、定義（\\tag{X-n}）より前の位置で参照されている。
   （同じノートの中で、読む順に後ろにある式を前で使っていないかを見る。
   「本編の (III-1)」のように他のノートの式を指す参照は対象外。）

使い方（リポジトリのルートから）:
    uv run python tools/lint_notes.py                       # 研究ノート/ 以下すべて
    uv run python tools/lint_notes.py 研究ノート/08_量子コンピュータ   # フォルダを指定
    uv run python tools/lint_notes.py path/to/note.md [...]    # ファイルを指定
    uv run python tools/lint_notes.py --summary              # ファイルごとの件数だけ

終了コードは常に 0（点検の結果は報告だけ）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "研究ノート"

SKIP_WORDS = ("同様に", "同様にして", "容易に", "明らかに", "明らか", "自明", "つもり", "ほぼ明らか", "計算すると")
TAG_RE = re.compile(r"\\tag\{([^}]+)\}")
REF_RE = re.compile(r"\(([A-Za-z]{1,3}-[0-9]+|[IVX]+-[0-9]+)\)")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)[^$\n]+\$(?!\$)")
MANY_INLINE = 7          # 1つの段落に、文中の式がこの個数以上あれば報告する
LONG_PARAGRAPH = 450     # 文字数の目安（式が多い段落のみ対象）


def note_files(args: list[str]) -> list[Path]:
    if not args:
        args = [str(NOTES)]
    out: list[Path] = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_dir():
            out += sorted(q for q in p.rglob("*.md") if "figures" not in q.parts)
        elif p.suffix == ".md":
            out.append(p)
    return out


def strip_code(lines: list[str]) -> list[tuple[int, str]]:
    """コードブロックと HTML コメント（複数行にまたがるものを含む）を除いた行を、(行番号, 本文) で返す。"""
    out: list[tuple[int, str]] = []
    in_code = False
    in_comment = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        # 1行で閉じるコメントを除く。開いたまま終わるコメントは、以降の行を読み飛ばす
        line = re.sub(r"<!--.*?-->", "", line)
        if "<!--" in line:
            line = line.split("<!--", 1)[0]
            in_comment = True
        out.append((i, line))
    return out


def paragraphs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """空行で区切った段落（表・見出し・別行の数式・HTML 行は除く）を、(開始行, 本文) で返す。"""
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    in_display = False
    for i, line in lines:
        s = line.strip()
        if s.startswith("$$"):
            # 別行の数式の開始・終了（1行で完結する $$...$$ もある）
            if s.count("$$") >= 2:
                continue
            in_display = not in_display
            continue
        if in_display:
            continue
        if not s:
            if buf:
                out.append((start, "".join(buf)))
                buf = []
            continue
        if s.startswith(("|", "#", "<", "!", ">", "---")):
            if buf:
                out.append((start, "".join(buf)))
                buf = []
            continue
        if not buf:
            start = i
        buf.append(s)
    if buf:
        out.append((start, "".join(buf)))
    return out


def lint(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    body = strip_code(lines)
    result: dict[str, list[str]] = {"飛ばし表現": [], "式の埋没": [], "先取りの参照": []}

    # 1. 飛ばし表現
    for i, line in body:
        s = line.strip()
        if s.startswith(("|", "#", "<")):
            continue
        for w in SKIP_WORDS:
            if w in s:
                k = s.index(w)
                result["飛ばし表現"].append(f"{path.name}:{i}：「{w}」…{s[max(0, k - 14):k + 18]}…")
                break

    # 2. 式の埋没
    for start, para in paragraphs(body):
        n = len(INLINE_MATH_RE.findall(para))
        if n >= MANY_INLINE and len(para) >= LONG_PARAGRAPH:
            result["式の埋没"].append(f"{path.name}:{start}：文中の式が {n} 個、{len(para)} 文字の段落")

    # 3. 先取りの参照
    defined: dict[str, int] = {}
    for i, line in body:
        for m in TAG_RE.finditer(line):
            defined.setdefault(m.group(1), i)
    for i, line in body:
        if "\\tag" in line or line.strip().startswith(("#", "<")):
            continue
        for m in REF_RE.finditer(line):
            tag = m.group(1)
            if tag not in defined or defined[tag] <= i:
                continue
            before = line[max(0, m.start() - 6):m.start()]
            if "本編の" in before or "本編" in line[max(0, m.start() - 10):m.start()]:
                continue
            result["先取りの参照"].append(f"{path.name}:{i}：({tag}) を、定義（{defined[tag]} 行目）より前で参照")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="ノートのファイルまたはフォルダ（省略時は 研究ノート/ 以下すべて）")
    ap.add_argument("--summary", action="store_true", help="ファイルごとの件数だけを出す")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    files = note_files(args.paths)
    total = {"飛ばし表現": 0, "式の埋没": 0, "先取りの参照": 0}
    for f in files:
        try:
            res = lint(f)
        except UnicodeDecodeError:
            continue
        counts = {k: len(v) for k, v in res.items()}
        for k, v in counts.items():
            total[k] += v
        if not any(counts.values()):
            continue
        rel = f.relative_to(ROOT)
        print(f"\n■ {rel}  （" + "、".join(f"{k} {v}" for k, v in counts.items() if v) + "）")
        if args.summary:
            continue
        for k, items in res.items():
            for it in items:
                print(f"  [{k}] {it}")
    print("\n合計：" + "、".join(f"{k} {v}" for k, v in total.items()) + f"（{len(files)} ファイル）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
