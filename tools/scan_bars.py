"""ブラケット記法の縦棒の抜けを探す（表の中で | が列の区切りとして消えた不具合の検出用）。

実行: uv run python tools/scan_bars.py 研究ノート/05_量子力学/bra_ket_notation_path_integral.md
数式の中に \langle / \rangle があるのに | も \vert もない箇所を、行番号つきで表示する。
内積 <u,v> や期待値 <A> も表示されるので、目で見て判断する。
"""
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
segs = re.finditer(r"\$\$(.+?)\$\$|\$(.+?)\$", text, flags=re.S)
for m in segs:
    seg = m.group(1) or m.group(2)
    if "\\langle" in seg or "\\rangle" in seg:
        bars = seg.count("|") + seg.count("\\vert")
        kets = seg.count("\\rangle")
        bras = seg.count("\\langle")
        if bars == 0:
            line = text[: m.start()].count("\n") + 1
            print(line, seg.strip()[:110])
