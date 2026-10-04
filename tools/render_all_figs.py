"""各コードセルの実行後に、そのセルで作られた図（fig* という名前）を HTML に書き出す。

実行: uv run python tools/render_all_figs.py ノートブック.ipynb 出力フォルダ
そのあと tools/screenshot_html.ps1 出力フォルダ で PNG にして、画像を見て確認する。
"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import plotly.graph_objects as go
nb = json.load(open(sys.argv[1], encoding="utf-8")); out = Path(sys.argv[2]); stem = Path(sys.argv[1]).stem
ns = {"display": lambda *a, **k: None}; seen = set()
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code": continue
    exec("".join(cell["source"]), ns)
    for k, v in list(ns.items()):
        if k.startswith("fig") and isinstance(v, (go.Figure, go.FigureWidget)) and id(v) not in seen:
            seen.add(id(v)); p = out / f"{stem}_c{i:02d}_{k}.html"; v.write_html(p, include_plotlyjs="cdn"); print(p.name)
