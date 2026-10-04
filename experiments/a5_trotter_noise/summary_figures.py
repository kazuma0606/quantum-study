"""まとめの記事用の図を、既存の CSV から作る（計算はし直さない）。

出力（figures/）:
    summary_tradeoff_N4.png    誤差と分割数 n：3つの指標（不忠実度・トレース距離・局所的な量）、1次と2次、p = 0.005
    summary_exponents_N4.png   最適な n* と雑音 p（両対数）：指標ごとに傾きが違う

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/summary_figures.py
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
LABEL = {"infidelity": "不忠実度（状態全体）", "trace_dist": "トレース距離（状態全体）", "local_err": "局所的な量 $|\\Delta\\langle Z_0\\rangle|$"}
OFFSET = {"trace_dist": 4, "infidelity": -14, "local_err": 8}
COLOR = {"infidelity": "#1f77b4", "trace_dist": "#2ca02c", "local_err": "#d62728"}


def main() -> None:
    src = HERE / "results" / "sweep_exponents.csv"
    rows = analyze.load(src)
    N, p_show = 4, 0.005
    sel = defaultdict(dict)
    for r in rows:
        if r["n_qubits"] == N and abs(r["p"] - p_show) < 1e-12:
            sel[r["order"]][r["n_steps"]] = r

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), sharey=True)
    for ax, order in zip(axes, (1, 2)):
        ns = np.array(sorted(sel[order]))
        for m in ("infidelity", "trace_dist", "local_err"):
            e = np.array([sel[order][n][m] for n in ns])
            k = int(np.argmin(e))
            ax.semilogy(ns, e, "-", color=COLOR[m], lw=1.8, label=LABEL[m])
            ax.plot(ns[k], e[k], "o", color=COLOR[m], ms=8, mec="k")
        ax.set_xlim(0, 40)
        ax.set_xlabel("分割数 $n$")
        ax.set_title(f"{'1次（トロッター）' if order == 1 else '2次（ストラング）'}、N={N}、CNOT の雑音 p={p_show}", fontsize=11)
    axes[0].set_ylabel("誤差（丸印が最小）")
    axes[1].legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / f"summary_tradeoff_N{N}.png", dpi=150)
    plt.close(fig)

    table = analyze.analyze(rows)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), sharey=True)
    for ax, order in zip(axes, (1, 2)):
        for m in ("trace_dist", "infidelity", "local_err"):
            pts = sorted((r["p"], r["n_star"], r["n_star_pred"]) for r in table
                         if r["n_qubits"] == N and r["order"] == order and r["metric"] == m and not r["hit_nmax"])
            ps = np.array([x[0] for x in pts])
            ax.loglog(ps, [x[1] for x in pts], "o", color=COLOR[m], ms=6, label=f"{LABEL[m]}：実際の $n^*$")
            ax.loglog(ps, [x[2] for x in pts], "-", color=COLOR[m], lw=1.3, alpha=0.8)
            s = np.polyfit(np.log(ps), np.log([x[2] for x in pts]), 1)[0]
            ax.annotate(f"傾き {s:.2f}", (ps[0], pts[0][2]), (6, OFFSET[m]), textcoords="offset points", color=COLOR[m], fontsize=9)
        ax.set_xlabel("CNOT 1個あたりの雑音 $p$")
        ax.set_title(f"{'1次（トロッター）' if order == 1 else '2次（ストラング）'}、N={N}（線はモデルの予測）", fontsize=11)
    axes[0].set_ylabel("最適な分割数 $n^*$")
    axes[0].legend(fontsize=8.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / f"summary_exponents_N{N}.png", dpi=150)
    plt.close(fig)
    print("書き出し: figures/summary_tradeoff_N4.png, figures/summary_exponents_N4.png")


if __name__ == "__main__":
    main()
