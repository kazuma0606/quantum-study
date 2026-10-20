"""研究ノートの「説明の粒度」を機械的に点検する（報告だけで、ファイルは編集しない）。

点検すること（方針は docs/note_style.md）：

1. 飛ばし表現：「同様に」「容易に」「明らか」「自明」「つもり」など、途中式を省くときの言い回し。
   （直後に手順が書いてあれば問題ないので、あくまで「確認のきっかけ」を出す。）
2. 式の埋没：文中の式（$...$）が多い段落。別行の数式にすると読みやすい。
3. 先取りの参照：式番号 (X-n) が、定義（\\tag{X-n}）より前の位置で参照されている。
   （同じノートの中で、読む順に後ろにある式を前で使っていないかを見る。
   「本編の (III-1)」のように他のノートの式を指す参照は対象外。参照として拾うのは、
   このノートの \\tag で定義されている番号だけ。半角・全角の括弧に対応する。）
4. タグの重複：同じ \\tag が2回以上定義されている。

コードブロック（``` と ~~~）、インラインコード、HTML コメントの中は点検しない。

注意：これは Markdown の完全な解析ではなく、「確認のきっかけ」を出す補助ツール。出力は、直す・直さないの判断材料で、
ゼロ件でも「問題なし」の証明にはならない（説明の粒度の判断は granularity-reviewer、式の正しさは math-auditor が見る）。
まれな書き方への対応（端点の細かい誤検出・見逃し）を、これ以上作り込むことは目的にしない。

使い方（リポジトリのルートから）:
    uv run python tools/lint_notes.py                       # 研究ノート/ 以下すべて
    uv run python tools/lint_notes.py 研究ノート/08_量子コンピュータ   # フォルダを指定
    uv run python tools/lint_notes.py path/to/note.md [...]    # ファイルを指定
    uv run python tools/lint_notes.py --summary              # ファイルごとの件数だけ

終了コードは、点検の結果によらず 0（報告だけ）。存在しないパスを渡したときは、警告を出して 2。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "研究ノート"

SKIP_WORDS = ("同様に", "同様にして", "容易に", "明らかに", "明らか", "自明", "つもり", "ほぼ明らか", "計算すると")
EXCLUDE_DIRS = {".git", ".lake", ".venv", "node_modules", "__pycache__", "figures"}
TAG_RE = re.compile(r"\\tag\{([^}]+)\}")
CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")        # 開きと同じ長さのバッククォート列で閉じる
INLINE_MATH_RE = re.compile(r"(?<![\$\\])\$(?!\$)(?:\\.|[^$\\\n])+\$(?!\$)")
NOTE_REF_PREFIX_RE = re.compile(r"本編(?:の付録[A-D](?:-\d+)*)?\s*の\s*$")   # 「本編の (III-1)」など
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
LIST_ITEM_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s")
MANY_INLINE = 7          # 1つの段落に、文中の式がこの個数以上あれば報告する
LONG_PARAGRAPH = 450     # 文字数の目安（式が多い段落のみ対象）
CATEGORIES = ("飛ばし表現", "式の埋没", "先取りの参照", "タグの重複")


def note_files(args: list[str]) -> tuple[list[Path], list[str]]:
    """点検するファイルの一覧と、見つからなかったパスの一覧を返す。"""
    if not args:
        args = [str(NOTES)]
    out: list[Path] = []
    missing: list[str] = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            p = Path.cwd() / p
            if not p.exists():
                p = ROOT / a
        if p.is_dir():
            for q in sorted(p.rglob("*")):
                if q.suffix.lower() != ".md" or not q.is_file():
                    continue
                if EXCLUDE_DIRS & set(q.relative_to(p).parts[:-1]):   # 渡したフォルダからの相対で判定する
                    continue
                out.append(q)
        elif p.is_file() and p.suffix.lower() == ".md":
            out.append(p)
        else:
            missing.append(a)
    return out, missing


def mask_code_spans(line: str, fill: str = "x") -> str:
    """インラインコードの部分を、同じ長さの fill に置き換える（位置を保つ）。"""
    return CODE_SPAN_RE.sub(lambda m: fill * len(m.group()), line)


def remove_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    """1行から HTML コメントの部分を取り除き、(残った本文, 行末でコメントの中にいるか) を返す。

    コメントの開始 `<!--` は、インラインコードの中では記号として扱わない。いったん始まったコメントは、
    HTML の規則どおり、バッククォートに関係なく最初の `-->` で閉じる。
    `<!-->` と `<!--->` は、HTML5 のとおり、すぐ閉じる（空の）コメントとして扱う。
    """
    masked = mask_code_spans(line)
    out: list[str] = []
    i = 0
    while i < len(line):
        if in_comment:
            j = line.find("-->", i)          # コメントの中では、バッククォートを特別扱いせず、最初の --> で閉じる
            if j == -1:
                return "".join(out), True
            i = j + 3
            in_comment = False
        else:
            j = masked.find("<!--", i)
            if j == -1:
                out.append(line[i:])
                break
            out.append(line[i:j])
            i = j + 4
            if masked.startswith(">", i):          # <!-->
                i += 1
            elif masked.startswith("->", i):       # <!--->
                i += 2
            else:
                in_comment = True
    return "".join(out), in_comment


def strip_code(lines: list[str]) -> list[tuple[int, str]]:
    """コードブロック（``` と ~~~）と HTML コメントを除いた行を、(行番号, 本文) で返す。

    - コードブロックの中では、コメントの記号を無視する。閉じるフェンスは、開いたものと同じ文字で、同じ長さ以上。
    - コメントの処理を、フェンスの判定より先に行う（コメントの中のフェンスは無視される）。
    """
    out: list[tuple[int, str]] = []
    fence: tuple[str, int] | None = None     # 開いているフェンス（文字, 長さ）
    in_comment = False
    for i, line in enumerate(lines, 1):
        if fence is not None:
            m = FENCE_RE.match(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not line.strip()[len(m.group(1)):].strip():
                fence = None
            continue
        line, in_comment = remove_comments(line, in_comment)
        m = FENCE_RE.match(line)
        if m and not in_comment:
            fence = (m.group(1)[0], len(m.group(1)))
            continue
        out.append((i, line))
    return out


def paragraphs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """空行・別行の数式・表・見出しで区切った段落を、(開始行, 本文) で返す。別行の数式の中身は含めない。"""
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    in_display = False

    def flush() -> None:
        nonlocal buf
        if buf:
            out.append((start, " ".join(buf)))
            buf = []

    def add(s: str, i: int) -> None:
        nonlocal start
        if not buf:
            start = i
        buf.append(s)

    for i, line in lines:
        if not in_display and line.strip().startswith(("|", "#", "<", "!", "---")):
            flush()                              # 表・見出し・HTML 行は、$$ を含んでいても段落に入れない
            continue
        if "$$" in line:
            # $$ の出現ごとに、別行の数式の内側かどうかを切り替える（行のどこにあってもよい）。
            # 数式の外の文章は、区切り記号ごとに、その場で段落へ追加する。数式は段落の区切り。
            segs = line.split("$$")
            for k, seg in enumerate(segs):
                s = seg.strip()
                if not in_display and s:
                    add(s, i)
                if k < len(segs) - 1:
                    in_display = not in_display
                    flush()
            continue
        s = line.strip()
        if in_display:
            continue
        if not s:
            flush()
            continue
        if s.startswith(("|", "#", "<", "!", "---")):
            flush()
            continue
        if s.startswith(">"):
            s = s.lstrip("> ").strip()
            if not s:
                flush()
                continue
        if LIST_ITEM_RE.match(s):
            flush()                              # 箇条書きは、項目ごとに別の段落として数える
        add(s, i)
    flush()
    return out


def lint(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    body = strip_code(lines)
    result: dict[str, list[str]] = {k: [] for k in CATEGORIES}

    # 1. 飛ばし表現（インラインコードの中は除く）
    for i, line in body:
        s = mask_code_spans(line.strip(), " ")
        if s.startswith(("|", "#", "<")):
            continue
        for w in SKIP_WORDS:
            if w in s:
                k = s.index(w)
                result["飛ばし表現"].append(f"{path.name}:{i}：「{w}」…{s[max(0, k - 14):k + 18]}…")
                break

    # 2. 式の埋没
    for start, para in paragraphs([(i, mask_code_spans(line, " ")) for i, line in body]):
        n = len(INLINE_MATH_RE.findall(para))
        if n >= MANY_INLINE and len(para) >= LONG_PARAGRAPH:
            result["式の埋没"].append(f"{path.name}:{start}：文中の式が {n} 個、{len(para)} 文字の段落")

    # 3・4. タグの定義と、先取りの参照
    defined: dict[str, int] = {}
    for i, line in body:
        for m in TAG_RE.finditer(mask_code_spans(line, " ")):      # インラインコードの中の \tag は定義ではない
            tag = m.group(1)
            if tag in defined:
                result["タグの重複"].append(f"{path.name}:{i}：\\tag{{{tag}}} は {defined[tag]} 行目でも定義されている")
            else:
                defined[tag] = i
    if defined:
        ref_re = re.compile(r"[（(]\s*(" + "|".join(re.escape(t) for t in sorted(defined, key=len, reverse=True)) + r")\s*[）)]")
        for i, line in body:
            text_only = INLINE_MATH_RE.sub(" ", mask_code_spans(line, " "))
            if line.strip().startswith(("#", "<")):
                continue
            for m in ref_re.finditer(text_only):
                tag = m.group(1)
                if defined[tag] <= i:
                    continue
                if NOTE_REF_PREFIX_RE.search(text_only[:m.start()]):
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
        sys.stderr.reconfigure(encoding="utf-8")

    files, missing = note_files(args.paths)
    for a in missing:
        print(f"警告：見つからないか、Markdown ではありません：{a}", file=sys.stderr)
    total = {k: 0 for k in CATEGORIES}
    for f in files:
        try:
            res = lint(f)
        except UnicodeDecodeError:
            print(f"警告：UTF-8 で読めません：{f}", file=sys.stderr)
            continue
        counts = {k: len(v) for k, v in res.items()}
        for k, v in counts.items():
            total[k] += v
        if not any(counts.values()):
            continue
        try:
            rel: Path = f.relative_to(ROOT)
        except ValueError:
            rel = f
        print(f"\n■ {rel}  （" + "、".join(f"{k} {v}" for k, v in counts.items() if v) + "）")
        if args.summary:
            continue
        for k, items in res.items():
            for it in items:
                print(f"  [{k}] {it}")
    print("\n合計：" + "、".join(f"{k} {v}" for k, v in total.items()) + f"（{len(files)} ファイル）")
    return 2 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
