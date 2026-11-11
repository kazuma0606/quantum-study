"""研究ノート（コミット前の下書きでもよい）を、Codex に読み取り専用で監査させる。報告を保存するだけで、何も止めない。

push 前の監査（codex_pre_push.py）は、コミット済みの差分を対象にする。このスクリプトは、案を人に見せる前に、
作業中のファイルを対象にする。次の監査を、同時に起動する。

- math：数式と論理の正しさ（式の再計算、端点、量化、式番号の参照）。全文を1回。
- consistency：説明の文と、直後の式の一致。全文を1回。
- granularity：説明の粒度。Part（「# Part …」「# 付録…」の見出し）ごとに1回ずつ。
  全文を1回で読ませると、粒度の指摘が大幅に減るので、Part ごとに分け、点検項目を箇条書きで渡す。
- diff：--base で直す前のファイルを渡したときだけ。差分のまとまりごとに、直しが正しいかを確かめる。

使い方（リポジトリのルートから）:
    uv run --no-sync python tools/codex_note_audit.py 研究ノート/…/note.md
    uv run --no-sync python tools/codex_note_audit.py draft.md --base 研究ノート/…/note.md --only math consistency diff
    uv run --no-sync python tools/codex_note_audit.py 研究ノート/…/note.md --dry-run   # 起動する監査の一覧だけを表示する

報告は .codex/audit-reports/notes/<ノート名>-<日時>/ に、監査ごとの Markdown と、進捗の log.txt で保存する（Git には入れない）。
終了コードは、引数が正しくないとき（--only diff に --base がない、など）、起動する監査がないとき、
監査を1つでも完了できなかったとき 1、それ以外は 0（指摘の有無では変えない）。
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".codex" / "audit-reports" / "notes"
PART_RE = re.compile(r"^# (Part [0IVX]+|付録[A-Z])[：:]", re.MULTILINE)
ASPECTS = ("math", "consistency", "granularity", "diff")

COMMON = """研究ノートを監査してください。ファイルは編集しないでください。
対象のノート：{note}
基準：docs/note_style.md と docs/concepts.md。
名前が _source のフォルダは、読まないでください（対象外）。
報告は日本語で、重大な順に、(行番号、引用、問題、根拠、最小の直し方) の形で書いてください。問題がなければ、そう書いてください。推測で問題を作らないでください。
報告の最後に、「行ったこと」として、コマンドを実行して計算したか、読んだだけか、読んだ行の範囲、確かめられなかったことを書いてください。
"""

MATH = """観点：数式と論理の正しさ。番号つきの式と数値例を、できる範囲で独立に再計算してください。端点（0、1、空集合、次元 0 など）、量化（「すべて」「どの」「だけ」）、式番号の参照が正しいかを確かめてください。
指示書 .claude/agents/math-auditor.md の進め方と観点に従ってください（ツール名やサブエージェントの話は、読み替えてください）。"""

CONSISTENCY = """観点：説明の文と、直後の式の一致。「入れます」「使います」「なので」「から」と書いた文ごとに、その操作を実際に行った結果が、直後の式と合うかを確かめてください。
指示書 .claude/agents/proposal-auditor.md の観点に従ってください（案のファイルはなく、ノートそのものが対象です）。"""

GRANULARITY = """観点：説明の粒度。初学者（手で書き写しながら読む学習者）の目で読んでください。式の計算の正しさは、対象外です。
対象の範囲：このノートの「{part}」だけ（その見出しから、次の Part・付録・まとめの見出しの前まで）。ほかの部分は、記号の定義を確かめるために読んで構いません。
基準：docs/note_style.md（§2 と §5）と、.claude/agents/granularity-reviewer.md。

次の点検を、対象の範囲の、導出の段（「*(D1) …*」のような斜体の見出し）と、定義・数値例の段落ごとに、1つずつ行ってください。
(a) 等号・不等号1つごとに、使った規則が、その場の文に書かれているか。1つの式で、2つ以上の操作を同時に行っていないか。途中の式が抜けていないか。
(b) 「〜を使います」「(式番号) から」と書いた参照で、何に何を当てはめるかが書かれているか。参照先の式が数十行より遠いのに、内容の再掲がない所はないか。
(c) 用語と記号が、定義の文より前で使われていないか。定義がないまま使われていないか。同じ文字が2つの意味で使われていないか。
(d) 背理法、場合分け、対偶が、そうと分かるように書かれているか。
(e) その段を行う目的、選んだ値や例の理由が、書かれているか。
(f) 「だけ」「すべて」「どの」「必ず」「〜とは限りません」の断定が、言い過ぎたり、弱すぎたりしていないか。
(g) 同じ意味の語が、揺れていないか。
見つけたものは、軽いものも省かずに、すべて挙げてください（件数の上限はありません）。確かめて問題がなかった段は、段の名前だけを挙げてください。"""

DIFF = """観点：差分の監査。{patch} は、直す前のファイルから対象のノートへの差分（unified diff）です。差分のまとまり（hunk）ごとに、次を確かめてください。
(1) 足した文・式が正しいか（式は計算で確かめる）。
(2) 足した文の操作を実際に行った結果が、直後の式と合うか。式を分けた所では、分けた式を順につなぐと、元の式になるか。
(3) 前後の文とつながっているか（重複、指す先のない語、式番号のずれ、書式の崩れ）。
(4) 直したことで、新しく生じた問題（未定義の記号、言い過ぎ、定義の順の逆転）がないか。
差分に含まれない箇所への指摘は、不要です。hunk ごとに、問題がなければ「一致」と1行で書いてください。"""


def find_parts(text: str) -> list[str]:
    """ノートの Part・付録の名前（「Part I」「付録A」など）を、出てくる順に返す。"""
    return [m.group(1) for m in PART_RE.finditer(text)]


def build_jobs(note: Path, text: str, only: set[str], patch: Path | None) -> dict[str, str]:
    """監査の名前 → Codex に渡す指示、の辞書を作る。"""
    common = COMMON.format(note=note)
    jobs: dict[str, str] = {}
    if "math" in only:
        jobs["math"] = common + MATH
    if "consistency" in only:
        jobs["consistency"] = common + CONSISTENCY
    if "granularity" in only:
        parts = find_parts(text)
        if parts:
            for part in parts:
                jobs["granularity-" + part.replace(" ", "")] = common + GRANULARITY.format(part=part)
        else:
            jobs["granularity"] = common + GRANULARITY.format(part="ノートの全体")
    if "diff" in only and patch is not None:
        jobs["diff"] = common + DIFF.format(patch=patch)
    return jobs


def make_patch(base: Path, note: Path, out: Path) -> Path:
    """直す前（base）から対象（note）への unified diff を書き出す。"""
    old = base.read_text(encoding="utf-8").splitlines(keepends=True)
    new = note.read_text(encoding="utf-8").splitlines(keepends=True)
    patch = out / "changes.patch"
    patch.write_text("".join(difflib.unified_diff(old, new, str(base), str(note), n=2)), encoding="utf-8")
    return patch


def codex_command(executable: str, answer: Path) -> list[str]:
    return [executable, "exec", "--skip-git-repo-check", "--sandbox", "read-only",
            "--output-last-message", str(answer), "-"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="研究ノートを Codex に読み取り専用で監査させる（報告だけ）")
    parser.add_argument("note", type=Path, help="対象のノート（コミット前の下書きでもよい）")
    parser.add_argument("--base", type=Path, help="直す前のファイル。渡すと、差分の監査（diff）も行う")
    parser.add_argument("--only", nargs="+", choices=ASPECTS,
                        help="行う監査（既定は、math・consistency・granularity と、--base があるときの diff）")
    parser.add_argument("--timeout", type=int, default=1200, help="監査1つの上限（秒）")
    parser.add_argument("--dry-run", action="store_true", help="起動する監査の一覧だけを表示する")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    note = args.note.resolve()
    if not note.is_file():
        print(f"対象のノートがありません：{note}", file=sys.stderr)
        return 1
    if args.base is not None and not args.base.is_file():
        print(f"直す前のファイルがありません：{args.base}", file=sys.stderr)
        return 1
    if args.only is None:
        only = set(ASPECTS) if args.base is not None else set(ASPECTS) - {"diff"}
    else:
        only = set(args.only)
        if "diff" in only and args.base is None:
            print("--only diff には、--base <直す前のファイル> が必要です", file=sys.stderr)
            return 1
    text = note.read_text(encoding="utf-8")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = REPORTS / f"{note.stem}-{stamp}"

    if args.dry_run:
        jobs = build_jobs(note, text, only, out / "changes.patch" if args.base else None)
        if not jobs:
            print("起動する監査がありません", file=sys.stderr)
            return 1
        print("起動する監査：" + "、".join(jobs))
        return 0

    executable = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if executable is None:
        print("Codex CLI が見つかりません", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    patch = make_patch(args.base.resolve(), note, out) if args.base else None
    jobs = build_jobs(note, text, only, patch)
    if not jobs:
        print("起動する監査がありません", file=sys.stderr)
        return 1
    log_file = out / "log.txt"
    lock = threading.Lock()
    failed: list[str] = []

    def log(message: str) -> None:
        line = f"{datetime.datetime.now():%H:%M:%S} {message}"
        with lock:
            print(line, flush=True)
            with log_file.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def run(name: str, prompt: str) -> None:
        answer = out / f"{name}.md"
        log(f"{name}: 開始")
        start = datetime.datetime.now()
        try:
            result = subprocess.run(
                codex_command(executable, answer), cwd=ROOT, input=prompt, text=True, encoding="utf-8",
                errors="replace", capture_output=True, timeout=args.timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            failed.append(name)
            log(f"{name}: 完了できず（{type(error).__name__}）")
            return
        seconds = (datetime.datetime.now() - start).seconds
        if result.returncode != 0 or not answer.exists() or not answer.read_text(encoding="utf-8").strip():
            failed.append(name)
            (out / f"{name}.stderr.txt").write_text(result.stderr[-20000:], encoding="utf-8")
            log(f"{name}: 完了できず（終了コード {result.returncode}、{seconds} 秒）")
            return
        log(f"{name}: 終了（{seconds} 秒、{answer.stat().st_size} バイト）")

    log(f"対象：{note}（監査 {len(jobs)} 個を同時に起動、上限 {args.timeout} 秒）")
    threads = [threading.Thread(target=run, args=item) for item in jobs.items()]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    log(f"すべて終了。報告：{out}")
    if failed:
        print("完了できなかった監査：" + "、".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
