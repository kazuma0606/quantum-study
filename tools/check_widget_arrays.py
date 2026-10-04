"""ノートブックのコードを実行し、スライダーを動かした後、FigureWidget のトレースに numpy 配列が残っていないかを調べる。
さらに、ブラウザが型付き配列を「添字 → 値」の辞書で送り返す状況を、各トレースの x について再現する。

実行: uv run python tools/check_widget_arrays.py ノートブック1.ipynb ノートブック2.ipynb ...
「問題のあるトレース： 0」なら合格。
"""
import json
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import ipywidgets as W
import plotly.graph_objects as go
from plotly.basewidget import BaseFigureWidget


def find_arrays(obj, path=()):
    if isinstance(obj, np.ndarray):
        yield path
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from find_arrays(v, path + (k,))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from find_arrays(v, path + (i,))


bad = 0
for nbpath in sys.argv[1:]:
    nb = json.load(open(nbpath, encoding="utf-8"))
    ns = {"display": lambda *a, **k: None}
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            exec("".join(cell["source"]), ns)
    sliders = [v for v in ns.values() if isinstance(v, (W.FloatSlider, W.IntSlider, W.Dropdown, W.SelectionSlider))]
    for sl in sliders:                                   # スライダーを動かして、コールバックを呼ぶ
        if isinstance(sl, (W.FloatSlider, W.IntSlider)):
            for val in (sl.min, (sl.min + sl.max) // 2 if isinstance(sl, W.IntSlider) else (sl.min + sl.max) / 2, sl.max, sl.value):
                sl.value = val
        elif isinstance(sl, W.SelectionSlider):
            for _, val in sl.options:
                sl.value = val
        else:
            for opt in sl.options:
                sl.value = opt[1] if isinstance(opt, tuple) else opt
    figs = {k: v for k, v in ns.items() if isinstance(v, go.FigureWidget)}
    for name, fig in figs.items():
        for i, tr in enumerate(fig.data):
            arrays = list(find_arrays(tr._props))
            if arrays:
                bad += 1
                print(f"  {nbpath} {name}.data[{i}]：numpy 配列が残っている {arrays[:3]}")
            if isinstance(tr._props.get("x"), np.ndarray):   # 型付き配列だけ、ブラウザが辞書で送り返す
                defaults = {"x": {str(k): 0.0 for k in range(3)}}
                try:
                    BaseFigureWidget._remove_overlapping_props(dict(tr._props), defaults)
                except (ValueError, AssertionError) as e:
                    bad += 1
                    print(f"  {nbpath} {name}.data[{i}]：{e}")
    print(f"{nbpath}：FigureWidget {len(figs)} 個、スライダー {len(sliders)} 個を確認")
print("問題のあるトレース：", bad)
sys.exit(1 if bad else 0)
