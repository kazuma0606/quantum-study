"""研究ノートの目次（全体と各 Part の小目次）とアンカーを生成・更新するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/tools/build_toc.py            # christoffel_riemann_intro.md を更新して書き込む
    uv run python 研究ノート/tools/build_toc.py --check    # 書き込まずに、整合性だけ検査する
    uv run python 研究ノート/tools/build_toc.py 研究ノート/02_微分幾何/lie_derivative.md   # 別のノートを指定する

節番号の付け方は2通りに対応する:
  Part ごとの番号（"## 1." が Part ごとに 1 から始まる）       → アンカーは p{n}-1（既定）
  ノート全体の通し番号（"## 12."、"## 0-3."、"### 2-1." など） → アンカーは s12、s0-3、s2-1
  後者を使うノートには、本文のどこかに <!-- toc-style: global --> と書いておく。

やること:
  1. 各見出し（# Part…, ## 1. …, ### 4-c. …, ## A-3. … など）の直前に、アンカー <a id="..."></a> を入れる
     （見出しに数式が入っていて、Part ごとに番号が重複するため、自動のアンカーに頼らない）。
  2. <!-- toc:start --> ～ <!-- toc:end --> の間に、全体の目次（Part と節）を作る。
  3. 各 Part 見出しの直後に、その Part の小目次（節と小項目）を作る（<!-- part-toc:start --> ～ <!-- part-toc:end -->）。
  4. すべてのリンクの行き先（アンカー）が存在することを確認する。

見出しを増やす・直す・番号を振り直したときは、もう一度実行すれば目次が更新される（何度実行しても同じ結果になる）。

アンカー名の規則:
  Part n          → p{n}（Part 0 は p0）、付録 → appA / appB / appC、補遺 → supp、まとめ → summary
  Part の節 "## 2."      → p{n}-2        小項目 "### 4-c." → p{n}-4c（補遺は supp-2、supp-2c）
  付録の節 "## A-3." / "### B-2-5." → A-3 / B-2-5、付録の「まとめ」→ A-sum / B-sum / C-sum
"""

import re
import sys
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "02_微分幾何" / "christoffel_riemann_intro.md"
ROMAN = {"0": 0, "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9,
         "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15}

LATEX = {r"\Gamma": "Γ", r"\partial": "∂", r"\nabla": "∇", r"\theta": "θ", r"\phi": "φ", r"\Omega": "Ω", r"\Sigma": "Σ",
         r"\ne": "≠", r"\sqrt": "√", r"\ln": "ln", r"\det": "det", r"\tilde": "~", r"\mathbf": "", r"\mathbb": "",
         r"\operatorname": "", r"\bar": "", r"\varepsilon": "ε", r"\delta": "δ", r"\mu": "μ", r"\nu": "ν", r"\ast": "*",
         r"\mathcal": "", r"\mathfrak": "", r"\mathrm": "", r"\text": "", r"\circ": "∘", r"\times": "×",
         r"\to": "→", r"\mapsto": "↦", r"\langle": "⟨", r"\rangle": "⟩", r"\omega": "ω", r"\star": "⋆", r"\Delta": "Δ",
         r"\alpha": "α", r"\beta": "β", r"\lambda": "λ", r"\sigma": "σ", r"\psi": "ψ", r"\chi": "χ", r"\rho": "ρ",
         r"\leq": "≤", r"\geq": "≥", r"\le": "≤", r"\ge": "≥", r"\infty": "∞", r"\cdot": "·", r"\ker": "ker",
         r"\operatorname{im}": "im", r"\subset": "⊂", r"\in": "∈", r"\cap": "∩", r"\cup": "∪", r"\iff": "⇔", r"\Rightarrow": "⇒",
         # 短い記号（\in, \le, \cdot）が、長い記号の先頭に一致しないように、長い記号も登録しておく（長い順に置換する）
         r"\int": "∫", r"\inf": "inf", r"\left": "", r"\right": "", r"\cdots": "⋯", r"\ldots": "…", r"\dots": "…",
         r"\mathbb R": "ℝ", r"\mathbb C": "ℂ", r"\mathbb Z": "ℤ", r"\mathbb N": "ℕ", r"\mathbb Q": "ℚ"}


def plain(title):
    """目次のリンク文字列用に、見出しの数式をおおまかな平文にする（リンクの中に数式を入れると崩れやすいため）"""
    t = title.replace("**", "")

    def conv(m):
        s = m.group(1)
        for k in sorted(LATEX, key=len, reverse=True):
            s = s.replace(k, LATEX[k])
        s = s.replace("{}", "").replace("{", "").replace("}", "").replace("\\,", "").replace("\\ ", " ").replace("\\", "")
        return s.strip().replace("≠ ", "≠")

    t = re.sub(r"\$([^$]+)\$", conv, t)
    # Markdown の記号（_ * [ ]）が、リンク文字列の中で強調やリンクとして解釈されないようにする
    t = t.replace("[", r"\[").replace("]", r"\]").replace("_", r"\_").replace("*", r"\*")
    return t.strip()


def classify(lines, global_style=False):
    """各行を走査して、見出しの情報 [(行番号, レベル, id, 見出し文字列, 親 Part の id)] を返す"""
    out, warn = [], []
    part = None
    in_code = False
    seen_title = False
    for i, ln in enumerate(lines):
        if ln.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,3}) (.*)$", ln)
        if not m:
            continue
        lv, text = len(m.group(1)), m.group(2).strip()
        if lv == 1:
            if not seen_title:
                seen_title = True
                continue
            mp = re.match(r"^Part ([0IVX]+)：", text)
            ma = re.match(r"^付録([ABC])：", text)
            if mp:
                part = f"p{ROMAN[mp.group(1)]}"
                out.append((i, 1, part, text, part))
            elif ma:
                part = f"app{ma.group(1)}"
                out.append((i, 1, part, text, part))
            elif text.startswith("まとめ"):
                part = "summary"
                out.append((i, 1, part, text, part))
            elif text.startswith("補遺："):
                part = "supp"
                out.append((i, 1, part, text, part))
            else:
                warn.append(f"L{i + 1}: 想定外の # 見出し: {text[:40]}")
            continue
        if part is None:
            continue  # 最初の Part より前（目次など）の見出しは対象外
        hid = None
        if part.startswith("app"):
            letter = part[-1]
            ms = re.match(rf"^({letter}-\d+(?:-\d+)*)\.", text)
            if ms:
                hid = ms.group(1)
            elif text.endswith("まとめ"):
                hid = f"{letter}-sum"
        elif global_style:
            ms = re.match(r"^(\d+(?:-\d+)*(?:-[a-z])?)\.", text)
            if ms:
                hid = f"s{ms.group(1)}"
        else:
            ms = re.match(r"^(\d+)(?:-([a-z]))?\.", text)
            if ms:
                hid = f"{part}-{ms.group(1)}{ms.group(2) or ''}"
        if hid is None:
            warn.append(f"L{i + 1}: 番号のない見出し（アンカーなし）: {text[:40]}")
            continue
        out.append((i, lv, hid, text, part))
    return out, warn


def build(text):
    crlf = "\r\n" in text
    t = text.replace("\r\n", "\n")
    # 既存のアンカーと小目次を取り除く（再実行しても同じ結果になるように）
    t = re.sub(r'<a id="(?!toc")[^"]+"></a>\n\n', "", t)  # 目次の戻り先（toc）は手書きなので残す
    t = re.sub(r"<!-- part-toc:start -->\n.*?<!-- part-toc:end -->\n\n", "", t, flags=re.S)
    lines = t.split("\n")
    heads, warn = classify(lines, global_style="<!-- toc-style: global -->" in t)

    ids = [h[2] for h in heads]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        warn.append(f"アンカー名が重複: {sorted(dup)}")

    # 小目次（Part ごと）
    mini = {}
    for idx, (ln, lv, hid, text_, part) in enumerate(heads):
        if lv != 1:
            continue
        items = [(h[1], h[2], h[3]) for h in heads if h[4] == part and h[1] > 1]
        if not items:
            continue
        label = {"supp": "**この補遺の内容**"}.get(part, "**この Part の内容**" if part.startswith("p") else "**この付録の内容**")
        rows = ["<!-- part-toc:start -->", "", label, ""]
        for level, hid2, title in items:
            rows.append(f"{'  ' * (level - 2)}- [{plain(title)}](#{hid2})")
        rows += ["", "<!-- part-toc:end -->", ""]
        mini[ln] = rows

    # アンカーと小目次を、後ろの行から挿入していく（行番号がずれないように）
    out_lines = list(lines)
    for ln, lv, hid, text_, part in sorted(heads, key=lambda h: -h[0]):
        if ln in mini:  # 小目次は Part 見出しの直後（空行を1つ挟んで）に入れる
            out_lines[ln + 1:ln + 1] = [""] + mini[ln][:-1]
        out_lines[ln:ln] = [f'<a id="{hid}"></a>', ""]  # アンカーは見出しの直前（空行を挟む）

    t2 = "\n".join(out_lines)

    # 全体の目次（Part と節）
    toc = ["<!-- toc:start -->", ""]
    for ln, lv, hid, text_, part in heads:
        if lv == 1:
            toc.append(f"- [{plain(text_)}](#{hid})")
        elif lv == 2:
            toc.append(f"  - [{plain(text_)}](#{hid})")
    toc += ["", "<!-- toc:end -->"]
    if "<!-- toc:start -->" in t2:
        t2 = re.sub(r"<!-- toc:start -->.*?<!-- toc:end -->", "\n".join(toc).replace("\\", "\\\\"), t2, flags=re.S)
    else:
        warn.append("<!-- toc:start --> ～ <!-- toc:end --> の枠がない（全体の目次を入れる場所を作ってください）")

    # リンクの行き先の検査
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', t2))
    if "toc" not in anchors:
        warn.append('目次の戻り先 <a id="toc"></a> がない')
    links = re.findall(r"\]\(#([^)]+)\)", t2)
    missing = sorted({x for x in links if x not in anchors})
    if missing:
        warn.append(f"行き先のないリンク: {missing}")
    if crlf:
        t2 = t2.replace("\n", "\r\n")
    return t2, heads, warn, len(links)


def main():
    global FILE
    check = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        FILE = Path(args[0]).resolve()
    raw = FILE.read_bytes().decode("utf-8")
    new, heads, warn, nlinks = build(raw)
    n1 = sum(1 for h in heads if h[1] == 1)
    n2 = sum(1 for h in heads if h[1] == 2)
    n3 = sum(1 for h in heads if h[1] == 3)
    print(f"見出し: Part/付録 {n1}、節 {n2}、小項目 {n3}（アンカー {len(heads)}、目次リンク {nlinks}）")
    for w in warn:
        print("  警告:", w)
    if check:
        print("（--check: 書き込みません）" + ("　変更あり" if new != raw else "　変更なし"))
        return 1 if any("行き先" in w or "重複" in w for w in warn) else 0
    if new != raw:
        FILE.write_bytes(new.encode("utf-8"))
        print("更新しました:", FILE.name)
    else:
        print("変更なし（すでに最新です）")
    return 1 if any("行き先" in w or "重複" in w for w in warn) else 0


if __name__ == "__main__":
    sys.exit(main())
